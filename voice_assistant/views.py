import time

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from users.ai import ErreurIA

from .services import repondre


TYPES_AUDIO = {"audio/wav", "audio/x-wav", "audio/webm", "audio/ogg", "audio/mpeg",
               "audio/mp3", "audio/mp4", "audio/aac", "audio/flac"}


@login_required
def assistant(request):
    return render(request, "voice_assistant/assistant.html")


def _limite_atteinte(utilisateur_id):
    cle = f"voice-assistant:{utilisateur_id}:{int(time.time() // 60)}"
    try:
        valeur = cache.incr(cle)
    except ValueError:
        cache.set(cle, 1, timeout=70)
        valeur = 1
    return valeur > settings.ASSISTANT_RATE_LIMIT


@login_required
@require_POST
def message(request):
    if _limite_atteinte(request.user.pk):
        return JsonResponse({"erreur": "Trop de demandes. Réessayez dans une minute."}, status=429)
    question = request.POST.get("question", "").strip()
    audio = request.FILES.get("audio")
    if not question and not audio:
        return JsonResponse({"erreur": "Écrivez une question ou utilisez le micro."}, status=400)
    if len(question) > 1000:
        return JsonResponse({"erreur": "La question est trop longue (1 000 caractères maximum)."}, status=400)
    donnees, mime = None, ""
    if audio:
        mime = (audio.content_type or "").split(";")[0].lower()
        if mime not in TYPES_AUDIO:
            return JsonResponse({"erreur": "Format audio non pris en charge."}, status=400)
        if audio.size > settings.ASSISTANT_AUDIO_MAX_BYTES:
            return JsonResponse({"erreur": "Enregistrement trop volumineux (5 Mo maximum)."}, status=400)
        donnees = audio.read()
    historique = request.session.get("assistant_historique", [])[-6:]
    try:
        resultat = repondre(request.user, question, donnees, mime, historique, request.LANGUAGE_CODE[:2])
    except ErreurIA:
        return JsonResponse({"erreur": "La reconnaissance vocale Gemini est indisponible. Vérifiez GEMINI_API_KEY ou réessayez."}, status=503)
    historique.extend([
        {"role": "utilisateur", "texte": (resultat["transcription"] or question)[:1000]},
        {"role": "assistant", "texte": resultat["reponse"][:2000]},
    ])
    request.session["assistant_historique"] = historique[-8:]
    return JsonResponse(resultat)


@login_required
@require_POST
def effacer(request):
    request.session.pop("assistant_historique", None)
    return redirect("voice_assistant:assistant")
