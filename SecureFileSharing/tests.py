from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core import signing
from .models import User, UploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile

class FileSharingAPITestCase(APITestCase):
    def setUp(self):
        # Create Ops user
        self.ops_user = User.objects.create_user(
            username='ops1', email='ops1@example.com', password='opspass', user_type='ops', is_active=True
        )
        # Create Client user
        self.client_user = User.objects.create_user(
            username='client1', email='client1@example.com', password='clientpass', user_type='client', is_active=True
        )
        self.ops_token = self.get_token('ops1', 'opspass')
        self.client_token = self.get_token('client1', 'clientpass')
        self.api_client = APIClient()

    def get_token(self, username, password):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': username, 'password': password}, format='json')
        return response.data['access']

    def test_signup_and_email_verification(self):
        url = reverse('client-signup')
        data = {
            'username': 'newclient',
            'email': 'newclient@example.com',
            'password': 'newpass',
            'user_type': 'client'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('verify_url', response.data)
        # Simulate email verification
        token = response.data['verify_url'].split('token=')[1]
        verify_url = reverse('verify-email') + f'?token={token}'
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': 'client1', 'password': 'clientpass'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_upload_file_ops_user(self):
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.ops_token)
        url = reverse('file-upload')
        file = SimpleUploadedFile('test.docx', b'file_content', content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response = self.api_client.post(url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_file_client_user_forbidden(self):
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.client_token)
        url = reverse('file-upload')
        file = SimpleUploadedFile('test.docx', b'file_content', content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response = self.api_client.post(url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_files_client_user(self):
        # Upload a file as ops user first
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.ops_token)
        url = reverse('file-upload')
        file = SimpleUploadedFile('test.docx', b'file_content', content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.api_client.post(url, {'file': file}, format='multipart')
        # List files as client user
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.client_token)
        url = reverse('file-list')
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_generate_and_download_file(self):
        # Upload a file as ops user
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.ops_token)
        url = reverse('file-upload')
        file = SimpleUploadedFile('test.docx', b'file_content', content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        upload_response = self.api_client.post(url, {'file': file}, format='multipart')
        file_id = upload_response.data['id']
        # Generate download link as client user
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.client_token)
        url = reverse('generate-download-link', args=[file_id])
        response = self.api_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('download_url', response.data)
        # Download file as client user
        download_url = response.data['download_url']
        # Extract token and file_id from download_url
        import urllib.parse
        parsed = urllib.parse.urlparse(download_url)
        token = urllib.parse.parse_qs(parsed.query)['token'][0]
        url = reverse('download-file', args=[file_id]) + f'?token={token}'
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get('Content-Disposition'), f'attachment; filename="test.docx"')

    def test_download_file_wrong_user(self):
        # Upload a file as ops user
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.ops_token)
        url = reverse('file-upload')
        file = SimpleUploadedFile('test.docx', b'file_content', content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        upload_response = self.api_client.post(url, {'file': file}, format='multipart')
        file_id = upload_response.data['id']
        # Generate download link as client user
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.client_token)
        url = reverse('generate-download-link', args=[file_id])
        response = self.api_client.post(url)
        download_url = response.data['download_url']
        import urllib.parse
        parsed = urllib.parse.urlparse(download_url)
        token = urllib.parse.parse_qs(parsed.query)['token'][0]
        # Try to download as ops user (should fail)
        self.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.ops_token)
        url = reverse('download-file', args=[file_id]) + f'?token={token}'
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
