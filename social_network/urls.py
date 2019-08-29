from django.conf.urls import url
from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api_v1 import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'posts', views.PostViewSet)

urlpatterns = [
    path('', include('rest_framework.urls', namespace='rest_framework')),
    url('v1/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url('v1/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/', include(router.urls))
]