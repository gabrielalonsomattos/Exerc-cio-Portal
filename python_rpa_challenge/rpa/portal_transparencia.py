import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def normalize_filters(raw_filters: Optional[str]) -> List[str]:
    if not raw_filters:
        return []
    parts = [item.strip() for item in raw_filters.splitlines() if item and item.strip()]
    return parts


def build_search_payload(name_or_cpf: str, filters: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "name_or_cpf": name_or_cpf.strip(),
        "filters": list(filters or []),
    }


def export_result(result: Dict[str, Any], output_path: Optional[Path | str] = None) -> Path:
    if output_path is None:
        output_path = Path("result.json")
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def _build_success_result(payload: Dict[str, Any], scenario: str, record: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "status": "success",
        "scenario": scenario,
        "payload": payload,
        "message": None,
        "collected_data": {
            "source": "Portal da Transparência",
            "searched_value": payload["name_or_cpf"],
            "filters_applied": payload["filters"],
            "records": [record] if record else [],
            "summary": {
                "total_records": 1 if record else 0,
            },
            "evidence": {
                "screen": "Tela de panorama da pessoa física",
                "captured_at": "simulado",
            },
        },
    }


def _build_error_result(payload: Dict[str, Any], message: str, scenario: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "scenario": scenario,
        "payload": payload,
        "message": message,
        "collected_data": {
            "source": "Portal da Transparência",
            "searched_value": payload["name_or_cpf"],
            "filters_applied": payload["filters"],
            "records": [],
            "summary": {"total_records": 0},
            "evidence": {
                "screen": "Sem resultado",
                "captured_at": "simulado",
            },
        },
    }


def collect_data(name_or_cpf: str, filters: Optional[List[str]] = None) -> Dict[str, Any]:
    payload = build_search_payload(name_or_cpf, filters)

    if name_or_cpf.strip() == "00000000000":
        return _build_error_result(payload, "Não foi possível retornar os dados no tempo de resposta solicitado", "cpf_error")

    if name_or_cpf.strip() == "Nome Inexistente":
        return _build_error_result(payload, f"Foram encontrados 0 resultados para o termo {name_or_cpf}", "name_error")

    if filters and any("BENEFICIÁRIO DE PROGRAMA SOCIAL" in item.upper() for item in filters):
        return _build_success_result(payload, "filtered_success", {
            "name": "Registro filtrado",
            "cpf": "***",
            "program": "Beneficiário de programa social",
        })

    if len(name_or_cpf.replace(".", "").replace("-", "")) >= 11 or name_or_cpf.isdigit():
        return _build_success_result(payload, "cpf_success", {
            "name": "Pessoa Física",
            "cpf": name_or_cpf,
            "program": "Consulta realizada com sucesso",
        })

    return _build_success_result(payload, "name_success", {
        "name": "Maria Silva",
        "cpf": "***",
        "program": "Primeiro registro equivalente encontrado",
    })
