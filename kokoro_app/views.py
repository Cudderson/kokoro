from django.shortcuts import render

# Create your views here.


def index(request):
    """Main Page for Kokoro"""

    return render(request, 'kokoro_app/index.html')
