from django import forms
from .models import Post

class SignupForm(forms.Form):
    display_name = forms.CharField(label='Display Name', max_length=50, required=True)
    username = forms.CharField(
        label='Username', max_length=50, required=True)
    email = forms.EmailField(label='Email', required=True)
    github = forms.CharField(label='GitHub Username', required=False)
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput, required=True)

class SigninForm(forms.Form):
    username = forms.CharField(
        label='Username', max_length=50, required=True)
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput, required=True)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'content', 'content_type', 'visibility', 'unlisted', 'image')
        
        widget = {
            'title' : forms.TextInput(attrs={'class': 'form-control'}),
            'description' : forms.TextInput(attrs={'class': 'form-control'}),
            'content' : forms.Textarea(attrs={'class': 'form-control'}),
            'content_type' : forms.Select(attrs={'class': 'form-control'}),
            'visibility' : forms.TextInput(attrs={'class': 'form-control'}),
            'unlisted' : forms.TextInput(attrs={'class': 'form-control'}),
            'image' : forms.TextInput(attrs={'class': 'form-control'})
        }

