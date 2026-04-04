import django_filters as filters

from core_apps.articles.models import Article


class ArticleFilter(filters.FilterSet):
    author = filters.CharFilter(field_name="author__first_name", lookup_expr="icontains")
    author_pkid = filters.NumberFilter(field_name="author__pkid")
    # Filter by profile UUID — used on the author profile page
    author_profile_id = filters.UUIDFilter(field_name="author__profile__id")
    # Exact slug lookup — used by the article detail page to find UUID from slug
    slug = filters.CharFilter(field_name="slug", lookup_expr="exact")
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    tags = filters.CharFilter(field_name="tags__name", lookup_expr="iexact")
    created_at = filters.DateFromToRangeFilter(field_name="created_at")
    updated_at = filters.DateFromToRangeFilter(field_name="updated_at")

    class Meta:
        model = Article
        fields = [
            "author",
            "author_pkid",
            "author_profile_id",
            "slug",
            "title",
            "tags",
            "created_at",
            "updated_at",
        ]
