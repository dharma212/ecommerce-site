from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import FormView, CreateView, DetailView, UpdateView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from .forms import UserRegisterForm, UserLoginForm, ForgotPasswordForm, UserProfileUpdateForm, ContactForm, AboutPageForm, TermsForm
from .models import Contact, AboutPage, TermsAndConditions
# =============================
# ========= SIGN UP ===========
# =============================

class UserSignupView(FormView):
    template_name = "signup.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # Save user
        user = form.save()

        # Auto login after signup
        login(self.request, user)

        # Role-based redirect (optional)
        if hasattr(user, 'role') and user.role in ['admin', 'a']:
            return redirect('dashboard_index')

        return super().form_valid(form)

# =============================
# =========== LOGIN ===========
# =============================

@method_decorator(csrf_protect, name='dispatch')
class LoginView(FormView):
    template_name = "login.html"
    form_class = UserLoginForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        if user.role in ['admin', 'a']:
            return redirect('dashboard_index')
        return redirect('/')

# =============================
# =========== LOGOUT ==========
# =============================

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')

# =============================
# ===== FORGOT PASSWORD =======
# =============================

class ForgotPasswordView(FormView):
    template_name = "forgot_password.html"
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Password updated successfully.")
        return super().form_valid(form)

# =============================
# ===== USER PROFILE ==========
# =============================

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
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)

# =============================
# ===== CONTACT PAGE ==========
# =============================

class ContactCreateView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "contact.html"
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Your message has been sent successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please fix the errors below.")
        return self.render_to_response(self.get_context_data(form=form))

# =============================
# ===== ABOUT PAGE (VIEW) =====
# =============================

class AboutDetailView(DetailView):
    model = AboutPage
    template_name = "about.html"
    context_object_name = "about_data"

    def get_object(self):
        obj, _ = AboutPage.objects.get_or_create(id=1)
        return obj

# =============================
# === ABOUT PAGE (EDIT) =======
# =============================

class AboutUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AboutPage
    form_class = AboutPageForm
    template_name = "dashboard/about_form.html"
    success_url = reverse_lazy("about_edit")
    success_message = "About Us page updated successfully."

    def get_object(self):
        obj, _ = AboutPage.objects.get_or_create(id=1)
        return obj

# =============================
# === TERMS PAGE (VIEW) =======
# =============================

class TermsDetailView(DetailView):
    model = TermsAndConditions
    template_name = "terms.html"
    context_object_name = "terms_data"

    def get_object(self):
        obj, _ = TermsAndConditions.objects.get_or_create(id=1)
        return obj

# =============================
# === TERMS PAGE (EDIT) =======
# =============================

class TermsUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TermsAndConditions
    form_class = TermsForm
    template_name = "dashboard/terms_form.html"
    success_url = reverse_lazy("terms_edit")
    success_message = "Terms & Conditions updated successfully."

    def get_object(self):
        obj, _ = TermsAndConditions.objects.get_or_create(id=1)
        return obj
    
# class HeaderView(View):
#     def get(self, request):
#         cart_count = 0
#         if request.user.is_authenticated:
#             cart_count = request.user.cart_items.count()
#         return render(request, "header.html", {"cart_count": cart_count})