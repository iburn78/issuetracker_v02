from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
        ListView, 
        DetailView,
        CreateView,
        UpdateView, 
        DeleteView
        )
from django.http import HttpResponse
from blog.models import Post, PrivatePost
from taggit.models import Tag
from django.views.generic.edit import FormView
from blog.forms import PostSearchForm, PrivatePostSearchForm
from django.db.models import Q
from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

class AuthorListView(ListView):
    model = User
    template_name = 'blog/author_list.html'
    paginate_by = 50
    context_object_name = 'authors'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class TagListView(ListView):
    model = Tag
    template_name = 'blog/tag_list.html'
    paginate_by = 50
    context_object_name = 'tags'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        public_tags = Post.tags.all()
        context['public_tags'] = public_tags
        public_tag_articles = {}
        for tag in public_tags:
            public_tag_articles[tag.name] = Post.objects.filter(tags=tag.id).count()
        context['public_tag_article_count'] = public_tag_articles

        private_tags = PrivatePost.tags.all()
        context['private_tags'] = private_tags
        private_tag_articles = {}
        for tag in private_tags:
            private_tag_articles[tag.name] = PrivatePost.objects.filter(tags=tag.id).count()
        context['private_tag_article_count'] = private_tag_articles

        return context

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 7 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = Post.tags.most_common()[:5]
        context['level'] = Post.level
        return context

#    def get_queryset(self):
#        return Post.objects.filter(level = 'public').order_by('-date_posted')

class PrivatePostListView(ListView):
    model = PrivatePost
    template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 7 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = PrivatePost.tags.most_common()[:5]
        context['level'] = PrivatePost.level
        return context

class PostCompactListView(PostListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/post_compact_list.html'
    ordering = ['-date_posted']
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = Post.tags.most_common()[:15]
        context['total_num'] = Post.objects.count() 
        context['level'] = Post.level
        return context

class PrivatePostCompactListView(PrivatePostListView):
    model = PrivatePost
    context_object_name = 'posts'
    template_name = 'blog/post_compact_list.html'
    ordering = ['-date_posted']
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = PrivatePost.tags.most_common()[:15]
        context['total_num'] = PrivatePost.objects.count() 
        context['level'] = PrivatePost.level
        return context

class PostCompact_UserListView(PostCompactListView):
    def get_queryset(self): 
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['total_num'] = Post.objects.filter(author=user).order_by('-date_posted').count()
        return context
        
class PrivatePostCompact_UserListView(PrivatePostCompactListView):
    def get_queryset(self): 
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return PrivatePost.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['total_num'] = PrivatePost.objects.filter(author=user).order_by('-date_posted').count()
        return context
        
class PostCompact_TagListView(PostCompactListView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        return Post.objects.filter(tags=tag).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        context['total_num'] = Post.objects.filter(tags=tag).order_by('-date_posted').count()
        return context

class PrivatePostCompact_TagListView(PrivatePostCompactListView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        return PrivatePost.objects.filter(tags=tag).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        context['total_num'] = PrivatePost.objects.filter(tags=tag).order_by('-date_posted').count()
        return context

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 7 

    def get_queryset(self): # overriding a method
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = Post.tags.most_common()[:5]
        context['level'] = Post.level
        return context

class UserPrivatePostListView(ListView):
    model = PrivatePost
    template_name = 'blog/user_posts.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 7 

    def get_queryset(self): # overriding a method
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return PrivatePost.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = PrivatePost.tags.most_common()[:5]
        context['level'] = PrivatePost.level
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = Post.level
        return context

class PrivatePostDetailView(DetailView):
    model = PrivatePost
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = PrivatePost.level
        return context

class TaggedPostListView(ListView):
    model = Post
    template_name = 'blog/tag_posts.html'
    context_object_name = 'tagged_posts'
    paginate_by = 7
    
    def get_queryset(self): 
        tag = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        return Post.objects.filter(tags=tag).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = Post.tags.most_common()[:5]
        context['current_tag'] = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        context['level'] = Post.level
        return context

class TaggedPrivatePostListView(ListView):
    model = PrivatePost
    template_name = 'blog/tag_posts.html'
    context_object_name = 'tagged_posts'
    paginate_by = 7
    
    def get_queryset(self): 
        tag = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        return PrivatePost.objects.filter(tags=tag).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = PrivatePost.tags.most_common()[:5]
        context['current_tag'] = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        context['level'] = PrivatePost.level
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    # template_name = 'blog/post_form.html'
    fields = ['title', 'image', 'content', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        newpost = form.save(commit=False)
        newpost.save()
        form.save_m2m()
        return super().form_valid(form)

class PrivatePostCreateView(LoginRequiredMixin, CreateView):
    model = PrivatePost
    template_name = 'blog/post_form.html'
    fields = ['title', 'image', 'content', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        newpost = form.save(commit=False)
        newpost.save()
        form.save_m2m()
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'image', 'content', 'tags']
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        newpost = form.save(commit=False)
        newpost.save()
        form.save_m2m()
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PrivatePostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PrivatePost
    fields = ['title', 'image', 'content', 'tags']
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        newpost = form.save(commit=False)
        newpost.save()
        form.save_m2m()
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.html'
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PrivatePostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PrivatePost
    success_url = '/private/'
    template_name = 'blog/post_confirm_delete.html'
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    return render(request, 'blog/about.html')

def dashboard_view(request):
    return render(request, 'blog/web_stats.html')

class SearchFormView(FormView):
    form_class = PostSearchForm
    template_name = 'blog/search_form.html'

    def form_valid(self, form):
        search_term = str(self.request.POST['search_term']) 
        context = self.get_context_data()
        context['search_term'] = search_term
        context['search_result_list'] = Post.objects.filter(Q(title__icontains=search_term) | Q(content__icontains=search_term) ).distinct().order_by('-date_posted') 
        return  render(self.request, self.template_name, context)

class PrivateSearchFormView(FormView):
    form_class = PrivatePostSearchForm
    template_name = 'blog/search_form.html'

    def form_valid(self, form):
        search_term = str(self.request.POST['search_term']) 
        context = self.get_context_data()
        context['search_term'] = search_term
        context['search_result_list'] = PrivatePost.objects.filter(Q(title__icontains=search_term) | Q(content__icontains=search_term) ).distinct().order_by('-date_posted') 
        return  render(self.request, self.template_name, context)
