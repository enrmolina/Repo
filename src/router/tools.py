from typing import Literal


Route = Literal["preventa", "postventa", "generica"]


def fallback_route(message: str) -> tuple[Route, str]:
    """Clasificación local para poder ejecutar el esqueleto sin una API key."""
    text = message.casefold()
    postventa_terms = (
        "pedido", "compré", "compre", "devolver", "devolución", "devolucion",
        "cambio", "garantía", "garantia", "roto", "dañado", "danado", "reclamo",
        "queja", "seguimiento",
    )
    preventa_terms = (
        "tienen", "precio", "cuánto", "cuanto", "talla", "stock", "envío", "envio",
        "promoción", "promocion", "descuento", "pago", "comprar", "costo",
    )
    if any(term in text for term in postventa_terms) or "problema" in text:
        return "postventa", "Menciona una compra o gestión de un pedido existente."
    if any(term in text for term in preventa_terms):
        return "preventa", "Consulta sobre productos o condiciones antes de comprar."
    return "generica", "No plantea una necesidad relacionada con la tienda."
