from django import forms
from django.contrib.auth.models import User
from .models import Profile, Complaint

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control border-0 shadow-none ps-4', 'placeholder': 'What is this regarding?'}),
            'message': forms.Textarea(attrs={'class': 'form-control border-0 shadow-none ps-4', 'rows': 5, 'placeholder': 'Describe your complaint in detail...'}),
        }