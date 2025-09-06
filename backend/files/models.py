import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

class File(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='files')
    shareable_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # File metadata
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    size = models.PositiveIntegerField()
    supabase_path = models.CharField(max_length=1024, unique=True)

    # Access control
    password = models.CharField(max_length=128, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    # State
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        if raw_password:
            self.password = make_password(raw_password)
        else:
            self.password = None

    def check_password(self, raw_password):
        if not self.password:
            return False # No password is set
        if not raw_password:
            return False # No password was provided for checking
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.file_name} ({self.owner.email})"