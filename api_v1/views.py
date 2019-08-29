from django.contrib.auth.models import User

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post
from .serializers import UserSerializer, PostSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['post'], detail=True)
    def like(self, request, *args, **kwargs):
        """
        Like post action.
        """
        post = self.get_object()

        post.likes_counter += 1
        post.save()

        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def dislike(self, request, *args, **kwargs):
        """
        Dislike post action.
        """
        post = self.get_object()

        if post.likes_counter > 0:
            post.likes_counter -= 1
            post.save()

        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

