from database import SessionLocal, Prompt
from datetime import datetime

def create_prompt(name: str, system_prompt: str, commit_message: str = "Initial version"):
    """Save a new prompt to the database"""
    db = SessionLocal()
    
    # Check if this prompt name already exists
    existing = db.query(Prompt).filter(Prompt.name == name).all()
    new_version = len(existing) + 1
    
    # Deactivate all previous versions
    for p in existing:
        p.is_active = 0
    
    # Create new version
    new_prompt = Prompt(
        name=name,
        version=new_version,
        system_prompt=system_prompt,
        commit_message=commit_message,
        is_active=1
    )
    
    db.add(new_prompt)
    db.commit()
    print(f"✅ Saved '{name}' as version {new_version}")
    db.close()

def get_active_prompt(name: str):
    """Get the currently active version of a prompt"""
    db = SessionLocal()
    prompt = db.query(Prompt).filter(
        Prompt.name == name,
        Prompt.is_active == 1
    ).first()
    db.close()
    return prompt

def list_versions(name: str):
    """Show all versions of a prompt"""
    db = SessionLocal()
    versions = db.query(Prompt).filter(Prompt.name == name).all()
    db.close()
    
    print(f"\n📋 All versions of '{name}':")
    for v in versions:
        status = "✅ ACTIVE" if v.is_active else "  archived"
        print(f"  v{v.version} | {status} | {v.commit_message}")

def rollback(name: str, version: int):
    """Roll back to a specific version"""
    db = SessionLocal()
    
    # Deactivate all versions
    all_versions = db.query(Prompt).filter(Prompt.name == name).all()
    for p in all_versions:
        p.is_active = 0
    
    # Activate the requested version
    target = db.query(Prompt).filter(
        Prompt.name == name,
        Prompt.version == version
    ).first()
    
    if target:
        target.is_active = 1
        db.commit()
        print(f"✅ Rolled back '{name}' to version {version}")
    else:
        print(f"❌ Version {version} not found")
    
    db.close()