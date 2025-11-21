"""
Unit tests for PIX module.
Validates idempotency, status control, and validations.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.pix.service import criar_pix, confirmar_pix
from app.pix.schemas import PixCreateRequest, TipoChavePix
from app.pix.models import StatusPix


def test_criacao_pix_sucesso():
    """Tests successful PIX creation."""
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None  # No duplicate PIX

    dados = PixCreateRequest(
        valor=150.0,
        chave_pix="teste@email.com",
        tipo_chave=TipoChavePix.EMAIL,
        descricao="Pagamento teste"
    )

    # Mock get_saldo to return sufficient balance
    with patch("app.pix.service.get_saldo", return_value=1000.0):
        pix = criar_pix(db_mock, dados, "idem-key-123", "corr-123", "user-123")

    assert pix.valor == 150.0
    assert pix.status == StatusPix.CRIADO
    assert pix.idempotency_key == "idem-key-123"


def test_idempotencia_pix():
    """Tests that idempotency returns existing PIX."""
    pix_existente = Mock()
    pix_existente.id = "pix-123"
    pix_existente.valor = 200.0

    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = pix_existente

    dados = PixCreateRequest(
        valor=200.0,
        chave_pix="chave@test.com",
        tipo_chave=TipoChavePix.EMAIL,
        descricao="Teste idempotência"
    )

    pix = criar_pix(db_mock, dados, "idem-key-duplicada", "corr-123", "user-123")

    assert pix.id == "pix-123"
    assert pix.valor == 200.0


def test_validacao_cpf():
    """Validates CPF format."""
    with pytest.raises(Exception):
        PixCreateRequest(
            valor=100.0,
            chave_pix="12345",  # Invalid CPF
            tipo_chave=TipoChavePix.CPF,
            descricao="Teste CPF inválido"
        )


def test_validacao_email():
    """Validates email format."""
    with pytest.raises(Exception):
        PixCreateRequest(
            valor=100.0,
            chave_pix="email-invalido",
            tipo_chave=TipoChavePix.EMAIL,
            descricao="Teste email inválido"
        )


def test_validacao_valor_negativo():
    """Validates rejection of negative value."""
    with pytest.raises(Exception):
        PixCreateRequest(
            valor=-50.0,
            chave_pix="teste@email.com",
            tipo_chave=TipoChavePix.EMAIL,
            descricao="Teste valor negativo"
        )


def test_confirmacao_pix():
    """Tests PIX confirmation."""
    pix_mock = Mock()
    pix_mock.id = "pix-456"
    pix_mock.status = StatusPix.CRIADO

    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = pix_mock

    pix = confirmar_pix(db_mock, "pix-456", "corr-123")

    assert pix is not None
    assert pix.status == StatusPix.CONFIRMADO


def test_confirmacao_pix_inexistente():
    """Tests confirmation of non-existent PIX."""
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None

    pix = confirmar_pix(db_mock, "pix-inexistente", "corr-123")

    assert pix is None


def test_validacao_telefone():
    """Validates phone format."""
    # Valid phone with 11 digits
    pix = PixCreateRequest(
        valor=100.0,
        chave_pix="11987654321",
        tipo_chave=TipoChavePix.TELEFONE,
        descricao="Teste telefone válido"
    )
    assert pix.chave_pix == "11987654321"

    # Invalid phone
    with pytest.raises(Exception):
        PixCreateRequest(
            valor=100.0,
            chave_pix="123",
            tipo_chave=TipoChavePix.TELEFONE,
            descricao="Teste telefone inválido"
        )
