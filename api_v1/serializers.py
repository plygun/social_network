from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.validators import UniqueValidator

from .models import Post
from .services import verify_user_email, get_user_extra_info


class PostSingleSerializer(serializers.ModelSerializer):
    link = serializers.HyperlinkedIdentityField(view_name='post-detail')

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'likes_counter', 'link']


class UserSingleSerializer(serializers.ModelSerializer):
    password = serializers.Field(write_only=True)
    link = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'username', 'link']


class UserSerializer(serializers.ModelSerializer):
    posts = PostSingleSerializer(many=True, read_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    email = serializers.EmailField(
        validators=[UniqueValidator(User.objects.all())]
    )
    password = serializers.CharField(
        min_length=4,
        write_only=True,
        required=True,
        style={'input_type': 'password'}
        )
    link = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'username', 'link', 'posts']
        extra_kwargs = {'password': {'write_only': True}}

    @authentication_classes([])
    @permission_classes([])
    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        print(validated_data)
        fields = ['email', 'username', 'password', 'first_name', 'last_name']
        data = {f: validated_data.get(f) for f in fields}
        email = validated_data['email']
        additional_data = get_user_extra_info(email)

        # override values only in case when original values are empty
        for k in ['first_name', 'last_name']:
            if data[k] == "" and additional_data.get(k):
                data[k] = additional_data[k]

        return User.objects.create_user(**data)

    def validate_email(self, email):
        if not verify_user_email(email):
            raise serializers.ValidationError(f"This email address doesn't exist")
        return email


class PostSerializer(serializers.ModelSerializer):
    user = UserSingleSerializer(read_only=True)
    likes_counter = serializers.ReadOnlyField()
    link = serializers.HyperlinkedIdentityField(view_name='post-detail')

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'likes_counter', 'link', 'user']

