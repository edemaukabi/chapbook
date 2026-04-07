import logging

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ArticleFilter
from .models import Article, ArticleView, Clap
from .pagination import ArticlePagination
from .permissions import IsOwnerOrReadOnly
from .renderers import ArticleJSONRenderer, ArticlesJSONRenderer
from .serializers import ArticleSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    # GET is public (browsing/search); POST requires login
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ArticlePagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ArticleFilter
    ordering_fields = ["created_at", "updated_at"]
    renderer_classes = [ArticlesJSONRenderer]

    def perform_create(self, serializer):
        article = serializer.save(author=self.request.user)
        logger.info(f"Article '{article.title}' created by {self.request.user.email}")


class ArticleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    # GET is public; PATCH/DELETE require ownership
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = "id"
    renderer_classes = [ArticleJSONRenderer]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user if request.user.is_authenticated else None
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        viewer_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR")
        ArticleView.record_view(
            article=instance,
            user=user,
            viewer_ip=viewer_ip,
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class StatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, _request):
        from core_apps.profiles.models import Profile

        articles_count = Article.objects.count()
        writers_count = Profile.objects.count()
        authenticated_readers = (
            ArticleView.objects.filter(user__isnull=False)
            .values("user")
            .distinct()
            .count()
        )
        guest_readers = (
            ArticleView.objects.filter(user__isnull=True)
            .values("viewer_ip")
            .distinct()
            .count()
        )
        readers_count = authenticated_readers + guest_readers

        return Response(
            {
                "articles_count": articles_count,
                "writers_count": writers_count,
                "readers_count": readers_count,
            }
        )


class ClapArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if Clap.objects.filter(user=request.user, article=article).exists():
            return Response(
                {"detail": "You have already clapped for this article."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Clap.objects.create(user=request.user, article=article)
        return Response({"detail": "Clap added."}, status=status.HTTP_201_CREATED)

    def delete(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        clap = get_object_or_404(Clap, user=request.user, article=article)
        clap.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
