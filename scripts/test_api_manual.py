"""
Script de teste dos endpoints da API.
Demonstração rápida de funcionalidades.
"""
import requests
import json
from typing import Dict, Any
from requests import Response

BASE_URL = "http://localhost:8000"


def print_response(title: str, response: Response):
    """Imprime resposta formatada."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(response.text)


def test_health():
    """Testa health check."""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)


def test_parcelamento():
    """Testa simulação de parcelamento."""
    payload: Dict[str, Any] = {
        "valor": 1000.0,
        "parcelas": 12,
        "taxa_mensal": 0.035
    }
    response = requests.post(f"{BASE_URL}/parcelamento/simular", json=payload)
    print_response("Simulação de Parcelamento", response)

    if response.status_code == 201:
        print("\nResumo:")
        data = response.json()
        print(f"   Valor da parcela: R$ {data['parcela']}")
        print(f"   Total a pagar: R$ {data['total_pago']}")
        print(f"   CET anual: {data['cet_anual']}%")


def test_pix():
    """Testa criação de PIX."""
    payload: Dict[str, Any] = {
        "valor": 150.50,
        "chave_pix": "teste@email.com",
        "tipo_chave": "EMAIL",
        "descricao": "Pagamento teste"
    }
    headers = {"idempotency-key": "test-key-123"}

    response = requests.post(f"{BASE_URL}/pix/create", json=payload, headers=headers)
    print_response("Criação de PIX", response)

    if response.status_code == 201:
        pix_id = response.json()["id"]
        print(f"\nPIX ID: {pix_id}")

        # Confirma PIX
        confirm_payload = {"pix_id": pix_id}
        confirm_response = requests.post(f"{BASE_URL}/pix/confirm", json=confirm_payload)
        print_response("Confirmação de PIX", confirm_response)


def test_antifraude():
    """Testa análise antifraude."""
    # Caso 1: Baixo risco
    payload_baixo: Dict[str, Any] = {
        "valor": 50.0,
        "horario": "14:30",
        "tentativas_ultimas_24h": 1
    }
    response_baixo = requests.post(f"{BASE_URL}/antifraude/analisar", json=payload_baixo)
    print_response("Antifraude - Baixo Risco", response_baixo)

    # Caso 2: Alto risco
    payload_alto: Dict[str, Any] = {
        "valor": 1500.0,
        "horario": "23:00",
        "tentativas_ultimas_24h": 5
    }
    response_alto = requests.post(f"{BASE_URL}/antifraude/analisar", json=payload_alto)
    print_response("Antifraude - Alto Risco", response_alto)


def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("  Fintech Tech Challenge - Testes de API")
    print("="*60)
    print("\nCertifique-se de que o servidor está rodando em http://localhost:8000")

    try:
        test_health()
        test_parcelamento()
        test_pix()
        test_antifraude()

        print("\n" + "="*60)
        print("  Todos os testes executados com sucesso!")
        print("="*60)
        print(f"\nDocumentação: {BASE_URL}/docs")
        print(f"ReDoc: {BASE_URL}/redoc")

    except requests.exceptions.ConnectionError:
        print("\nErro: Não foi possível conectar ao servidor.")
        print("   Execute: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\nErro: {e}")


if __name__ == "__main__":
    main()
