# demo/admin.py
from django.contrib import admin
from .models import HealthConditions, Meal, UserProfile

# Register your models here.
admin.site.register(HealthConditions)
admin.site.register(Meal)
admin.site.register(UserProfile)
