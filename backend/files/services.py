from django.conf import settings
from supabase import create_client, Client

class SupabaseService:
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("Supabase URL and Key must be set in settings.")
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket_name: str = settings.SUPABASE_BUCKET_NAME

    def create_signed_upload_url(self, path: str) -> dict:
        """
        Generates a signed URL for uploading a file.
        """
        try:
            signed_url = self.client.storage.from_(self.bucket_name).create_signed_url(path=path, expires_in=3600)
            return signed_url
        except Exception as e:
            print(f"Error creating signed upload URL: {e}")
            return None

    def create_signed_download_url(self, path: str) -> dict:
        """
        Generates a signed URL for downloading a file.
        """
        try:
            signed_url = self.client.storage.from_(self.bucket_name).create_signed_url(
                path=path,
                expires_in=600
            )
            return signed_url
        except Exception as e:
            print(f"Error creating signed download URL: {e}")
            return None


supabase_service = SupabaseService()