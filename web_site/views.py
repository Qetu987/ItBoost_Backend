from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dotenv import load_dotenv
import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from web_site.serializers import (
    CallBackRequestCreateSerializer,
    CallBackRequestDisplaySerializer
    )
from user.permissions import IsModerator
from rest_framework.permissions import AllowAny




class CallBackRequestCreateView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Create Callback Request",
        operation_description="Creates a new callback request if provided with the correct API key",
        request_body=CallBackRequestCreateSerializer,
        responses={
            201: openapi.Response("Created", CallBackRequestCreateSerializer),
            401: "Unauthorized",
            400: "Bad Request"
        },
        tags=['Web-site Request']
    )
    def post(self, request):
        print('hi')
        load_dotenv()

        api_key = request.headers.get('X-API-KEY')

        print(f"my key: {os.getenv('STATIC_API_KEY')}")
        print(f'request key: {api_key}')

        if api_key != os.getenv('STATIC_API_KEY'):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = CallBackRequestCreateSerializer(data=request.data)

        if serializer.is_valid():            
            serializer.save()
            return Response({"message": "Created"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)