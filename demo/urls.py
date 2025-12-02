from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # Public pages
    path('', views.home_unauthorized, name='home_unauthorized'),
    path('dashboard/', login_required(views.home_view), name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('password_reset/', views.custom_password_reset, name='password_reset'),
    
    # Authenticated user pages
    path('profile/', views.user_profile, name='user_profile'),
    path('profile_success/', views.profile_success, name='profile_success'),
    path('recipe_list/', views.recipe_list_view, name='recipe_list'),
    path('recipe_detail/<int:recipe_id>/', views.recipe_detail_view, name='recipe_detail'),
    path('feedback/', views.feedback_page, name='feedback_page'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('logout/', views.logout_view, name='logout'),
]
