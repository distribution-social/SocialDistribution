from django import forms

class SignupForm(forms.Form):
    display_name = forms.CharField(label='Display Name', max_length=50, required=True)
    username = forms.CharField(
        label='Username', max_length=50, required=True)
    email = forms.EmailField(label='Email', required=True)
    github_username = forms.CharField(label='GitHub', required=False)
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput, required=True)

class SigninForm(forms.Form):
    username = forms.CharField(
        label='Username', max_length=50, required=True)
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput, required=True)
