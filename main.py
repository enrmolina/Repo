import argparse

from src.router.graph import build_graph, run_router


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta un agente LangGraph")
    parser.add_argument("nombre_agente")
    parser.add_argument("mensaje")
    parser.add_argument("--saltos", action="store_true")
    parser.add_argument("--diagrama", action="store_true")
    args = parser.parse_args()
    if args.nombre_agente != "router":
        raise SystemExit(f"Agente no configurado: {args.nombre_agente}")
    if args.diagrama:
        print(build_graph().get_graph().draw_mermaid())
        return
    result = run_router(args.mensaje)
    if args.saltos:
        nodo = {
            "preventa": "agente_preventa",
            "postventa": "agente_postventa",
            "generica": "respuesta_generica",
        }[result["ruta"]]
        print(f"router → {nodo}")
        print(f"motivo: {result['motivo']}")
    else:
        print(result["respuesta"])


if __name__ == "__main__":
    main()
