from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'destination', 'total_reactions', 'created_at']
    list_filter = ['created_at', 'destination']
    search_fields = ['title', 'content', 'user__username']
    actions = ['feature_post', 'delete_old_posts']
    
    def feature_post(self, request, queryset):
        # Implement featuring logic here
        self.message_user(request, f'{queryset.count()} posts featured.')
    feature_post.short_description = "Feature selected posts"
    
    def delete_old_posts(self, request, queryset):
        # Delete posts older than a certain date
        deleted = queryset.count()
        queryset.delete()
        self.message_user(request, f'{deleted} old posts deleted.')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username']