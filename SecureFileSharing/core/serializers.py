from rest_framework import serializers
from .models import User, UploadedFile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False  # Require email verification
        user.save()
        return user

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'file', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']

    def validate_file(self, value):
        allowed_types = ['.pptx', '.docx', '.xlsx']
        import os
        ext = os.path.splitext(value.name)[1]
        if ext.lower() not in allowed_types:
            raise serializers.ValidationError('Only pptx, docx, and xlsx files are allowed.')
        return value
