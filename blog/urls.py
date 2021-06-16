from django.urls import path

from blog.views import (
        AuthorListView,
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
        PrivatePostListView, 
        PrivatePostDetailView, 
        PrivatePostCreateView,
        PrivatePostUpdateView,
        PrivatePostDeleteView, 
        UserPrivatePostListView, 
        TaggedPrivatePostListView, 
        PrivatePostCompactListView,
        PrivatePostCompact_UserListView,
        PrivatePostCompact_TagListView,
        PrivateSearchFormView,
        )

from blog import views

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'), 
    path('authors/', AuthorListView.as_view(), name='author-list'), 
    path('private/', PrivatePostListView.as_view(), name='post-private'), 
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'), 
    path('user/<str:username>/private/', UserPrivatePostListView.as_view(), name='user-privateposts'), 
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'), 
    path('post/<int:pk>/private/', PrivatePostDetailView.as_view(), name='privatepost-detail'), 
    path('post/new/', PostCreateView.as_view(), name='post-create'), 
    path('post/new/private/', PrivatePostCreateView.as_view(), name='privatepost-create'), 
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'), 
    path('post/<int:pk>/update/private/', PrivatePostUpdateView.as_view(), name='privatepost-update'), 
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'), 
    path('post/<int:pk>/delete/private', PrivatePostDeleteView.as_view(), name='privatepost-delete'), 
    path('about/', views.about, name='blog-about'),
    path('tag/<int:pk>/', TaggedPostListView.as_view(), name='tagged-posts'), 
    path('tag/<int:pk>/private/', TaggedPrivatePostListView.as_view(), name='tagged-privateposts'), 
    path('list/', PostCompactListView.as_view(), name='post-compact-list'),
    path('list/private/', PrivatePostCompactListView.as_view(), name='privatepost-compact-list'),
    path('user_list/<str:username>/', PostCompact_UserListView.as_view(), name='user-post-list'), 
    path('user_list/<str:username>/private/', PrivatePostCompact_UserListView.as_view(), name='user-privatepost-list'), 
    path('tag_list/<int:pk>/', PostCompact_TagListView.as_view(), name='tag-post-list'), 
    path('tag_list/<int:pk>/private/', PrivatePostCompact_TagListView.as_view(), name='tag-privatepost-list'), 
    path('dashboard/', views.dashboard_view, name='website-stats'),
    path('search/', SearchFormView.as_view(), name='search-form'),
    path('search/private/', PrivateSearchFormView.as_view(), name='privatesearch-form'),
] 




