"""Assistant Gemini en lecture seule, ancré dans les données autorisées du compte."""
import base64
import json
import unicodedata

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.utils import timezone

from community.models import NotificationCommunaute, Publication
from food_rescue.models import AnnonceSurplus, ProfilBeneficiaire, ReservationSurplus
from impact.models import TransactionPoints
from planning.models import PlanMenu
from repas.models import Repas
from users.ai import ErreurIA, generer


LANGUES = {"fr": "français", "en": "English", "ar": "العربية / تونسي"}


def _profil(utilisateur):
    try:
        return utilisateur.profil
    except (AttributeError, ObjectDoesNotExist):
        return None


def construire_contexte(utilisateur):
    """Retourne seulement des données lisibles par cet utilisateur, sans données sensibles."""
    profil = _profil(utilisateur)
    repas = Repas.objects.filter(utilisateur=utilisateur).prefetch_related("elements")[:5]
    plans = PlanMenu.objects.filter(utilisateur=utilisateur).prefetch_related("menus")[:2]
    dons = AnnonceSurplus.objects.filter(donateur=utilisateur)[:5]
    reservations = ReservationSurplus.objects.filter(beneficiaire=utilisateur).select_related("annonce")[:5]
    disponibles = AnnonceSurplus.objects.filter(
        statut=AnnonceSurplus.Statut.DISPONIBLE,
        disponible_jusquau__gt=timezone.now(),
    ).values("titre", "categorie", "quantite", "unite", "ville", "disponible_jusquau")[:8]
    beneficiaire = ProfilBeneficiaire.objects.filter(utilisateur=utilisateur).first()
    return {
        "compte": {"prenom": utilisateur.first_name or utilisateur.username, "role": utilisateur.role},
        "profil_alimentaire": None if not profil else {
            "regime": profil.get_regime_display(), "aliments_aimes": profil.aliments_aimes,
            "aliments_evites": profil.aliments_evites, "taille_foyer": profil.taille_foyer,
            "ville": profil.ville,
        },
        "repas_recents": [{
            "date": str(r.date), "type": r.get_type_repas_display(), "note": r.note,
            "aliments": [e.aliment for e in r.elements.all()], "co2_kg": r.co2_kg,
        } for r in repas],
        "plans_recents": [{
            "semaine": str(p.semaine_du), "objectif_co2": float(p.objectif_co2),
            "menus": [m.nom for m in p.menus.all()[:14]],
        } for p in plans],
        "points": TransactionPoints.objects.filter(utilisateur=utilisateur).aggregate(
            total=Sum("montant")
        )["total"] or 0,
        "eligibilite_food_rescue": beneficiaire.get_statut_display() if beneficiaire else "non demandée",
        "mes_dons": [{"titre": a.titre, "statut": a.get_statut_display()} for a in dons],
        "mes_reservations": [{
            "surplus": r.annonce.titre, "statut": r.get_statut_display(),
            "heure_collecte": r.heure_collecte.isoformat(),
        } for r in reservations],
        # Les annonces sont publiques, mais lieu_collecte et donateur sont volontairement exclus.
        "surplus_publics": [{**a, "quantite": str(a["quantite"]),
                              "disponible_jusquau": a["disponible_jusquau"].isoformat()} for a in disponibles],
        "communaute": {
            "mes_publications": Publication.objects.filter(auteur=utilisateur).count(),
            "notifications_non_lues": NotificationCommunaute.objects.filter(
                destinataire=utilisateur, lue_le__isnull=True
            ).count(),
        },
    }


