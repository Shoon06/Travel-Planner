# C:\Users\ASUS\MyanmarTravelPlanner\posts\models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    destination = models.ForeignKey('planner.Destination', on_delete=models.SET_NULL, null=True, blank=True)
    trip = models.ForeignKey('planner.TripPlan', on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    
    # Reactions
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    loves = models.ManyToManyField(User, related_name='loved_posts', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_posts', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"
    
    def total_likes(self):
        return self.likes.count()
    
    def total_loves(self):
        return self.loves.count()
    
    def total_dislikes(self):
        return self.dislikes.count()
    
    def total_reactions(self):
        return self.total_likes() + self.total_loves() + self.total_dislikes()
    
    def get_user_reaction(self, user):
        """Get the user's reaction to this post"""
        if user in self.likes.all():
            return 'like'
        elif user in self.loves.all():
            return 'love'
        elif user in self.dislikes.all():
            return 'dislike'
        return None
    
    def get_notifications(self):
        """Get all notifications for this post"""
        return self.notifications.all()
    
    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    
    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None
    
    def get_replies(self):
        """Get all replies to this comment"""
        return self.replies.all().order_by('created_at')
    
    class Meta:
        ordering = ['created_at']

# NEW: Notification Model
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('love', 'Love'),
        ('dislike', 'Dislike'),
        ('comment', 'Comment'),
        ('reply', 'Reply'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification_type} notification for {self.recipient.username}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
        ]