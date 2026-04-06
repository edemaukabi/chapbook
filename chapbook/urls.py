from dj_rest_auth.views import PasswordResetConfirmView
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from core_apps.users.views import CustomUserDetailsView


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def api_root(request):
    base = request.build_absolute_uri("/api/v1/")
    return Response({
        "name": "Chapbook API",
        "version": "v1",
        "status": "operational",
        "description": "REST API for Chapbook — a multi-author publishing platform.",
        "docs": request.build_absolute_uri("/redoc/"),
        "endpoints": {
            "auth": f"{base}auth/",
            "profiles": f"{base}profiles/",
            "articles": f"{base}articles/",
            "bookmarks": f"{base}bookmarks/",
            "ratings": f"{base}ratings/",
            "responses": f"{base}responses/",
            "search": f"{base}elastic/search/",
        },
    })

schema_view = get_schema_view(
    openapi.Info(
        title="Chapbook API",
        default_version="v1",
        description="API endpoints for Chapbook",
        contact=openapi.Contact(email="edemacode@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", api_root, name="api-root"),
    path("api/v1/", api_root, name="api-v1-root"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0)),
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/auth/user/", CustomUserDetailsView.as_view(), name="user_details"),
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "api/v1/auth/password/reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("api/v1/profiles/", include("core_apps.profiles.urls")),
    path("api/v1/articles/", include("core_apps.articles.urls")),
    path("api/v1/ratings/", include("core_apps.ratings.urls")),
    path("api/v1/bookmarks/", include("core_apps.bookmarks.urls")),
    path("api/v1/responses/", include("core_apps.responses.urls")),
    path("api/v1/elastic/", include("core_apps.search.urls")),
]

admin.site.site_header = "Chapbook Admin"

admin.site.site_title = "Chapbook Admin Portal"

admin.site.index_title = "Welcome to Chapbook Admin Portal"
