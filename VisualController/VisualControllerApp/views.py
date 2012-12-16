# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from VisualControllerApp.models import ComputationForm, Computation, ConfigurationForm, ParallelForm, MonitoringForm

def orderComputation(request):
    if request.method == 'POST':
        form = ComputationForm(request.POST)
        if form.is_valid():
            request.session.update(get_data(form.cleaned_data,'algorithm','problem','repeat'))
            return HttpResponseRedirect('/VisualControllerApp/order/configuration') # Redirect after POST
    if request.session.get('algorithm') is not None:
        form = ComputationForm(get_data(request.session,'algorithm','problem','repeat'))
    else:
        form = ComputationForm()
    c = RequestContext(request, {'form': form,})
    return render_to_response('order/general.html', c)

def comp_detail(request,pk):
    comp = Computation.objects.get(pk=pk)
    c = RequestContext(request, {'comp': comp,'pk' : pk,'range':range(30)})
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
    if request.session.get('configuration') is not None:
        form = ConfigurationForm(get_data(request.session,'configuration'))
    else:
        conf = retrieve_conf_for_alg(request.session)
        form = ConfigurationForm({'configuration':conf})
    c = RequestContext(request, {'form': form,})
    return render_to_response('order/configuration.html', c)

def set_monitoring(request):
    if request.method == 'POST':
        form = MonitoringForm(request.POST)
        if form.is_valid():
            request.session.update(get_data(form.cleaned_data,'monitoring'))
            return HttpResponseRedirect('/VisualControllerApp/order/parallelization') # Redirect after POST
    if request.session.get('monitoring') is not None:
        form = MonitoringForm(get_data(request.session,'monitoring'))
    else:
        form = MonitoringForm()
    c = RequestContext(request, {'form': form,})
    return render_to_response('order/monitoring.html', c)

def set_parallel(request):
    if request.method == 'POST':
        form = ParallelForm(request.POST)
        if form.is_valid():
            request.session.update(get_data(form.cleaned_data,'parallel'))
            return HttpResponseRedirect('/VisualControllerApp/order/computation/') # Redirect after POST
    if request.session.get('parallel') is not None:
        form = ParallelForm(get_data(request.session,'parallel'))
    else:
        form = ParallelForm()
    c = RequestContext(request, {'form': form,})
    return render_to_response('order/parallelization.html', c)


def simple_render(request,view_name):
    c = RequestContext(request)
    return render_to_response(view_name+".html", c)

def comp_delete(request, pk):
    comp = Computation.objects.get(pk=pk)
    comp.delete()
    return HttpResponseRedirect('/VisualControllerApp/') # Redirect after POST

def start_computation(request):
    parameters = get_data(request.session,'problem','parallel','algorithm','configuration','monitoring','repeat')
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