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


def group_posts(request,slug):
    group = get_object_or_404 (Group, slug=slug)
    group_posts_list = Post.objects.filter(group=group).order_by('-pub_date').all()
    paginator = Paginator(group_posts_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    context_dict = {'title':'Добавить запись', 'button':'Добавить'}
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            Post.objects.create(author=request.user, group=form.cleaned_data['group'], text=form.cleaned_data['text'])
            return redirect('index')
        return render(request, 'new_post.html', {'form':form, 'context_dict':context_dict})
    form = PostForm()
    return render(request, 'new_post.html', {'form':form, 'context_dict':context_dict})


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    profile_posts_list = Post.objects.prefetch_related('author').filter(author=user_profile).order_by('-pub_date').all()
    counter_posts = profile_posts_list.count()
    paginator = Paginator(profile_posts_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'page': page, 'paginator': paginator, 'username': username, 'counter': counter_posts, 'user_profile': user_profile})


def post_view(request, username, post_id):
    user_profile = Post.objects.get(pk=post_id).author #Сначало мы  достали объект автора, а потом по этому же объекту мы ищем этот же пост, нету ли тут нелогичности?
    post = Post.objects.prefetch_related('author').filter(author=user_profile).get(pk=post_id)
    counter_posts = Post.objects.filter(author=user_profile).count()
    return render(request, 'post.html', {'username': username, 'user_profile': user_profile, 'post': post, 'counter': counter_posts})


@login_required
def post_edit(request, username, post_id):
    post_author = Post.objects.get(pk=post_id).author
    if post_author == request.user:
        context_dict = {'title': 'Редактировать запись', 'button':'Сохранить'}
        if request.method == 'POST':
            post = Post.objects.get(pk=post_id)#как подргузить в форму редактирования текущие значения?
            form = PostForm(request.POST)
            if form.is_valid():
                post.text = form.cleaned_data['text']
                post.Group = form.cleaned_data['group']
                post.save()
                return redirect(post_view, username=username, post_id=post_id)
            return render(request, 'new_post.html', {'form': form, 'context_dict':context_dict})
        form = PostForm()
        return render(request, 'new_post.html', {'form': form, 'context_dict': context_dict})
    return redirect (post_view, username=username, post_id=post_id)
