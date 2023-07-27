from django.urls import path
from . import views

# URL Configuration Module
# every app can have its own

urlpatterns = [ #django looks for this variable name specifically
	path('hello/', views.greet_user)	    #always end routes with /
]