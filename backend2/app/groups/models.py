from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    UniqueConstraint,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Group(Base):
    __tablename__ = "groups"
    __table_args__ = (
        UniqueConstraint("name", name="uq_groups_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User")


class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    # Relationship to access the user entity
    user = relationship("User")


class InvitationToken(Base):
    __tablename__ = "invitation_tokens"
    __table_args__ = (
        UniqueConstraint("token", name="uq_invitation_token"),
    )

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    token = Column(String(255), nullable=False, index=True)
    is_revoked = Column(Boolean, nullable=False, default=False)
    expires_at = Column(DateTime, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Club(Base):
    __tablename__ = "clubs"
    __table_args__ = (
        UniqueConstraint("external_id", name="uq_clubs_external_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    external_id = Column(String(255), nullable=False, index=True)
    logo = Column(Text, nullable=True)
    country = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
