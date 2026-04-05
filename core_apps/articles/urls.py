from django.urls import path

from .views import (
    ArticleListCreateView,
    ArticleRetrieveUpdateDestroyView,
    ClapArticleView,
    StatsView,
)

urlpatterns = [
    path("", ArticleListCreateView.as_view(), name="article-list-create"),
    path("stats/", StatsView.as_view(), name="article-stats"),
    path(
        "<uuid:id>/",
        ArticleRetrieveUpdateDestroyView.as_view(),
        name="article-retrieve-update-destroy",
    ),
    path("<uuid:article_id>/clap/", ClapArticleView.as_view(), name="clap-article"),
]
