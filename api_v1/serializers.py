from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Post
from .services import get_user_extra_info, verify_user_email

User = get_user_model()


class PostSingleSerializer(serializers.ModelSerializer):
    link = serializers.HyperlinkedIdentityField(view_name='post-detail')
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'likes_count', 'link']


class UserSingleSerializer(serializers.ModelSerializer):
    link = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'link']


class UserSerializer(serializers.ModelSerializer):
    posts = PostSingleSerializer(many=True, read_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    email = serializers.EmailField(validators=[UniqueValidator(User.objects.all())])
    password = serializers.CharField(
        min_length=4,
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )
    link = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email',
            'password', 'username', 'link', 'posts',
        ]

    def create(self, validated_data):
        fields = ['email', 'username', 'password', 'first_name', 'last_name']
        data = {f: validated_data.get(f) for f in fields}

        # Backfill names from Clearbit when the user left them blank.
        additional_data = get_user_extra_info(validated_data['email'])
        for k in ['first_name', 'last_name']:
            if not data[k] and additional_data.get(k):
                data[k] = additional_data[k]

        return User.objects.create_user(**data)

    def validate_email(self, email):
        if not verify_user_email(email):
            raise serializers.ValidationError("This email address doesn't exist")
        return email


class PostSerializer(serializers.ModelSerializer):
    user = UserSingleSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    link = serializers.HyperlinkedIdentityField(view_name='post-detail')

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'likes_count', 'link', 'user']
