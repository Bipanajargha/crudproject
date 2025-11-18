from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from .models import Registartion

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

#Create your views here. 
def home(request):
    return render(request, 'crud/index.html')


def form(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Your form is successfully submitted!")
            form.save()
            return redirect('form')
    else:
        form = RegistrationForm()
    return render(request, 'crud/form.html', {'form': form})


def list(request):
    data = Registartion.objects.filter(isdelete=False)
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


# ---------------- API Views ---------------- 

class FormCreate(APIView):
    """Handles create operations"""
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
