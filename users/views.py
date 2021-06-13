from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import Http404


def register(request):
    """Register a new user"""

    if request.method != "POST":
        # Display blank registration form
        register_form = UserCreationForm()
    else:
        # Process completed form
        register_form = UserCreationForm(data=request.POST)

        if register_form.is_valid():
            try:
                new_user = register_form.save()

                # Log in the new user and return to home page
                login(request, new_user)
                return redirect('users:thank_you')

            except Exception as e:
                raise Http404("Something went wrong during registration. Please try again later.")

    # Display blank or invalid form
    context = {'register_form': register_form}

    return render(request, 'registration/register.html', context)


@login_required()
def thank_you(request):
    """
    Page to thank newly-registered users
    :param request: http data
    :return: render of thank_you.html
    """

    context = {
        'message': f'Thank you, {request.user}!',
        'sub_message': "We hope you enjoy kokoro!",
    }

    return render(request, 'registration/thank_you.html', context)
