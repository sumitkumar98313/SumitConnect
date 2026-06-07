from django.contrib import admin
from .models import Profile, Post, Like, Comment, Follow


# register Profile model in admin panel
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_bio', 'has_picture')
    search_fields = ('user__username', 'bio')
    readonly_fields = ('user',)  # user field should not be editable in admin
    list_per_page = 20

    # shows a short version of bio in the list view
    # truncates to 50 characters if too long
    def short_bio(self, obj):
        if obj.bio:
            if len(obj.bio) > 50:
                return obj.bio[:50] + '...'
            else:
                return obj.bio
        return '-'
    short_bio.short_description = 'Bio'

    # shows a green tick or red cross depending on whether user has a picture
    def has_picture(self, obj):
        return bool(obj.profile_picture)
    has_picture.boolean = True
    has_picture.short_description = 'Picture'


# register Post model in admin panel
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'short_content', 'likes_count', 'comments_count', 'created_at')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)  # created_at is auto set so make it read only
    list_per_page = 20

    # truncate long post content in list view
    def short_content(self, obj):
        if len(obj.content) > 60:
            return obj.content[:60] + '...'
        else:
            return obj.content
    short_content.short_description = 'Content'

    # show likes count in admin list
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

    # show comments count in admin list
    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = 'Comments'


# register Like model in admin panel
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username',)
    list_per_page = 20


# register Comment model in admin panel
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_content', 'post', 'created_at')
    search_fields = ('user__username', 'content')
    readonly_fields = ('created_at',)
    list_per_page = 20

    # truncate long comments in list view
    def short_content(self, obj):
        if len(obj.content) > 60:
            return obj.content[:60] + '...'
        else:
            return obj.content
    short_content.short_description = 'Comment'


# register Follow model in admin panel
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_per_page = 20
