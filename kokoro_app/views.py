from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Activity
from .forms import ActivityForm

# Create your views here.


def index(request):
    """Landing Page for Kokoro"""

    return render(request, 'kokoro_app/index.html', {})


@login_required()
def home(request):
    """Home Page for Kokoro users"""

    form = ActivityForm()

    if request.method == "POST":
        form = ActivityForm(data=request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.owner = request.user
            new_form.save()
            form = ActivityForm()

    activities = Activity.objects.filter(owner=request.user).order_by('date_added')

    context = {
        'form': form,
        'activities': activities,
    }

    return render(request, 'kokoro_app/home.html', context)
