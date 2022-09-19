from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import related

# Create your models here.

class AboutUser(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
        ('Prefer Not to Say', 'Prefer Not to Say')
    )

    user = models.OneToOneField(User, on_delete = models.CASCADE)
    gender = models.CharField(max_length = 100, choices = GENDER_CHOICES)
    age = models.IntegerField() # For checking restriction (age is required)
    contact_number = models.IntegerField(blank = True, null=True, unique=True)
    description = models.TextField(blank = True, null=True)
    created = models.DateTimeField(auto_now_add=True)




class PostCategory(models.Model):
    category_name = models.CharField(max_length = 150)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name

    class Meta:
        ordering = ['-created']

class Post(models.Model):
    posted_by = models.ForeignKey(User, on_delete = models.CASCADE)
    post_title = models.CharField(max_length = 100)
    post_category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, null = True)
    post_content = models.TextField()
    post_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post_title

    class Meta:
        ordering = ['-post_created']


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'following')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']


class Like(models.Model):
    liked_by = models.ForeignKey(User, on_delete = models.CASCADE)
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    created = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-created']


class Save(models.Model):
    saved_by = models.ForeignKey(User, on_delete = models.CASCADE)
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    created = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-created']


class Comment(models.Model):
    comment_by = models.ForeignKey(User, on_delete = models.CASCADE)
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.comment


class CommentLike(models.Model):
    liked_by = models.ForeignKey(User, on_delete = models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete = models.CASCADE)
    created = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-created']