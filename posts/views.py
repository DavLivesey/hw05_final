from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
                )


def server_error(request):
    return render(
        request,
        'misc/500.html',
        {'path': request.path},
        status=500
                )


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page, 'paginator': paginator}
        )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'page': page,
        'paginator': paginator,
        'posts': posts
        })


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None,)
        if form.is_valid():
            post_get = form.save(commit=False)
            post_get.author = request.user
            post_get.save()
            return redirect('index')
    form = PostForm()
    return render(request, 'new.html', {'form': form})


@login_required
def groups(request):
    all_groups = Group.objects.all()
    paginator = Paginator(all_groups, 7)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group_all.html',
        {'groups': all_groups, 'page': page, 'paginator': paginator}
        )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(author=user, user=request.user)
    return render(
        request,
        'profile.html',
        {'author': user,
         'page': page,
         'paginator': paginator,
         'following': following}
        )


def post_view(request, username, post_id):
    post = get_object_or_404(
        Post,
        author__username=username,
        pk=post_id
        )
    items = post.comments.all()
    form = CommentForm(request.POST or None)
    return render(request, 'post.html', {
        'author': post.author, 'post': post, 'items': items, 'form': form
        })


def post_edit(request, username, post_id):
    post = get_object_or_404(
        Post,
        pk=post_id,
        author__username=username
        )
    if request.user != post.author:
        return redirect('post', post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    else:
        edit = True
        return render(request, 'new.html', {'form': form,
                                            'post': post,
                                            'edit': edit})


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment_get = form.save(commit=False)
        comment_get.author = request.user
        comment_get.post_id = post.pk
        comment_get.save()
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post, pk=post_id)
    items = post.comments.all()
    return render(request, 'post.html', {'form': form,
                                         'items': items,
                                         'post': post})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    follow = False
    if post_list is not None:
        paginator = Paginator(post_list, 10)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        follow = True
    return render(
        request,
        "follow.html",
        {"page": page,
         'paginator': paginator,
         'follow': follow}
        )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author.username != request.user.username:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author.username != request.user.username:
        Follow.objects.get(user=request.user, author=author).delete()
    return redirect('profile', username=username)
