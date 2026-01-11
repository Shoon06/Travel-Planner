# C:\Users\ASUS\MyanmarTravelPlanner\posts\views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import models
from django.db.models import Q
from django.utils import timezone
from .models import Post, Comment, Notification
from planner.models import Destination, TripPlan
from users.models import CustomUser as User

class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Post.objects.select_related('user', 'destination', 'trip').prefetch_related('likes', 'loves', 'dislikes')
        
        # Filter by destination if specified
        destination_id = self.request.GET.get('destination')
        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        
        # Filter by user if specified
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by trip if specified
        trip_id = self.request.GET.get('trip')
        if trip_id:
            queryset = queryset.filter(trip_id=trip_id)
        
        # Sorting
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'popular':
            queryset = sorted(queryset, key=lambda x: x.total_reactions(), reverse=True)
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        else:  # newest
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destinations'] = Destination.objects.all()
        
        # Get top users (users with most posts)
        top_users = User.objects.annotate(
            post_count=models.Count('posts')
        ).order_by('-post_count')[:5]
        context['top_users'] = top_users
        
        # Get notification count for logged-in user
        if self.request.user.is_authenticated:
            unread_count = Notification.objects.filter(
                recipient=self.request.user,
                is_read=False
            ).count()
            context['unread_notifications'] = unread_count
        
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'posts/post_create.html'
    fields = ['title', 'content', 'destination', 'trip', 'image', 'video']
    success_url = reverse_lazy('posts:post_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter trips to only show user's trips
        if self.request.user.is_authenticated:
            form.fields['trip'].queryset = TripPlan.objects.filter(user=self.request.user)
            form.fields['destination'].queryset = Destination.objects.filter(is_active=True)
        return form
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destinations'] = Destination.objects.filter(is_active=True)
        if self.request.user.is_authenticated:
            context['user_trips'] = TripPlan.objects.filter(user=self.request.user)
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(parent=None).select_related('user').order_by('created_at')
        
        # Add related posts
        related_posts = Post.objects.filter(
            destination=self.object.destination
        ).exclude(id=self.object.id).select_related('user')[:3]
        context['related_posts'] = related_posts
        
        # Get unread notifications count
        if self.request.user.is_authenticated:
            unread_count = Notification.objects.filter(
                recipient=self.request.user,
                is_read=False
            ).count()
            context['unread_notifications'] = unread_count
        
        return context

@login_required
@require_POST
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
        # Delete notification if exists
        Notification.objects.filter(
            recipient=post.user,
            sender=request.user,
            post=post,
            notification_type='like'
        ).delete()
    else:
        post.likes.add(request.user)
        # Remove from other reactions if exists
        if request.user in post.loves.all():
            post.loves.remove(request.user)
            Notification.objects.filter(
                recipient=post.user,
                sender=request.user,
                post=post,
                notification_type='love'
            ).delete()
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)
            Notification.objects.filter(
                recipient=post.user,
                sender=request.user,
                post=post,
                notification_type='dislike'
            ).delete()
        liked = True
        
        # Create notification for post owner (if not reacting to own post)
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                sender=request.user,
                post=post,
                notification_type='like',
                message=f"{request.user.username} liked your post: '{post.title[:50]}...'"
            )
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count(),
        'loves_count': post.loves.count(),
        'dislikes_count': post.dislikes.count()
    })

@login_required
@require_POST
def love_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.loves.all():
        post.loves.remove(request.user)
        loved = False
        # Delete notification if exists
        Notification.objects.filter(
            recipient=post.user,
            sender=request.user,
            post=post,
            notification_type='love'
        ).delete()
    else:
        post.loves.add(request.user)
        # Remove from other reactions if exists
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            Notification.objects.filter(
                recipient=post.user,
                sender=request.user,
                post=post,
                notification_type='like'
            ).delete()
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)
            Notification.objects.filter(
                recipient=post.user,
                sender=request.user,
                post=post,
                notification_type='dislike'
            ).delete()
        loved = True
        
        # Create notification for post owner (if not reacting to own post)
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                sender=request.user,
                post=post,
                notification_type='love',
                message=f"{request.user.username} loved your post: '{post.title[:50]}...'"
            )
    
    return JsonResponse({
        'loved': loved,
        'likes_count': post.likes.count(),
        'loves_count': post.loves.count(),
        'dislikes_count': post.dislikes.count()
    })

@login_required
@require_POST
def dislike_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
        disliked = False
        # Delete notification if exists
        Notification.objects.filter(
            recipient=post.user,
            sender=request.user,
            post=post,
            notification_type='dislike'
        ).delete()
    else:
        post.dislikes.add(request.user)
        # Remove from other reactions if exists
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            Notification.objects.filter(
                recipient=post.user,
                sender=request.user,
                post=post,
                notification_type='like'
            ).delete()
        if request.user in post.loves.all():
            post.loves.remove(request.user)
            Notification.objects.filter(
                recipient=post.user,
                sender=request.user,
                post=post,
                notification_type='love'
            ).delete()
        disliked = True
        
        # Create notification for post owner (if not reacting to own post)
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                sender=request.user,
                post=post,
                notification_type='dislike',
                message=f"{request.user.username} disliked your post: '{post.title[:50]}...'"
            )
    
    return JsonResponse({
        'disliked': disliked,
        'likes_count': post.likes.count(),
        'loves_count': post.loves.count(),
        'dislikes_count': post.dislikes.count()
    })

@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')  # For replies
    
    if content:
        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
        
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            parent=parent_comment,
            content=content
        )
        
        # Create notification for post owner (if not commenting on own post)
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                sender=request.user,
                post=post,
                comment=comment,
                notification_type='reply' if parent_comment else 'comment',
                message=f"{request.user.username} {'replied to your comment' if parent_comment else 'commented on your post'}: '{content[:50]}...'"
            )
        
        # If this is a reply, also notify the parent comment owner
        if parent_comment and parent_comment.user != request.user and parent_comment.user != post.user:
            Notification.objects.create(
                recipient=parent_comment.user,
                sender=request.user,
                post=post,
                comment=comment,
                notification_type='reply',
                message=f"{request.user.username} replied to your comment: '{content[:50]}...'"
            )
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'user': comment.user.username,
                'user_id': comment.user.id,
                'created_at': comment.created_at.strftime('%b %d, %Y %I:%M %p'),
                'user_avatar': '👤',
                'parent_id': comment.parent.id if comment.parent else None,
                'is_reply': comment.is_reply()
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Comment cannot be empty'})

@login_required
def get_replies(request, comment_id):
    """Get all replies for a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    replies = comment.get_replies().select_related('user')
    
    replies_data = []
    for reply in replies:
        replies_data.append({
            'id': reply.id,
            'content': reply.content,
            'user': reply.user.username,
            'user_id': reply.user.id,
            'created_at': reply.created_at.strftime('%b %d, %Y %I:%M %p'),
            'user_avatar': '👤'
        })
    
    return JsonResponse({'replies': replies_data})

@login_required
def notifications_view(request):
    """View for notifications page"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'post', 'comment').order_by('-created_at')[:50]
    
    # Mark all as read
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return render(request, 'posts/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})

@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    return JsonResponse({'success': True})

@login_required
def get_notification_count(request):
    """Get unread notification count"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})