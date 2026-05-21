from database import SessionLocal, Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
import hashlib

# Experiment table - stores experiment settings
class Experiment(Base):
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)          # Experiment name
    prompt_name = Column(String, nullable=False)   # Which prompt are we testing?
    variant_a_version = Column(Integer)            # Version A (e.g. v1)
    variant_b_version = Column(Integer)            # Version B (e.g. v2)
    traffic_split = Column(Float, default=0.5)     # 0.5 = 50/50 split
    status = Column(String, default="running")     # running / completed / stopped
    created_at = Column(DateTime, default=datetime.utcnow)

# Result table - stores each test result
class ExperimentResult(Base):
    __tablename__ = "experiment_results"
    
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer)
    user_id = Column(String)         # Which user got this result
    variant = Column(String)         # "A" or "B"
    prompt_version = Column(Integer) # Which version was used
    input_text = Column(Text)        # The question that was asked
    output_text = Column(Text)       # The AI's answer
    quality_score = Column(Float)    # Score (1-5)
    latency_ms = Column(Float)       # How long did it take? (milliseconds)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(SessionLocal().bind)
print("✅ Experiment tables ready!")


def create_experiment(name: str, prompt_name: str, variant_a: int, variant_b: int, traffic_split: float = 0.5):
    """Create a new experiment"""
    db = SessionLocal()
    
    experiment = Experiment(
        name=name,
        prompt_name=prompt_name,
        variant_a_version=variant_a,
        variant_b_version=variant_b,
        traffic_split=traffic_split
    )
    
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    print(f"✅ Experiment '{name}' created! (v{variant_a} vs v{variant_b}, {int(traffic_split*100)}/{int((1-traffic_split)*100)} split)")
    db.close()
    return experiment.id


def assign_variant(experiment_id: int, user_id: str) -> str:
    """
    Decide which variant a user gets.
    Same user always gets the same variant (consistent experience).
    """
    db = SessionLocal()
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    db.close()
    
    # Use a hash of user_id to consistently assign the same variant
    hash_value = int(hashlib.md5(f"{user_id}{experiment_id}".encode()).hexdigest(), 16)
    ratio = hash_value % 100 / 100
    
    if ratio < experiment.traffic_split:
        return "A"
    else:
        return "B"


def log_result(experiment_id: int, user_id: str, variant: str, 
               prompt_version: int, input_text: str, output_text: str,
               quality_score: float, latency_ms: float):
    """Save the result of one experiment trial"""
    db = SessionLocal()
    
    result = ExperimentResult(
        experiment_id=experiment_id,
        user_id=user_id,
        variant=variant,
        prompt_version=prompt_version,
        input_text=input_text,
        output_text=output_text,
        quality_score=quality_score,
        latency_ms=latency_ms
    )
    
    db.add(result)
    db.commit()
    print(f"📊 Logged result for user '{user_id}' → Variant {variant} | Score: {quality_score}/5")
    db.close()