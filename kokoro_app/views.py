from django.shortcuts import render

from .models import Activity
from .forms import ActivityForm

# Create your views here.


def index(request):
    """Main Page for Kokoro"""

    form = ActivityForm()

    if request.method == "POST":
        form = ActivityForm(data=request.POST)
        if form.is_valid():
            form.save()
            form = ActivityForm()

    context = {'form': form}
    return render(request, 'kokoro_app/index.html', context)
