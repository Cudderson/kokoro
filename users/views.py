from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from kokoro_app.forms import PerfectBalanceForm


def register(request):
    """Register a new user"""

    if request.method != "POST":
        # Display blank registration form
        form = UserCreationForm()
    else:
        # Process completed form
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()

            # Log in the new user and return to home page
            login(request, new_user)
            return redirect('kokoro_app:index')

    # Display blank or invalid form
    context = {'form': form}

    return render(request, 'registration/register.html', context)


@login_required
def profile(request):

    # Identify User
    user = request.user

    # *** add form-submission logic ***
    form = PerfectBalanceForm()

    # *** add logic so that form can only be submitted if all 3 (MBS) specified ***

    context = {
        'user': user,
        'form': form,
    }

    return render(request, 'user/profile.html', context)
