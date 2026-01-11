# C:\Users\ASUS\MyanmarTravelPlanner\posts\urls.py
from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/like/', views.like_post, name='like_post'),
    path('<int:pk>/love/', views.love_post, name='love_post'),
    path('<int:pk>/dislike/', views.dislike_post, name='dislike_post'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/replies/', views.get_replies, name='get_replies'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/count/', views.get_notification_count, name='get_notification_count'),
]