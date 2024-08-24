from django.contrib.auth import authenticate
from django import forms

class PasswordRestForm(forms.Form):

    password1 = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'id':"password1" , 'name':"password1",'autocomplete':"current-password", 'type':"password", 'class':"block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"}))
    password2 = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'id':"password2" , 'name':"password2",'autocomplete':"current-password", 'type':"password", 'class':"block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"}))

class DeleteUserForm(forms.Form):

    email = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'id':"email" , 'name':"email",'autocomplete':"current-password", 'type':"email", 'class':"block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"}))

class OTPForm(forms.Form):

    otp = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'id':"otp" , 'name':"otp",'autocomplete':"current-password", 'type':"text", 'class':"block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"}))


    # def save(self, commit=True):
    #     user = super(SignUpForm, self).save(commit=False)
    #     user.email = self.cleaned_data["email"]
    #     user.name = self.cleaned_data["name"]
    #     user.phone = self.cleaned_data["phone"]
    #     user.birthday = self.cleaned_data["birthday"]
    #     user.gender = self.cleaned_data["gender"]

    #     if commit:
    #         user.save()
    #     return user
