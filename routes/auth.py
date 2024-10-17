from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from config.database import insert_one, find_one
from utils.auth import create_access_token, verify_password, get_password_hash
from schema.auth_user import User
from config.constant import AUTH_USER_COLLECTION

router = APIRouter()


@router.post("/register")
async def register(user: User):
     
    payload = {"email": user.email}
    existing_user = await find_one(payload, AUTH_USER_COLLECTION)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    payload = {"email": user.email, "password": hashed_password}
    _id = await insert_one(payload, AUTH_USER_COLLECTION)
    return {"msg": "User registered successfully","data": _id}


@router.post("/token", include_in_schema=False)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    payload = {"email": form_data.username}
    db_user = await find_one(payload, AUTH_USER_COLLECTION)
    
    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"user": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}