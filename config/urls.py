from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from users import pwa

admin.site.site_header = "EcoAssiette — Administration"
admin.site.site_title = "EcoAssiette"
admin.site.index_title = "Tableau de bord"

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("sw.js", pwa.service_worker, name="service_worker"),          # application installable (PWA)
    path("hors-ligne/", pwa.hors_ligne, name="hors_ligne"),
    path("admin/", admin.site.urls),
    path("comptes/", include("users.urls")),
    path("api/", include("users.api.urls")),
    path("repas/", include("repas.urls")),
    path("impact/", include("impact.urls")),
    path("planning/", include("planning.urls")),
    path("food-rescue/", include("food_rescue.urls")),
    path("communaute/", include("community.urls")),
    path("assistant/", include("voice_assistant.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = "users.views.erreur_403"
handler404 = "users.views.erreur_404"
handler500 = "users.views.erreur_500"
