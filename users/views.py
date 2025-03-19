import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import SignUpForm, SignInForm
from .models import User
from .backends import MultiFieldAuthBackend

logger = logging.getLogger('users')


def sign_up_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    phone_number=form.cleaned_data['phone_number'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    username=form.cleaned_data['username']
                )
                login(request, user)
                logger.info(f"User {user.username} successfully signed up.")
                return redirect('home')
            except Exception as e:
                logger.error(f"Error during signup: {str(e)}")
                form.add_error(None, 'خطا در ثبت نام! لطفاً دوباره تلاش کنید.')
        else:
            logger.warning("Invalid signup form submission.")
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


def sign_in_view(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            try:
                user = MultiFieldAuthBackend().authenticate(
                    request,
                    login_identifier=form.cleaned_data['login_identifier'],
                    password=form.cleaned_data['password']
                )
                if user:
                    login(request, user)
                    logger.info(f"User {user.username} successfully signed in.")
                    return redirect('home')
                else:
                    logger.warning(f"Failed login attempt for {form.cleaned_data['login_identifier']}.")
                    form.add_error(None, 'اطلاعات وارد شده صحیح نیست!')
            except Exception as e:
                logger.error(f"Error during signin: {str(e)}")
                form.add_error(None, 'خطا در ورود! لطفاً دوباره تلاش کنید.')
        else:
            logger.warning("Invalid signin form submission.")
    else:
        form = SignInForm()

    return render(request, 'signin.html', {'form': form})


def sign_out_view(request):
    try:
        if request.user.is_authenticated:
            logger.info(f"User {request.user.username} signed out.")
        logout(request)
    except Exception as e:
        logger.error(f"Error during signout: {str(e)}")
    return redirect('home')