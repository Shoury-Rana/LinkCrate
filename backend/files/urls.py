from django.urls import path
from .views import (
    FileUploadInitiateView,
    FileUploadCompleteView,
    FileListView,
    FileDetailView,
    FilePublicDetailView,
    FileDownloadView,
)

urlpatterns = [
    # Authenticated user routes for managing their files
    path('upload/initiate/', FileUploadInitiateView.as_view(), name='file-upload-initiate'),
    path('upload/complete/', FileUploadCompleteView.as_view(), name='file-upload-complete'),
    path('', FileListView.as_view(), name='file-list'),
    path('<uuid:shareable_id>/', FileDetailView.as_view(), name='file-detail'),

    # Public routes for accessing shared files
    path('public/<uuid:shareable_id>/', FilePublicDetailView.as_view(), name='file-public-detail'),
    path('public/<uuid:shareable_id>/download/', FileDownloadView.as_view(), name='file-download'),
]