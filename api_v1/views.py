from django.contrib.auth import get_user_model
from django.db.models import Count

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Like, Post
from .serializers import PostSerializer, UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.annotate(likes_count=Count('likes'))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['post'], detail=True)
    def like(self, request, *args, **kwargs):
        post = self.get_object()
        Like.objects.get_or_create(user=request.user, post=post)
        post = self.get_queryset().get(pk=post.pk)
        return Response(self.get_serializer(post).data)

    @action(methods=['post'], detail=True)
    def dislike(self, request, *args, **kwargs):
        post = self.get_object()
        Like.objects.filter(user=request.user, post=post).delete()
        post = self.get_queryset().get(pk=post.pk)
        return Response(self.get_serializer(post).data)
