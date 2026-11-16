import json
from pathlib import Path

import pytest

from src.router.graph import run_router


CASOS = json.loads((Path(__file__).parent / "casos_router.json").read_text())
RESULTADOS: list[bool] = []


@pytest.mark.parametrize("caso", CASOS)
def test_router_casos(caso: dict[str, str]) -> None:
    resultado = run_router(caso["mensaje"], thread_id=f"pytest-{len(RESULTADOS)}")
    RESULTADOS.append(resultado["ruta"] == caso["esperado"])

    # Se comprueba el umbral en el último caso para tolerar la variabilidad del modelo.
    if len(RESULTADOS) == len(CASOS):
        assert sum(RESULTADOS) >= 13, (
            f"El router acertó {sum(RESULTADOS)}/{len(CASOS)} casos; "
            "se esperaban al menos 13."
        )
