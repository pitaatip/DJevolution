import datetime
from django.db import models
from django import forms
from djangotoolbox.fields import ListField, RawField

# Create your models here.
class Computation(models.Model):
    created_on = models.DateTimeField(default=datetime.datetime.now())
    computed = models.BooleanField()
    population_size = models.IntegerField()
    results = ListField(models.FloatField(),null=True,default=[])
    restrigin_val = models.FloatField(null=True)
    parallel = models.TextField()
    computation_time = models.TextField()
    algorithm = models.TextField()
    new_result = RawField()


class ComputationForm(forms.Form):
    population_size = forms.IntegerField()
    algorithm = forms.ChoiceField(choices=(('SGA', 'SGA',), ('NSGA', 'NSGA-II',),('SPEA', 'SPEA 2',)))
    parallel = forms.ChoiceField(choices=(('None', 'None',), ('Demes pipe model', 'Demes pipe model',),('Demes Mpi model', 'Demes Mpi model',)))
