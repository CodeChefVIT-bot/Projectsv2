import re

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from project.models import RepoModel

from . import utilities
from .serializers import CommandSerializer

# Create your views here.


class CommandAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        if request.user.role == "admin":
            serializer = CommandSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            command = serializer.validated_data["command"]
            response = {}

            create_repo_pattern = re.compile(
                (
                    r"^create_repo (?P<name>\S+)"
                    r"( --desc (?P<description>\S*))?"
                    r"( --gitignore (?P<gitignore_template>\S*))?"
                    r"( --home (?P<homepage>\S*))?"
                    r"( --license (?P<license_template>\S*))?"
                    r"( --vis (?P<visibility>\S*))?"
                )
            )

            if match := re.match(create_repo_pattern, command):
                try:
                    response = utilities.create_repo(match)
                    instance = RepoModel()
                    instance.name = response["name"]
                    instance.url = response["url"]
                    instance.save()

                finally:
                    return Response(response)
        else:
            response = {"message":"User not authenticated"}
            return Response(response)

    def delete(self, request):

        if request.user.role == "admin":
            serializer = CommandSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            command = serializer.validated_data["command"]
            response = {}

            delete_repo_pattern = re.compile(r"delete_repo (?P<repo>.+)")

            if match := re.match(delete_repo_pattern, command):
                response = utilities.delete_repo(match)

            if response:
                response = dict()
                response["message"] = "Repository deleted"
                instance = RepoModel.objects.get(name=match.group("repo"))
                instance.delete()

            else:
                response = dict()
                response["message"] = "Repository not found"

        else:
            response = {"message":"User not authenticated"}

            
        return Response(response)