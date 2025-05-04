
from django.contrib import admin
from .models import Room, Topic, Message, Profile, PasswordReset

# Register your models here.
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Profile)
admin.site.register(PasswordReset)