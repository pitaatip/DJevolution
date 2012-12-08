import datetime
from django.db import models
from django import forms
from djangotoolbox.fields import ListField, RawField
from deap import benchmarks

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
    configuration = models.TextField()
    problem = models.TextField()
    partial_result = RawField()

class ActualConfig(models.Model):
    population_size = models.IntegerField()
    configuration = models.TextField()


def retrieve_choices(benchmarks):
    choices = []
    for b in dir(benchmarks):
        if "__" not in b:
            choices.append((str(b),str(b),))
    return choices


class ComputationForm(forms.Form):
    population_size = forms.IntegerField(label="Population")
    algorithm = forms.ChoiceField(choices=(('SGA', 'SGA',), ('NSGA', 'NSGA-II',),('SPEA', 'SPEA 2',)),label="Algorithm")
    parallel = forms.ChoiceField(choices=(('None', 'None',), ('Demes pipe model', 'Demes pipe model',),('Demes Mpi model', 'Demes Mpi model',)),label="Parallelization")
    problem = forms.ChoiceField(choices=retrieve_choices(benchmarks),label="Problem")

class ConfigurationForm(forms.Form):
    configuration = forms.CharField(widget=forms.Textarea(attrs={"rows":"15", "cols":"95"}),label="")