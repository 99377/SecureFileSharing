from django.urls import path
from .views import (
    ClientSignUpView, VerifyEmailView, FileUploadView, FileListView,
    GenerateDownloadLinkView, DownloadFileView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', ClientSignUpView.as_view(), name='client-signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('files/', FileListView.as_view(), name='file-list'),
    path('generate-download-link/<int:pk>/', GenerateDownloadLinkView.as_view(), name='generate-download-link'),
    path('download/<int:pk>/', DownloadFileView.as_view(), name='download-file'),
]
