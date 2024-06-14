from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from accounts.models.UserModel import User, dk, UserProfile

from phonenumbers import parse as validate_phone
from pyisemail import is_email as validate_email

from accounts.signals import Create_Profile
# from accounts.signals import Create_Verif_Device

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField()
    email_or_phone = serializers.CharField()
    
    class Meta:
        model = UserProfile
        fields = ['type', 'email_or_phone', 'first_name', 'last_name', 'gender', 'birthday', 'password']

    def valid_email_phone(self, email_or_phone):
        if validate_email(address=email_or_phone, check_dns=True):
            return {'email': email_or_phone, 'phone': False}
        try:
            if validate_phone(email_or_phone):
                return {'phone': email_or_phone, 'email': False}
        except:
            raise serializers.ValidationError('Not Valid')

    def create(self, data):
        email_or_phone = self.valid_email_phone(email_or_phone=data.get('email_or_phone'))

        id = dk(email_or_phone.get('email') if email_or_phone.get('email') else email_or_phone.get('phone'))

        errors = []
        try:
            if validate_password(data.get('password')) is None:
                # print('password is valid')
                user = User.objects.create(user=id)
                Create_Profile.send(sender=user, data=data, email_phone=email_or_phone)
                user.set_password(data.get('password'))
                user.is_active = False
                user.save()
                return user
        except ValidationError as e:
            # print('password not valid or other exception')
            for error in e:
                # print(error)
                errors.append(str(error))
            raise serializers.ValidationError(errors)


class SignInSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ['email_or_phone', 'password']

    def valid_user(self, email_or_phone):
        id = dk(email_or_phone)
        try:
            user = User.objects.get(user=id)
        except:
            raise serializers.ValidationError('User With This Email Or Phone Not Exsist')

        if user:
            return user

    def authenticate(self ,password, user):
        if user.check_password(password):
            return True
        else:
            raise serializers.ValidationError('Password For This User Is Incorrect')

    def validate(self, data):
        user = self.valid_user(data.get('email_or_phone'))
        if user and user.is_active:
            auth = self.authenticate(password=data.get('password'), user=user)
            if auth:
                return data
        raise serializers.ValidationError('User Is Not Active')

class PasswordResetSerializer(serializers.ModelSerializer):

    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['password1', 'password2']

    def validate(self, data):
        errors=[]
        if data.get('password1') == data.get('password2'):
            try:
                if validate_password(data.get('password1')) is None:
                    user = self.context.get('user')
                    user.set_password(data.get('password1'))
                    user.save()
                    user.reset_token.delete()
                    user.refresh_from_db
                    return data
            except ValidationError as e:
                for error in e:
                    # print(error)
                    errors.append(str(error))
                raise serializers.ValidationError(errors)
        raise serializers.ValidationError('Passwords Must Be Same')
    

class ChangePasswordSerializer(serializers.ModelSerializer):

    prev_pass = serializers.CharField(required=True)
    new_pass0 = serializers.CharField(required=True)
    new_pass1 = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['prev_pass', 'new_pass0', 'new_pass1']

    def validate(self, data):
        errors=[]
        if data.get('new_pass0') == data.get('new_pass1'):
            user = self.context.get('user')
            if user.check_password(data.get('prev_pass')):


                return data
            raise serializers.ValidationError('Previous Password Not Correct')
        raise serializers.ValidationError('New Passwords Must Be Same')
    
    def update(self, data):
        user = self.context.get('user')
        user.set_password(data.get('new_pass0'))
        user.save()
        user.reset_token.delete()
        user.refresh_from_db
        return user