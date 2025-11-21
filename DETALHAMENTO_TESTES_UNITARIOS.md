# Detalhamento Técnico de Testes Unitários

Este documento apresenta a especificação técnica da suíte de testes unitários do projeto Fintech, demonstrando a cobertura de código e as estratégias de isolamento utilizadas.

## Métricas de Cobertura (Unitária)

Os testes unitários focam exclusivamente na **Lógica de Negócio (Domain Layer)**, isolando dependências externas como banco de dados e API HTTP.

| Módulo | Arquivo | Cobertura | Status |
| :--- | :--- | :--- | :--- |
| **Antifraude** | `app/antifraude/rules.py` | **98%** | Excelente |
| **Antifraude** | `app/antifraude/schemas.py` | **97%** | Excelente |
| **PIX** | `app/pix/schemas.py` | **98%** | Excelente |
| **PIX** | `app/pix/models.py` | **96%** | Excelente |
| **PIX** | `app/pix/service.py` | **80%** | Bom |
| **Parcelamento** | `app/parcelamento/schemas.py` | **96%** | Excelente |
| **Parcelamento** | `app/parcelamento/models.py` | **94%** | Excelente |
| **Parcelamento** | `app/parcelamento/service.py` | **79%** | Bom |

> **Nota:** Arquivos de infraestrutura (`router.py`, `main.py`) não são alvo de testes unitários, mas sim de testes de integração (não cobertos neste relatório).

---

## Estratégia de Testes

Utilizamos **Pytest** como runner e **Unittest.Mock** para isolamento.

### 1. Isolamento de Banco de Dados

Para testar serviços que dependem do banco de dados sem conectar num banco real, utilizamos `MagicMock`.

**Exemplo (`tests/test_pix.py`):**

```python
# Mock da sessão do banco de dados
db_mock = MagicMock()
# Simulando que não existe registro duplicado
db_mock.query().filter().first.return_value = None

pix = criar_pix(db_mock, dados, ...)
```

### 2. Testes de Regras de Negócio (Puros)

Testamos a lógica matemática e condicional sem nenhuma dependência externa.

**Exemplo (`tests/test_parcelamento.py`):**

```python
# Teste direto da função de cálculo (Input -> Output)
resultado = calcular_parcelas(dados)
assert resultado["cet_anual"] > 0
```

---

## Especificação dos Casos de Teste

### Módulo: Parcelamento (`tests/test_parcelamento.py`)

| Caso de Teste | Entrada (Input) | Comportamento Esperado |
| :--- | :--- | :--- |
| `test_calculo_parcelamento_basico` | R$ 1000, 12x, 3.5% | Tabela com 12 linhas, Total > 1000, CET calculado. |
| `test_primeira_parcela_juros` | R$ 1000, 3.5% | Juros da 1ª parcela deve ser exatamente R$ 35,00. |
| `test_saldo_final_zero` | Simulação completa | O saldo devedor na última linha deve ser 0.00. |
| `test_validacao_valor_negativo` | Valor: -100.0 | Deve lançar exceção de validação. |
| `test_validacao_taxa_excessiva` | Taxa: 20% | Deve lançar exceção (Regra: Teto de 15%). |

### Módulo: PIX (`tests/test_pix.py`)

| Caso de Teste | Entrada (Input) | Comportamento Esperado |
| :--- | :--- | :--- |
| `test_criacao_pix_sucesso` | Dados válidos | Objeto PIX criado com status `CRIADO`. |
| `test_idempotencia_pix` | Mesma `idempotency-key` | Deve retornar o objeto PIX original (sem criar novo). |
| `test_validacao_cpf` | CPF: "123" | Deve lançar erro de formato inválido. |
| `test_confirmacao_pix` | ID existente | Status deve mudar para `CONFIRMADO`. |
| `test_confirmacao_pix_inexistente` | ID inexistente | Deve retornar `None` ou erro 404. |

### Módulo: Antifraude (`tests/test_antifraude.py`)

| Caso de Teste | Entrada (Input) | Comportamento Esperado |
| :--- | :--- | :--- |
| `test_transacao_aprovada` | R$ 50, 14:30h | Score < 60, Aprovado = True. |
| `test_transacao_reprovada` | R$ 1500, 23:00h | Score >= 60, Aprovado = False, Risco ALTO. |
| `test_regra_horario_noturno` | Horário: 23:30 | Regra deve retornar `True` (Ativada). |
| `test_regra_valor_alto` | Valor > Limite | Regra deve retornar `True` (Ativada). |
| `test_score_acumulado` | Múltiplos fatores de risco | Score deve ser a soma dos pesos das regras. |

---

## Como Executar

Para reproduzir estes testes e gerar o relatório de cobertura:

```bash
# Executar testes
python -m pytest -v

# Gerar relatório de cobertura
python -m pytest --cov=app
```
