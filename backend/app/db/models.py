"""Database Models"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, DateTime, Integer, Boolean, ForeignKey, Index, JSON, BigInteger
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    tier = Column(String(20), default="free")
    api_key_hash = Column(String(255), nullable=True)
    credits_remaining = Column(Integer, default=100)
    credits_reset_at = Column(DateTime, default=datetime.utcnow)
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    settings = Column(SQLiteJSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    messages = Column(SQLiteJSON, default=[])
    session_metadata = Column(SQLiteJSON, default={})
    project = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sessions")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    details = Column(SQLiteJSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")


class Plugin(Base):
    __tablename__ = "plugins"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    manifest = Column(SQLiteJSON, nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    rating = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    key_encrypted = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("ix_user_provider", "user_id", "provider", unique=True),)


# Indexes
Index("ix_sessions_user_created", Session.user_id, Session.created_at)
Index("ix_audit_user_created", AuditLog.user_id, AuditLog.created_at)