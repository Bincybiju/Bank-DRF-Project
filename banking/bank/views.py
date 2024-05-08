from bank.serializer import *
from rest_framework import status
from .models import User
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if 'user_type' in serializer.validated_data and serializer.validated_data['user_type'] == 'staff':
                user.is_staff = True
                user.save()
            return Response({'message': 'User created'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
 
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
           
            user = authenticate(request, username=username, password=password)
            # print(user)
            if user is not None:
                user.save()  
                access_token = AccessToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)

                return Response({
                    'message': 'Login successful',
                    'access': str(access_token),
                    'refresh': str(refresh_token),

                })
            else:
                return Response({'detail': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        data = request.data.copy()  

        allowed_fields = [ 'password', 'first_name','last_name', 'dob']
        additional_fields = [field for field in data if field not in allowed_fields]
        if additional_fields:
            return Response({"error": f"Updating fields other than {', '.join(allowed_fields)} is not allowed"}, status=status.HTTP_400_BAD_REQUEST)
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

        serializer = ProfileUpdateSerializer(user, data=filtered_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   

from django.contrib.auth import logout
class LogoutAPIView(APIView):     
    permission_classes = [IsAuthenticated]    
    def post(self, request):        
        logout(request)        
        return Response({'message':'Logout successful'})


# class LogoutAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         try:
#             auth_header = request.headers['Authorization']
#             refresh_token = request.headers['refresh']
#             if refresh_token.startswith('Bearer ') and auth_header.startswith('Bearer '):
#                 bearer_refresh_token = refresh_token.split('Bearer ')[1]
#                 RefreshToken(bearer_refresh_token).blacklist()
#             return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  