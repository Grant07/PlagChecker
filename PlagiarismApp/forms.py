from django import forms
from captcha.fields import CaptchaField

class CaptchaForm(forms.Form):
    captcha_field = CaptchaField()


class ProfileForm(forms.Form):
    email_address = forms.EmailField(label='Email Address')
    phone_number = forms.CharField(label='Phone Number', max_length=15)
    program = forms.CharField(label='Program', max_length=100, required=False)
    image_upload = forms.ImageField(label='Image Upload', required=False)