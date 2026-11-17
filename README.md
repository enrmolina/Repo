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

## Telegram

Primero, en Telegram abre `@BotFather`, ejecuta `/newbot`, copia el token y
elige un secreto propio. No compartas ninguno de los dos valores.

El endpoint `/telegram` usa solo `httpx`, valida la cabecera
`X-Telegram-Bot-Api-Secret-Token`, enruta el texto por `chat_id` y responde con
`sendMessage`. Los updates sin texto se ignoran.

Sigue estos pasos en orden:

1. Configura el token y el secreto en Heroku:

```bash
heroku config:set TELEGRAM_TOKEN="tu-token-de-BotFather" TELEGRAM_SECRET="tu-secreto" --app NOMBRE_DE_TU_APP
```

2. Haz commit y publica los cambios en GitHub y Heroku:

```bash
git add api/app.py scripts/set_webhook.py scripts/webhook_info.py README.md
git commit -m "conecta Telegram al router"
git push origin main
git push heroku main
```

3. Con `PUBLIC_URL` apuntando a Heroku, registra y verifica el webhook:

```bash
python scripts/set_webhook.py
python scripts/webhook_info.py
```

La URL registrada será `PUBLIC_URL/telegram`. `getWebhookInfo` muestra la URL,
la fecha de la última sincronización y los errores pendientes.

4. Escribe al bot estos seis mensajes y observa la ruta en los logs:

```text
¿tienen la polera azul en talla M?
mi pedido 4521 llegó roto
hola
¿cuánto cuesta el envío a Valparaíso?
quiero devolver unas zapatillas
¿qué hora es en Tokio?
```

```bash
heroku logs --tail --app NOMBRE_DE_TU_APP
```

5. Si no responde, revisa que:

- el webhook apunte a `https://.../telegram`, no a HTTP ni a la raíz;
- `TELEGRAM_SECRET` sea idéntico en Heroku y en el webhook;
- `TELEGRAM_TOKEN` sea el token correcto de BotFather;
- el dyno web esté activo y los logs no muestren errores.

### Probar antes de desplegar (opcional)

Con la API local levantada, crea un túnel público:

```bash
cloudflared tunnel --url http://localhost:8000
```

Usa la URL HTTPS que entregue Cloudflared como `PUBLIC_URL` y ejecuta los dos
scripts del paso 3.

## Bruno

La colección está en `bruno/`. Selecciona el entorno `local` o `heroku` y cambia
`baseUrl` y `apiKey` en el entorno correspondiente. Incluye peticiones para
`health`, `chat-preventa`, `chat-postventa` y `chat-generica`.
