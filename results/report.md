# Relatório de Análise de Tokens - LangChain

**Data de execução**: 2026-02-16 14:53:32

## 1. Resumo Executivo

- Prompts testados: 1 prompt médio (explicação técnica sobre AIOps)
- Providers avaliados: Anthropic, Google
- Modelos testados: 4 (2 Claude + 2 Gemini)
- Idiomas comparados: Português (BR) e Inglês
- Total de execuções: 8

## 2. Comparação por Provider

### Anthropic Claude

| Modelo | Idioma | Média Input | Média Output | Média Total |
|--------|--------|-------------|--------------|-------------|
| claude-sonnet-4-5-20250929 | PT | 36 | 498 | 534 |
| claude-sonnet-4-5-20250929 | EN | 30 | 352 | 382 |
| claude-haiku-4-5-20251001 | PT | 36 | 432 | 468 |
| claude-haiku-4-5-20251001 | EN | 30 | 346 | 376 |

### Google Gemini

| Modelo | Idioma | Média Input | Média Output | Média Total |
|--------|--------|-------------|--------------|-------------|
| gemini-3-pro-preview | PT | 23 | 1337 | 1360 |
| gemini-3-pro-preview | EN | 20 | 1241 | 1261 |
| gemini-3-flash-preview | PT | 23 | 1290 | 1313 |
| gemini-3-flash-preview | EN | 20 | 962 | 982 |

## 3. Comparação de Idiomas

### Diferença Português vs Inglês

**Anthropic Claude**:
- Português usa em média 32.2% mais tokens que inglês

**Google Gemini**:
- Português usa em média 19.2% mais tokens que inglês

## 4. Insights

1. **Tokenização por idioma**: O português consistentemente utiliza mais tokens que o inglês, com diferença média de 25.7%
2. **Eficiência por modelo**: Modelos menores (Haiku, Flash) tendem a gerar respostas mais concisas
3. **Provider comparison**: Ambos os providers mostram padrões similares de tokenização entre idiomas

## 5. Análise do Prompt Médio

**Prompt testado**: "Explique o conceito de AIOps em 3 parágrafos..."

Este prompt foi escolhido para representar uma solicitação técnica de complexidade média, típica em cenários de documentação e educação.

**Exemplo de resposta (primeiros 200 caracteres)**:

> # AIOps: Inteligência Artificial para Operações de TI

**AIOps** (Artificial Intelligence for IT Operations) é uma abordagem que combina big data, machine learning e inteligência artificial para autom...

## 6. Conclusões

1. A escolha do idioma impacta significativamente o consumo de tokens, com português usando 15-35% mais tokens
2. Para otimizar custos em aplicações multilíngues, considere usar inglês quando possível
3. Modelos menores (Haiku, Flash) são adequados para tarefas explicativas simples, economizando tokens
4. O LangChain facilita a captura de métricas através de callbacks, permitindo análises detalhadas de consumo
