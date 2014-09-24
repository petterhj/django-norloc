# Imports
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout as django_logout
from django.shortcuts import redirect
from productions.models import Production


# View: Index
def index(request):
    # Productions
    productions = Production.productions.order_by('-release')
    
    for production in productions:
    	production.scene_count = production.scene_set.count()
    	production.location_count = 0

    	for scene in production.scene_set.all():
    		if scene.location:
    			production.location_count += 1

    # Template
    template = loader.get_template('index.html')

    context = RequestContext(request, {
        'productions': productions,
    })

    return HttpResponse(template.render(context))


# View: Log in
def login(request):
    # Request: POST
    if request.method == 'POST':
        # Authenticate
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
            else:
                print 'disabled account'
        else:
            print 'invalid login'

    # Redirect
    return redirect('/')


# View: Log out
def logout(request):
    # Log out
    django_logout(request)

    # Redirect
    return redirect('/')