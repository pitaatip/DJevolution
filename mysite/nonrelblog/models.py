from django.db import models
from djangotoolbox.fields import ListField
from django import forms
from djangotoolbox.fields import EmbeddedModelField

class Post(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True) 
    title = models.CharField(max_length=100)
    text = models.TextField()
    tags = ListField()
    comments = ListField(EmbeddedModelField('Comment'))
    
class Comment(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    author = EmbeddedModelField('Author')
    text = models.TextField()
    
class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.email)

class PostForm(forms.Form):
    title = forms.CharField(max_length=30)
    text = forms.CharField(max_length=300)
    
class CommentForm(forms.Form):
    text = forms.CharField(max_length=300)
    author = forms.CharField(max_length=20)
    email = forms.EmailField()
