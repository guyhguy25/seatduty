from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    club_id: Optional[int] = None


class GroupOut(GroupBase):
    id: int
    creator_id: int
    club_id: Optional[int] = None
    club: Optional['ClubOut'] = None

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
    country_id: Optional[str] = None
    competition_id: Optional[str] = None
    competition_name: Optional[str] = None
    symbolic_name: Optional[str] = None
    name_for_url: Optional[str] = None
    popularity_rank: Optional[int] = None
    color: Optional[str] = None
    away_color: Optional[str] = None

    class Config:
        from_attributes = True


class CountryOut(BaseModel):
    id: int
    name: str
    has_league: bool = False


class CompetitionOut(BaseModel):
    id: int
    name: str
    image_path: Optional[str] = None
    country_id: Optional[int] = None
    current_season_num: Optional[int] = None
    current_stage_num: Optional[int] = None


class TeamOut(BaseModel):
    id: int
    name: str
    image_url: Optional[str] = None
    country_name: Optional[str] = None
    country_id: Optional[int] = None
    symbolic_name: Optional[str] = None
    name_for_url: Optional[str] = None
    popularity_rank: Optional[int] = None
    color: Optional[str] = None
    away_color: Optional[str] = None


class UpdateGroupClub(BaseModel):
    club_id: Optional[int] = None
