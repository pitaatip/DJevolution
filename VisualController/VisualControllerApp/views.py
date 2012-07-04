# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from VisualControllerApp.models import ComputationForm, Computation

def orderComputation(request):
    if request.method == 'POST':
        form = ComputationForm(request.POST)
        if form.is_valid():
            f_pop = form.cleaned_data['population_size']
            f_paral = form.cleaned_data['parallel']
            comp=Computation(population_size=f_pop,parallel=f_paral, computed=False)
            comp.save()
            return HttpResponseRedirect('/VisualControllerApp/') # Redirect after POST
    else:
        pass
    form = ComputationForm() # An unbound form

    c = RequestContext(request, {'form': form,})
    return render_to_response('orderComputation.html', c)

def comp_detail(request,pk):
    comp = Computation.objects.get(pk=pk)
    c = RequestContext(request, {'comp': comp,})
    return render_to_response('computationDetails.html', c)


def comp_delete(request, pk):
    comp = Computation.objects.get(pk=pk)
    comp.delete()
    return HttpResponseRedirect('/VisualControllerApp/') # Redirect after POST