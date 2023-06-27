from django.shortcuts import render
from rest_framework.views import APIView, Request, Response, status
from groups.models import Group
from groups.serializers import GroupSerializer

# Create your views here.

class GroupView(APIView):
    ...