# Catálogo de Testes e Validações - Fintech Tech Challenge

Este documento cataloga todos os testes automatizados e cenários de validação implementados no sistema, demonstrando a cobertura de requisitos funcionais, regras de negócio e segurança.

## Resumo da Cobertura

- **Total de Testes Automatizados**: 24
- **Áreas Cobertas**: Parcelamento (Price), PIX (Idempotência), Antifraude (Scoring)
- **Tipos de Teste**: Unitários, Integração, Regressão

---

## 1. Módulo de Parcelamento (Crédito)

Valida a precisão matemática e as regras de concessão de crédito.

| Teste | Descrição do Cenário | Valor de Negócio |
| :--- | :--- | :--- |
| `test_calculo_parcelamento_basico` | **Cálculo Básico (Tabela Price)** | Garante que o cálculo fundamental de parcelas, total pago e CET está matematicamente correto. |
| `test_primeira_parcela_juros` | **Precisão de Juros** | Verifica se os juros da primeira parcela são calculados exatamente sobre o saldo devedor inicial. |
| `test_saldo_final_zero` | **Integridade da Amortização** | Assegura que, ao final do prazo, o saldo devedor seja exatamente zero (sem resíduos). |
| `test_total_pago_maior_que_valor` | **Consistência Financeira** | Valida que o montante total pago é sempre superior ao valor emprestado (lucro da operação). |
| `test_validacao_valor_negativo` | **Proteção de Input** | Impede a simulação de valores negativos ou nulos, protegendo o sistema de dados inválidos. |
| `test_validacao_taxa_excessiva` | **Compliance de Taxas** | Bloqueia taxas de juros abusivas (acima de 15%), garantindo conformidade regulatória. |
| `test_parcelas_decrescentes` | **Consistência de Saldo** | Verifica se o saldo devedor diminui progressivamente a cada parcela paga. |

---

## 2. Módulo PIX (Pagamentos)

Foca na segurança transacional, idempotência e validação de chaves.

| Teste | Descrição do Cenário | Valor de Negócio |
| :--- | :--- | :--- |
| `test_criacao_pix_sucesso` | **Fluxo Feliz de Criação** | Valida a criação bem-sucedida de uma transação PIX com status inicial correto. |
| `test_idempotencia_pix` | **Garantia de Idempotência** | **Crítico**: Garante que requisições duplicadas (mesma `idempotency-key`) não gerem pagamentos duplicados. |
| `test_validacao_cpf` | **Validação de CPF** | Impede o uso de CPFs com formato inválido nas chaves PIX. |
| `test_validacao_email` | **Validação de Email** | Garante que chaves de email sigam o formato padrão (user@domain). |
| `test_validacao_telefone` | **Validação de Telefone** | Assegura que números de telefone tenham o formato e comprimento corretos. |
| `test_validacao_valor_negativo` | **Segurança Financeira** | Bloqueia tentativas de transferência com valores negativos. |
| `test_confirmacao_pix` | **Fluxo de Confirmação** | Testa a transição de status de CRIADO para CONFIRMADO. |
| `test_confirmacao_pix_inexistente` | **Tratamento de Erro** | Valida o comportamento do sistema ao tentar confirmar uma transação inexistente (Erro 404). |

---

## 3. Módulo Antifraude (Segurança)

Testa o motor de regras, cálculo de score e decisões automáticas.

| Teste | Descrição do Cenário | Valor de Negócio |
| :--- | :--- | :--- |
| `test_transacao_aprovada_baixo_risco` | **Aprovação Automática** | Valida que transações legítimas (baixo risco) são aprovadas sem fricção. |
| `test_transacao_reprovada_alto_risco` | **Bloqueio de Fraude** | Garante que transações suspeitas são bloqueadas automaticamente. |
| `test_regra_horario_noturno` | **Regra: Horário de Risco** | Verifica a detecção de transações fora do horário comercial (22h-06h). |
| `test_regra_valor_alto` | **Regra: Ticket Médio** | Testa o gatilho de risco para valores acima do limite configurado (> R$ 300). |
| `test_regra_tentativas_excessivas` | **Regra: Comportamento** | Identifica comportamento anômalo (muitas tentativas em curto período). |
| `test_score_acumulado` | **Motor de Scoring** | Valida a soma correta de pontos de risco de múltiplas regras simultâneas. |
| `test_nivel_risco_medio` | **Classificação de Risco** | Testa a categorização correta de transações em risco MÉDIO. |
| `test_multiplas_regras_ativadas` | **Cenário Extremo** | Simula uma transação que viola todas as regras simultaneamente (Score 100). |
| `test_validacao_horario_invalido` | **Integridade de Dados** | Rejeita formatos de hora inválidos (ex: "25:00"). |

---

## 4. Cenários de Integração (Manual)

Estes cenários são cobertos pelo script `scripts/test_api_manual.py` e validam o fluxo ponta a ponta via HTTP.

1. **Health Check**: Verifica se a API está online e respondendo.
2. **Simulação Completa**: Envia um payload JSON para o endpoint de parcelamento e valida a resposta completa (CET, Tabela).
3. **Ciclo de Vida PIX**:
    - Cria uma intenção de pagamento.
    - Recebe o ID da transação.
    - Confirma a transação usando o ID recebido.
4. **Análise de Risco em Tempo Real**:
    - Envia transação "segura" -> Espera aprovação.
    - Envia transação "suspeita" -> Espera rejeição e lista de motivos.

---

## Conclusão para o Recrutador

Este catálogo demonstra que o sistema não apenas "funciona", mas foi construído com **Qualidade e Confiabilidade** como prioridades.

- **Segurança**: Validada por testes de input e regras de fraude.
- **Confiabilidade Financeira**: Validada por testes de cálculo Price e Idempotência.
- **Manutenibilidade**: Código testável, modular e documentado.
