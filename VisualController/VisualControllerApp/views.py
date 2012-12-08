# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from VisualControllerApp.models import ComputationForm, Computation

def orderComputation(request):
    if request.method == 'POST':
        form = ComputationForm(request.POST)
        if form.is_valid():
            request.session.update(get_data(form.cleaned_data,'f_pop','f_paral','f_alg','f_problem'))
            return HttpResponseRedirect('/VisualControllerApp/order/configuration') # Redirect after POST
    else:
        pass
    if request.session.get('f_alg') is not None:
        form = ComputationForm(get_data(request.session,'f_pop','f_paral','f_alg','f_problem'))
    else:
        form = ComputationForm()
    c = RequestContext(request, {'form': form,})
    return render_to_response('order/general.html', c)

def comp_detail(request,pk):
    comp = Computation.objects.get(pk=pk)
    c = RequestContext(request, {'comp': comp,})
    if comp.algorithm == 'SGA':
        return render_to_response('computation/singleDetails.html', c)
    else:
        if comp.algorithm == 'NSGA':
            comp.algorithm = 'NSGA-II'
        else:
            comp.algorithm = "SPEA2"
        return render_to_response('computation/multiDetails.html', c)


def simple_render(request,view_name):
    c = RequestContext(request)
    return render_to_response(view_name+".html", c)

def comp_delete(request, pk):
    comp = Computation.objects.get(pk=pk)
    comp.delete()
    return HttpResponseRedirect('/VisualControllerApp/') # Redirect after POST

def start_computation(request):
    comp=Computation(problem=request.session.get('f_problem',None),population_size=request.session.get('f_pop',None),parallel=request.session.get('f_paral',None), computed=False,algorithm=request.session.get('f_alg',None))
    request.session.clear()
    comp.save()
    return HttpResponseRedirect('/VisualControllerApp/') # Redirect after POST

def get_data(container, *args):
    ret_val = {}
    for a in args:
        ret_val[a] = container.get(a)
    return ret_val