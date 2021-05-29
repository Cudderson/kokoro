from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm


def register(request):
    """Register a new user"""

    if request.method != "POST":
        # Display blank registration form
        register_form = UserCreationForm()
    else:
        # Process completed form
        register_form = UserCreationForm(data=request.POST)

        if register_form.is_valid():
            new_user = register_form.save()

            # Log in the new user and return to home page
            login(request, new_user)
            return redirect('kokoro_app:index')

    # Display blank or invalid form
    context = {'register_form': register_form}

    return render(request, 'registration/register.html', context)
