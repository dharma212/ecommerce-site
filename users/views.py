from django.views.generic import FormView
from django.urls import reverse_lazy
from users.forms import *
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View  
from django.contrib.auth import login
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import UserProfileUpdateForm
from .models import *

# =============================
# ====== UserSignupView =======
# =============================

class UserSignupView(FormView):
    template_name = "signup.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')  # redirect after successful signup

    def form_valid(self, form):
        form.save()  # save the user
        return super().form_valid(form)
    
# =============================
# ========= LoginView =========
# =============================

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.shortcuts import redirect
from .forms import UserLoginForm

@method_decorator(csrf_protect, name='dispatch')
class LoginView(FormView):
    template_name = "login.html"
    form_class = UserLoginForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        if user.role == 'admin' or user.role == 'a':
            return redirect('dashboard_index')
        return redirect('/')

# =============================
# ========= LogoutView ========
# =============================

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)  # log out the user
        return redirect('login')  # redirect to login page
    
# =============================
# ==== ForgotPasswordView =====
# =============================
    
class ForgotPasswordView(FormView):
    template_name = "forgot_password.html"
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('login')  # Redirect to login after password reset

    def form_valid(self, form):
        form.save()  # update the password
        return super().form_valid(form)



class UserProfileView(LoginRequiredMixin, FormView):
    template_name = "profile.html"
    form_class = UserProfileUpdateForm
    success_url = reverse_lazy("profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Contact
from .forms import ContactForm

class ContactCreateView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contact.html'
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        return super().form_valid(form)
