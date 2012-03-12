from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from nonrelblog.models import Post, Comment, Author, PostForm, CommentForm
from django.template.context import RequestContext

def addPost(request):
    if request.method == 'POST': 
        form = PostForm(request.POST) 
        if form.is_valid():
            f_title = form.cleaned_data['title']
            f_text = form.cleaned_data['text']
            p=Post(title=f_title,text=f_text,tags=['mongodb', 'django'], comments=[])
            p.save()
            return HttpResponseRedirect('/pita_django/') # Redirect after POST
    else:
        form = PostForm() # An unbound form
        
    c = RequestContext(request, {'form': form,})
    return render_to_response('post_insert_data.html', c)
    
def post_detail(request,pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'POST': 
        form = CommentForm(request.POST) 
        if form.is_valid():
            f_author = form.cleaned_data['author']
            f_text = form.cleaned_data['text']
            f_mail = form.cleaned_data['email']
            comment=Comment(author=Author(name=f_author, email=f_mail),text=f_text)
            comment.save()
            post.comments.append(comment)
            post.save()
            return HttpResponseRedirect('.') # Redirect after POST
    else:
        form = CommentForm() # An unbound form
    c = RequestContext(request, {'form_add_post': form,'post': post})
    return render_to_response('post_detail.html',c)

def post_delete(request,pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    return HttpResponseRedirect('/pita_django/') # Redirect after POST

