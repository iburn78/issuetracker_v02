from django.db import models
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from tinymce.models import HTMLField
from django.contrib.auth.models import User 
from bs4 import BeautifulSoup

class PostRoot(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=100)
    content = HTMLField()
    image = models.ImageField(upload_to='post_imgs', blank=True)
    tags = TaggableManager(blank = True)
    
    def get_preview_text(self):
        soup = BeautifulSoup(self.content)
        return soup.find('p').text[:50]

    def __str__(self):
        return self.title

    class Meta: 
        abstract = True

class Post(PostRoot):
    level = "public"

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk':self.pk})

class PrivatePost(PostRoot):
    level = "private"

    def get_absolute_url(self):
        return reverse('privatepost-detail', kwargs={'pk':self.pk})



