from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password'
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm password'
        }))
    
    class Meta:
        model = Account
        fields  = ['first_name', 'last_name', 'email', 'phone_number', 'password']


    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
    
        if password != confirm_password:
            raise forms.ValidationError(
                 "Password does not match!"
            )


    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter fisrt name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter email address'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter phone number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class BootstrapModelForm(forms.ModelForm):
    """
    Base ModelForm that automatically applies Bootstrap styling
    to all form fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            css_class = 'form-control'

            if isinstance(field.widget, forms.FileInput):
                css_class = 'form-control'

            field.widget.attrs.setdefault('class', css_class)


class UserForm(BootstrapModelForm):
    class Meta:
        model = Account
        fields = (
            'first_name',
            'last_name',
            'phone_number',
        )


class UserProfileForm(BootstrapModelForm):
    profile_picture = forms.ImageField(required=False, error_messages= {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = (
            'profile_picture',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'country',
        )