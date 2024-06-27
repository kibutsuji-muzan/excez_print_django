from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from exizprint.models.services import NotificationToken

from accounts.models.UserModel import User, dk

from pyisemail import is_email as validate_email

# from accounts.signals import Create_Verif_Device
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','phone']

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField()
    email = serializers.CharField()
    fcm_token = serializers.CharField()
    class Meta:
        model = User
        fields = ['email', 'password', 'fcm_token']

    def create(self, data):
        try:
            email =validate_email(data.get('email'))
        except:
            raise serializers.ValidationError('Not Valid')

        errors = []
        try:
            if validate_password(data.get('password')) is None:
                # print('password is valid')
                print(data.get('email'))
                user = User.objects.create(email = data.get('email').lower())
                print(data.get('email'))
                # Create_Profile.send(sender=user, data=data, email_phone=phone)
                user.set_password(data.get('password'))
                user.is_active = False
                user.save()
                token = NotificationToken.objects.get(token = data.get('fcm_token'))
                token.user = user
                token.save()
                return user
        except ValidationError as e:
            print('password not valid or other exception')
            for error in e:
                print(error)
                errors.append(str(error))
            raise serializers.ValidationError(e)


class SignInSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    fcm_token = serializers.CharField()
    class Meta:
        fields = ['email', 'password', 'fcm_token']

    def valid_user(self, email):
        id = dk(email)
        print(id)
        try:
            user = User.objects.get(email=email)
        except:
            raise serializers.ValidationError('User With This Email Not Exsist')

        if user:
            return user

    def authenticate(self ,password, user):
        if user.check_password(password):
            return True
        else:
            raise serializers.ValidationError('Password For This User Is Incorrect')

    def validate(self, data):
        user = self.valid_user(data.get('email'))
        print(user)
        if user or user.is_active:
            auth = self.authenticate(password=data.get('password'), user=user)
            if auth:
                try:
                    token = NotificationToken.objects.get(token = data.get('fcm_token'))
                    token.user = user
                    token.save()
                    print(f'token: {token}')
                except Exception as e:
                    NotificationToken.objects.create(token = data.get('fcm_token') , user = user)
                    print(e)
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
        user.refresh_from_db
        return user