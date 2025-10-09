from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import requests
from app.core.database import get_db
from app.core.deps import get_current_user
from app.users.models import User
from app.groups.models import Group, GroupMember, InvitationToken, Club
from app.groups.schemas import (
    GroupCreate, GroupOut, GroupMemberOut,
    InvitationCreate, InvitationOut, ClubOut,
)

router = APIRouter(prefix="/groups", tags=["groups"])

# Clubs: assign a club to each group creation from provided standings source
STANDINGS_URL = (
    "https://webws.365scores.com/web/standings/?appTypeId=5&langId=2&timezoneName=Asia/Jerusalem&userCountryId=6&competitions=42&live=false&withSeasonsFilter=true"
)


def upsert_club(db: Session, name: str, external_id: str, logo: str | None, country: str | None) -> Club:
    existing = db.query(Club).filter(Club.external_id == external_id).first()
    if existing:
        if (existing.logo != logo) or (existing.name != name) or (existing.country != country):
            existing.name = name
            existing.logo = logo
            existing.country = country
            db.add(existing)
            db.commit()
            db.refresh(existing)
        return existing
    club = Club(name=name, external_id=external_id, logo=logo, country=country)
    db.add(club)
    db.commit()
    db.refresh(club)
    return club


@router.get("/clubs", response_model=list[ClubOut])
def fetch_clubs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch clubs from standings source and upsert locally; return all stored clubs."""
    try:
        r = requests.get(STANDINGS_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
        standings = data.get("standings", [])
        # Example structure: standings[0]["rows"][i]["competitor"{"id","name","country",...}]
        for table in standings:
            rows = table.get("rows", [])
            for row in rows:
                comp = row.get("competitor") or {}
                external_id = str(comp.get("id")) if comp.get("id") is not None else None
                name = comp.get("name")
                logo = comp.get("imageUrl") or comp.get("image")
                country = (comp.get("country") or {}).get("name") if isinstance(comp.get("country"), dict) else comp.get("country")
                if external_id and name:
                    upsert_club(db, name=name, external_id=external_id, logo=logo, country=country)
    except Exception:
        # If remote fails, return what we already have
        pass

    clubs = db.query(Club).all()
    return clubs


@router.post("", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a group. Limit: max 2 groups created per user."""
    created_count = db.query(Group).filter(Group.creator_id == current_user.id).count()
    if created_count >= 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group creation limit reached (2)")

    group = Group(name=payload.name, description=payload.description, creator_id=current_user.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    # Add creator as admin member
    membership = GroupMember(group_id=group.id, user_id=current_user.id, is_admin=True)
    db.add(membership)
    db.commit()

    return group


@router.get("", response_model=list[GroupOut])
def list_my_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List groups where current user is a member."""
    group_ids = [gm.group_id for gm in db.query(GroupMember).filter(GroupMember.user_id == current_user.id).all()]
    if not group_ids:
        return []
    groups = db.query(Group).filter(Group.id.in_(group_ids)).all()
    return groups


@router.get("/{group_id}", response_model=GroupOut)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id,
    ).first()
    if member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")
    return group


@router.post("/{group_id}/admins/{user_id}", response_model=GroupMemberOut)
def add_admin(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add admin to group. Only creator or existing admins can promote."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Check permissions
    requester_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id,
    ).first()
    if requester_member is None or not requester_member.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
    ).first()
    if member is None:
        member = GroupMember(group_id=group_id, user_id=user_id, is_admin=True)
        db.add(member)
    else:
        member.is_admin = True
        db.add(member)
    db.commit()
    db.refresh(member)
    return member


# Invitations by token (no email)

@router.post("/{group_id}/invites", response_model=InvitationOut)
def create_invite_token(
    group_id: int,
    payload: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    requester_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id,
    ).first()
    if requester_member is None or not requester_member.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    token_value = secrets.token_urlsafe(16)
    expires_at = None
    if payload.expires_in_minutes:
        expires_at = datetime.utcnow() + timedelta(minutes=payload.expires_in_minutes)

    invite = InvitationToken(
        group_id=group_id,
        token=token_value,
        is_revoked=False,
        expires_at=expires_at,
        created_by_user_id=current_user.id,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.post("/join/{token}", response_model=GroupMemberOut)
def join_group_by_token(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invite = db.query(InvitationToken).filter(InvitationToken.token == token).first()
    if invite is None or invite.is_revoked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invite token")
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite token expired")

    # Check if user is already a member
    existing = db.query(GroupMember).filter(
        GroupMember.group_id == invite.group_id,
        GroupMember.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already a member of this group")

    member = GroupMember(group_id=invite.group_id, user_id=current_user.id, is_admin=False)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.post("/invites/{token}/revoke", response_model=InvitationOut)
def revoke_invite(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invite = db.query(InvitationToken).filter(InvitationToken.token == token).first()
    if invite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")

    requester_member = db.query(GroupMember).filter(
        GroupMember.group_id == invite.group_id,
        GroupMember.user_id == current_user.id,
    ).first()
    if requester_member is None or not requester_member.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    invite.is_revoked = True
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.delete("/{group_id}")
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete group. Only creator or admin can delete."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Check if user is creator
    if group.creator_id == current_user.id:
        # Creator can always delete
        pass
    else:
        # Check if user is admin
        member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
            GroupMember.is_admin == True,
        ).first()
        if member is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only creator or admin can delete group")

    # Delete all related data
    db.query(InvitationToken).filter(InvitationToken.group_id == group_id).delete()
    db.query(GroupMember).filter(GroupMember.group_id == group_id).delete()
    db.delete(group)
    db.commit()
    
    return {"message": "Group deleted successfully"}


@router.get("/{group_id}/members", response_model=list[GroupMemberOut])
def get_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get group members. Only group members can see the list."""
    # Check if user is a member
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id,
    ).first()
    if member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this group")

    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    # Map user name into the schema field
    result: list[GroupMemberOut] = []
    for m in members:
        result.append(GroupMemberOut(
            id=m.id,
            group_id=m.group_id,
            user_id=m.user_id,
            is_admin=m.is_admin,
            user_name=(m.user.name if getattr(m, "user", None) else None),
        ))
    return result


@router.delete("/{group_id}/members/{user_id}")
def remove_member(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove member from group. Only admins can remove members."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Check if requester is admin
    requester_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id,
        GroupMember.is_admin == True,
    ).first()
    if requester_member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    # Prevent removing creator
    if group.creator_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove group creator")

    # Prevent self-removal (use leave endpoint instead)
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Use leave endpoint to remove yourself")

    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
    ).first()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not a member of this group")

    db.delete(member)
    db.commit()
    return {"message": "Member removed successfully"}


@router.delete("/{group_id}/leave")
def leave_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Leave group. Members can leave themselves."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Prevent creator from leaving (they should delete the group instead)
    if group.creator_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Creator cannot leave group. Delete the group instead.")

    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id,
    ).first()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You are not a member of this group")

    db.delete(member)
    db.commit()
    return {"message": "Left group successfully"}
