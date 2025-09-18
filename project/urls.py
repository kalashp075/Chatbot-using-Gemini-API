"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import *

urlpatterns = [
    path('', myapp, name="myapp"),
    path('login_page/', login_page, name="login_page"),
    path('signup_page1/', signup_page1, name="signup_page1"),
    path('signup_page2/', signup_page2, name="signup_page2"),
    path('signup_page3/', signup_page3, name="signup_page3"),
    path('verification/', verification, name="verification"),
    path('home_page/', home_page, name="home_page"),
    path('landing/', landing, name="landing"),
    path('logout/', logout_view, name='logout_view'),
    path('resend_verification/', resend_verification, name='resend_verification'),
    path('profile_page/',profile_page, name='profile_page'),
    path('ai_interaction/', ai_interaction, name='ai_interaction'),
    path('ask_gemini/',ask_gemini, name='ask_gemini'),
    path('admin/', admin.site.urls),
]
