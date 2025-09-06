import uuid
from datetime import datetime
import pytz

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from .models import File
from .serializers import (
    FileUploadInitiateSerializer,
    FileUploadCompleteSerializer,
    FileDetailSerializer,
    FilePublicDetailSerializer,
    FileDownloadSerializer,
)
from .permissions import IsOwner
from .services import supabase_service


class FileUploadInitiateView(generics.GenericAPIView):
    """
    Initiates the file upload process.
    Takes file_name and file_type, returns a signed URL for the client to upload the file to.
    """
    serializer_class = FileUploadInitiateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_name = serializer.validated_data['file_name']
        
        # Generate a unique path for the file in storage
        unique_file_name = f"{uuid.uuid4()}-{file_name}"
        supabase_path = f"{request.user.id}/{unique_file_name}"

        signed_url_data = supabase_service.create_signed_upload_url(supabase_path)

        if not signed_url_data:
            return Response(
                {"error": "Could not generate signed URL"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response_data = {
            'signed_url': signed_url_data['signedURL'],
            'supabase_path': supabase_path
        }
        return Response(response_data, status=status.HTTP_200_OK)


class FileUploadCompleteView(generics.CreateAPIView):
    """
    Completes the file upload process.
    Saves the file metadata to the database after the client confirms the upload.
    """
    serializer_class = FileUploadCompleteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class FileListView(generics.ListAPIView):
    """
    Lists all non-deleted files for the authenticated user.
    """
    serializer_class = FileDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return File.objects.filter(owner=self.request.user, is_deleted=False).order_by('-created_at')


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or soft-delete a file instance.
    Only the owner can perform these actions.
    """
    queryset = File.objects.all()
    serializer_class = FileDetailSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    lookup_field = 'shareable_id'

    def perform_destroy(self, instance):
        # Perform a soft delete
        instance.is_deleted = True
        instance.save()


class FilePublicDetailView(generics.RetrieveAPIView):
    """
    Provides public-facing details for a file, checking for expiry or deletion.
    """
    queryset = File.objects.all()
    serializer_class = FilePublicDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'shareable_id'

    def get_object(self):
        obj = super().get_object()
        if obj.is_deleted:
            raise NotFound()
        if obj.expires_at and obj.expires_at < datetime.now(pytz.utc):
            raise NotFound("This link has expired.")
        return obj


class FileDownloadView(generics.GenericAPIView):
    """
    Generates a signed download URL for a file.
    Validates the password if the file is password-protected.
    """
    serializer_class = FileDownloadSerializer
    permission_classes = [AllowAny]
    lookup_field = 'shareable_id'

    def get_object(self):
        shareable_id = self.kwargs[self.lookup_field]
        try:
            obj = File.objects.get(shareable_id=shareable_id)
        except File.DoesNotExist:
            raise NotFound()
        
        if obj.is_deleted:
            raise NotFound()
        if obj.expires_at and obj.expires_at < datetime.now(pytz.utc):
            raise NotFound("This link has expired.")
        
        return obj

    def post(self, request, *args, **kwargs):
        file_instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if file_instance.password:
            provided_password = serializer.validated_data.get('password')
            if not file_instance.check_password(provided_password):
                raise PermissionDenied("Invalid password.")
        
        signed_url_data = supabase_service.create_signed_download_url(file_instance.supabase_path)

        if not signed_url_data:
            return Response(
                {"error": "Could not generate download link"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({'download_url': signed_url_data['signedURL']}, status=status.HTTP_200_OK)