"""
Urls for maping feed app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from feed import views


router = DefaultRouter()
router.register('posts', views.PostsViewSet, basename='posts')

app_name = 'feed'

urlpatterns = [
    path('', include(router.urls))
]
