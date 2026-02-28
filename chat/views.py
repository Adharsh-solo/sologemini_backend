from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics
from django.conf import settings
from .models import History
from .serializers import RegisterSerializer, HistorySerializer, UserSerializer
import google.generativeai as genai

from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterView(generics.CreateAPIView):
    queryset = History.objects.none()  # Or User.objects.all(), but we don't need it for creation
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class HistoryListView(generics.ListAPIView):
    serializer_class = HistorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return History.objects.filter(user=self.request.user).order_by('created_at')

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        # We also want to return the profile picture if it exists
        return self.request.user

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login_view(request):
    token = request.data.get('token')
    
    if not token:
        return Response({'error': 'Token is required'}, status=400)

    try:
        # Verify the token with Google
        # For production, specify CLIENT_ID: id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        # Using placeholder verification for generic usage if no specific client ID is set yet
        idinfo = id_token.verify_oauth2_token(token, requests.Request())
        
        email = idinfo.get('email')
        name = idinfo.get('name')
        picture = idinfo.get('picture')

        if not email:
            return Response({'error': 'Email not provided by Google'}, status=400)

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create user
            # Username could be email prefix or generate a unique string
            username = email.split('@')[0]
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            user = User.objects.create_user(username=username, email=email)
            user.set_unusable_password()
            user.save()

        # Update or create profile with the Google picture
        profile, created = UserProfile.objects.get_or_create(user=user)
        if picture:
            profile.profile_picture = picture
            profile.save()

        # Generate standard SimpleJWT tokens for this user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'profile_picture': profile.profile_picture
            }
        })
        
    except ValueError as e:
        # Invalid token
        return Response({'error': 'Invalid Google token'}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_view(request):
    message = request.data.get('message')
    history = request.data.get('history', [])
    
    if not message:
        return Response({'error': 'Message is required'}, status=400)
        
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        return Response({'error': 'GEMINI_API_KEY is not set'}, status=500)
    
    genai.configure(api_key=api_key)
    
    # Use flash model as it is faster and recommended for chat
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        # History format from frontend is mapped directly 
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(message)
        
        reply_text = response.text
        if request.user.is_authenticated:
            History.objects.create(
                user=request.user,
                user_message=message,
                ai_response=reply_text
            )

        return Response({'reply': reply_text})
    except Exception as e:
        return Response({'error': str(e)}, status=500)
