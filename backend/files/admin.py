from django.contrib import admin
from .models import File

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'file_name',
        'owner',
        'file_type',
        'size',
        'is_deleted',
        'created_at',
        'expires_at'
    )
    list_filter = ('is_deleted', 'file_type', 'created_at')
    search_fields = ('file_name', 'owner__email')
    readonly_fields = ('created_at', 'updated_at', 'shareable_id', 'supabase_path')