from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class FirebaseAuthRequest(BaseModel):
    id_token: str


class AuthUser(BaseModel):
    id: str
    name: str
    email: EmailStr


class AuthPayload(BaseModel):
    user: AuthUser
    token: str
