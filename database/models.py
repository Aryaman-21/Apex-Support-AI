"""
SQLAlchemy ORM Models for Student Support Agent.
Includes Student, FeeRecord, Scholarship, SupportTicket, LongTermMemory, and AgentTrace.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(32), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    programme = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    academic_year = Column(String(30), nullable=False)
    status = Column(String(30), default="Active")
    phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    fee_records = relationship("FeeRecord", back_populates="student", cascade="all, delete-orphan")
    scholarships = relationship("Scholarship", back_populates="student", cascade="all, delete-orphan")
    tickets = relationship("SupportTicket", back_populates="student", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "programme": self.programme,
            "department": self.department,
            "academic_year": self.academic_year,
            "status": self.status,
            "phone": self.phone,
        }


class FeeRecord(Base):
    __tablename__ = "fee_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(32), ForeignKey("students.student_id"), nullable=False, index=True)
    total_fees = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False, default=0.0)
    outstanding_balance = Column(Float, nullable=False, default=0.0)
    payment_status = Column(String(30), nullable=False)  # Paid, Partial, Pending, Overdue
    due_date = Column(String(30), nullable=False)
    last_payment_date = Column(String(30), nullable=True)
    currency = Column(String(10), default="INR")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="fee_records")

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "total_fees": self.total_fees,
            "amount_paid": self.amount_paid,
            "outstanding_balance": self.outstanding_balance,
            "payment_status": self.payment_status,
            "due_date": self.due_date,
            "last_payment_date": self.last_payment_date,
            "currency": self.currency,
        }


class Scholarship(Base):
    __tablename__ = "scholarships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(32), ForeignKey("students.student_id"), nullable=False, index=True)
    scholarship_name = Column(String(150), nullable=False)
    application_status = Column(String(50), nullable=False)  # Approved, Under Review, Pending Documents, Rejected
    award_amount = Column(Float, nullable=False, default=0.0)
    disbursement_date = Column(String(30), nullable=True)
    details = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="scholarships")

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "scholarship_name": self.scholarship_name,
            "application_status": self.application_status,
            "award_amount": self.award_amount,
            "disbursement_date": self.disbursement_date,
            "details": self.details,
        }


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    ticket_id = Column(String(32), primary_key=True, index=True)
    student_id = Column(String(32), ForeignKey("students.student_id"), nullable=False, index=True)
    issue_category = Column(String(60), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(30), default="Open")  # Open, In Review, Escalated, Resolved
    priority = Column(String(30), default="Medium")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="tickets")

    def to_dict(self):
        return {
            "ticket_id": self.ticket_id,
            "student_id": self.student_id,
            "issue_category": self.issue_category,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LongTermMemory(Base):
    __tablename__ = "long_term_memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(32), nullable=False, index=True)
    memory_key = Column(String(100), nullable=False)  # e.g., preferred_name, programme, study_goal
    memory_value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    source_query = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "memory_key": self.memory_key,
            "memory_value": self.memory_value,
            "confidence": self.confidence,
            "source_query": self.source_query,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    trace_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), nullable=False, index=True)
    student_id = Column(String(32), nullable=True, index=True)
    query = Column(Text, nullable=False)
    intent_decision = Column(String(64), nullable=False)
    tools_called = Column(Text, nullable=True)  # JSON serialized
    tool_results = Column(Text, nullable=True)  # JSON serialized
    retrieved_evidence = Column(Text, nullable=True)  # JSON serialized chunks
    memory_retrieved = Column(Text, nullable=True)  # JSON serialized memories
    context_selected = Column(Text, nullable=True)  # Summary of what was sent to LLM
    response = Column(Text, nullable=False)
    latency_ms = Column(Float, default=0.0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    status = Column(String(30), default="SUCCESS")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "student_id": self.student_id,
            "query": self.query,
            "intent_decision": self.intent_decision,
            "tools_called": self.tools_called,
            "tool_results": self.tool_results,
            "retrieved_evidence": self.retrieved_evidence,
            "memory_retrieved": self.memory_retrieved,
            "context_selected": self.context_selected,
            "response": self.response,
            "latency_ms": self.latency_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
