import datetime
from django.db import models
from django import forms
from djangotoolbox.fields import ListField, RawField
from deap import benchmarks


# HELPER METHODS

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
    new_result = RawField()
    configuration = models.TextField()
    problem = models.TextField()
    partial_result = RawField()
    monitoring = models.IntegerField()
    repeat = models.IntegerField()
    final_space = ListField(models.FloatField(null=True))
    is_part_spacing = models.BooleanField(default=False)
    partial_spacing = RawField()


#FORMS
class ComputationForm(forms.Form):
    algorithm = forms.ChoiceField(choices=(('NSGA', 'NSGA-II',),('SPEA', 'SPEA 2',)),label="Algorithm")
    problem = forms.ChoiceField(choices=retrieve_choices(benchmarks),label="Problem")
    repeat = forms.IntegerField(label="Repeat computation")

class ConfigurationForm(forms.Form):
    configuration = forms.CharField(widget=forms.Textarea(attrs={"rows":"15", "cols":"95"}),label="")

class MonitoringForm(forms.Form):
    monitoring = forms.IntegerField(label="Gather results after this many generations")
    is_part_spacing = forms.BooleanField(label="Compute spacing value after each generation?")

class ParallelForm(forms.Form):
    parallel = forms.ChoiceField(choices=(('None', 'None',), ('Demes pipe model', 'Demes pipe model',), ('picloud', 'Run multiple repeats at PiCloud',),('Demes Mpi model', 'Demes Mpi model',)),label="Parallelization")



