from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
        ListView, 
        DetailView,
        CreateView,
        UpdateView, 
        DeleteView
        )
from django.http import HttpResponse
from .models import Post 
from taggit.models import Tag
from django.views.generic.edit import FormView
from blog.forms import PostSearchForm
from django.db.models import Q

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 7 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = Post.tags.most_common()[:5]
        return context

class PostCompactListView(PostListView):
    template_name = 'blog/post_compact_list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = Post.tags.most_common()[:15]
        context['total_num'] = Post.objects.count() 
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
        
class PostCompact_TagListView(PostCompactListView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        return Post.objects.filter(tags=tag).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        context['total_num'] = Post.objects.filter(tags=tag).order_by('-date_posted').count()
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
        return context

class PostDetailView(DetailView):
    model = Post

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
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'image', 'content', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        newpost = form.save(commit=False)
        newpost.save()
        form.save_m2m()
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image', 'tags']

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
