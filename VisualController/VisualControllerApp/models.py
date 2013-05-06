import datetime
from django.db import models
from django import forms
from djangotoolbox.fields import ListField, RawField

# HELPER METHODS
from VisualControllerApp import problems

def retrieve_choices(benchmarks):
    choices = []
    for b in dir(benchmarks):
        if "__" not in b:
            choices.append((str(b),str(b),))
    return choices

# ENTITIES
class Computation(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    computed = models.BooleanField()
    results = ListField(models.FloatField(),null=True,default=[])
    restrigin_val = models.FloatField(null=True)
    parallel = models.TextField()
    computation_time = models.TextField()
    algorithm = models.TextField()
    sorted_individuals = RawField()
    fitness_values = RawField()
    configuration = models.TextField()
    problem = models.TextField()
    partial_result = RawField()
    monitoring = models.IntegerField()
    repeat = models.IntegerField()
    final_space = ListField(models.FloatField(null=True))
    #is_part_spacing = models.BooleanField(default=False)
    iter_spacing = models.IntegerField(null=True)
    partial_spacing = RawField()

#FORMS
class ComputationForm(forms.Form):
    algorithm = forms.ChoiceField(choices=(('NsgaIIAlgorithm', 'NSGA-II',),('Spea2Algorithm', 'SPEA 2',),('SimpleGeneticAlgorithm', 'SGA',)),label="Algorithm")
    problem = forms.ChoiceField(choices=retrieve_choices(problems),label="Problem")
    repeat = forms.IntegerField(label="Repeat computation")

class ConfigurationForm(forms.Form):
    configuration = forms.CharField(widget=forms.Textarea(attrs={"rows":"15", "cols":"95"}),label="")

class MonitoringForm(forms.Form):
    monitoring = forms.IntegerField(label="Gather results after this many generations")
    #is_part_spacing = forms.BooleanField(label="Compute spacing value after each generation?",initial=False,required=False)
    iter_spacing = forms.IntegerField(label="Calculate spacing value after this many iterations")


class ParallelForm(forms.Form):
    parallel = forms.ChoiceField(choices=(('None', 'None',),('Multiprocess','Simple multiprocessing',), ('Demes pipe model', 'Demes pipe model',),('Demes Mpi model', 'Demes Mpi model',)),label="Parallelization")



