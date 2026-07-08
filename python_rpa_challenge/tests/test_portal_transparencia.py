import json
import tempfile
import unittest
from pathlib import Path

from rpa.portal_transparencia import (
    build_search_payload,
    collect_data,
    export_result,
    normalize_filters,
)


class PortalTransparenciaTests(unittest.TestCase):
    def test_normalize_filters(self) -> None:
        filters = normalize_filters("BENEFICIÁRIO DE PROGRAMA SOCIAL\nOutro filtro")
        self.assertEqual(filters, ["BENEFICIÁRIO DE PROGRAMA SOCIAL", "Outro filtro"])

    def test_build_search_payload(self) -> None:
        payload = build_search_payload("12345678909", ["Benefícios ao Cidadão"])
        self.assertEqual(payload["name_or_cpf"], "12345678909")
        self.assertEqual(payload["filters"], ["Benefícios ao Cidadão"])

    def test_export_result_writes_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "result.json"
            export_result({"status": "success"}, output_path)
            self.assertTrue(output_path.exists())
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8"))["status"], "success")

    def test_cpf_success_returns_evidence(self) -> None:
        result = collect_data("070.680.938-68", [])
        self.assertEqual(result["status"], "success")
        self.assertIn("evidence", result["collected_data"])

    def test_cpf_error_returns_timeout_message(self) -> None:
        result = collect_data("00000000000", [])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Não foi possível retornar os dados no tempo de resposta solicitado")

    def test_name_success_returns_first_record(self) -> None:
        result = collect_data("Maria Silva", [])
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["collected_data"]["records"]), 0)

    def test_name_error_returns_zero_results_message(self) -> None:
        result = collect_data("Nome Inexistente", [])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Foram encontrados 0 resultados para o termo Nome Inexistente")

    def test_filtered_social_success_returns_record(self) -> None:
        result = collect_data("Silva", ["BENEFICIÁRIO DE PROGRAMA SOCIAL"])
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["scenario"], "filtered_success")


if __name__ == "__main__":
    unittest.main()
