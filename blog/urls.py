from django.urls import path

from blog.views import * 
from blog import views

urlpatterns = [
    path('test/', views.test, name='test'), 
    path('nav/', views.nav, name='nav'), 
    path('milo/', views.milo, name='milo-test'), 
    path('', PostListView.as_view(), name='blog-home'), 
    path('authors/', AuthorListView.as_view(), name='author-list'), 
    path('tags/', TagListView.as_view(), name='tag-list'), 
    path('private_tags/<str:username>', PrivateTagListView.as_view(), name='privatetag-list'), 
    path('private/<str:username>', PrivatePostListView.as_view(), name='post-private'), 
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'), 
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
    path('tag/<int:pk>/private/<str:username>', TaggedPrivatePostListView.as_view(), name='tagged-privateposts'), 
    path('list/', PostCompactListView.as_view(), name='post-compact-list'),
    path('list/private/<str:username>', PrivatePostCompactListView.as_view(), name='privatepost-compact-list'),
    path('user_list/<str:username>/', PostCompact_UserListView.as_view(), name='user-post-list'), 
    path('tag_list/<int:pk>/', PostCompact_TagListView.as_view(), name='tag-post-list'), 
    path('tag_list/<int:pk>/private/<str:username>', PrivatePostCompact_TagListView.as_view(), name='tag-privatepost-list'), 
    path('search/', SearchFormView.as_view(), name='search-form'),
    path('search/private/', PrivateSearchFormView.as_view(), name='privatesearch-form'),
] 

        # (AuthorListView,
        # TagListView,
        # PrivateTagListView, 
        # PostListView, 
        # PostDetailView, 
        # PostCreateView,
        # PostUpdateView,
        # PostDeleteView, 
        # UserPostListView, 
        # TaggedPostListView, 
        # PostCompactListView,
        # PostCompact_UserListView,
        # PostCompact_TagListView,
        # SearchFormView,
        # PrivatePostListView, 
        # PrivatePostDetailView, 
        # PrivatePostCreateView,
        # PrivatePostUpdateView,
        # PrivatePostDeleteView, 
        # TaggedPrivatePostListView, 
        # PrivatePostCompactListView,
        # PrivatePostCompact_TagListView,
        # PrivateSearchFormView,
        # )
