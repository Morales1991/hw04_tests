from django.shortcuts import render,get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts_list = Post.objects.filter(group=group).order_by('-pub_date').all()
    paginator = Paginator(group_posts_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'page': page, 'paginator': paginator, 'group': group})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            Post.objects.create(author=request.user, **form.cleaned_data)
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    profile_posts_list = Post.objects.prefetch_related('author').filter(author=user_profile).order_by('-pub_date').all()
    counter_posts = profile_posts_list.count()
    paginator = Paginator(profile_posts_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'page': page, 'paginator': paginator, 'username': username, 'counter': counter_posts, 'user_profile': user_profile})


def post_view(request, username, post_id):
    user_profile = get_object_or_404(User, username=username)  
    post = get_object_or_404(Post.objects.select_related('author'), author=user_profile, pk=post_id) #добавил еще выборку по автору, иначе получается что посты других пользователей видно под авторством авторизованного пользователя
    counter_posts = Post.objects.filter(author=user_profile).count()
    return render(request, 'post.html', {'username': username, 'user_profile': user_profile, 'post': post, 'counter': counter_posts})


@login_required
def post_edit(request, username, post_id):# Да и в правду в таком варианте все читабильнее
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post.objects.select_related('author'), pk=post_id)
    if post.author != request.user != author:
        return redirect(post_view, username=username, post_id=post_id)
        
    if request.method == 'POST': # есть ли разница if или elif?
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post.save()
            return redirect(post_view, username=username, post_id=post_id)
        return render(request, 'new_post.html', {'form': form, 'post': post})
        
    form = PostForm(instance=post)
    return render(request, 'new_post.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path':request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)