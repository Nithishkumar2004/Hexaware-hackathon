from django import forms

class InstructorForm(forms.Form):
    employeeId = forms.CharField(max_length=100, label='Employee ID')
    name = forms.CharField(max_length=100, label='Full Name')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
