# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone
import google.generativeai as genai
import os 
import random
import pathlib

google_token = os.getenv('GENAI_API_KEY')
genai.configure(api_key=google_token)
model_id = "meta-llama/Meta-Llama-3-8B"
safety_settings = [
            {
                "category": "HARM_CATEGORY_DANGEROUS",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
personalities = [["Genghis Khan, the mongol emperor","TheKhadKhan"], 
                 ["Julius Caesar, the Roman emperor", "IVeniVidiViciInYourM0M"], 
                 ["Shinzo Abe, japanese prime minister", "5hinz0Ab3"], 
                 ["Mohandas Karamchand Gandhi","CIVBestNuker"], 
                 ["Yukio Mishima, The Japanese author, poet, playwright, actor, model, Shintoist, nationalist, and founder of the Tatenokai", "MishimaThisBalls"],
                ["Davinci, Italian inventor", "IpaintedLaMonaLisa"],
                 ["Socrates, Greek Philosopher", "PPSmall=SmartBrain"],
                ["Cleopatra, queen of egypt", "EgyptQueen"],
                ["Messi, the best football player and argentinian", "TeConseguiLaTercera"]
                  ]


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_posts')   
    last_editor= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,blank=True, null=True, related_name='edited_posts')   
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    photo = models.ImageField(upload_to='post-images', blank=True, null=True)
    #personality_suscribed = models.IntegerField()
    def publish(self):
        self.published_date = timezone.now() 
        self.save()       
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)        
        personalitycom = random.randrange(len(personalities))
        #self.personality_suscribed = personalitycom
        if (self.photo == None):
            instruction = "You are " + personalities[personalitycom][0] +". You are looking at social media posts, which has a Title and Text, and you are writing a comment for the post. You can answer in English or Spanish, as you see more fit"
            model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction= instruction, safety_settings = safety_settings)  
            response = model.generate_content("Title: " + self.title + ", Text: " + self.text)  
        else:   
            print(self.photo)
            image1 = {
                'mime_type': 'image/jpeg',
                'data': self.photo.read()
            }
            instruction = "You are " + personalities[personalitycom][0] +". You are looking at social media posts, which has a Title and Text, and you are writing a comment for the post. The post also has an image attached. You can answer in English or Spanish, as you see more fit"
            model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction= instruction, safety_settings = safety_settings)  
            response = model.generate_content(["Title: " + self.title + ", Text: " + self.text, image1]) 
            
        
        Comment.objects.create(post=self, author=personalities[personalitycom][1], text=response.text, created_date = self.published_date)

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