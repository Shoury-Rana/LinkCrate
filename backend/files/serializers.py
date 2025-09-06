from rest_framework import serializers
from .models import File

class FileUploadInitiateSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    file_type = serializers.CharField(max_length=100)


class FileUploadCompleteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=128)
    shareable_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = File
        fields = (
            'shareable_id',
            'supabase_path',
            'file_name',
            'file_type',
            'size',
            'password',
            'expires_at',
        )

    def create(self, validated_data):
        file = File(**validated_data)
        raw_password = validated_data.get('password')
        file.set_password(raw_password)
        file.save()
        return file


class FileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = (
            'shareable_id',
            'file_name',
            'file_type',
            'size',
            'supabase_path',
            'expires_at',
            'created_at',
            'updated_at',
        )


class FilePublicDetailSerializer(serializers.ModelSerializer):
    is_password_protected = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = (
            'shareable_id',
            'file_name',
            'file_type',
            'size',
            'is_password_protected',
        )

    def get_is_password_protected(self, obj):
        return bool(obj.password)


class FileDownloadSerializer(serializers.Serializer):
    password = serializers.CharField(required=False, allow_blank=True)