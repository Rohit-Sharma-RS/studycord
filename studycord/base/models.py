from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # if room deleted, set topic to null allow null to set topic to null
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length = 200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated', '-created'] 
        # ordering by updated and created date
    
    def __str__(self):
        return self.name

    #is_active = models.BooleanField(default=True)
    #is_private = models.BooleanField(default=False)
    #is_deleted = models.BooleanField(default=False)
    #is_archived = models.BooleanField(default=False)
    #is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.name)

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.body[0:50])
    
