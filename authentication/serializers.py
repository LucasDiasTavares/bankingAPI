from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.conf import settings
from .models import User, UserAddress, UserBankAccount


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['id', 'street_address', 'city', 'postal_code', 'country']


class UserBankAccountRegister(serializers.ModelSerializer):
    class Meta:
        model = UserBankAccount
        fields = ['id', 'account_type', 'gender', 'birth_date']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    userAddress = UserAddressSerializer(write_only=True)
    userBankAccount = UserBankAccountRegister(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'userAddress', 'userBankAccount']

    def validate(self, attrs):
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError('Username should only contains alphanumeric characters')

        return attrs

    def create(self, validated_data):
        user_Address = validated_data.pop('userAddress')
        user_Bank_Account = validated_data.pop('userBankAccount')
        user = User.objects.create_user(**validated_data)
        account_number = user.id+settings.ACCOUNT_NUMBER_START_FROM

        UserAddress.objects.create(user=user, **user_Address)
        UserBankAccount.objects.create(user=user, **user_Bank_Account, account_no=account_number)

        user.save()

        return user


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'access': user.tokens()['access'],
            'refresh': user.tokens()['refresh']
        }

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'username', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again!')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin!')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified!')

        return {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }


class ResetPasswordEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        model = User
        fields = ['email', 'redirect_url']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']
        
    def validate(self, attrs):

        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return user

        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is expired or invalid'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']

        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class UserBankAccountData(serializers.ModelSerializer):
    class Meta:
        model = UserBankAccount
        fields = ['id', 'account_type', 'balance', 'account_no', 'gender', 'birth_date']


class UserDataSerializer(serializers.ModelSerializer):
    address = UserAddressSerializer(read_only=True)
    account = UserBankAccountData(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'address', 'account']


class UserAddressForUpdateSerializer(serializers.ModelSerializer):
    street_address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    postal_code = serializers.IntegerField(required=False)
    country = serializers.CharField(required=False)

    class Meta:
        model = UserAddress
        fields = ['street_address', 'city', 'postal_code', 'country']


class UserAddressUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    userAddress = UserAddressForUpdateSerializer(write_only=True, partial=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'userAddress']

    def update(self, instance, validated_data):
        nested_serializer = self.fields['userAddress']
        nested_instance = instance.address
        # remove nested object
        nested_data = validated_data.pop('userAddress')
        # update the object without nested
        instance.username = validated_data.get('username', instance.username)
        # update the nested object
        nested_serializer.update(nested_instance, nested_data)

        instance.save()
        return instance
