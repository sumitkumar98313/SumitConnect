from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
import re
from .models import Post, Like, Comment, Follow


def home(request):
    return render(request, 'accounts/home.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'accounts/signup.html')

        if not re.match(r'^\w+$', username):
            messages.error(request, 'Username can only contain letters, numbers and underscores.')
            return render(request, 'accounts/signup.html')

        if len(username) < 3 or len(username) > 30:
            messages.error(request, 'Username must be between 3 and 30 characters.')
            return render(request, 'accounts/signup.html')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'accounts/signup.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
            return render(request, 'accounts/signup.html')

        User.objects.create_user(username=username, password=password)
        messages.success(request, 'Account created! Please log in.')
        return redirect('login')

    return render(request, 'accounts/signup.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')


@login_required
def dashboard(request):
    recent_users = User.objects.exclude(
        id=request.user.id
    ).order_by('-date_joined').select_related('profile')[:5]

    context = {
        'recent_users': recent_users,
        'my_posts_count': Post.objects.filter(author=request.user).count(),
        'followers_count': Follow.objects.filter(following=request.user).count(),
        'following_count': Follow.objects.filter(follower=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        bio = request.POST.get('bio', '').strip()
        picture = request.FILES.get('profile_picture')
        p = request.user.profile
        p.bio = bio
        if picture:
            p.profile_picture = picture
        p.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')
    return render(request, 'accounts/profile.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        current = request.POST.get('current_password', '')
        new = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'accounts/change_password.html')

        if len(new) < 6:
            messages.error(request, 'New password must be at least 6 characters.')
            return render(request, 'accounts/change_password.html')

        if new != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/change_password.html')

        if new == current:
            messages.error(request, 'New password cannot be same as current.')
            return render(request, 'accounts/change_password.html')

        request.user.set_password(new)
        request.user.save()
        messages.success(request, 'Password updated! Please log in again.')
        return redirect('login')

    return render(request, 'accounts/change_password.html')


@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password', '')
        if request.user.check_password(password):
            logout(request)
            request.user.delete()
            messages.success(request, 'Account deleted successfully.')
            return redirect('home')
        messages.error(request, 'Incorrect password.')
    return render(request, 'accounts/delete_account.html')


@login_required
def users_list(request):
    query = request.GET.get('search', '').strip()
    if query:
        users = User.objects.filter(
            username__icontains=query
        ).exclude(id=request.user.id).select_related('profile')
    else:
        users = User.objects.exclude(
            id=request.user.id
        ).order_by('-date_joined').select_related('profile')
    return render(request, 'accounts/users.html', {'users': users, 'query': query})


@login_required
def user_profile(request, username):
    viewed_user = get_object_or_404(
        User.objects.select_related('profile'), username=username
    )
    user_posts = Post.objects.filter(
        author=viewed_user
    ).select_related('author', 'author__profile')

    context = {
        'viewed_user': viewed_user,
        'user_posts': user_posts,
        'is_following': Follow.objects.filter(follower=request.user, following=viewed_user).exists(),
        'followers_count': Follow.objects.filter(following=viewed_user).count(),
        'following_count': Follow.objects.filter(follower=viewed_user).count(),
    }
    return render(request, 'accounts/user_profile.html', context)


@login_required
def feed(request):
    posts = Post.objects.select_related(
        'author', 'author__profile'
    ).prefetch_related('likes', 'comments').order_by('-created_at')

    liked_ids = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    for post in posts:
        post.liked_by_user = post.id in liked_ids

    return render(request, 'accounts/feed.html', {'posts': posts})


@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        if not content:
            messages.error(request, 'Post cannot be empty.')
            return redirect('feed')

        if len(content) > 500:
            messages.error(request, 'Post cannot exceed 500 characters.')
            return redirect('feed')

        Post.objects.create(author=request.user, content=content, image=image)
        messages.success(request, 'Post created!')
        return redirect('feed')

    return redirect('feed')


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('feed')
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('feed')


@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like = Like.objects.filter(user=request.user, post=post)
    if like.exists():
        like.delete()
    else:
        Like.objects.create(user=request.user, post=post)
    next_url = request.POST.get('next', 'feed')
    return redirect(next_url)


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile'), id=post_id
    )
    comments = post.comments.select_related('user', 'user__profile')
    post.liked_by_user = post.is_liked_by(request.user)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if not content:
            messages.error(request, 'Comment cannot be empty.')
            return redirect('post_detail', post_id=post_id)
        if len(content) > 300:
            messages.error(request, 'Comment is too long.')
            return redirect('post_detail', post_id=post_id)
        Comment.objects.create(user=request.user, post=post, content=content)
        messages.success(request, 'Comment added!')
        return redirect('post_detail', post_id=post_id)

    return render(request, 'accounts/post_detail.html', {'post': post, 'comments': comments})


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        messages.error(request, 'You can only delete your own comments.')
        return redirect('post_detail', post_id=comment.post.id)
    comment.delete()
    messages.success(request, 'Comment deleted.')
    return redirect('post_detail', post_id=comment.post.id)


@login_required
@require_POST
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow == request.user:
        messages.error(request, "You can't follow yourself.")
        return redirect('user_profile', username=username)

    follow = Follow.objects.filter(follower=request.user, following=user_to_follow)
    if follow.exists():
        follow.delete()
        messages.success(request, f'Unfollowed {username}.')
    else:
        Follow.objects.create(follower=request.user, following=user_to_follow)
        messages.success(request, f'Now following {username}!')

    return redirect('user_profile', username=username)


def error_404(request, exception):
    return render(request, 'accounts/404.html', status=404)


def error_500(request):
    return render(request, 'accounts/500.html', status=500)