import logging
import os
import secrets
from typing import Any, Literal

import httpx
from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, Header, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from src.router.graph import GRAPH

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ecommerce Router API",
    version="1.0.0",
    description=(
        "API que enruta mensajes de un chat de ecommerce hacia una de tres rutas: "
        "preventa, postventa o generica."
    ),
)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class HealthResponse(BaseModel):
    ok: bool = Field(description="Indica si la API está disponible.", examples=[True])
    modelo: str = Field(description="Modelo configurado para el router.", examples=["gemini-3.5-flash-lite"])


class ChatRequest(BaseModel):
    user_id: str = Field(
        min_length=1,
        description="Identificador del usuario; también se usa como thread_id de memoria.",
        examples=["usuario-123"],
    )
    texto: str = Field(
        min_length=1,
        description="Mensaje que se desea enrutar.",
        examples=["¿Tienen la polera azul en talla M?"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "usuario-123",
                "texto": "¿Tienen la polera azul en talla M?",
            }
        }
    }


class ChatResponse(BaseModel):
    ruta: Literal["preventa", "postventa", "generica"] = Field(
        description="Ruta elegida por el router.",
        examples=["preventa"],
    )
    motivo: str = Field(
        description="Explicación breve de por qué se eligió la ruta.",
        examples=["Consulta sobre un producto antes de comprar."],
    )
    respuesta: str = Field(
        description="Respuesta del agente destino.",
        examples=["Soy el agente de preventa. Recibí: ..."],
    )


class ErrorResponse(BaseModel):
    detail: str = Field(description="Descripción segura del error.", examples=["El modelo no pudo procesar la solicitud."])


def require_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    configured_key = os.getenv("API_KEY", "")
    if not configured_key or not api_key or not secrets.compare_digest(api_key, configured_key):
        raise HTTPException(status_code=401, detail="Falta una clave API válida en X-API-Key")
    return api_key


@app.get("/health", tags=["salud"], response_model=HealthResponse, summary="Comprobar salud de la API")
def health() -> HealthResponse:
    return HealthResponse(ok=True, modelo=os.getenv("MODELO", "gemini-3.5-flash-lite"))


@app.post(
    "/chat",
    tags=["chat"],
    response_model=ChatResponse,
    summary="Enrutar un mensaje del ecommerce",
    description="Usa el grafo router y conserva la memoria asociada al `user_id`.",
    responses={
        200: {"description": "Mensaje enrutado correctamente.", "model": ChatResponse},
        401: {"description": "La cabecera X-API-Key falta o no es válida.", "model": ErrorResponse},
        422: {"description": "El body no cumple el esquema de ChatRequest.", "model": ErrorResponse},
        502: {"description": "El modelo no pudo procesar la solicitud.", "model": ErrorResponse},
    },
)
def chat(payload: ChatRequest, _: str = Depends(require_api_key)) -> ChatResponse:
    try:
        result = GRAPH.invoke(
            {"mensaje": payload.texto},
            {"configurable": {"thread_id": payload.user_id}},
        )
    except Exception:
        logger.exception("Error al ejecutar el grafo router para user_id=%s", payload.user_id)
        raise HTTPException(status_code=502, detail="El modelo no pudo procesar la solicitud.") from None

    return ChatResponse(
        ruta=result["ruta"],
        motivo=result["motivo"],
        respuesta=result["respuesta"],
    )


@app.post("/telegram", tags=["telegram"], include_in_schema=False)
def telegram(
    update: Any = Body(...),
    secret_token: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
) -> dict[str, bool]:
    configured_secret = os.getenv("TELEGRAM_SECRET", "")
    if not configured_secret or not secret_token or not secrets.compare_digest(secret_token, configured_secret):
        raise HTTPException(status_code=403, detail="Secreto de Telegram inválido")

    message = update.get("message", {}) if isinstance(update, dict) else {}
    chat = message.get("chat", {}) if isinstance(message, dict) else {}
    chat_id = chat.get("id") if isinstance(chat, dict) else None
    texto = message.get("text") if isinstance(message, dict) else None
    if chat_id is None or not isinstance(texto, str) or not texto.strip():
        return {"ok": True}

    try:
        result = GRAPH.invoke(
            {"mensaje": texto},
            {"configurable": {"thread_id": str(chat_id)}},
        )
        respuesta = result["respuesta"]
        logger.info("Telegram chat_id=%s ruta=%s motivo=%s", chat_id, result["ruta"], result["motivo"])
    except Exception:
        logger.exception("Error al ejecutar el grafo para Telegram chat_id=%s", chat_id)
        respuesta = "No pude procesar tu mensaje en este momento. Intenta nuevamente más tarde."

    token = os.getenv("TELEGRAM_TOKEN", "")
    if not token:
        logger.error("TELEGRAM_TOKEN no está configurado; no se pudo responder a chat_id=%s", chat_id)
        return {"ok": True}

    try:
        telegram_response = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": respuesta},
            timeout=20.0,
        )
        telegram_response.raise_for_status()
    except Exception:
        logger.exception("Error al enviar respuesta de Telegram a chat_id=%s", chat_id)

    return {"ok": True}
