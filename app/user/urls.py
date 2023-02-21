"""
URLs for the user api.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user import views

router = DefaultRouter()
router.register('follower', views.UserFollowerViewSet, basename='follower')
router.register('following', views.UserFollowingViewSet, basename='following')

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView().as_view(), name='token'),
    path('<str:username>/', views.UserProfileView().as_view(), name='me'),
    path('<str:username>/', include(router.urls))
]
