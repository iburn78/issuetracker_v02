from django.urls import path

from .views import (
        PostListView, 
        PostDetailView, 
        PostCreateView,
        PostUpdateView,
        PostDeleteView, 
        UserPostListView, 
        TaggedPostListView, 
        PostCompactListView,
        PostCompact_UserListView,
        PostCompact_TagListView,
        SearchFormView,
        )
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'), 
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'), 
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'), 
    path('post/new/', PostCreateView.as_view(), name='post-create'), 
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='post-update'), 
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'), 
    path('about/', views.about, name='blog-about'),
    path('tag/<int:pk>', TaggedPostListView.as_view(), name='tagged-posts'), 
    path('list/', PostCompactListView.as_view(), name='post-compact-list'),
    path('user_list/<str:username>', PostCompact_UserListView.as_view(), name='user-post-list'), 
    path('tag_list/<int:pk>', PostCompact_TagListView.as_view(), name='tag-post-list'), 
    path('dashboard/', views.dashboard_view, name='website-stats'),
    path('search/', SearchFormView.as_view(), name='search-form'),
] 




