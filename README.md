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
```json
{
    "detail": "All fields are required."
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

#### 4. Password reset request

- **URL:**  [http://127.0.0.1:8000/api/password-reset/request/]() 
- **Method:**  POST 
- **Authorization:**  Not required 
- **Parameters:** 
- ```email``` (string, required): User email.

- **Request Example:** 
```json
{
    "email": "test@email.com"
}
```
- **Response Example (Success):** 
- **Status Code:**  `200` OK
```json
{
    "detail": "Password reset code sent to your email."
}
```
- **Response Example (error):** 
- **Status Code:**  `400` Bad Request
```json
{
    "detail": "Email is required."
}
```
- **Response Example (error):** 
- **Status Code:**  `404` Not Found
```json
{
    "detail": "Email not found in the database."
}
```

#### 5. Password reset confirm

- **URL:**  [http://127.0.0.1:8000/api/password-reset/confirm/]() 
- **Method:**  POST 
- **Authorization:**  Not required 
- **Parameters:** 
- ```email``` (string, required): User email.
- ```code``` (string, required): The code sent to the user email in the passord reset request API.
- ```password``` (string, required): New password.
- ```confirm_password``` (string, required): Confirm new password.

- **Request Example:** 
```json
{
    "email": "test@email.com",
    "code": "135246",
    "password": "12345678",
    "confirm_password": "12345678"
}
```
- **Response Example (Success):** 
- **Status Code:**  `200` OK
```json
{
    "detail": "Password reset successful."
}
```
- **Response Example (error):** 
- **Status Code:**  `400` Bad Request
```json
{
    "detail": "All fields are required."
}
```
```json
{
    "detail": "Invalid code."
}
```
```json
{
    "detail": "Passwords do not match."
}
```
- **Response Example (error):** 
- **Status Code:**  `404` Not Found
```json
{
    "detail": "Email not found in the database."
}
```

#### 6. Get User Details by ID
- **URL:**  [http://127.0.0.1:8000/api/users/<id>/]() 
- **Method:**  GET 
- **Authorization:**  Not required 
- **Parameters:** 
- None 
- **Request Example:** 
- No additional parameters required. 
- **Response Example (Success):** 
- **Status Code:**  `200` OK
```json
{
    "id": 6,
    "username": "Alisl001",
    "email": "test@email.com",
    "first_name": "Ali",
    "last_name": "Sliman",
    "date_joined": "2024-04-09T13:01:51.139743Z",
    "role": "staff"
}
```
- **Response Example (error):** 
- **Status Code:**  `404` Not Found
```json
{
    "detail": "User not found"
}
```

#### 7. Get User Details by Auth Token
- **URL:**  [http://127.0.0.1:8000/api/my-details/]() 
- **Method:**  GET 
- **Authorization:**  Required (Bearer Token) 
- **Parameters:** 
- None 
- **Request Example:** 
- No additional parameters required. 
- **Response Example (Success):** 
- **Status Code:**  `200` OK
```json
{
    "id": 6,
    "username": "Alisl001",
    "email": "test@email.com",
    "first_name": "Ali",
    "last_name": "Sliman",
    "date_joined": "2024-04-09T13:01:51.139743Z",
    "role": "staff"
}
```
- **Response Example (error):** 
- **Status Code:**  `401` Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 8. Change my password API 

- **URL:**  [http://127.0.0.1:8000/api/user/change-password/]() 
- **Method:**  POST 
- **Authorization:**  Required (Bearer Token) 
- **Parameters:** 
- ```old_password``` (string, required): Old password.
- ```new_password``` (string, required): New password.
- ```confirm_new_password``` (string, required): New password confirmation.

- **Request Example:** 
```json
{
    "old_password": "12345678",
    "new_password": "12345678",
    "confirm_new_password": "12345678"
}
```
- **Response Example (Success):** 
- **Status Code:**  `200` OK
```json
{
    "detail": "Password changed successfully"
}
```
- **Response Example (error):** 
- **Status Code:**  `400` Bad Request
```json
{
    "detail": "Old password is incorrect"
}
```
```json
{
    "detail": "New password and confirm password do not match"
}
```

#### 9. Update user info API 

- **URL:**  [http://127.0.0.1:8000/api/user/update-info/]() 
- **Method:**  PUT 
- **Authorization:**  Required (Bearer Token) 
- **Parameters:** 
- ```first_name``` (string, optional): User first name.
- ```last_name``` (string, optional): User last name.
- ```username``` (string, optional): User username.
- ```email``` (string, optional): User email.

- **Request Example:** 
```json
{
    "first_name": "Ali",
    "last_name": "Sliman",
    "username": "Alisl001",
    "email": "test@email.com"
}
```
- **Response Example (Success):** 
- **Status Code:**  `200` OK
```json
{
    "detail": "User info updated successfully."
}
```
- **Response Example (error):** 
- **Status Code:**  `400` Bad Request
```json
{
    "username": [
        "A user with that username already exists."
    ]
}
```
```json
{
    "non_field_errors": [
        "Email is already in use."
    ]
}
```

#### 10. Delete my account by user auth token 
- **URL:**  [http://127.0.0.1:8000/api/user/delete-my-account/]() 
- **Method:**  DELETE 
- **Authorization:**  Required (Bearer Token) 
- **Parameters:** 
- None 
- **Request Example:** 
- No additional parameters required. 
- **Response Example (Success):** 
- **Status Code:**  `204` No Content 
```json
{
    "detail": "User account deleted successfully"
}
```
- **Response Example (error):** 
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

#### 11. Delete user account by admin  
- **URL:**  [http://127.0.0.1:8000/api/user/delete/<id>/]() 
- **Method:**  DELETE 
- **Authorization:**  Required (Bearer Token Admin account only) 
- **Parameters:** 
- None (but the user id in the link)
- **Request Example:** 
- No additional parameters required. 
- **Response Example (Success):** 
- **Status Code:**  `204` No Content 
```json
{
    "detail": "User deleted successfully"
}
```
- **Response Example (error):** 
- **Status Code:**  `401` Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```
- **Response Example (error):** 
- **Status Code:**  `404` Not Found
```json
{
    "error": "User does not exist"
}
```

#### 12. Get Staff members list 
- **URL:**  [http://127.0.0.1:8000/api/users/staff/]() 
- **Method:**  GET 
- **Authorization:**  Required (Bearer Token Admin account only) 
- **Parameters:** 
- None 
- **Request Example:** 
- No additional parameters required. 
- **Response Example (Success):** 
- **Status Code:**  `200` OK
```json
[
    {
        "id": 3,
        "first_name": "Ali",
        "last_name": "Sliman"
    },
    {
        "id": 4,
        "first_name": "Ali",
        "last_name": "Qasem"
    },
]
```
- **Response Example (error):** 
- **Status Code:**  `401` Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```


