from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import View
from django.contrib import messages
from .forms_admin import AdminUserCreationForm

class AdminAddUserView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'users/admin_add_user.html'
    
    def test_func(self):
        return self.request.user.is_admin_user()
    
    def get(self, request):
        form = AdminUserCreationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully!')
            
            # Log the action
            print(f"Admin {request.user.username} created user {user.username} ({user.user_type})")
            
            return redirect('users:admin_dashboard_users')
        
        return render(request, self.template_name, {'form': form})