from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_bio', 'has_picture')
    search_fields = ('user__username', 'bio')
    readonly_fields = ('user',)
    list_per_page = 20

    def short_bio(self, obj):
        if obj.bio:
            return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
        return '-'
    short_bio.short_description = 'Bio'

    def has_picture(self, obj):
        return bool(obj.profile_picture)
    has_picture.boolean = True
    has_picture.short_description = 'Picture'