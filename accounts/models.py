from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# custom validator to check image file size
# i added this because pillow doesn't check size automatically
def validate_image_size(image):
    # 2MB limit - 2 * 1024 * 1024 = 2097152 bytes
    if image.size > 2 * 1024 * 1024:
        raise ValidationError('Image size must be under 2MB.')


# Profile model - extends the default Django User model
# every user gets one profile (created automatically via signals.py)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=200)
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        validators=[validate_image_size]
    )

    def __str__(self):
        return self.user.username

    # count how many users follow this profile
    @property
    def followers_count(self):
        return Follow.objects.filter(following=self.user).count()

    # count how many users this profile is following
    @property
    def following_count(self):
        return Follow.objects.filter(follower=self.user).count()


# Post model - for user posts in the feed
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=500)
    # image is optional - blank=True, null=True means not required
    image = models.ImageField(upload_to='posts/', blank=True, null=True, validators=[validate_image_size])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # newest posts show first
        ordering = ['-created_at']

    def __str__(self):
        return self.author.username + ' - ' + self.created_at.strftime('%d %b %Y')

    # total likes on this post
    @property
    def likes_count(self):
        return self.likes.count()

    # total comments on this post
    @property
    def comments_count(self):
        return self.comments.count()

    # check if a specific user has liked this post
    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()


# Like model - stores which user liked which post
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # one user can only like a post once
        unique_together = ('user', 'post')

    def __str__(self):
        return self.user.username + ' liked post ' + str(self.post.id)


# Comment model - stores comments on posts
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # oldest comments show first (like normal comment sections)
        ordering = ['created_at']

    def __str__(self):
        return self.user.username + ' on post ' + str(self.post.id)


# Follow model - stores who follows who
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # can't follow same person twice
        unique_together = ('follower', 'following')

    def __str__(self):
        return self.follower.username + ' follows ' + self.following.username
