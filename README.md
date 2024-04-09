# WMS API Documentation

## Introduction

This document outlines the functionalities and usage of the WMS APIs. It serves as a reference for front-end developers integrating with the backend system.

### User Management Endpoints 

#### 1. Register 

- **URL:**  [http://127.0.0.1:8000/api/register/]() 
- **Method:**  POST 
- **Authorization:**  Not required 
- **Parameters:** 
- ```first_name``` (string, required): User first name.
- ```last_name``` (string, required): User last name.
- ```username``` (string, required): User username (must be unique).
- ```email``` (string, required): User email (must be unique).
- ```password``` (string, required): User password. 
- ```confirm_password``` (string, required): User password for confirmation (must match the password). 
- ```role``` (string, required): User role (admin, staff, customer). 

- **Request Example:** 
```json
{
    "first_name": "Ali",
    "last_name": "Sliman",
    "username": "Alisl001",
    "email": "test@email.com",
    "password": "12345678",
    "confirm_password": "12345678",
    "role": "staff"
}
``` 
- **Response Example (Success):** 
- **Status Code:**  `201` Created
```json
{
    "message": "User registered successfully."
}
```
- **Response Example (error):** 
- **Status Code:**  `400` Bad Request
```json
{
    "username": [
        "A user with that username already exists."
    ],
    "email": [
        "A user with that email already exists."
    ],
    "password": [
        "Password fields didn't match."
    ]
}
```

#### 2. Login

- **URL:**  [http://127.0.0.1:8000/api/login/]() 
- **Method:**  POST 
- **Authorization:**  Not required 
- **Parameters:** 
- ```username_or_email``` (string, required): User username or email (users can log in with either their username or email).
- ```password``` (string, required): User password. 

- **Request Example:** 
```json
{
    "username_or_email": "Alisl001",
    "password": "12345678"
}
```
- **Response Example (Success):** 
- **Status Code:**  `200` OK
```json
{
    "access_token": "ed745e109b4b6ef602a1f6d574c217d85be670e8",
    "token_type": "bearer",
    "expires_in": 36000,
    "user": {
        "id": 6,
        "first_name": "Ali",
        "last_name": "Sliman",
        "username": "Alisl001",
        "email": "test@email.com",
        "date_joined": "2024-04-09T13:01:51.139743Z",
        "role": "staff"
    }
}
```
- **Response Example (error):** 
- **Status Code:**  `400` Bad Request
```json
{
    "non_field_errors": [
        "Unable to log in with provided credentials."
    ]
}
```

#### 3. Logout 
- **URL:**  [http://127.0.0.1:8000/api/logout/]() 
- **Method:**  POST 
- **Authorization:**  Required (Bearer Token) 
- **Parameters:**  None 
- **Request Example:** 
- No additional parameters are required. 

- **Response Example (Success):** 
- **Status Code:**  `200` OK 
```json
{
    "detail": "Logged out successfully."
}
``` 
- **Response Example (Error):** 
- **Status Code:**  `401` Unauthorized 
```json
{
    "detail": "Authentication credentials were not provided."
}
```
```json
{
    "detail": "Invalid token."
}
```


