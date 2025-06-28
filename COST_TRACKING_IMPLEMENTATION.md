# Plano Implementado: Suporte para Previsão de Gasto e Contabilização de Tokens

## Resumo das Funcionalidades Adicionadas

### 1. **Modelos de Dados para Tokens e Custos**
- `TokenUsage`: Armazena informações detalhadas de uso de tokens por requisição
- `CostEstimate`: Calcula estimativas de custo antes da execução  
- `UsageReport`: Relatório completo de uma sessão de screening

### 2. **Calculadora de Custos (`cost_calculator.py`)**
- Tabela de preços atualizada para todos os provedores (OpenAI, Gemini, Anthropic)
- Estimativa de tokens usando tiktoken para OpenAI
- Cálculo de custos em tempo real
- Função para estimar custo total antes do screening

### 3. **Rastreamento de Uso (`usage_tracker.py`)**
- Classe `UsageTracker` para monitorar sessões de screening
- Coleta estatísticas detalhadas: tokens, custos, sucessos/falhas
- Geração de relatórios em JSON
- Exibição de resumos no console

### 4. **Novos Comandos CLI**

#### `estimate-cost`
```bash
slr-assessor estimate-cost papers.csv --provider openai --model gpt-4
```
- Estima custo total antes de executar o screening
- Mostra breakdown detalhado de tokens e custos
- Ajuda na tomada de decisão de qual modelo usar

#### `screen` (atualizado)
```bash
slr-assessor screen papers.csv --provider openai --output results.csv --usage-report usage.json
```
- Agora coleta informações de tokens para cada paper
- Mostra resumo de uso ao final
- Opção de salvar relatório detalhado

#### `analyze-usage`
```bash
slr-assessor analyze-usage usage.json
```
- Analisa relatórios de uso salvos
- Mostra estatísticas detalhadas
- Breakdown por paper individual

### 5. **Providers Atualizados**
- Todos os providers agora retornam informações de tokens
- OpenAI e Anthropic: dados precisos da API
- Gemini: estimativa baseada no texto (API não fornece tokens detalhados)
- Cálculo automático de custos

### 6. **CSV com Informações de Tokens**
O CSV de resultados agora inclui:
- `input_tokens`, `output_tokens`, `total_tokens`
- `estimated_cost` (em USD)
- `model`, `provider`

## Casos de Uso

### Antes de Começar um Projeto
```bash
# Estimar custo de diferentes modelos
slr-assessor estimate-cost papers.csv --provider openai --model gpt-4
slr-assessor estimate-cost papers.csv --provider gemini --model gemini-2.5-flash
slr-assessor estimate-cost papers.csv --provider anthropic --model claude-3-sonnet-20240229
```

### Durante o Screening
```bash
# Executar com rastreamento de uso
slr-assessor screen papers.csv \
  --provider openai \
  --output results.csv \
  --usage-report session_usage.json
```

### Análise Pós-Screening
```bash
# Analisar o que foi gasto
slr-assessor analyze-usage session_usage.json

# Ver tokens por paper no CSV
head -5 results.csv
```

## Benefícios da Implementação

1. **Transparência de Custos**: Saber exatamente quanto custou cada paper
2. **Planejamento de Orçamento**: Estimar custos antes de executar
3. **Otimização**: Comparar eficiência de diferentes modelos
4. **Controle**: Monitorar usage em tempo real
5. **Auditoria**: Relatórios detalhados para prestação de contas
6. **Insights**: Entender padrões de uso de tokens

## Estrutura de Preços (Junho 2025)

### OpenAI
- GPT-4: $0.030 input / $0.060 output per 1K tokens
- GPT-3.5-turbo: $0.0015 input / $0.002 output per 1K tokens

### Gemini  
- Gemini-2.5-Flash: $0.000075 input / $0.0003 output per 1K tokens
- Gemini-2.5-Pro: $0.00075 input / $0.003 output per 1K tokens

### Anthropic
- Claude-3-Sonnet: $0.003 input / $0.015 output per 1K tokens
- Claude-3-Haiku: $0.00025 input / $0.00125 output per 1K tokens

## Exemplo de Relatório de Uso

```json
{
  "session_id": "abc123",
  "provider": "openai",
  "model": "gpt-4",
  "total_papers_processed": 100,
  "successful_papers": 98,
  "failed_papers": 2,
  "total_input_tokens": 85420,
  "total_output_tokens": 42100,
  "total_tokens": 127520,
  "total_cost": 3.84,
  "average_tokens_per_paper": 1301.2
}
```

Esta implementação fornece controle completo sobre custos e usage, permitindo que pesquisadores façam escolhas informadas sobre qual provider e modelo usar baseado em orçamento e necessidades do projeto.
