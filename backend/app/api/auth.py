from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import verify_password, create_access_token, decode_access_token, hash_password
from app.core.config import settings
from app.models.user import LoginRequest, TokenResponse, UserOut, USERS_DB

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserOut:
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    email = payload.get("sub")
    user = USERS_DB.get(email)
    if not user or not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return UserOut(**{k: v for k, v in user.items() if k != "hashed_password"})


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = USERS_DB.get(body.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": user["email"], "role": user["role"]})
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    user_out = UserOut(**{k: v for k, v in user.items() if k != "hashed_password"})
    return TokenResponse(access_token=token, expires_in=expires_in, user=user_out)


@router.get("/me", response_model=UserOut)
def get_me(current_user: UserOut = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout():
    # JWT is stateless; client drops the token
    return {"message": "Logged out successfully"}
