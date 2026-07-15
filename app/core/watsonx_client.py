"""
watsonx_client.py
─────────────────
Thin wrapper around IBM watsonx.ai SDK.
Handles authentication, model initialisation, and inference calls.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# ── Load .env from the project root (course_simplifier/) ───────────
# Resolve relative to this file so it works regardless of CWD:
#   parents[0] = core/
#   parents[1] = app/
#   parents[2] = course_simplifier/   ← .env lives here
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)

# ── SDK imports (ibm-watsonx-ai ≥ 1.0) ───────────────────────────
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from app.core.agent_instructions import build_system_prompt


def _get_model() -> ModelInference:
    """
    Create and return a configured ModelInference instance.

    Credentials are read inside this function (not at import time) so
    that os.environ always reflects the fully-loaded .env values,
    even when the module was imported before load_dotenv() ran.
    """
    api_key    = os.environ.get("IBM_API_KEY", "")
    project_id = os.environ.get("IBM_PROJECT_ID", "")
    url        = os.environ.get("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    model_id   = os.environ.get("GRANITE_MODEL_ID", "mistralai/mistral-small-3-1-24b-instruct-2503")
    max_tokens = int(os.environ.get("MAX_NEW_TOKENS", 1024))
    temperature= float(os.environ.get("TEMPERATURE", 0.7))

    credentials = Credentials(api_key=api_key, url=url)
    params = {
        GenParams.MAX_NEW_TOKENS: max_tokens,
        GenParams.TEMPERATURE:    temperature,
        GenParams.TOP_P:          0.9,
        "max_tokens": max_tokens,   # chat API uses max_tokens
    }
    return ModelInference(
        model_id=model_id,
        credentials=credentials,
        project_id=project_id,
        params=params,
    )


def generate_response(
    user_message: str,
    proficiency: str = "Beginner",
    subject: str = "General / Other",
    rag_context: Optional[str] = None,
    conversation_history: Optional[list] = None,
) -> str:
    """
    Generate a response using the watsonx.ai Chat API.

    Parameters
    ----------
    user_message        : The learner's current question / request.
    proficiency         : 'Beginner' | 'Intermediate' | 'Expert'
    subject             : Subject area string (see agent_instructions.py)
    rag_context         : Retrieved document text chunks (optional).
    conversation_history: List of {"role": "user"|"assistant", "content": str}

    Returns
    -------
    The model's text response as a string.
    """
    system_prompt = build_system_prompt(proficiency, subject)

    # ── Inject RAG context into the system prompt if available ────
    if rag_context:
        from app.core.agent_instructions import RAG_CONTEXT_TEMPLATE
        system_prompt += "\n\n" + RAG_CONTEXT_TEMPLATE.format(context=rag_context)

    # ── Build messages list for the Chat API ─────────────────────
    messages = [{"role": "system", "content": system_prompt}]

    # Inject last 8 conversation turns (4 exchanges)
    if conversation_history:
        for turn in conversation_history[-8:]:
            role = turn.get("role", "user")
            # Chat API expects "assistant" not "bot"
            if role not in ("user", "assistant"):
                role = "user"
            messages.append({"role": role, "content": turn.get("content", "")})

    # Append the current user message
    messages.append({"role": "user", "content": user_message})

    try:
        model    = _get_model()
        response = model.chat(messages=messages)
        # Extract text from the chat response structure
        text = (
            response.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
        )
        return text.strip() if text else "I'm sorry, I couldn't generate a response. Please try again."
    except Exception as exc:                           # noqa: BLE001
        error_msg = str(exc)
        if "authentication" in error_msg.lower() or "401" in error_msg:
            return "⚠️ Authentication error: Please check your IBM_API_KEY in the .env file."
        if "project" in error_msg.lower() or "404" in error_msg:
            return "⚠️ Project not found: Please verify your IBM_PROJECT_ID in the .env file."
        return f"⚠️ An error occurred while contacting the AI service: {error_msg}"


def check_credentials() -> dict:
    """
    Quick health-check for watsonx credentials.
    Returns {"ok": bool, "message": str}.
    """
    api_key    = os.environ.get("IBM_API_KEY", "")
    project_id = os.environ.get("IBM_PROJECT_ID", "")
    model_id   = os.environ.get("GRANITE_MODEL_ID", "mistralai/mistral-small-3-1-24b-instruct-2503")

    if not api_key or api_key == "your_ibm_cloud_api_key_here":
        return {"ok": False, "message": "IBM_API_KEY is not configured."}
    if not project_id or project_id == "your_watsonx_project_id_here":
        return {"ok": False, "message": "IBM_PROJECT_ID is not configured."}
    try:
        model = _get_model()
        response = model.chat(messages=[
            {"role": "system",  "content": "You are a test assistant."},
            {"role": "user",    "content": "Say OK."},
        ])
        text = (
            response.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
        )
        return {"ok": True, "message": f"Connected to {model_id}. Response: {text.strip()[:40]}"}
    except Exception as exc:                           # noqa: BLE001
        return {"ok": False, "message": str(exc)}
