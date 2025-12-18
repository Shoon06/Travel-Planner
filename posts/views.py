from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Post, Comment
from planner.models import Destination

class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Post.objects.select_related('user', 'destination').prefetch_related('likes', 'loves')
        
        # Filter by destination if specified
        destination_id = self.request.GET.get('destination')
        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        
        # Filter by user if specified
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destinations'] = Destination.objects.all()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'posts/post_create.html'
    fields = ['title', 'content', 'destination', 'image', 'video']
    success_url = reverse_lazy('posts:post_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destinations'] = Destination.objects.all()
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('user').order_by('created_at')
        return context

@login_required
@require_POST
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        # Remove from loves if exists
        if request.user in post.loves.all():
            post.loves.remove(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count(),
        'loves_count': post.loves.count()
    })

@login_required
@require_POST
def love_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.loves.all():
        post.loves.remove(request.user)
        loved = False
    else:
        post.loves.add(request.user)
        # Remove from likes if exists
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        loved = True
    
    return JsonResponse({
        'loved': loved,
        'likes_count': post.likes.count(),
        'loves_count': post.loves.count()
    })

@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    content = request.POST.get('content', '').strip()
    
    if content:
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'user': comment.user.username,
                'created_at': comment.created_at.strftime('%b %d, %Y %I:%M %p'),
                'user_avatar': '👤'  # You can add actual avatar URLs later
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Comment cannot be empty'})