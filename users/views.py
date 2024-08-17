from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            authenticated_user = authenticate(request, username=email, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, f'Account created for {email}!')
                return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('home')  # or any other page you want to redirect to