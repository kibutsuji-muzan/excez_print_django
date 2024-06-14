from accounts.models.UserModel import User, UserProfile, ProfileImage, UserType

from rest_framework import serializers

from phonenumbers import parse as validate_phone
from pyisemail import is_email as validate_email


class UserTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserType
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['user']

class ProfileImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileImage
        fields = ['image']

    def update(self, instance, data):
        instance.image = data.get('image')
        instance.save()
        return instance

class ProfileSerializer(serializers.ModelSerializer):

    profile_image = ProfileImageSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'email', 'phone', 'first_name', 'last_name', 'gender', 'birthday', 'profile_image', 'email_verified', 'phone_verified']

    def validate(self, data):
        if data.get('email'):
            email = validate_email(address= data.get('email'), check_dns=True, diagnose=True)
            if email:
                pass
        if data.get('phone'):
            phone = validate_phone(data.get('phone'),None)
            if phone:
                pass
        if data.get('profile_image'):
            pass
        return data
        
    def update(self, instance, data):
        
        if self.context.get('request').data.get('email') is not None:
            instance.user_profile.email_verified = False

        instance.user_profile.first_name = data.get('first_name')
        instance.user_profile.last_name = data.get('last_name')
        instance.user_profile.email = data.get('email')
        instance.user_profile.gender = data.get('gender')
        instance.user_profile.birthday = data.get('birthday')

        p_s = ProfileImageSerializer(data=data.get('profile_image'))
        if p_s.is_valid(raise_exception=True):
            print(p_s.data)
            p_s.update(instance=instance.user_profile.profile_image, data=data.get('profile_image'))
            instance.user_profile.save()
        return instance
