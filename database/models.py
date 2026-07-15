# database/models.py
# ----------------------------------------------------------------------
# SQLAlchemy table definitions for Nexus-Ops incident archiving.
# Three tables: 
#   1. Incident (Overarching execution record)
#   2. AgentTrace (Thought tracks for individual swarm agents)
#   3. FeatureProposal (Phase 5 Autonomous Code Architecture Extensions)
# ----------------------------------------------------------------------

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class Incident(Base):
    """
    Stores the full record of one pipeline execution.
    One row = one `python main.py` run or dashboard analysis loop.
    """
    __tablename__ = "incidents"

    id                   = Column(Integer, primary_key=True, index=True)
    created_at           = Column(DateTime, default=datetime.utcnow)

    # Input Metadata
    issue_description    = Column(Text,    nullable=False)
    category             = Column(String(50),  default="Unknown")
    priority             = Column(Integer,     default=3)
    complexity           = Column(String(100), default="Unknown")

    # Stage 3 Swarm Outputs
    root_cause_analysis  = Column(Text,    nullable=True)
    draft_fix            = Column(Text,    nullable=True)
    audit_verdict        = Column(String(20),  default="PENDING")
    audit_reasoning      = Column(Text,    nullable=True)

    # Stage 4 Testing Verification Outputs
    tests_passed         = Column(Boolean, default=False)
    test_details         = Column(Text,    nullable=True)
    iteration_count      = Column(Integer, default=0)

    # Ragas Evaluation Scores (Stage 4A)
    ragas_faithfulness   = Column(String(10), nullable=True)  # e.g. "0.87"
    ragas_relevancy      = Column(String(10), nullable=True)

    # Final Summary Document Output
    final_report         = Column(Text,    nullable=True)

    # Relational connections to child tables (Cascades deletes automatically)
    traces = relationship("AgentTrace", back_populates="incident", cascade="all, delete-orphan")
    proposals = relationship("FeatureProposal", back_populates="incident", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Incident id={self.id} category={self.category} passed={self.tests_passed}>"


class AgentTrace(Base):
    """
    Stores the individual intermediate analytical thoughts for a single agent.
    Multiple rows per Incident — one per agent per iteration run loop.
    """
    __tablename__ = "agent_traces"

    id           = Column(Integer, primary_key=True, index=True)
    incident_id  = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    agent_role   = Column(String(100), nullable=False)   # e.g. "Senior Code Researcher"
    stage        = Column(String(50),  nullable=False)   # e.g. "Stage 3 - Diagnosis"
    output_text  = Column(Text,        nullable=True)
    iteration    = Column(Integer,     default=1)        # Which retry self-healing pass

    incident = relationship("Incident", back_populates="traces")

    def __repr__(self):
        return f"<AgentTrace id={self.id} agent={self.agent_role} iteration={self.iteration}>"


class FeatureProposal(Base):
    """
    PHASE 5 EXTENSION:
    Stores autonomous AI architect code feature suggestions and modular engineering upgrades
    discovered during the codebase structural analysis profile scanning pass.
    """
    __tablename__ = "feature_proposals"

    id           = Column(Integer, primary_key=True, index=True)
    incident_id  = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    title        = Column(String(200), nullable=False)   # e.g., "Add Redis Cache Layer"
    target_file  = Column(String(200), nullable=True)    # Specific codebase module requiring structural care
    effort       = Column(String(20),  default="Medium") # Low / Medium / High
    description  = Column(Text,        nullable=False)   # Rationale + Blueprint generated scaffolding
    status       = Column(String(20),  default="pending")# pending / approved / dismissed

    incident = relationship("Incident", back_populates="proposals")

    def __repr__(self):
        return f"<FeatureProposal id={self.id} title={self.title} status={self.status}>"