from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from pymongo.errors import DuplicateKeyError

from .db import papers_col, saved_col, users_col
from .security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter()


class SignupIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def user_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name", ""),
        "email": doc["email"],
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }


@router.post("/auth/signup", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupIn):
    now = datetime.now(timezone.utc)
    doc = {
        "name": body.name,
        "email": body.email.lower(),
        "password": hash_password(body.password),
        "created_at": now,
        "updated_at": now,
    }
    try:
        result = await users_col().insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Email already registered")

    doc["_id"] = result.inserted_id
    token = create_access_token(doc["email"])
    return AuthOut(access_token=token, user=user_out(doc))


@router.post("/auth/login", response_model=AuthOut)
async def login(body: LoginIn):
    user = await users_col().find_one({"email": body.email.lower()})
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user["email"])
    return AuthOut(access_token=token, user=user_out(user))


@router.get("/auth/me")
async def me(current=Depends(get_current_user)):
    return current


@router.put("/auth/update")
async def update_user(body: UserUpdateIn, current=Depends(get_current_user)):
    update: dict = {"updated_at": datetime.now(timezone.utc)}
    if body.name is not None:
        update["name"] = body.name
    if body.email is not None:
        update["email"] = body.email.lower()
    if body.password is not None:
        update["password"] = hash_password(body.password)

    try:
        await users_col().update_one({"_id": ObjectId(current["id"])}, {"$set": update})
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = await users_col().find_one({"_id": ObjectId(current["id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    response = {"user": user_out(user)}
    if body.email is not None:
        response["access_token"] = create_access_token(user["email"])
        response["token_type"] = "bearer"
    return response


@router.delete("/auth/delete")
async def delete_user(current=Depends(get_current_user)):
    owner_id = current["id"]
    await saved_col().delete_many({"owner_id": owner_id})
    await papers_col().delete_many({"owner_id": owner_id})
    result = await users_col().delete_one({"_id": ObjectId(owner_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}
