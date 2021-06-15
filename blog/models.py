from django.db import models
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from tinymce.models import HTMLField
from django.contrib.auth.models import User as BASE_USER_MODEL

class User(BASE_USER_MODEL):
    def post_count(self):
        return Post.objects.filter(author=self.pk).count()

class PostRoot(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=100)
    content = HTMLField()
    image = models.ImageField(upload_to='post_imgs', blank=True)
    tags = TaggableManager(blank = True)
#    LEVELS = (
#        ('private', 'private'), 
#        ('public', 'public'), 
#    )
#    level = models.CharField(max_length=10, choices=LEVELS, default='private')

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



