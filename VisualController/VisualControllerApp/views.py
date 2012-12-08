# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from VisualControllerApp.models import ComputationForm, Computation, ConfigurationForm

def orderComputation(request):
    if request.method == 'POST':
        form = ComputationForm(request.POST)
        if form.is_valid():
            request.session.update(get_data(form.cleaned_data,'population_size','parallel','algorithm','problem'))
            return HttpResponseRedirect('/VisualControllerApp/order/configuration') # Redirect after POST
    else:
        pass
    if request.session.get('algorithm') is not None:
        form = ComputationForm(get_data(request.session,'population_size','parallel','algorithm','problem'))
    else:
        form = ComputationForm()
    c = RequestContext(request, {'form': form,})
    return render_to_response('order/general.html', c)

def comp_detail(request,pk):
    comp = Computation.objects.get(pk=pk)
    c = RequestContext(request, {'comp': comp,'pk' : pk,})
    if comp.algorithm == 'SGA':
        return render_to_response('computation/singleDetails.html', c)
    else:
        if comp.algorithm == 'NSGA':
            comp.algorithm = 'NSGA-II'
        else:
            comp.algorithm = "SPEA2"
        return render_to_response('computation/multiDetails.html', c)

def partial_res(request,pk):
    comp = Computation.objects.get(pk=pk)
    print "printing partial res"
    for a in comp.partial_result:
        print "for each a"
        for b in a:
            print b
    c = RequestContext(request, {'comp': comp,'pk' : pk,})
    return render_to_response('computation/partial.html', c)

def view_configuration(request,pk):
    comp = Computation.objects.get(pk=pk)
    c = RequestContext(request, {'comp': comp,'pk' : pk,})
    return render_to_response('computation/configuration.html', c)

def set_configuration(request):
    if request.method == 'POST':
        form = ConfigurationForm(request.POST)
        if form.is_valid():
            request.session.update(get_data(form.cleaned_data,'configuration'))
            return HttpResponseRedirect('/VisualControllerApp/order/monitoring') # Redirect after POST
    else:
        pass
    if request.session.get('configuration') is not None:
        form = ConfigurationForm(get_data(request.session,'configuration'))
    else:
        conf = retrieve_conf_for_alg(request.session)
        form = ConfigurationForm({'configuration':conf})
    c = RequestContext(request, {'form': form,})
    return render_to_response('order/configuration.html', c)

def simple_render(request,view_name):
    c = RequestContext(request)
    return render_to_response(view_name+".html", c)

def comp_delete(request, pk):
    comp = Computation.objects.get(pk=pk)
    comp.delete()
    return HttpResponseRedirect('/VisualControllerApp/') # Redirect after POST

def start_computation(request):
    parameters = get_data(request.session,'problem','population_size','parallel','algorithm','configuration')
    parameters['computed'] = False
    comp=Computation(**parameters)
    request.session.clear()
    comp.save()
    return HttpResponseRedirect('/VisualControllerApp/') # Redirect after POST

def get_data(container, *args):
    ret_val = {}
    for a in args:
        ret_val[a] = container.get(a)
    return ret_val

def retrieve_conf_for_alg(session):
    if not "algorithm" in session.keys() or session.get("algorithm") is None:
        return "Select algorithm first"
    file_name = {"NSGA":"nsga_config.py","SPEA":"spea_config.py"}[session.get("algorithm")]
    with open(file_name) as f:
        return f.read()