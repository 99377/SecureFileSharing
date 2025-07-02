from django.shortcuts import render
from .models import UploadedFile, User
from rest_framework import generics, permissions, status
from .serializers import UserSerializer, UploadedFileSerializer
from django.core import signing
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse, Http404

# Create your views here.

class ClientSignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user_id = serializer.data['id']
        token = signing.dumps({'user_id': user_id})
        verify_url = f"http://127.0.0.1:8000/api/verify-email/?token={token}"
        headers = self.get_success_headers(serializer.data)
        data = serializer.data.copy()
        data['verify_url'] = verify_url
        return Response(data, status=201, headers=headers)

class IsOpsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'ops'

class FileUploadView(generics.CreateAPIView):
    queryset = UploadedFile.objects.all()  # type: ignore
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOpsUser]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

class VerifyEmailView(APIView):
    def get(self, request):
        token = request.GET.get('token')
        try:
            data = signing.loads(token)
            user_id = data['user_id']
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified!'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

class FileListView(generics.ListAPIView):
    queryset = UploadedFile.objects.all()  # type: ignore
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'client':
            return UploadedFile.objects.all() # type: ignore
        return UploadedFile.objects.none() # type: ignore

class GenerateDownloadLinkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if request.user.user_type != 'client':
            return Response({'error': 'Only client users can download files.'}, status=403)
        token = signing.dumps({'file_id': pk, 'user_id': request.user.id})
        download_url = f"http://127.0.0.1:8000/api/download/{pk}/?token={token}"
        return Response({'download_url': download_url})

class DownloadFileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        token = request.GET.get('token')
        try:
            data = signing.loads(token)
            if data['file_id'] != int(pk) or data['user_id'] != request.user.id:
                return Response({'error': 'Invalid token.'}, status=403)
            file_obj = UploadedFile.objects.get(pk=pk)  # type: ignore
            return FileResponse(file_obj.file, as_attachment=True)
        except Exception:
            raise Http404
