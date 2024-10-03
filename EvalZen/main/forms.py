from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

class InstructorForm(forms.Form):
    employeeId = forms.CharField(max_length=100, label='Employee ID')
    name = forms.CharField(max_length=100, label='Full Name')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    dob = forms.DateField()
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    mobile = forms.CharField(max_length=15)
    email = forms.EmailField()
    address = forms.CharField(max_length=255)
    state = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    pincode = forms.CharField(max_length=10)
    qualification = forms.CharField(max_length=255)
    institution = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)
