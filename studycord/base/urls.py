from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('register/', views.registerUser, name='register'),

    path('', views.home, name='home'), # always get home as name makes it awesome

    path('room/<str:pk>/', views.room, name='room'),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<int:pk>', views.updateRoom, name='update-room'),
    path('delete-room/<int:pk>', views.deleteRoom, name='delete-room'),
    
    path('update-user/', views.updateUser, name='update-user'),
    path('delete-message/<int:pk>', views.deleteMessage, name='delete-message')
]
