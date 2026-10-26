from datetime import timedelta
from unittest import mock

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from food_rescue.models import AnnonceSurplus
from impact.models import TransactionPoints
from users.models import Utilisateur

from .services import construire_contexte, repondre


@override_settings(GEMINI_API_KEY="", ASSISTANT_RATE_LIMIT=100)
class AssistantVocalTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = Utilisateur.objects.create_user(
            username="amina", email="amina@example.com", password="MotDePasse123!", first_name="Amina"
        )
        self.other = Utilisateur.objects.create_user(
            username="sami", email="sami@example.com", password="MotDePasse123!"
        )
        TransactionPoints.objects.create(utilisateur=self.user, montant=35, motif="Test")
        self.annonce = AnnonceSurplus.objects.create(
            donateur=self.other, titre="Couscous solidaire", description="Deux portions",
            categorie="PLAT_PREPARE", quantite=2, unite="PORTION", conservation="REFRIGERE",
            ville="Tunis", lieu_collecte="12 rue privée, Tunis",
            disponible_jusquau=timezone.now() + timedelta(days=1), statut="DISPONIBLE",
        )
        self.client.force_login(self.user)

    def test_page_exige_authentification(self):
        self.client.logout()
        response = self.client.get(reverse("voice_assistant:assistant"))
        self.assertEqual(response.status_code, 302)

    def test_contexte_ne_contient_pas_adresse_ni_identite_donateur(self):
        contexte = construire_contexte(self.user)
        texte = str(contexte)
        self.assertIn("Couscous solidaire", texte)
        self.assertNotIn("12 rue privée", texte)
        self.assertNotIn("sami@example.com", texte)
        self.assertNotIn("sami", texte)

    def test_repli_local_comprend_question_tunisienne(self):
        resultat = repondre(self.user, "9adech 3andi points?")
        self.assertEqual(resultat["langue"], "ar")
        self.assertIn("35", resultat["reponse"])
        self.assertEqual(resultat["source"], "LOCAL")

    def test_message_texte_et_historique_session(self):
        response = self.client.post(reverse("voice_assistant:message"), {"question": "Combien de points ?"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("35", response.json()["reponse"])
        self.assertEqual(len(self.client.session["assistant_historique"]), 2)

    def test_audio_refuse_un_format_invalide(self):
        fichier = SimpleUploadedFile("audio.txt", b"not audio", content_type="text/plain")
        response = self.client.post(reverse("voice_assistant:message"), {"audio": fichier})
        self.assertEqual(response.status_code, 400)

    @mock.patch("voice_assistant.views.repondre")
    def test_audio_est_transmis_a_gemini_sans_stockage(self, service):
        service.return_value = {"transcription": "chnowa fama", "reponse": "Fama couscous.",
                                "langue": "ar", "suggestions": [], "source": "GEMINI"}
        fichier = SimpleUploadedFile("question.webm", b"webm-bytes", content_type="audio/webm;codecs=opus")
        response = self.client.post(reverse("voice_assistant:message"), {"audio": fichier})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(service.call_args.args[2], b"webm-bytes")
        self.assertFalse(hasattr(self.user, "audio"))

    def test_selecteur_arabe_active_rtl(self):
        response = self.client.post(reverse("set_language"), {"language": "ar", "next": reverse("voice_assistant:assistant")}, follow=True)
        self.assertContains(response, 'lang="ar"')
        self.assertContains(response, 'dir="rtl"')
        self.assertContains(response, "المساعد الصوتي")
