from rest_framework import serializers
from django.contrib.auth.models import User


class FirebaseAuthSerializer(serializers.Serializer):
    firebase_token = serializers.CharField()

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.ChoiceField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username','email','password']

#     def create(self,validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data.get('email'),
#             password=validated_data['password']
#         )
#         return user

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()