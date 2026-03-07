from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Like, Comment, Follow


# Home Page
def home(request):
    return render(request, 'accounts/home.html')


# Dashboard
@login_required
def dashboard(request):
    recent_users = User.objects.order_by('-date_joined')[:5]
    my_posts_count = Post.objects.filter(author=request.user).count()
    followers_count = Follow.objects.filter(following=request.user).count()
    following_count = Follow.objects.filter(follower=request.user).count()
    context = {
        'recent_users': recent_users,
        'my_posts_count': my_posts_count,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    return render(request, 'accounts/dashboard.html', context)


# Signup
def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'accounts/signup.html')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'accounts/signup.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return render(request, 'accounts/signup.html')

        User.objects.create_user(username=username, password=password)
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')

    return render(request, 'accounts/signup.html')


# Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


# Logout
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# Profile Page
@login_required
def profile(request):
    if request.method == "POST":
        bio = request.POST.get('bio', '').strip()
        picture = request.FILES.get('profile_picture')
        user_profile = request.user.profile
        user_profile.bio = bio
        if picture:
            user_profile.profile_picture = picture
        user_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'accounts/profile.html')


# View Another User's Profile
@login_required
def user_profile(request, username):
    viewed_user = get_object_or_404(User, username=username)
    is_following = Follow.objects.filter(
        follower=request.user,
        following=viewed_user
    ).exists()
    user_posts = Post.objects.filter(author=viewed_user)
    context = {
        'viewed_user': viewed_user,
        'is_following': is_following,
        'user_posts': user_posts,
        'followers_count': Follow.objects.filter(following=viewed_user).count(),
        'following_count': Follow.objects.filter(follower=viewed_user).count(),
    }
    return render(request, 'accounts/user_profile.html', context)


# Users List + Search
@login_required
def users_list(request):
    query = request.GET.get('search', '').strip()
    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    else:
        users = User.objects.exclude(id=request.user.id).order_by('-date_joined')
    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'accounts/users.html', context)


# Change Password
@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'accounts/change_password.html')

        if len(new_password) < 6:
            messages.error(request, 'New password must be at least 6 characters.')
            return render(request, 'accounts/change_password.html')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'accounts/change_password.html')

        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Password changed successfully! Please log in again.')
        return redirect('login')

    return render(request, 'accounts/change_password.html')


# Delete Account
@login_required
def delete_account(request):
    if request.method == "POST":
        password = request.POST.get('password', '')
        if request.user.check_password(password):
            request.user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Account not deleted.')
    return render(request, 'accounts/delete_account.html')


# Feed — All Posts
@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    # Add liked status for each post
    for post in posts:
        post.liked_by_user = post.is_liked_by(request.user)
    context = {
        'posts': posts,
    }
    return render(request, 'accounts/feed.html', context)


# Create Post
@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        if not content:
            messages.error(request, 'Post content cannot be empty.')
            return redirect('feed')

        Post.objects.create(
            author=request.user,
            content=content,
            image=image
        )
        messages.success(request, 'Post created successfully!')
        return redirect('feed')

    return redirect('feed')


# Delete Post
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Only the author can delete their post
    if post.author != request.user:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('feed')

    post.delete()
    messages.success(request, 'Post deleted successfully.')
    return redirect('feed')


# Like / Unlike Post
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like = Like.objects.filter(user=request.user, post=post)

    if like.exists():
        like.delete()  # Unlike
    else:
        Like.objects.create(user=request.user, post=post)  # Like

    # Go back to wherever the user came from
    next_url = request.GET.get('next', 'feed')
    return redirect(next_url)


# Post Detail + Comments
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    post.liked_by_user = post.is_liked_by(request.user)

    if request.method == "POST":
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                user=request.user,
                post=post,
                content=content
            )
            messages.success(request, 'Comment added!')
        else:
            messages.error(request, 'Comment cannot be empty.')
        return redirect('post_detail', post_id=post_id)

    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'accounts/post_detail.html', context)


# Delete Comment
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id

    # Only comment author can delete
    if comment.user != request.user:
        messages.error(request, 'You can only delete your own comments.')
        return redirect('post_detail', post_id=post_id)

    comment.delete()
    messages.success(request, 'Comment deleted.')
    return redirect('post_detail', post_id=post_id)


# Follow / Unfollow User
@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    # Can't follow yourself
    if user_to_follow == request.user:
        messages.error(request, "You can't follow yourself.")
        return redirect('user_profile', username=username)

    follow = Follow.objects.filter(
        follower=request.user,
        following=user_to_follow
    )

    if follow.exists():
        follow.delete()  # Unfollow
        messages.success(request, f'You unfollowed {username}.')
    else:
        Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )
        messages.success(request, f'You are now following {username}!')

    return redirect('user_profile', username=username)