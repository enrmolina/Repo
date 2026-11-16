# Ecommerce Router

Agente de chat para un ecommerce construido con Python 3.12, LangGraph,
LangChain y Gemini. El grafo clasifica cada mensaje en una de tres rutas:

- **preventa**: productos, precios, tallas, stock y compras antes de comprar.
- **postventa**: pedidos existentes, devoluciones, cambios, garantías y reclamos.
- **generica**: saludos y mensajes que no corresponden a la tienda.

La API FastAPI expone el router por `/chat`, protege ese endpoint con la cabecera
`X-API-Key` y conserva memoria por `user_id`/`thread_id`.

## Configuración local

Desde la raíz del proyecto:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Completa `.env` con tu `GOOGLE_API_KEY` y una clave privada para `API_KEY`.
No subas `.env` al repositorio.

Para generar una clave API:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

## Ejecutar el router en local

El comando se ejecuta desde la raíz:

```bash
python main.py router "¿tienen la polera azul en talla M?"
```

Para mostrar el camino y el motivo:

```bash
python main.py router "mi pedido llegó roto" --saltos
```

Para imprimir el diagrama Mermaid sin ejecutar el grafo:

```bash
python main.py router "mensaje ignorado" --diagrama
```

## Levantar la API

```bash
source .venv/bin/activate
uvicorn api.app:app --reload --port 8000
```

La documentación interactiva está en <http://localhost:8000/docs>.

Comprobar salud:

```bash
curl http://localhost:8000/health
```

Ejemplo de `/chat`:

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: cambia-esta-clave' \
  -d '{"user_id":"usuario-123","texto":"¿Tienen la polera azul en talla M?"}'
```

## Pruebas

Ejecutar toda la suite:

```bash
pytest
```

Ejecutar la prueba parametrizada del router:

```bash
pytest tests/test_router.py -q
```

Ejecutar la tabla de 15 casos:

```bash
python scripts/test_router.py
```

## Desplegar en Heroku

El proyecto incluye `Procfile`, `.python-version` y `requirements.txt`. Con
Heroku CLI instalado:

```bash
heroku login
heroku create NOMBRE_DE_TU_APP
heroku config:set GOOGLE_API_KEY="tu-clave-de-google" MODELO="gemini-3.5-flash-lite" TELEGRAM_TOKEN="" TELEGRAM_SECRET="genera-un-secreto" PUBLIC_URL="https://NOMBRE_DE_TU_APP.herokuapp.com" API_KEY="tu-clave-api" --app NOMBRE_DE_TU_APP
git push heroku main
heroku open --app NOMBRE_DE_TU_APP
```

El proceso web ejecuta exactamente:

```text
web: uvicorn api.app:app --host 0.0.0.0 --port $PORT
```

## Conectar Telegram

1. En Telegram, abre `@BotFather`, ejecuta `/newbot` y guarda el token en
   `TELEGRAM_TOKEN`.
2. Configura `TELEGRAM_SECRET` y `PUBLIC_URL` como variables locales o Config
   Vars de Heroku.
3. Registra el webhook apuntando a la API pública:

```bash
curl -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook" \
  -d "url=${PUBLIC_URL}/telegram" \
  -d "secret_token=${TELEGRAM_SECRET}"
```

4. Consulta el webhook configurado:

```bash
curl "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo"
```

El endpoint `/telegram` está creado como receptor provisional y actualmente
responde `{"ok":true}` a cualquier JSON. La validación del `secret_token` y el
procesamiento de mensajes de Telegram se completarán en la parte 5.

## Bruno

La colección está en `bruno/`. Selecciona el entorno `local` o `heroku` y cambia
`baseUrl` y `apiKey` en el entorno correspondiente. Incluye peticiones para
`health`, `chat-preventa`, `chat-postventa` y `chat-generica`.
