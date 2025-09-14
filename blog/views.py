# blog/views.py
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post
from .forms import PostForm

# helper biar authors kepakai di beberapa view
def _published_authors_usernames():
    return (Post.objects
            .filter(published_date__isnull=False)
            .values_list('author__username', flat=True)
            .distinct()
            .order_by('author__username'))

def post_list(request):
    posts = (Post.objects
             .filter(published_date__isnull=False)
             .order_by('-published_date'))

    authors = _published_authors_usernames()

    selected = request.GET.get('author')
    if selected:
        posts = posts.filter(author__username=selected)

    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'authors': authors,
        'selected_author': selected,
    })

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # kalau mau langsung publish, keep line ini:
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # kalau belum ada published_date, publish sekarang:
            post.published_date = post.published_date or timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

def post_by_author(request, username):
    author = get_object_or_404(User, username__iexact=username)

    posts = (Post.objects
             .filter(author=author, published_date__isnull=False)
             .order_by('-published_date'))

    # untuk dropdown header (opsional)
    authors_usernames = (Post.objects
                         .filter(published_date__isnull=False)
                         .values_list('author__username', flat=True)
                         .distinct()
                         .order_by('author__username'))

    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'authors': authors_usernames,
        'selected_author': author.username,
    })


def authors_list(request):
    authors = (User.objects
               .filter(post__published_date__isnull=False)   
               .annotate(published_count=Count('post'))
               .order_by('username'))

    # NOTE:
  
    author_usernames = (Post.objects
                        .filter(published_date__isnull=False)
                        .values_list('author__username', flat=True)
                        .distinct()
                        .order_by('author__username'))

    return render(request, 'blog/authors_list.html', {
        'authors': authors,
        'authors_usernames': author_usernames, 
    })
