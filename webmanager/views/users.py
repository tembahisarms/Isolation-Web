from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from webmanager.models import Person
import uuid
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class IsoWebUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=("Email"),
    )

def signup(request):
    if request.method == 'POST':
        # this part verifies that an email address is in the POST
        form_data = request.POST.copy()
        form_data['email'] = form_data.get('username')
        form = IsoWebUserCreationForm(form_data)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            # this part saves the email address
            user.email = user.username
            user.save()

            new_person = Person(user=user, name=form_data.get('name'))
            new_person.save()
            login(request, user)
            return redirect('place-add')
    else:
        form = IsoWebUserCreationForm()
    return render(request, 'signup.html', {'form': form})
