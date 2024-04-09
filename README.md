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
    "last_name": "Qasem",
    "username": "aliq",
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

