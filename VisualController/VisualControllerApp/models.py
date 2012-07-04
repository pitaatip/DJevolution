from django.db import models
from django import forms
from djangotoolbox.fields import ListField

# Create your models here.
class Computation(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    computed = models.BooleanField()
    population_size = models.IntegerField()
    results = ListField(models.FloatField(),null=True,default=[])
    restrigin_val = models.FloatField(null=True)
    parallel = models.TextField()
    computation_time = models.TextField()

class ComputationForm(forms.Form):
    population_size = forms.IntegerField()
    parallel = forms.ChoiceField(choices=(('None', 'None',), ('Demes pipe model', 'Demes pipe model',),('Demes Mpi model', 'Demes Mpi model',)))
