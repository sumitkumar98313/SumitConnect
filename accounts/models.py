from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# User Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username

    # Helper to count followers
    def followers_count(self):
        return Follow.objects.filter(following=self.user).count()

    # Helper to count following
    def following_count(self):
        return Follow.objects.filter(follower=self.user).count()


# Auto create and save profile when user is created
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


# Post Model
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Newest posts first

    def __str__(self):
        return f"{self.author.username} - {self.created_at.strftime('%d %b %Y')}"

    # Helper to count likes
    def likes_count(self):
        return self.likes.count()

    # Helper to count comments
    def comments_count(self):
        return self.comments.count()

    # Check if a specific user has liked this post
    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()


# Like Model
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # One like per user per post

    def __str__(self):
        return f"{self.user.username} liked {self.post.id}"


# Comment Model
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']  # Oldest comments first

    def __str__(self):
        return f"{self.user.username} on post {self.post.id}"


# Follow Model
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # Can't follow same person twice

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"