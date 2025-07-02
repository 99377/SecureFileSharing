# Secure File Sharing System (Django REST API)

## Overview
This project is a secure file-sharing backend system built with Django and Django REST Framework. It allows two types of users—Ops and Client—to interact with files securely via REST APIs. All endpoints are tested and demonstrated using Postman.

## Features
- **Ops User:**
  - Login
  - Upload files (`.pptx`, `.docx`, `.xlsx` only)
- **Client User:**
  - Sign up (returns encrypted email verification URL)
  - Email verification
  - Login
  - List all uploaded files
  - Generate secure download links
  - Download files (with secure, user-specific, encrypted URL)
- **Security:**
  - JWT authentication
  - File access restricted by user type
  - Download links are encrypted and user-specific

---

## Setup Instructions

### 1. Clone the Repository
```sh
git clone <your-repo-url>
cd <your-repo-directory>
```

### 2. Install Dependencies
```sh
pip install django djangorestframework djangorestframework-simplejwt
```

### 3. Project Initialization
```sh
django-admin startproject fileshare .
python manage.py startapp core
```

### 4. Database Migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Server
```sh
python manage.py runserver
```

---

## API Usage (with Postman)

### **A. Sign Up as Ops User**
- **POST** `/api/signup/`
- **Body (JSON):**
  ```json
  {
    "username": "ops1",
    "email": "ops1@example.com",
    "password": "yourpassword",
    "user_type": "ops"
  }
  ```
- **Response:** Contains `verify_url` for email verification.

### **B. Verify Email (Ops User)**
- **GET** `verify_url` from signup response (paste in browser or use Postman)

### **C. Login as Ops User**
- **POST** `/api/login/`
- **Body (JSON):**
  ```json
  {
    "username": "ops1",
    "password": "yourpassword"
  }
  ```
- **Response:** Contains `access` and `refresh` tokens.

### **D. Upload File (Ops User Only)**
- **POST** `/api/upload/`
- **Headers:** `Authorization: Bearer <ops_access_token>`
- **Body:** `form-data`, key: `file`, type: File, value: select `.pptx`, `.docx`, or `.xlsx` file

### **E. Sign Up as Client User**
- **POST** `/api/signup/`
- **Body (JSON):**
  ```json
  {
    "username": "client1",
    "email": "client1@example.com",
    "password": "yourpassword",
    "user_type": "client"
  }
  ```
- **Response:** Contains `verify_url` for email verification.

### **F. Verify Email (Client User)**
- **GET** `verify_url` from signup response

### **G. Login as Client User**
- **POST** `/api/login/`
- **Body (JSON):**
  ```json
  {
    "username": "client1",
    "password": "yourpassword"
  }
  ```
- **Response:** Contains `access` and `refresh` tokens.

### **H. List Files (Client User Only)**
- **GET** `/api/files/`
- **Headers:** `Authorization: Bearer <client_access_token>`

### **I. Generate Download Link (Client User Only)**
- **POST** `/api/generate-download-link/<file_id>/`
- **Headers:** `Authorization: Bearer <client_access_token>`
- **Response:** Contains `download_url`.

### **J. Download File (Client User Only)**
- **GET** `download_url` from previous step
- **Headers:** `Authorization: Bearer <client_access_token>`

---

## Endpoints Summary

| Endpoint                                      | Method | Who         | Description                                 |
|-----------------------------------------------|--------|-------------|---------------------------------------------|
| `/api/signup/`                               | POST   | Ops/Client  | User signup (returns verify URL)            |
| `/api/verify-email/?token=...`               | GET    | Ops/Client  | Email verification                          |
| `/api/login/`                                | POST   | Ops/Client  | JWT login                                   |
| `/api/upload/`                               | POST   | Ops         | Upload file (pptx, docx, xlsx only)         |
| `/api/files/`                                | GET    | Client      | List all uploaded files                     |
| `/api/generate-download-link/<file_id>/`     | POST   | Client      | Generate secure download link               |
| `/api/download/<file_id>/?token=...`         | GET    | Client      | Download file (with secure token)           |

---

## Notes
- All endpoints require JWT authentication except signup, login, and email verification.
- Only Ops users can upload files; only Client users can download.
- Use Postman's `form-data` for file uploads.
- Download links are user-specific and encrypted for security.

---

## License
This project is for educational/demo purposes. 