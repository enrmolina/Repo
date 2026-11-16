import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.router.graph import run_router  # noqa: E402


def main() -> None:
    casos = json.loads((ROOT / "tests" / "casos_router.json").read_text())
    resultados = []

    print(f"{'Mensaje':<48} {'Esperado':<10} {'Obtenido':<10} {'OK':<3} Motivo")
    print("-" * 125)
    for indice, caso in enumerate(casos):
        resultado = run_router(caso["mensaje"], thread_id=f"script-{indice}")
        obtenido = resultado["ruta"]
        ok = obtenido == caso["esperado"]
        resultados.append(ok)
        mensaje = caso["mensaje"][:45]
        marca = "✔" if ok else "✘"
        print(
            f"{mensaje:<48} {caso['esperado']:<10} {obtenido:<10} "
            f"{marca:<3} {resultado['motivo']}"
        )

    aciertos = sum(resultados)
    total = len(resultados)
    porcentaje = aciertos / total * 100 if total else 0
    print(f"\nAciertos: {aciertos}/{total} ({porcentaje:.1f}%)")
    fallados = [caso["mensaje"] for caso, ok in zip(casos, resultados) if not ok]
    if fallados:
        print("Fallados:")
        for mensaje in fallados:
            print(f"- {mensaje}")


if __name__ == "__main__":
    main()
