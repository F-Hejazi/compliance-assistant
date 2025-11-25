from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.services.search_service import search_utterances
from backend.services.openai_service import classify_intent_with_openai
from backend.services.runbook_evaluator import evaluate_rules
from backend.services.foundry_agent import call_foundry_agent

from backend.agents.classifier import classify_intent
from backend.agents.retriever import retrieve_documents
from backend.agents.validator import validate_document
from backend.agents.escalation import check_escalation
from backend.agents.explainer import explain_steps
from backend.agents.safety import run_safety_check

app = FastAPI(title="Compliance Assistant API")

# CORS (frontend -> backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for hackathon / dev only
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "backend is running"}

# This is where the orchestrator will eventually go
@app.post("/process")
def process_request(payload: dict):
    
    # Switch between demo mode and full pipeline
    DEMO_MODE = True   # set to False once the full pipeline is ready

    # Extract user text
    text = payload.get("text", "")

    if DEMO_MODE:
        # ---------------------------------------------------------
        # Simplified Foundry-agent demo path (used for the hackathon)
        # ---------------------------------------------------------
        agent_response = call_foundry_agent(text)
        return {
            "mode": "demo_foundry_agent",
            "input": text,
            "final_output": agent_response,
        }

    # =============================================================
    # Full pipeline
    # =============================================================
    
    # ---------------------
    # Step 1: Classification
    # ---------------------
    raw_intent = classify_intent(text)

    # normalize to string if dict is returned
    if isinstance(raw_intent, dict):
        intent = raw_intent.get("intent", "")
    else:
        intent = raw_intent

    # Ensure intent is always a string
    intent = str(intent)

    # ---------------------
    # Step 2: Azure Search Retrieval
    # ---------------------
    raw_docs = retrieve_documents(intent)

    # normalize to list
    if isinstance(raw_docs, dict):
        docs = raw_docs.get("docs", [])
    else:
        docs = raw_docs or []

    # ---------------------
    # Step 3: Runbook evaluation
    # ---------------------
    context = {
        "intent": intent,
        "docs": docs
    }
    runbook_result = evaluate_rules(context)

    # ---------------------
    # Step 4: Validation
    # ---------------------
    validation_data = validate_document(intent, docs)

    # if the validator returns unexpected formats, normalize:
    if isinstance(validation_data, bool):
        validation = {"checklist_pass": validation_data}
    else:
        validation = validation_data or {}

    # ---------------------
    # Step 5: Escalation
    # ---------------------
    escalation = check_escalation(intent, docs)

    # normalize escalation
    if not isinstance(escalation, bool):
        escalation = False

    # ---------------------
    # Step 6: Explanation
    # ---------------------
    explanation = explain_steps(
        intent=intent,
        docs=docs,
        validation=validation,
        escalation=escalation
    )

    if explanation is None:
        explanation = "No explanation available."

    # ---------------------
    # Step 7: Safety check
    # ---------------------
    safe_output = run_safety_check(explanation)

    return {
        "intent": intent,
        "retrieved_docs": docs,
        "runbook_result": runbook_result,
        "validation": validation,
        "escalation": escalation,
        "explanation": explanation,
        "final_output": safe_output
    }
