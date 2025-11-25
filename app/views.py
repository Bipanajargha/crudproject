from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from .models import Registartion

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer,UserRegisterSerializer,UserLoginSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# authentication
from datetime import datetime
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

#for usesr auth
from django.contrib.auth.models import User

# to change the password
from django.contrib.auth.forms import PasswordChangeForm

#jwt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
#swagger
from rest_framework.permissions import AllowAny, IsAuthenticated
#auth serializer

#for email
from django.core.mail import send_mail
from django.conf import settings

#Create your views here. 
date = datetime.now()

#html views
def home(request):
    return render(request, 'crud/index.html')

def form(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid(): #valid the forms from the fields
            messages.success(request, "Your form is successfully submitted!")
            form.save() #save to the db
            return redirect('form')
    else:
        form = RegistrationForm() #initalize empty form for get request
    return render(request, 'crud/form.html', {'form': form})

@login_required(login_url='log_in')
def list(request):
    data = Registartion.objects.filter(isdelete=False) #fetch only active
    return render(request, 'crud/list.html', {'data': data})

def delete_data(request, pk):
    """Soft delete"""
    obj = Registartion.objects.get(id=pk)
    obj.isdelete = True
    obj.save()
    return redirect('list')

def edit(request, pk):
    obj = Registartion.objects.get(id=pk)
    if request.method == "POST":
        form = RegistrationForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('list')
    else:
        form = RegistrationForm(instance=obj)
    return render(request, 'crud/edit.html', {'form': form})

@login_required(login_url='log_in')
def about(request):
    return render(request,'crud/about.html')
@login_required(login_url='log_in')
def services(request):
    return render(request,'crud/services.html')

def log_in(request):
    if request.method == "POST":
        username = request.POST ['username']
        password = request.POST['password']
        remeber_me = request.POST.get('remember_me')

        if not User.objects.filter(username=username).exists():
            messages.error(request,"You are not registered")
            return redirect('log_in')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request,user)
            if remeber_me:
                request.session.set_expiry(3600000)
            else:
                request.session.set.exipry(0)
            return redirect('home')
        else:
            messages.error(request,"Invalid password")
    return render(request,'auth/login.html')
        
#  auth partttttttttt
def register(request):
    if request.method == "POST":
        data1 = request.POST
        first_name = data1['first_name'] #html
        last_name = data1['last_name']
        username = data1['username']
        email = data1['email']
        password = data1['password']
        confirm_password = data1['confirm_password']

        if password==confirm_password:
            try:
                validate_password(password)
                if User.objects.filter(username=username).exists(): #fetching
                    messages.error(request,"Username already exists")
                    return redirect ('register')
                if User.objects.filter(email=email).exists():
                    messages.error(request,"Email already exists")
                    return redirect ('register')
                User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
                messages.success(request,"sucessfully register")
                return redirect('log_in')
            except ValidationError as e:
                for err in e.messages:
                    messages.error(request,err)
                    return redirect('register')
        else:
            messages.error(request,"Password and comfirm passwoed doesnot match ")
            return redirect('register')

    return render(request,"auth/register.html")

        

# ---------------- API Views ---------------- 

class FormCreate(APIView):
    """Handles create operations"""
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except (InvalidToken, TokenError):
            return Response({"message": "Token has expired"}, status=401)
    @swagger_auto_schema(
        operation_summary="Create a new registration",
        operation_description="Submit the registration form. Returns the created object on success.",
        request_body=RegistrationSerializer,
        responses={
            201: openapi.Response('Registration done successfully', RegistrationSerializer),
            400: 'Invalid data provided'
        }
    )
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration done successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class ListReg(APIView):
    """Handles list operations"""
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except (InvalidToken, TokenError):
            return Response({"message": "Token has expired"}, status=401)
        
    @swagger_auto_schema(
        operation_summary= "List all registartions",
        operation_description="Returns a list of all registrations that are not deleted.",
        responses={200:openapi.Response('success',RegistrationSerializer(many=True))}
    )
    def get(self, request):
        objs = Registartion.objects.filter(isdelete=False)
        serializer = RegistrationSerializer(objs, many=True)
        return Response({"message":"List of the registartions shown successfully", "data":serializer.data})


class FormDetailApi(APIView):
    """Handles retrieve, update, and soft delete for a single object"""
    permission_classes =[IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except (InvalidToken, TokenError):
            return Response({"message": "Token has expired"}, status=401)
        
    @swagger_auto_schema(
        operation_summary= "Retrieve the registartion by id",
        operation_description="Get a single registration object by its ID. Returns 404 if not found.",
        responses={
            200: openapi.Response('Registration retrieved successfully', RegistrationSerializer),
            404: 'Registration not found of given id'
        }
    )
    def get(self, request, pk):
        obj = Registartion.objects.filter(id=pk, isdelete=False).first()
        if not obj:
            return Response({"message": f"Registration with ID {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RegistrationSerializer(obj)
        return Response({"message": f"Registration with ID {pk} retrieved successfully", "data": serializer.data})


    @swagger_auto_schema(
        operation_summary="Update registration by id",
        operation_description= "Update fields of a registration object. 'isdelete' cannot be modified.",
        request_body=RegistrationSerializer,
        responses={
            200: openapi.Response('Registration updated successfully', RegistrationSerializer),
            400: 'Invalid data',
            404: 'Registration not found'
        }
    )
    def put(self, request, pk):
        obj = Registartion.objects.filter(id=pk, isdelete=False).first()
        if not obj:
            return Response({"message": "Registration not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only allow updating editable fields, prevent changing isdelete
        data = request.data.copy()
        data.pop('isdelete', None)

        serializer = RegistrationSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration updated successfully", "data": serializer.data})
        return Response({"message": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete registration",
        operation_description="Marks the registration as deleted.",
        responses={
            200: 'Registration deleted successfully',
            404: 'Registration not found'
        }
    )
    def delete(self, request, pk):
        obj = Registartion.objects.filter(id=pk, isdelete=False).first()
        if not obj:
            return Response({"message": "Registration not found"}, status=status.HTTP_404_NOT_FOUND)
        obj.isdelete = True
        obj.save()
        return Response({"message": "Registration deleted successfully"}, status=status.HTTP_200_OK)

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Register user here",
        request_body=UserRegisterSerializer,
        responses={200: "Registered sucessfully", 401: "Invalid credentials"}
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            reg_user = serializer.save()
            # Send confirmation email
            try:
                send_mail(
                    subject='Registration Successful',
                    message=f'Hello {reg_user.first_name},\n\nThank you for registering!\n\nYour details have been saved successfully.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reg_user.email],  # adjust field name based on your model
                    fail_silently=False,
                )
            except Exception as e:
                # Log error but don't fail the registration
                print(f"Email failed: {e}")
            return Response({"message": "User registered successfully", "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Registration failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Login and obtain JWT tokens",
        request_body=UserLoginSerializer,
        responses={200: "Sucessfully login", 401: "Invalid credentials"}
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                return Response({
                    "access_token": access,
                    "refresh": str(refresh),
                    "message": "Log in sucessfully",
                    "user": {"id": user.id, "username": user.username, "email": user.email}
                })
            return Response({"message": "Invalid credentials"}, status=401)
        return Response({"message": "Login failed","errors":serializer.errors}, status=400)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Logout and blacklist refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            },
            required=['refresh']
        ),
        responses={
            200: 'Logout successful',  # Changed from 205
            400: 'Invalid token'
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"message": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({"message": "Logout successfully"}, status=status.HTTP_200_OK)  # Changed here
        except TokenError:
            return Response({"message": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)