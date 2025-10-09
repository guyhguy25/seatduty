from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupOut(GroupBase):
    id: int
    creator_id: int

    class Config:
        from_attributes = True


class GroupMemberOut(BaseModel):
    id: int
    group_id: int
    user_id: int
    is_admin: bool
    user_name: Optional[str] = None

    class Config:
        from_attributes = True


class InvitationCreate(BaseModel):
    expires_in_minutes: Optional[int] = Field(default=60, ge=1, le=60 * 24 * 7)


class InvitationOut(BaseModel):
    id: int
    group_id: int
    token: str
    is_revoked: bool
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClubOut(BaseModel):
    id: int
    name: str
    external_id: str
    logo: Optional[str] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True
