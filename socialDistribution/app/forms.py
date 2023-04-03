from django import forms
from .models import *
from django.core import serializers
import base64

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
    post_image = forms.ImageField(widget=forms.FileInput, required=False)
    receivers = forms.ModelMultipleChoiceField(queryset=Author.objects.all(), widget=forms.CheckboxSelectMultiple, label='Select which followers to send to:', required=False, help_text='')
    class Meta:
        model = Post
        fields = ('title', 'description', 'content', 'content_type', 'visibility','receivers', 'post_image', 'unlisted')

        widget = {
            'title' : forms.TextInput(attrs={'class': 'form-control'}),
            'description' : forms.TextInput(attrs={'class': 'form-control'}),
            'content' : forms.Textarea(attrs={'class': 'form-control'}),
            'content_type' : forms.Select(attrs={'class': 'form-control'}),
            'visibility' : forms.TextInput(attrs={'class': 'form-control'}),
            # 'receivers' : forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
            'unlisted' : forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        author = kwargs.pop('author', None)
        super(PostForm, self).__init__(*args, **kwargs)

        if author:
            # import pdb; pdb.set_trace()
            receivers = author.followers.all()
            for receiver in receivers:
                # Get the auth token for this receiver
                try:
                    foreign_api_node = ForeignAPINodes.objects.get(base_url=receiver.host)
                    auth_token = foreign_api_node.getToken()
                except ForeignAPINodes.DoesNotExist:
                    auth_token = ''

                # Add the auth token to the option element data attribute
                receiver.auth_token = auth_token
            
            self.fields['receivers'].queryset = receivers
            #  # Add the necessary JavaScript code to the form's media definition
            # self.media += forms.Media(
            #     js=(
            #         'https://code.jquery.com/jquery-3.6.0.min.js',  # You can use a local copy of jQuery instead if you prefer
            #         'post_form.js',
            #     )
            # )

    def save(self, user,receiver_list = None,commit=True):
        print('save method called')
        post = super().save(commit=False)
        post.made_by = user
        if self.cleaned_data['content_type'] == 'image/png;base64' or self.cleaned_data['content_type'] == 'image/jpeg;base64':
            img_file = self.cleaned_data['post_image']
            img_data = img_file.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            post.content = img_base64
        if commit:
            post.save()
            if receiver_list:
                for receiver_id in receiver_list:
                    author = Author.objects.get(id=receiver_id)
                    post.receivers.add(author)

        return post

      

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment',)

        widgets = {
            'comment' : forms.Textarea(attrs={'class': 'form-control comment-text'}),
        }

    def save(self, user, post,commit=True):
        print('save method called')
        comment = super().save(commit=False)
        comment.author = user
        comment.post = post
        if commit:
            comment.save()

        return comment
    

class EditProfileForm(forms.ModelForm):
     class Meta:
         model = Author
         fields = ('displayName', 'email', 'github')

         widgets = {
             'displayName' : forms.TextInput(attrs={'class': 'form-control'}),
             'email': forms.EmailInput(attrs={'class': 'form-control'}),
             'github' : forms.TextInput(attrs={'class': 'form-control'}),
         }

     def save(self,commit=True):
         print('save method called')
         author = super().save(commit=False)
         if commit:
             author.save()

         return author