def _prompt(question, contexte, historique, langue_preferee):
    return (
        "Tu es l'assistant EcoAssiette. Tu comprends le français, l'anglais, l'arabe standard et le tounsi "
        "(darija tunisienne en alphabet arabe ou latin, y compris 3/7/9, et les phrases mélangées). "
        "Réponds dans la langue utilisée; si elle mélange les langues, réponds naturellement en tounsi. "
        "Utilise UNIQUEMENT le contexte JSON fourni. N'invente aucune donnée et dis quand elle manque. "
        "Tu es en lecture seule: ne prétends jamais avoir créé, modifié, réservé ou supprimé quelque chose. "
        "Ne révèle aucune adresse privée, code de collecte ou donnée d'un autre utilisateur. "
        "Pour la nutrition et la sécurité alimentaire, reste prudent. "
        "Retourne uniquement un objet JSON avec: "
        '"transcription" (question entendue, vide si texte), "reponse", '
        '"langue" parmi "fr", "en", "ar", et "suggestions" (0 à 3 questions courtes). '
        f"Langue d'interface: {LANGUES.get(langue_preferee, 'français')}. "
        f"Historique récent: {json.dumps(historique[-6:], ensure_ascii=False)}. "
        f"Contexte autorisé: {json.dumps(contexte, ensure_ascii=False)}. "
        f"Question texte éventuelle: {question or '[audio joint]'}"
    )


def _valider(brut, question):
    if not isinstance(brut, dict) or not str(brut.get("reponse", "")).strip():
        raise ErreurIA("Réponse de l'assistant invalide")
    langue = str(brut.get("langue", "fr")).lower()
    if langue not in LANGUES:
        langue = "fr"
    suggestions = brut.get("suggestions", [])
    if not isinstance(suggestions, list):
        suggestions = []
    return {
        "transcription": str(brut.get("transcription") or question or "")[:1000],
        "reponse": str(brut["reponse"]).strip()[:3000], "langue": langue,
        "suggestions": [str(x).strip()[:140] for x in suggestions[:3] if str(x).strip()],
        "source": "GEMINI",
    }


def _normaliser(texte):
    return unicodedata.normalize("NFKD", texte.casefold()).encode("ascii", "ignore").decode()


def reponse_locale(question, contexte):
    q = _normaliser(question)
    tounsi = any(x in q for x in ("chneya", "chnowa", "9adech", "kifech", "najem", "andi", "fama"))
    langue = "ar" if tounsi or any("\u0600" <= c <= "\u06ff" for c in question) else "en" if any(
        x in f" {q} " for x in (" what ", " how ", " my ", " available ")
    ) else "fr"
    if "point" in q:
        contenu = f"عندك {contexte['points']} points." if langue == "ar" else (
            f"You currently have {contexte['points']} points." if langue == "en" else
            f"Vous avez actuellement {contexte['points']} points.")
    elif any(x in q for x in ("surplus", "dispon", "fama", "available")):
        titres = [x["titre"] for x in contexte["surplus_publics"][:5]]
        liste = ", ".join(titres) if titres else "—"
        contenu = (f"Fama hedhouma disponibles: {liste}." if langue == "ar" else
                   f"Available surplus: {liste}." if langue == "en" else
                   f"Surplus disponibles : {liste}.")
    elif "eligib" in q or "etudiant" in q or "association" in q:
        contenu = f"Statut Food Rescue : {contexte['eligibilite_food_rescue']}."
    else:
        contenu = ("Nefhem tounsi. Es2elni 3la les repas, points, planning wala Food Rescue."
                   if langue == "ar" else
                   "I can answer about your meals, points, meal plans and Food Rescue."
                   if langue == "en" else
                   "Je peux répondre sur vos repas, vos points, vos menus et Food Rescue.")
    return {"transcription": question, "reponse": contenu, "langue": langue,
            "suggestions": [], "source": "LOCAL"}


def repondre(utilisateur, question="", audio=None, mime="", historique=None, langue="fr"):
    contexte = construire_contexte(utilisateur)
    parts = []
    if audio:
        parts.append({"inlineData": {"mimeType": mime, "data": base64.b64encode(audio).decode()}})
    parts.append({"text": _prompt(question, contexte, historique or [], langue)})
    try:
        return _valider(generer(parts, temperature=0.25), question)
    except ErreurIA:
        if audio:
            raise
        return reponse_locale(question, contexte)
