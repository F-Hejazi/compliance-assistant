from fastapi import FastAPI
from agents.classifier import classify_intent
from agents.retriever import retrieve_documents
from agents.validator import validate_document
from agents.escalation import check_escalation
from agents.explainer import explain_steps
from agents.safety import run_safety_check

app = FastAPI()

@app.get("/")
def root():
    return {"status": "backend is running"}

# This is where the orchestrator will eventually go
@app.post("/process")
def process_request(payload: dict):
    # Placeholder pipeline
    steps = []
    steps.append("classification done")
    steps.append("retrieval done")
    steps.append("validation done")
    steps.append("escalation checked")
    steps.append("explanation generated")
    steps.append("safety checked")
    return {"message": "pipeline placeholder", "steps": steps}
