from django.shortcuts import render
import firebase_admin
from firebase_admin import auth as firebase_auth
from django.contrib.auth import get_user_model
from rest_framework import status,generics,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializer import LoginSerializer,RegisterSerializer,LogoutSerializer
from django.db.models import Q
from .serializer import FirebaseAuthSerializer



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['username']
        password = serializer.validated_data['password']
        try:
            user = User.objects.get(Q(username=identifier) | Q(email=identifier))
        except User.DoesNotExist:
            return Response({"detail":"Invalid credentials"},status=status.HTTP_401_UNAUTHORIZED)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh':str(refresh),
                'access':str(refresh.access_token)
            })
        return Response({"detail":"invalid crendentials"},status=status.HTTP_401_UNAUTHORIZED)

    
class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer
    def post(self,request):
        try:
            refresh_token = self.get_serializer(data=request.data)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)





# User = get_user_model()

# class FirebaseLoginView(APIView):
#     def post(self,request):
#         serializer = FirebaseAuthSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         id_token = serializer.validated_data['firebase_token']

#         try:
#             decoded = firebase_auth.verify_id_token(id_token)
#         except Exception as e :
#             return Response({'detail': 'Invalid Firebase token'}, status=status.HTTP_400_BAD_REQUEST)
#         uid = decoded['uid']
#         email = decoded.get('email')
#         name = decoded.get('name','')

#         user,_ = User.objects.get_or_create(
#             username=uid,
#             default={'email':email,'first_name':name}
#         )
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             'access':str(refresh.access_token),
#             'refresh':str(refresh)
#         })

# def firebase_login_page(request):
#     return render(request, "firebase_login.html")