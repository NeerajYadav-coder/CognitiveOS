from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey, Table, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    profile_metadata: Mapped[dict] = mapped_column(JSONB, default={})
    cognition_preferences: Mapped[dict] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="user")
    reflections: Mapped[List["Reflection"]] = relationship("Reflection", back_populates="user")
    workspaces: Mapped[List["WorkspaceState"]] = relationship("WorkspaceState", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    session_context: Mapped[dict] = mapped_column(JSONB, default={})
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="sessions")
    interactions: Mapped[List["CognitiveInteraction"]] = relationship("CognitiveInteraction", back_populates="session")
    research_executions: Mapped[List["ResearchExecution"]] = relationship("ResearchExecution", back_populates="session")

class CognitiveInteraction(Base):
    __tablename__ = "cognitive_interactions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"))
    raw_input: Mapped[str] = mapped_column(Text)
    normalized_input: Mapped[Optional[str]] = mapped_column(Text)
    intent_output: Mapped[dict] = mapped_column(JSONB)
    cognitive_mode: Mapped[dict] = mapped_column(JSONB)
    ambiguity_score: Mapped[float] = mapped_column(Float)
    orchestration_trace: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["Session"] = relationship("Session", back_populates="interactions")
    prompt_outputs: Mapped[List["PromptOutput"]] = relationship("PromptOutput", back_populates="interaction")
    agent_executions: Mapped[List["AgentExecution"]] = relationship("AgentExecution", back_populates="interaction")
    governance_logs: Mapped[List["GovernanceLog"]] = relationship("GovernanceLog", back_populates="interaction")

class PromptOutput(Base):
    __tablename__ = "prompt_outputs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cognitive_interactions.id"))
    synthesized_prompt: Mapped[str] = mapped_column(Text)
    optimization_metadata: Mapped[dict] = mapped_column(JSONB)
    final_output: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)

    interaction: Mapped["CognitiveInteraction"] = relationship("CognitiveInteraction", back_populates="prompt_outputs")

class Reflection(Base):
    __tablename__ = "reflections"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    reflection_type: Mapped[str] = mapped_column(String(50))
    reflection_content: Mapped[dict] = mapped_column(JSONB)
    confidence: Mapped[float] = mapped_column(Float)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="reflections")

class ResearchExecution(Base):
    __tablename__ = "research_executions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"))
    research_tree: Mapped[dict] = mapped_column(JSONB)
    exploration_paths: Mapped[List[dict]] = mapped_column(JSONB)
    synthesis_state: Mapped[dict] = mapped_column(JSONB)
    execution_metadata: Mapped[dict] = mapped_column(JSONB)

    session: Mapped["Session"] = relationship("Session", back_populates="research_executions")

class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cognitive_interactions.id"))
    agent_type: Mapped[str] = mapped_column(String(100))
    execution_trace: Mapped[dict] = mapped_column(JSONB)
    confidence: Mapped[float] = mapped_column(Float)
    latency_ms: Mapped[float] = mapped_column(Float)

    interaction: Mapped["CognitiveInteraction"] = relationship("CognitiveInteraction", back_populates="agent_executions")

class WorkspaceState(Base):
    __tablename__ = "workspace_states"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    graph_layout: Mapped[dict] = mapped_column(JSONB)
    visual_state: Mapped[dict] = mapped_column(JSONB)
    semantic_filters: Mapped[List[str]] = mapped_column(JSONB)
    active_explorations: Mapped[List[str]] = mapped_column(JSONB)

    user: Mapped["User"] = relationship("User", back_populates="workspaces")

class GovernanceLog(Base):
    __tablename__ = "governance_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cognitive_interactions.id"))
    risk_scores: Mapped[dict] = mapped_column(JSONB)
    governance_actions: Mapped[List[dict]] = mapped_column(JSONB)
    transparency_metadata: Mapped[dict] = mapped_column(JSONB)

    interaction: Mapped["CognitiveInteraction"] = relationship("CognitiveInteraction", back_populates="governance_logs")
