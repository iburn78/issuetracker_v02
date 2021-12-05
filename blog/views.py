from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.http import HttpResponse
from blog.models import PostRoot, Post, PrivatePost
from taggit.models import Tag
from django.views.generic.edit import FormMixin, FormView
from blog.forms import PostSearchForm, PrivatePostSearchForm, TagSearchForm, AuthorSearchForm
from django.db.models import Q
from django.template.defaulttags import register
from django.urls import reverse
from bs4 import BeautifulSoup
from django.core.paginator import Paginator
from django.contrib import messages

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 7

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = Post.tags.most_common()[:5]
        context['tag_count'] = Post.tags.most_common()[:5].count()
        context['level'] = Post.level
        return context

    def get_queryset(self):
        return Post.objects.order_by('-date_posted')


class PrivatePostListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PrivatePost
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 7

    def get_context_data(self, common_tag_number=5, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        tag_articles = {}
        for tag in PrivatePost.tags.filter(privatepost__author=user).order_by('name'):
            tag_articles[tag.name] = PrivatePost.objects.filter(
                tags=tag.id, author=user).count()
        common_tag_dict = sorted(tag_articles.items(),
                                 key=lambda x: x[1], reverse=True)
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
        return PrivatePost.objects.filter(author=user).order_by('-date_posted')

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
        context['total_num'] = Post.objects.filter(
            author=user).order_by('-date_posted').count()
        return context


class PostCompact_TagListView(PostCompactListView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, id=self.kwargs.get('pk'))
        return Post.objects.filter(tags=tag).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, id=self.kwargs.get('pk'))
        context['total_num'] = Post.objects.filter(
            tags=tag).order_by('-date_posted').count()
        return context


class PrivatePostCompact_TagListView(PrivatePostCompactListView):
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        tag = get_object_or_404(Tag, id=self.kwargs.get('pk'))
        return PrivatePost.objects.filter(tags=tag, author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, id=self.kwargs.get('pk'))
        context['total_num'] = PrivatePost.objects.filter(
            tags=tag).order_by('-date_posted').count()
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 7

    def get_queryset(self):  # overriding a method
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
        tag = get_object_or_404(Tag, id=self.kwargs.get('pk'))
        return Post.objects.filter(tags=tag).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = Post.tags.most_common()[:5]
        context['current_tag'] = get_object_or_404(
            Tag, id=self.kwargs.get('pk'))
        context['level'] = Post.level
        return context


