ROUTER_PROMPT = """
Eres el router de un chat de ecommerce. Clasifica el último mensaje en una sola ruta.

- preventa: intención de compra, preguntas por productos, precios, tallas, stock,
  promociones o formas de pago antes de comprar.
- postventa: queja, reclamo, seguimiento de un pedido ya hecho, devolución, cambio,
  garantía o producto dañado.
- generica: cualquier cosa que no tenga que ver con el ecommerce (clima, chistes,
  preguntas generales) o saludos sin pedido.

Si dudas entre preventa y postventa, la clave es si YA compró: si habla de un pedido
existente es postventa.
Devuelve una frase breve explicando el motivo.
""".strip()

PREVENTA_PROMPT = "Responde usando exactamente el formato del agente de preventa."
POSTVENTA_PROMPT = "Responde usando exactamente el formato del agente de postventa."
GENERICA_PROMPT = "Responde amablemente que este chat es para la tienda."


def preventa_response(message: str) -> str:
    return f"Soy el agente de preventa. Recibí: {message}. Pronto podré ayudarte con productos y compras."


def postventa_response(message: str) -> str:
    return f"Soy el agente de postventa. Recibí: {message}. Pronto podré ayudarte con tu pedido."


def generica_response() -> str:
    return "Este chat es para ayudarte con nuestra tienda y sus productos."
