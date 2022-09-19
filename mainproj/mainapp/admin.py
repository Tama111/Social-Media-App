from django.contrib import admin
from .models import AboutUser, PostCategory, Post, Follow, Like, Save, Comment, CommentLike

# Register your models here.

@admin.register(AboutUser)
class AboutUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'gender', 'age', 'contact_number', 'description', 'created']


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name', 'created']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'posted_by', 'post_title', 'post_category', 'post_content', 'post_created']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'follower', 'following', 'created']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'liked_by', 'post', 'created']


@admin.register(Save)
class SaveAdmin(admin.ModelAdmin):
    list_display = ['id', 'saved_by', 'post', 'created']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'comment_by', 'post', 'comment', 'created']


@admin.register(CommentLike)
class CommentLike(admin.ModelAdmin):
    list_display = ['id', 'liked_by', 'comment', 'created']