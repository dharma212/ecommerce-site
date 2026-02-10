from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import Contact
from django.contrib.auth import get_user_model
class UserRegisterForm(UserCreationForm):
    terms_accepted = forms.BooleanField(
        required=True,
        label="I agree to the Terms & Conditions"
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(render_value=True,attrs={
            "class": "form-control",
            "placeholder": "Enter password"
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(render_value=True,attrs={
            "class": "form-control",
            "placeholder": "Confirm password"
        })
    )
    class Meta:
        model = User
        fields = ["username","first_name","email", "contact_number", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter username"
            }),
            
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter First Name"
            }),
            # "last_name": forms.TextInput(attrs={
            #     "class": "form-control",
            #     "placeholder": "Enter Last Name"
            # }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter email"
            }),
            "contact_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter contact number"
            }),
            # "password1": forms.PasswordInput(attrs={
            #     "class": "form-control",
            #     "placeholder": "Enter password"
            # }),
            # "password2": forms.PasswordInput(attrs={
            #     "class": "form-control",
            #     "placeholder": "Confirm password"
            # }),
        }

    # Validate username
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    # Validate email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    # Validate contact number
    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if User.objects.filter(contact_number=contact_number).exists():
            raise forms.ValidationError("This contact number is already registered.")
        if not contact_number.isdigit():
            raise forms.ValidationError("Contact number must contain only digits.")
        if len(contact_number) < 10:
            raise forms.ValidationError("Contact number must be at least 10 digits.")
        return contact_number


User = get_user_model()

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'contact_number',
            'password'
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact number'
            }),
        }
        
        
class ForgotPasswordForm(forms.Form):
    identifier = forms.CharField(
        label="Username / Email / Contact Number",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter username, email, or contact number"
        })
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter new password"
        })
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm new password"
        })
    )

    def clean_identifier(self):
        identifier = self.cleaned_data.get("identifier")
        user = None
        # Check username
        if User.objects.filter(username=identifier).exists():
            user = User.objects.get(username=identifier)
        # Check email
        elif User.objects.filter(email=identifier).exists():
            user = User.objects.get(email=identifier)
        # Check contact_number
        elif User.objects.filter(contact_number=identifier).exists():
            user = User.objects.get(contact_number=identifier)
        else:
            raise ValidationError("No user found with this username, email, or contact number.")
        
        self.user = user  # store for use in save()
        return identifier

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("new_password1")
        pw2 = cleaned_data.get("new_password2")
        if pw1 and pw2 and pw1 != pw2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
        return self.user
    
class UserLoginForm(AuthenticationForm):
    terms_accepted = forms.BooleanField(
        required=True,
        label="I agree to the Terms & Conditions"
    )
    username = forms.CharField(label="Username",widget=forms.TextInput(attrs={"class": "form-control",
            "placeholder": "Enter username"
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter password"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            # Check if username exists
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise forms.ValidationError("This username does not exist.")

            # Check if password is correct
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Incorrect password.")

        return cleaned_data
    

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "contact_number",
            "first_name",
            "last_name",
            "address",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "contact_number": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "address":forms.Textarea(attrs={"class":"form-control", "rows":2}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get("contact_number")
        if contact_number:
            if not contact_number.isdigit():
                raise forms.ValidationError("Contact number must contain only digits.")
            if len(contact_number) < 10:
                raise forms.ValidationError("Contact number must be at least 10 digits.")
            if User.objects.exclude(pk=self.instance.pk).filter(contact_number=contact_number).exists():
                raise forms.ValidationError("This contact number is already registered.")
        return contact_number
    
from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    terms_accepted = forms.BooleanField(
        required=True,
        label="I agree to the Terms & Conditions"
    )
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject' ,'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Your Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write Your Message.....',
                'rows': 2
            }),
        }
        
    def clean_contact(self):
        contact = self.cleaned_data.get('contact')

        # Check if contact is empty
        if not contact:
            raise forms.ValidationError("Phone number is required")

        # Check if it's all digits
        if not contact.isdigit():
            raise forms.ValidationError("Enter a valid phone number")

        # Optional: check length
        if len(contact) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits")

        return contact
    
from django import forms
from .models import AboutPage

class AboutPageForm(forms.ModelForm):
    class Meta:
        model = AboutPage
        fields = '__all__'
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'mission_statement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'story_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'story_image': forms.FileInput(attrs={'class': 'form-control'}),
            'value_one_title': forms.TextInput(attrs={'class': 'form-control'}),
            'value_one_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'value_two_title': forms.TextInput(attrs={'class': 'form-control'}),
            'value_two_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'value_three_title': forms.TextInput(attrs={'class': 'form-control'}),
            'value_three_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        
from django import forms
from .models import TermsAndConditions

class TermsForm(forms.ModelForm):
    class Meta:
        model = TermsAndConditions
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'introduction': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'use_of_website': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'user_accounts': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'product_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'liability': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'changes_to_terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }