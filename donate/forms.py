from django import forms
from django.contrib.auth.models import User
from .models import Adminprofile, Donor, DonationArea, Volunteer
# from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class AdminSignupForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    
    class Meta:
        model = Adminprofile
        fields = ['contact', 'adminpic', 'address']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")
        
        return cleaned_data

class UserSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username
# class UserSignupForm(forms.ModelForm):
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ['username', 'email']

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")

#         if password != confirm_password:
#             raise forms.ValidationError("Passwords do not match.")

#         return cleaned_data

class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['userpic', 'contact', 'address']

class DonationAreaForm(forms.ModelForm):
    class Meta:
        model = DonationArea
        fields = ['areaname', 'description']

# volunter part   ##############################

  # Make sure this model exists

class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        exclude = ['user', 'status']
