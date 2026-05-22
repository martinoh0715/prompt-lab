from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prompt_registry import create_prompt, get_active_prompt, list_versions, rollback
from experiment import create_experiment, assign_variant, log_result
from analyzer import analyze_experiment, run_live_test
from database import SessionLocal
from experiment import Experiment
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PromptLab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://prompt-lab-ui.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request models ---
class CreatePromptRequest(BaseModel):
    name: str
    system_prompt: str
    commit_message: str = "New version"

class CreateExperimentRequest(BaseModel):
    name: str
    prompt_name: str
    variant_a_version: int
    variant_b_version: int
    traffic_split: float = 0.5

class RunTestRequest(BaseModel):
    experiment_id: int
    user_id: str
    input_text: str

# --- Prompt endpoints ---
@app.post("/prompts")
def api_create_prompt(request: CreatePromptRequest):
    create_prompt(request.name, request.system_prompt, request.commit_message)
    return {"message": f"✅ Prompt '{request.name}' saved successfully"}

@app.get("/prompts/{name}/versions")
def api_list_versions(name: str):
    db = SessionLocal()
    from database import Prompt
    versions = db.query(Prompt).filter(Prompt.name == name).all()
    db.close()
    if not versions:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return [
        {
            "version": v.version,
            "system_prompt": v.system_prompt,
            "commit_message": v.commit_message,
            "is_active": bool(v.is_active),
            "created_at": v.created_at
        }
        for v in versions
    ]

@app.get("/prompts")
def api_list_prompts():
    db = SessionLocal()
    from database import Prompt
    names = db.query(Prompt.name).distinct().all()
    db.close()
    return [n[0] for n in names]

@app.delete("/prompts/{name}")
def api_delete_prompt_all(name: str):
    db = SessionLocal()
    from database import Prompt
    versions = db.query(Prompt).filter(Prompt.name == name).all()
    if not versions:
        db.close()
        raise HTTPException(status_code=404, detail="Prompt not found")
    for v in versions:
        db.delete(v)
    db.commit()
    db.close()
    return {"message": f"✅ Deleted all versions of '{name}'"}

@app.post("/prompts/{name}/rollback/{version}")
def api_rollback(name: str, version: int):
    rollback(name, version)
    return {"message": f"✅ Rolled back '{name}' to version {version}"}

@app.delete("/prompts/{name}/{version}")
def api_delete_prompt(name: str, version: int):
    db = SessionLocal()
    from database import Prompt
    target = db.query(Prompt).filter(
        Prompt.name == name,
        Prompt.version == version
    ).first()
    if not target:
        db.close()
        raise HTTPException(status_code=404, detail="Version not found")
    if target.is_active:
        db.close()
        raise HTTPException(status_code=400, detail="Cannot delete the active version. Activate another version first.")
    db.delete(target)
    db.commit()
    db.close()
    return {"message": f"✅ Deleted '{name}' v{version}"}

# --- Experiment endpoints ---
@app.post("/experiments")
def api_create_experiment(request: CreateExperimentRequest):
    experiment_id = create_experiment(
        request.name,
        request.prompt_name,
        request.variant_a_version,
        request.variant_b_version,
        request.traffic_split
    )
    return {"message": "✅ Experiment created", "experiment_id": experiment_id}

@app.get("/experiments")
def api_list_experiments():
    db = SessionLocal()
    experiments = db.query(Experiment).all()
    db.close()
    return [
        {
            "id": e.id,
            "name": e.name,
            "prompt_name": e.prompt_name,
            "variant_a_version": e.variant_a_version,
            "variant_b_version": e.variant_b_version,
            "status": e.status,
            "created_at": e.created_at
        }
        for e in experiments
    ]

@app.delete("/experiments/{experiment_id}")
def api_delete_experiment(experiment_id: int):
    from experiment import ExperimentResult
    db = SessionLocal()
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        db.close()
        raise HTTPException(status_code=404, detail="Experiment not found")
    db.query(ExperimentResult).filter(ExperimentResult.experiment_id == experiment_id).delete()
    db.delete(experiment)
    db.commit()
    db.close()
    return {"message": f"✅ Deleted experiment #{experiment_id}"}

@app.post("/experiments/{experiment_id}/test")
def api_run_test(experiment_id: int, request: RunTestRequest):
    db = SessionLocal()
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    db.close()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    variant = assign_variant(experiment_id, request.user_id)
    if variant == "A":
        prompt_version = experiment.variant_a_version
    else:
        prompt_version = experiment.variant_b_version
    rollback(experiment.prompt_name, prompt_version)
    prompt = get_active_prompt(experiment.prompt_name)
    run_live_test(
        experiment_id,
        request.user_id,
        request.input_text,
        prompt.system_prompt,
        variant,
        prompt_version
    )
    return {"message": f"✅ Test completed for {request.user_id} → Variant {variant}"}

@app.get("/experiments/{experiment_id}/results")
def api_get_results(experiment_id: int):
    from experiment import ExperimentResult
    import statistics
    db = SessionLocal()
    results = db.query(ExperimentResult).filter(
        ExperimentResult.experiment_id == experiment_id
    ).all()
    db.close()
    if not results:
        raise HTTPException(status_code=404, detail="No results found")
    variant_a = [r.quality_score for r in results if r.variant == "A"]
    variant_b = [r.quality_score for r in results if r.variant == "B"]
    avg_a = statistics.mean(variant_a) if variant_a else 0
    avg_b = statistics.mean(variant_b) if variant_b else 0
    difference = abs(avg_a - avg_b)
    if difference < 0.2:
        winner = "No clear winner yet"
    elif avg_a > avg_b:
        winner = "Variant A"
    else:
        winner = "Variant B"
    return {
        "experiment_id": experiment_id,
        "variant_a": {"count": len(variant_a), "average_score": round(avg_a, 2)},
        "variant_b": {"count": len(variant_b), "average_score": round(avg_b, 2)},
        "winner": winner
    }