class TaggedPrivatePostListView(PrivatePostListView):
    template_name = 'blog/tag_posts.html'
    context_object_name = 'tagged_posts'

    def get_queryset(self):
        tag = get_object_or_404(Tag, id=self.kwargs.get('pk'))
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return PrivatePost.objects.filter(tags=tag, author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_tags'] = PrivatePost.tags.most_common()[:5]
        context['current_tag'] = get_object_or_404(
            Tag, id=self.kwargs.get('pk'))
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

def test(request):
    return render(request, 'blog/test.html')

def milo(request):
    return render(request, 'blog/milo_test.html')


class SearchFormView(FormView):
    form_class = PostSearchForm
    template_name = 'blog/search_form.html'
    page_by = 10

    def search_db(self, db, search_term, page=1, page_tag=1, page_author=1):
        context = {}
        context['search_requested'] = True
        context['search_term'] = search_term
        if db != PrivatePost:
            search_result_list = db.objects.filter(Q(title__icontains=search_term) | Q(
                content__icontains=search_term)).distinct().order_by('-date_posted')
            search_result_list_tag = db.objects.filter(
                tags__name__icontains=search_term).distinct().order_by('-date_posted')
        else: 
            search_result_list = db.objects.filter(author__username=str(self.request.user)).filter(Q(title__icontains=search_term) | Q(
                content__icontains=search_term)).distinct().order_by('-date_posted')
            search_result_list_tag = db.objects.filter(author__username=str(self.request.user)).filter(
                tags__name__icontains=search_term).distinct().order_by('-date_posted')

        pgn_srl = Paginator(search_result_list, self.page_by)
        pgn_srl_tag = Paginator(search_result_list_tag, self.page_by)

        pgn_srl_content = pgn_srl.get_page(page)
        pgn_srl_content_tag = pgn_srl_tag.get_page(page_tag)

        context['search_result_list'] = pgn_srl_content
        context['search_result_list_tag'] = pgn_srl_content_tag

        context['pgn_srl'] = pgn_srl
        context['pgn_srl_tag'] = pgn_srl_tag

        if db != PrivatePost:
            search_result_list_author = db.objects.filter(
                author__username__icontains=search_term).distinct().order_by('-date_posted')
            pgn_srl_author = Paginator(search_result_list_author, self.page_by)
            pgn_srl_content_author = pgn_srl_author.get_page(page_author)
            context['search_result_list_author'] = pgn_srl_content_author
            context['pgn_srl_author'] = pgn_srl_author

        return context

    def page_session(self, request):
        page = request.GET.get('page')
        page_tag = request.GET.get('page_tag')
        page_author = request.GET.get('page_author')
        if page == None:
            request.session["collapse"] = ''
            if request.session.get("page") == None:
                page = 1
            else:
                page = request.session.get("page")
        else:
            request.session["collapse"] = 'show'
        if page_tag == None:
            request.session["collapse_tag"] = ''
            if request.session.get("page_tag") == None:
                page_tag = 1
            else:
                page_tag = request.session.get("page_tag")
        else:
            request.session["collapse_tag"] = 'show'
        if page_author == None:
            request.session["collapse_author"] = ''
            if request.session.get("page_author") == None:
                page_author = 1
            else:
                page_author = request.session.get("page_author")
        else:
            request.session["collapse_author"] = 'show'
        try:
            page = int(page)
            page_tag = int(page_tag)
            page_author = int(page_author)
        except:
            print("**** search error - page number should be integers")
            raise
        request.session["page"] = page
        request.session["page_tag"] = page_tag
        request.session["page_author"] = page_author
        return page, page_tag, page_author

    def get(self, request, *args, db=Post, **kwargs):
        search_term = str(request.GET.get('search_term'))
        context = self.get_context_data()
        if search_term == 'None' or search_term == '':
            return render(self.request, self.template_name, context)
        else:
            p, t, a = self.page_session(request)
            context["collapse"] = request.session.get("collapse")
            context["collapse_tag"] = request.session.get("collapse_tag")
            context["collapse_author"] = request.session.get("collapse_author")
            context = {
                **context, **self.search_db(db, search_term, p, t, a)}
            return render(self.request, self.template_name, context)

    def form_valid(self, form, db=Post):
        search_term = str(self.request.POST['search_term'])
        context = self.get_context_data()
        context["collapse"] = ''
        context["collapse_tag"] = ''
        context["collapse_author"] = ''
        self.request.session["page"] = 1
        self.request.session["page_tag"] = 1
        self.request.session["page_author"] = 1
        context = {**context, **self.search_db(db, search_term)}
        return render(self.request, self.template_name, context)

    def get_context_data(self, db=Post, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level'] = db.level
        return context


class PrivateSearchFormView(LoginRequiredMixin, SearchFormView):
    form_class = PrivatePostSearchForm

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, db=PrivatePost, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form, db=PrivatePost)

    def get_context_data(self, **kwargs):
        return super().get_context_data(db=PrivatePost, **kwargs)



class AuthorListView(FormMixin, ListView):
    form_class = AuthorSearchForm
    template_name = 'blog/author_list.html'
    paginate_by = 15
    context_object_name = 'authors'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid(): 
            search_term = form.cleaned_data.get("search_term")
            return self.form_valid(search_term, **kwargs)
        else:
            messages.info(request, "Enter search word for authors")
            return redirect("author-list")

    def form_valid(self, search_term, **kwargs):
        context = self.get_context_data(**kwargs)
        context['author_search_res'] = User.objects.filter(username__icontains=search_term).distinct().order_by('username')
        context['search_term'] = search_term
        context['search_requested'] = True
        return render(self.request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        order = request.GET.get("order")
        if order == None: order = 'mp'
        context = self.get_context_data(order = order, **kwargs)
        return render(self.request, self.template_name, context)

    def get_context_data(self, order ='mp', **kwargs):
        context = {}
        user_table = []   # username, id, number_posts, last_post(most recent), last_login, is_active
        user_list = User.objects.all().order_by('username')
        for user in user_list:
            number_posts = user.post_set.count()
            last_post = Post.objects.filter(author=user.id).order_by('-date_posted').first()
            if last_post != None: 
                last_post = last_post.date_posted
            user_table.append([user.username, user.id, number_posts, last_post, user.last_login, user.is_active])
        user_table_sort = [user for user in user_table if user[5] and user[2] > 0]  
        if order == 'mp': # most posts
            user_table_sort = sorted(user_table_sort, key=lambda a:-a[2])
        elif order == 'mr': # most recent
            user_table_sort = sorted(user_table_sort, key=lambda a:a[3], reverse=True)
        elif order == 'll': 
            user_table_sort = sorted(user_table_sort, key=lambda a:a[4], reverse=True)
        else:
            order = 'alp'
        context['form'] = self.get_form()
        context['order'] = order
        context['noposts'] = [user for user in user_table if user[5] and user[2] == 0]  
        context['inactives'] = [user for user in user_table if not user[5]]  
        self.object_list = user_table_sort
        context = {**context, **super().get_context_data(**kwargs)} # should do this last for pagination to work
        return context


class TagListView(FormMixin, ListView):
    form_class = TagSearchForm
    template_name = 'blog/tag_list.html'
    paginate_by = 15
    context_object_name = 'tags'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid(): 
            search_term = form.cleaned_data.get("search_term")
            return self.form_valid(search_term, **kwargs)
        else:
            messages.info(request, "Enter search word for tags")
            return redirect("tag-list")

    def form_valid(self, search_term, **kwargs):
        context = self.get_context_data_(**kwargs)
        context['tag_search_res'] = Post.tags.filter(name__icontains=search_term).distinct()
        context['search_term'] = search_term
        context['search_requested'] = True
        return render(self.request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        order = request.GET.get("order")
        if order == None: order = 'mp'
        context = self.get_context_data_(order = order, **kwargs)
        return render(self.request, self.template_name, context)

    def get_context_data_(self, order ='mp', **kwargs):
        db=Post
        context = {}
        tag_table = []   # tag_name, id, number_posts, number_authors
        tag_list = db.tags.order_by('name')
        for tag in tag_list:
            tag_articles = db.objects.filter(tags=tag.id).count()
            last_used = db.objects.filter(tags=tag.id).distinct().order_by('-date_posted').first().date_posted
            tag_authors = User.objects.filter(post__tags=tag.id).distinct().count()
            tag_table.append([tag.name, tag.id, tag_articles, tag_authors, last_used])
        if order == 'mp':
            tag_table = sorted(tag_table, key=lambda a:-a[2])
        elif order == 'ma': 
            tag_table = sorted(tag_table, key=lambda a:-a[3])
        elif order == 'mr': 
            tag_table = sorted(tag_table, key=lambda a:a[4], reverse=True)
        else: 
            order = 'alp'
        context['level'] = db.level
        context['form'] = self.get_form()
        context['order'] = order
        self.object_list = tag_table 
        context = {**context, **super().get_context_data(**kwargs)} # should do this last for pagination to work 
        return context


class PrivateTagListView(LoginRequiredMixin, UserPassesTestMixin, TagListView):

    def form_valid(self, search_term, **kwargs):
        context = self.get_context_data_(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['tag_search_res'] = PrivatePost.tags.filter(Q(privatepost__author=user) & Q(name__icontains=search_term)).distinct()
        context['search_term'] = search_term
        context['search_requested'] = True
        return render(self.request, self.template_name, context)

    def get_context_data_(self, order ='mp', **kwargs):
        db=PrivatePost
        context = {}
        tag_table = []   # tag_name, id, number_posts 
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        tag_list = db.tags.filter(privatepost__author=user).order_by('name')
        for tag in tag_list:
            tag_articles = db.objects.filter(author=user).filter(tags=tag.id).count()
            last_used = db.objects.filter(author=user).filter(tags=tag.id).distinct().order_by('-date_posted').first().date_posted
            tag_table.append([tag.name, tag.id, tag_articles, last_used])
        if order == 'mp':
            tag_table = sorted(tag_table, key=lambda a:-a[2])
        elif order == 'mr': 
            tag_table = sorted(tag_table, key=lambda a:a[3], reverse=True)
        else:
            order = "alp"
        context['level'] = db.level
        context['form'] = self.get_form()
        context['order'] = order
        self.object_list = tag_table 
        context = {**context, **super().get_context_data(**kwargs)} # should do this last for pagination to work
        return context

    def test_func(self):
        if str(self.request.user) == self.kwargs.get('username'):
            return True
        return False
