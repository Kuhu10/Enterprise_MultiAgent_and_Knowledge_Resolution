from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from evaluation.incident_detector import detect_incident
from agents.execution_agent import ExecutionAgent
from agents.reporting_verification_agent import ReportingVerificationAgent


app = FastAPI(
    title="Multi-Agent Incident Resolution API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Multi-Agent Incident Resolution API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/analyze")
async def analyze_log(
    file: UploadFile = File(...)
):

    content = await file.read()

    log_text = content.decode(
        "utf-8",
        errors="ignore"
    )

    resolution_output = detect_incident(
        log_text,
        "INC-WEB-001"
    )

    return {
        "success": True,
        "filename": file.filename,
        "resolution": resolution_output
    }


@app.post("/execute")
def execute_action(
    resolution_output: dict
):

    execution_agent = ExecutionAgent(
        simulation_mode=True
    )

    execution_result = execution_agent.execute(
        resolution_output
    )

    return {
        "success": True,
        "execution": execution_result
    }


@app.post("/verify")
def verify_incident(
    payload: dict
):

    resolution_output = payload[
        "resolution_output"
    ]

    execution_result = payload[
        "execution_result"
    ]

    post_action_state = payload[
        "post_action_state"
    ]

    verification_agent = ReportingVerificationAgent()

    final_report = verification_agent.verify(
        execution_result,
        resolution_output,
        post_action_state
    )

    return {
        "success": True,
        "report": final_report
    }