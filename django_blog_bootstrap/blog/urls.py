from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (CommentActionsView, HomePageView, PostCreateView,
                    PostDeleteView, PostDetailView, PostLikeView, PostListView,
                    PostUpdateView)

urlpatterns = [
    path('post-list/', PostListView.as_view(), name='post_list'),
    path('post-add/', PostCreateView.as_view(), name='post_add'),
    path('post-edit/<int:pk>/', PostUpdateView.as_view(), name='post_edit'),
    path('post-detail/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/comment/', PostDetailView.as_view(), name='comment_create'),
    path('comment/<int:pk>/<str:action>/', CommentActionsView.as_view(), name='comment_actions'),
    path('post/<int:pk>/<str:action>/', PostLikeView.as_view(), name='post_like'),
    path('home/', HomePageView.as_view(), name='home'),

] 

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)