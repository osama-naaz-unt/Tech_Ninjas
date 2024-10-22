from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from apps.users.forms import LoginForm, RegistrationForm, PersonalInformationForm, CustomPasswordChangeForm


def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        email = request.POST.get('email', None)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_name}.")
                return redirect('shop:index')
            else:
                messages.error(request, "An error occurred. Kindly try again with correct credentials, reset password if you have forgotten or contact us.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
            messages.error(request, f"Invalid credentials. Please try again.")
    return render(request, 'users/login.html', {
        'page': 'login',
        'form': form,
    })

def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            messages.success(request, f"Welcome {account.name}. You have successfully logged in.")
            login(request, account)
            return redirect('shop:index')
        else:
            messages.error(request, "Error creating account. Please correct the highlighted errors")
    return render(request, 'users/register.html', {
        'page': 'register',
        'form': form,
    })

def logout_user(request):
	if request.user.is_authenticated:
		username = request.user.name
		logout(request)
		messages.info(request, f"{username} has been logged out.")
	else:
		messages.warning(request, "No user is currently logged in.")
	return redirect('shop:index')

def profile(request):
    personal_form = PersonalInformationForm(instance=request.user)
    password_form = CustomPasswordChangeForm(request.user)
    if request.method == 'POST':
        if 'personal_info' in request.POST:
            personal_form = PersonalInformationForm(request.POST, instance=request.user)
            if personal_form.is_valid():
                personal_form.save()
                messages.success(request, 'Your personal information has been updated successfully.')
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')

    context = {
        'personal_form': personal_form,
        'password_form': password_form,
    }
    return render(request, 'users/profile.html', context)


def reset_email(request):
    if request.method == 'POST':
        # Handle password reset email logic here
        pass
    return render(request, 'users/reset-email.html', {'page': 'reset_password'})

def reset_success(request):
    return render(request, 'users/reset-success.html', {'page': 'reset_password'})

def reset_new(request):
    if request.method == 'POST':
        # Handle new password setting logic here
        pass
    return render(request, 'users/reset-new.html', {'page': 'reset_password'})

def reset_done(request):
    return render(request, 'users/reset-done.html', {'page': 'reset_password'})