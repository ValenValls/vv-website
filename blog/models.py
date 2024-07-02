# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone
import ollama 

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_posts')   
    last_editor= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,blank=True, null=True, related_name='edited_posts')   
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    photo = models.ImageField(upload_to='post-images', blank=True, null=True)
    def publish(self):
        self.published_date = timezone.now() 
        self.save()       
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        response = ollama.chat(model='gengis', messages=[{ 'role': 'system', 'content': 'You are the great Genghis Khan, Mongol emperator'},{'role': 'user', 'content': 'Title: ('+ self.title + ') Text: ('+ self.text + ')'}])
        Comment.objects.create(post=self, author='TheBestKh4n', text=response['message']['content'], created_date = self.published_date)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text