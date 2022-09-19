from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm, UserChangeForm
from .models import AboutUser, Comment, PostCategory, Post


class SignUpForm(UserCreationForm):

    def age_restrict(value):

        if (value > 100) | (value <= 0):
            raise forms.ValidationError('Invalid Age.')

        elif value < 13:
            raise forms.ValidationError('Age Below 13 not allowed.')

    def unique_contact(value):
        all_abt_us = AboutUser.objects.all()
        for abt in all_abt_us:
            if value == abt.contact_number:
                raise forms.ValidationError('This Contact number has already been registered.')

    def restrict_desc(value):
        if len(value) > 150:
            raise forms.ValidationError(f'Description must have less than 151 characters. Your has {len(value)} characters')
         

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
        ('Prefer Not To Say', 'Prefer Not To Say')
    )

    gender = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=GENDER_CHOICES)
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required = True, validators = [age_restrict])
    contact_number = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required = False, validators=[unique_contact])
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required = False, 
    label = 'About Yourself', validators=[restrict_desc])


    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label = 'Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label = 'Re-Enter Password')
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

        labels = {
            'email': 'Email'
        }

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'autofocus': True}), label = 'Old Password')
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label = 'New Password')
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label = 'Re-Enter New Password')
    class Meta:
        model = User
        fields = '__all__'


class EditProfileForm(UserChangeForm):
    password = None
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

        labels = {
            'email': 'Email'
        }

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class EditAboutUserForm(forms.ModelForm):
    class Meta:
        model = AboutUser
        fields = ['gender', 'age', 'contact_number', 'description']
        # exclude = ['user', 'created']

        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control', 'autofocus': True}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'contact_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

        labels = {
            'description': 'About Yourself',
        }

         

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_number'].required = False
        self.fields['description'].required = False
        self.fields['age'].required = True


    def clean(self):
        contact_number = self.cleaned_data.get('contact_number')
        age = self.cleaned_data.get('age')
        description = self.cleaned_data.get('description')

        for abt in AboutUser.objects.all():
            if (abt.contact_number == contact_number) & (contact_number is not None):
                raise forms.ValidationError('This Contact Number is already registered.')

        if age is not None:

            if (age > 100) | (age <= 0):
                raise forms.ValidationError('Invalid Age.')

            elif age < 13:
                raise forms.ValidationError('Age Below 13 not allowed.')

            

        if len(description) > 150:
            raise forms.ValidationError(f'Description must have less than 151 characters. Your has {len(description)} characters')

        

class PostCategoryForm(forms.ModelForm):
    class Meta:
        model = PostCategory
        fields = ['category_name']

        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True})
        }

        

class EditPostCategoryForm(forms.ModelForm):
    class Meta:
        model = PostCategory
        fields = ['category_name']

        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True})
        }
        


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_title', 'post_category', 'post_content']

        widgets = {
            'post_title': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'post_category': forms.Select(attrs={'class': 'form-control'}),
            'post_content': forms.Textarea(attrs={'class': 'form-control'}),
        }

        labels = {
            'post_title': 'Title',
            'post_category': 'Category',
            'post_content': 'Content'
        }


        

class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_title', 'post_category', 'post_content']

        widgets = {
            'post_title': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'post_category': forms.Select(attrs={'class': 'form-control'}),
            'post_content': forms.Textarea(attrs={'class': 'form-control'}),
        }

        labels = {
            'post_title': 'Title',
            'post_category': 'Category',
            'post_content': 'Content'
        }


class EditCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Comment', 'autofocus': True})
        }