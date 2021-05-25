from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager
from tinymce.models import HTMLField

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=100)
    content = HTMLField()
    image = models.ImageField(upload_to='post_imgs', blank=True)
    tags = TaggableManager(blank = True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk':self.pk})


