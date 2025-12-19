from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, TemplateView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Count, Q, Sum, Max
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import json
from django.urls import reverse_lazy
from django import forms

from users.models import CustomUser
from planner.models import Destination, Hotel, Flight, BusService, CarRental, TripPlan
from posts.models import Post, Comment
# Add this import at the top of users/views_admin.py
from .forms import CustomUserCreationForm

# Create a simple form class directly in views_admin.py
class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter a strong password"
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter the same password as above"
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'first_name', 'last_name', 
                  'phone_number', 'location', 'bio', 'profile_picture', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_user()

class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User statistics
        context['total_users'] = CustomUser.objects.count()
        context['new_users_today'] = CustomUser.objects.filter(
            date_joined__date=timezone.now().date()
        ).count()
        
        # Trip statistics
        context['total_trips'] = TripPlan.objects.count()
        context['active_trips'] = TripPlan.objects.filter(
            status__in=['planning', 'booked']
        ).count()
        context['completed_trips'] = TripPlan.objects.filter(status='completed').count()
        
        # Destination statistics
        context['total_destinations'] = Destination.objects.count()
        
        # Hotel statistics
        context['total_hotels'] = Hotel.objects.count()
        context['active_hotels'] = Hotel.objects.filter(is_active=True).count()
        
        # Transport statistics
        context['total_flights'] = Flight.objects.count()
        context['total_buses'] = BusService.objects.count()
        context['total_cars'] = CarRental.objects.count()
        
        # Revenue calculation (simplified)
        total_revenue = 0
        trips = TripPlan.objects.filter(status__in=['booked', 'completed'])
        for trip in trips:
            # Add hotel cost
            if trip.selected_hotel:
                nights = (trip.end_date - trip.start_date).days
                if nights <= 0:
                    nights = 1
                hotel_cost = float(trip.selected_hotel.price_per_night) * nights * 2100
                total_revenue += hotel_cost
            
            # Add transport cost if available
            if hasattr(trip, 'selected_transport') and trip.selected_transport:
                if 'price' in trip.selected_transport:
                    try:
                        transport_cost = float(trip.selected_transport['price'])
                        total_revenue += transport_cost
                    except (ValueError, TypeError):
                        pass
        
        context['total_revenue'] = total_revenue
        
        # Recent activity
        context['recent_users'] = CustomUser.objects.order_by('-date_joined')[:5]
        context['recent_trips'] = TripPlan.objects.select_related(
            'user', 'destination'
        ).order_by('-created_at')[:5]
        
        return context


class AdminUserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'users/admin_dashboard_users.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is admin
        if not request.user.is_authenticated or not request.user.is_admin_user():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('users:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = CustomUser.objects.all().order_by('-date_joined')
        
        # Search filter
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        # User type filter
        user_type = self.request.GET.get('type', '')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
        # Status filter
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Count statistics
        context['total_users'] = CustomUser.objects.count()
        context['admin_count'] = CustomUser.objects.filter(user_type='admin').count()
        context['regular_users'] = CustomUser.objects.filter(user_type='user').count()
        context['active_users_count'] = CustomUser.objects.filter(is_active=True).count()
        context['new_users_today'] = CustomUser.objects.filter(
            date_joined__date=timezone.now().date()
        ).count()
        
        return context

class AdminTripListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    template_name = 'users/admin_trip_list.html'
    model = TripPlan
    context_object_name = 'trips'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('user', 'destination')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by user
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by destination
        destination_id = self.request.GET.get('destination')
        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        
        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                start_date__gte=start_date,
                end_date__lte=end_date
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_users'] = CustomUser.objects.all()[:50]
        context['destinations'] = Destination.objects.all()
        return context

class AdminTripAnalyticsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_trip_analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Time period for analytics (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Trip creation trend
        trip_creation_data = []
        for i in range(30):
            date = thirty_days_ago + timedelta(days=i)
            count = TripPlan.objects.filter(created_at__date=date.date()).count()
            trip_creation_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        context['trip_creation_data'] = json.dumps(trip_creation_data)
        
        # Trip status distribution
        status_distribution = list(TripPlan.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status'))
        
        context['status_distribution'] = status_distribution
        
        # Popular destinations
        popular_destinations = list(TripPlan.objects.values(
            'destination__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        
        context['popular_destinations'] = popular_destinations
        
        # User activity
        active_users = list(TripPlan.objects.values(
            'user__username', 'user__email'
        ).annotate(
            trip_count=Count('id'),
            last_trip=Max('created_at')
        ).order_by('-trip_count')[:10])
        
        context['active_users'] = active_users
        
        # Monthly revenue trend (simplified)
        monthly_revenue = []
        for i in range(6):
            month_start = timezone.now() - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            
            trips = TripPlan.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end,
                status__in=['booked', 'completed']
            )
            
            revenue = 0
            for trip in trips:
                if trip.selected_hotel:
                    nights = (trip.end_date - trip.start_date).days
                    if nights <= 0:
                        nights = 1
                    hotel_cost = float(trip.selected_hotel.price_per_night) * nights * 2100
                    revenue += hotel_cost
            
            monthly_revenue.append({
                'month': month_start.strftime('%b'),
                'revenue': revenue
            })
        
        context['monthly_revenue'] = json.dumps(list(reversed(monthly_revenue)))
        
        return context

class AdminUserRoleManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    template_name = 'users/admin_user_roles.html'
    model = CustomUser
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        return CustomUser.objects.order_by('user_type', 'username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate counts
        all_users = CustomUser.objects.all()
        context['admin_count'] = all_users.filter(user_type='admin').count()
        context['user_count'] = all_users.filter(user_type='user').count()
        return context


# Add to users/views_admin.py (at the end of the file)


# Add this to users/views_admin.py if not already there
class AdminAddUserView(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/admin_add_user.html'
    success_url = reverse_lazy('users:admin_dashboard_users')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is admin
        if not request.user.is_authenticated or not request.user.is_admin_user():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('users:login')
        return super().dispatch(request, *args, **kwargs)
    
# Update the form_valid method in AdminAddUserView
def form_valid(self, form):
    user = form.save(commit=False)
    user_type = form.cleaned_data.get('user_type', 'user')
    user.user_type = user_type
    
    # Set is_active from form data
    is_active = self.request.POST.get('is_active') == 'on'
    user.is_active = is_active
    
    # Set staff status if superuser is creating
    if self.request.user.is_superuser:
        is_staff = self.request.POST.get('is_staff') == 'on'
        user.is_staff = is_staff
    
    user.save()
    messages.success(self.request, f'User {user.username} created successfully!')
    
    # Check if "Save & Add Another" was clicked
    if 'add_another' in self.request.POST:
        return redirect('users:admin_add_user')
    
    return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class AdminContentManagementView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_content.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get content statistics
        context['total_destinations'] = Destination.objects.count()
        context['total_hotels'] = Hotel.objects.count()
        context['total_flights'] = Flight.objects.count()
        context['total_buses'] = BusService.objects.count()
        context['total_cars'] = CarRental.objects.count()
        context['total_posts'] = Post.objects.count()
        context['total_comments'] = Comment.objects.count()
        
        # Get recent content
        context['recent_destinations'] = Destination.objects.order_by('-created_at')[:5]
        context['recent_hotels'] = Hotel.objects.order_by('-created_at')[:5]
        context['recent_posts'] = Post.objects.select_related('user', 'destination').order_by('-created_at')[:5]
        
        return context

class AdminDatabaseBackupView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_backup.html'
    
    def post(self, request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # In a real application, you would implement actual backup logic here
                # For now, we'll just return success
                import datetime
                backup_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                
                # Log the backup request
                print(f"Database backup requested by {request.user.username} at {backup_time}")
                
                return JsonResponse({
                    'success': True,
                    'message': f'Backup initiated successfully. Backup ID: {backup_time}',
                    'backup_id': backup_time
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return render(request, self.template_name)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get backup history (simulated)
        import datetime
        context['backup_history'] = [
            {'id': 'backup_2025_12_15_14_30', 'time': '2025-12-15 14:30', 'size': '45 MB'},
            {'id': 'backup_2025_12_10_09_15', 'time': '2025-12-10 09:15', 'size': '42 MB'},
            {'id': 'backup_2025_12_05_22_45', 'time': '2025-12-05 22:45', 'size': '40 MB'},
        ]
        
        return context