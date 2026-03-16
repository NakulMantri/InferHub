from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class InferenceLog(Base):
    __tablename__ = "inference_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    model_used = Column(String, index=True)
    prompt_length = Column(Integer)
    response_length = Column(Integer)
    latency_ms = Column(Float)
