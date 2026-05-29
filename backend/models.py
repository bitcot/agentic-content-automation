from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime
from database import Base

class ContentLog(Base):
    __tablename__ = "content_logs"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    icp_score = Column(Float)
    platform = Column(String, index=True) # LinkedIn, X, Blog, Newsletter
    content = Column(Text)
    status = Column(String, default="draft") # draft, pending_review, published, rejected
    needs_human_check = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    parent_id = Column(Integer, nullable=True) # For versioning
    version = Column(Integer, default=1)

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, index=True) # Links to ContentLog.id
    impressions = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    recorded_at = Column(DateTime, default=datetime.utcnow)

class BrandContext(Base):
    """
    Memory layer for storing learnings and brand context
    """
    __tablename__ = "brand_context"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True) # e.g., "target_audience", "avoid_phrases"
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
