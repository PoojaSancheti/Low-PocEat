# demo/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, HealthConditions

class UserProfileForm(forms.ModelForm):
    diet_pref = forms.MultipleChoiceField(
        choices=[
            ('Vegetarian', 'Vegetarian'),
            ('Non-Vegetarian', 'Non-Vegetarian'),
            ('Vegan', 'Vegan'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    food_allergies = forms.ChoiceField(
        choices=[
            ('lactose_intolerance', 'Lactose Intolerance'),
            ('gluten_intolerance', 'Gluten Intolerance'),
            ('fructose_intolerance', 'Fructose Intolerance'),
            ('histamine_intolerance', 'Histamine Intolerance'),
        ],
        widget=forms.Select,
        required=False
    )
    health_con = forms.ModelMultipleChoiceField(
        queryset= HealthConditions.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['name', 'age', 'height', 'weight', 'diet_pref', 'food_allergies', 'health_con']
class SignUpForm(forms.ModelForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text=(
            "Your password must contain at least 8 characters, "
            "can't be too similar to your other personal information, "
            "and can't be a commonly used password."
        ),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification.",
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please use a different email address.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class FeedbackForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    rating = forms.ChoiceField(choices=[(str(i), str(i)) for i in range(1, 6)], required=True)
