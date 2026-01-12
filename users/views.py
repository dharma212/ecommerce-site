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

class LoginView(FormView):
    template_name = "login.html"
    form_class = UserLoginForm
    success_url = "/"  # redirect after successful login

    def form_valid(self, form):
        # Authentication already done in form
        user = form.get_user()  # AuthenticationForm provides this
        login(self.request, user)
        return super().form_valid(form)

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
    
# from django.views.generic.edit import FormView
# from django.urls import reverse_lazy
# from .forms import ContactForm

# class ContactFormView(FormView):
#     template_name = 'contact/contact.html'
#     form_class = ContactForm
#     success_url = reverse_lazy('contact')  # Redirect to same page after success

#     def form_valid(self, form):
#         form.save()  # Save message to database
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['success'] = self.request.method == 'POST' and self.get_form().is_valid()
#         return context
