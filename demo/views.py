from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

from .models import Meal, UserProfile, HealthConditions, Feedback
from .forms import SignUpForm, UserProfileForm, FeedbackForm, User




# ----------------- Auth / Signup / OTP -----------------

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                # Save the user (this will handle password hashing)
                user = form.save()
                
                # Log the user in
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Account created successfully! You are now logged in.')
                    return redirect('home')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            # Form is not valid, collect all error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()
        
    return render(request, 'demo/signup.html', {'form': form})


# OTP verification has been removed


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        next_url = request.POST.get('next', '')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    # If not POST or authentication failed, show the login form
    return render(request, 'demo/login.html', {'next': request.GET.get('next', '')})


def logout_view(request):
    logout(request)
    return redirect('home_unauthorized')


# ----------------- Home / Profile -----------------

def home_unauthorized(request):
    """View for non-authenticated users"""
    return render(request, 'demo/home_unauthorized.html')

@login_required
def home_view(request):
    """View for authenticated users"""
    return render(request, 'demo/home.html', {'username': request.user.username})


@login_required
def user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user_profile, created = UserProfile.objects.update_or_create(
                user=request.user,
                defaults={
                    'name': form.cleaned_data['name'],
                    'age': form.cleaned_data['age'],
                    'height': form.cleaned_data['height'],
                    'weight': form.cleaned_data['weight'],
                    'diet_pref': form.cleaned_data['diet_pref'],
                    'food_allergies': form.cleaned_data['food_allergies'],
                }
            )
            # Update many-to-many relation
            user_profile.health_con.set(form.cleaned_data['health_con'])
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile_success')
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        user_profile = UserProfile.objects.filter(user=request.user).first()
        if user_profile:
            form = UserProfileForm(instance=user_profile)
        else:
            form = UserProfileForm()
    return render(request, 'demo/userprofile.html', {'form': form})


def profile_success(request):
    return render(request, 'demo/profilesuc.html')


# ----------------- Recipes -----------------

@login_required
def recipe_list_view(request):
    meal_type = request.GET.get('meal_type')
    diet_suitability = request.GET.get('diet_suitability')
    health_condition = request.GET.get('health_condition')
    total_cost = request.GET.get('total_cost')

    total_cost = float(total_cost) if total_cost else None

    meals = Meal.objects.all()

    if meal_type:
        meals = meals.filter(meal_type=meal_type)
    if diet_suitability:
        meals = meals.filter(diet_suitability=diet_suitability)
    if health_condition:
        meals = meals.filter(health_condition_suitability__name=health_condition)
    if total_cost:
        meals = meals.filter(total_cost__lte=total_cost)

    health_conditions = HealthConditions.objects.all()

    return render(request, 'demo/recipe_list.html', {
        'meals': meals,
        'health_conditions': health_conditions,
        'meal_type': meal_type,
        'diet_suitability': diet_suitability,
        'health_condition': health_condition,
        'total_cost': total_cost,
    })


@login_required
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(Meal, id=recipe_id)
    associated_health_conditions = recipe.health_condition_suitability.all()
    return render(request, 'demo/recipe_detail.html', {
        'recipe': recipe,
        'associated_health_conditions': associated_health_conditions,
    })


# ----------------- Feedback / Contact -----------------

def feedback_page(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            rating = form.cleaned_data['rating']

            feedback = Feedback(
                name=name,
                email=email,
                message=message,
                rating=rating
            )
            feedback.save()

            try:
                send_mail(
                    subject=f"Contact Us Form Submission from {name}",
                    message=f"Name: {name}\nEmail: {email}\nRating: {rating}\n\nMessage:\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['support@example.com'],  # Change to your email
                )
                return HttpResponse("Your message has been sent successfully. We'll get back to you shortly.")
            except Exception as e:
                return HttpResponse(f"Error: {e}")
    else:
        form = FeedbackForm()
    return render(request, 'demo/feedback.html', {'form': form})


def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        try:
            send_mail(
                subject=f"Contact Us Form Submission from {name}",
                message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['support@example.com'],  # Change to your email
            )
            return HttpResponse("Your message has been sent successfully. We'll get back to you shortly.")
        except Exception as e:
            return HttpResponse(f"Error: {e}")
    else:
        return HttpResponse("Invalid request.")


# ----------------- Password reset -----------------

def custom_password_reset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('password_reset')
            
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'User with this username does not exist.')
            return redirect('password_reset')
    
    return render(request, 'demo/password_reset.html')

# Remove email-related password reset views as they won't be used


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'demo/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'demo/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'demo/password_reset_complete.html'
