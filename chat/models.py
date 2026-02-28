from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history')
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
