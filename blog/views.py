from django.shortcuts import render, get_object_or_404, redirect
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
from blog.models import PostRoot, Post, PrivatePost
from taggit.models import Tag
from django.views.generic.edit import FormView
from blog.forms import MiloSearchForm, PostSearchForm, PrivatePostSearchForm
from django.db.models import Q
from django.template.defaulttags import register
from django.urls import reverse
from bs4 import BeautifulSoup
from django.core.paginator import Paginator

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
    paginate_by = 70
    context_object_name = 'tags'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tag_articles = {}
        tag_authors = {}
        for tag in Post.tags.order_by('name'):
            tag_articles[tag.name] = Post.objects.filter(tags=tag.id).count()
            tag_authors[tag.name] = User.objects.filter(post__tags=tag.id).distinct().count()
        context['article_count'] = tag_articles
        context['author_count'] = tag_authors
        context['level'] = Post.level

        return context
    
    def get_queryset(self): 
        return Post.tags.order_by('name')

class PrivateTagListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Tag
    template_name = 'blog/tag_list.html'
    paginate_by = 70
    context_object_name = 'tags'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        tag_articles = {}
        for tag in PrivatePost.tags.filter(privatepost__author=user).order_by('name'):
            tag_articles[tag.name] = PrivatePost.objects.filter(tags=tag.id, author=user).count()
        context['article_count'] = tag_articles
        context['level'] = PrivatePost.level

        return context
    
    def get_queryset(self): 
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return PrivatePost.tags.filter(privatepost__author=user).order_by('name')

    def test_func(self):
        if str(self.request.user) == self.kwargs.get('username'):
            return True
        return False

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 7 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = Post.tags.most_common()[:5]
        context['tag_count'] = Post.tags.most_common()[:5].count()
        context['level'] = Post.level
        return context

#    def get_queryset(self):
#        return Post.objects.filter(level = 'public').order_by('-date_posted')

class PrivatePostListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PrivatePost
    template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 7 

    def get_context_data(self, common_tag_number=5, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        tag_articles = {}
        for tag in PrivatePost.tags.filter(privatepost__author=user).order_by('name'):
            tag_articles[tag.name] = PrivatePost.objects.filter(tags=tag.id, author=user).count()
        common_tag_dict = sorted(tag_articles.items(), key=lambda x:x[1], reverse=True)
        common_tags = []
        for c in common_tag_dict:
            common_tags.append(PrivatePost.tags.filter(name=c[0]).get())
        context['common_tags'] = common_tags[:common_tag_number]
        context['tag_count'] = len(common_tags)
        # Note that common_tags is not a QuerySet, but a list, and a list does not have the same count() method in python (it requires an arg)
        # django html template is only able to execute function without arguments, so {{ <QuerySet>.count }} is working while {{ <list>.count }} is not
        context['level'] = PrivatePost.level
        context['total_num'] = PrivatePost.objects.filter(author=user).count() 
        return context

    def get_queryset(self): 
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return PrivatePost.objects.filter(author=user)

    def test_func(self):
        if str(self.request.user) == self.kwargs.get('username'):
            return True
        return False

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
    template_name = 'blog/post_compact_list.html'
    paginate_by = 50
    def get_context_data(self, common_tag_number=15, **kwargs):
        context = super().get_context_data(common_tag_number, **kwargs)
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

class PrivatePostCompact_TagListView(PrivatePostCompactListView):
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        tag = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        return PrivatePost.objects.filter(tags=tag, author=user).order_by('-date_posted')

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

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = Post.level
        return context

class PrivatePostDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = PrivatePost
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = PrivatePost.level
        return context

    def test_func(self):
        if self.request.user == self.get_object().author:
            return True
        return False

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

class TaggedPrivatePostListView(PrivatePostListView):
    template_name = 'blog/tag_posts.html'
    context_object_name = 'tagged_posts'
    
    def get_queryset(self): 
        tag = get_object_or_404(Tag, id = self.kwargs.get('pk')) 
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return PrivatePost.objects.filter(tags=tag, author=user).order_by('-date_posted')

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = Post.level
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = PrivatePost.level
        return context
        
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = Post.level
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = PrivatePost.level
        return context

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.html'
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = Post.level
        return context

class PrivatePostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PrivatePost
    template_name = 'blog/post_confirm_delete.html'
    success_url = '/'
    
    def test_func(self):
        post = self.get_object()
        self.success_url = reverse('post-private', args=[self.request.user])
        if self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = PrivatePost.level
        return context

def about(request):
    return render(request, 'blog/about.html')

def dashboard_view(request):
    return render(request, 'blog/web_stats.html')



def milo(request):
    if request.method == "POST":
        form = MiloSearchForm(request.POST)
        if form.is_valid():
            key_word = form.cleaned_data
        else:
            key_word = request.POST
    else: 
        key_word = "form is not submited (or not POST)"
    return render(request, 'blog/milo_test.html', {'milo_key_word':key_word})

def milo_twocol(request):
    return render(request, 'blog/home-twocolumn.html')


class SearchFormView(FormView):
    form_class = PostSearchForm
    template_name = 'blog/search_form.html'
    page_by = 5

    def search_db(self, db, search_term, page = 1, page_tag = 1, page_author = 1):
        context = {}
        context['search_requested'] = True
        context['search_term'] = search_term
        search_result_list = db.objects.filter(Q(title__icontains=search_term) | Q(content__icontains=search_term) ).distinct().order_by('-date_posted') 
        search_result_list_tag = db.objects.filter(tags__name__icontains=search_term).distinct().order_by('-date_posted') 
        search_result_list_author = db.objects.filter(author__username__icontains=search_term).distinct().order_by('-date_posted') 

        pgn_srl = Paginator(search_result_list, self.page_by)
        pgn_srl_tag = Paginator(search_result_list_tag, self.page_by)
        pgn_srl_author = Paginator(search_result_list_author, self.page_by)

        pgn_srl_content = pgn_srl.get_page(page)
        pgn_srl_content_tag = pgn_srl_tag.get_page(page_tag)
        pgn_srl_content_author = pgn_srl_author.get_page(page_author)

        context['search_result_list'] = pgn_srl_content
        context['search_result_list_tag'] = pgn_srl_content_tag
        context['search_result_list_author'] = pgn_srl_content_author

        context['pgn_srl'] = pgn_srl
        context['pgn_srl_tag'] = pgn_srl_tag
        context['pgn_srl_author'] = pgn_srl_author

        return context

    def get(self, request, *args, **kwargs):
        search_term = str(request.GET.get('search_term'))
        page = request.GET.get('page')
        page_tag = request.GET.get('page_tag')
        page_author = request.GET.get('page_author')

        context = self.get_context_data()
        if search_term == 'None' or search_term == '': 
            return  render(self.request, self.template_name, context)
        else:
            context = {**context, **self.search_db(Post, search_term, page, page_tag, page_author)}
            return  render(self.request, self.template_name, context)

    def form_valid(self, form):
        search_term = str(self.request.POST['search_term']) 
        context = self.get_context_data()
        context = {**context, **self.search_db(Post, search_term)}
        return  render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = Post.level
        context['search_requested'] = False
        return context

class PrivateSearchFormView(LoginRequiredMixin, SearchFormView):
    form_class = PrivatePostSearchForm

    def get(self, request, *args, **kwargs):
        search_term = str(request.GET.get('search_term'))
        page = request.GET.get('page')
        page_tag = request.GET.get('page_tag')
        page_author = request.GET.get('page_author')

        context = self.get_context_data()
        if search_term == 'None' or search_term == '': 
            return  render(self.request, self.template_name, context)
        else:
            context = {**context, **self.search_db(PrivatePost, search_term, page, page_tag, page_author)}
            return  render(self.request, self.template_name, context)

    def form_valid(self, form):
        search_term = str(self.request.POST['search_term']) 
        context = self.get_context_data()
        context = {**context, **self.search_db(PrivatePost, search_term)}
        return  render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = PrivatePost.level
        return context
