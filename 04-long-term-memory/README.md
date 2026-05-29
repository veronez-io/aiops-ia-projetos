# 04 - Memória de Longo Prazo (o que persiste entre sessões)

Demonstração interativa em Streamlit da diferença entre a **janela de contexto** (volátil) e a **memória de longo prazo** (persistente). Adicione fatos sobre você, ligue/desligue a memória e veja como o agente "lembra" ou "esquece" entre as conversas.

## Objetivos de Aprendizado

- Entender a memória de longo prazo como o **oposto da janela** no espectro de duração
- Sentir, na prática, a diferença entre o que é volátil (janela) e o que persiste (disco)
- Ver fatos do usuário **sobreviverem ao fim da sessão** e serem recuperados em uma nova conversa
- Perceber por que separar fato durável de ruído de sessão importa (combate ao *poisoning*)

## Conceitos

### A analogia: RAM vs. disco

A **janela de contexto** é como a **RAM**: rápida e volátil, some quando a sessão acaba. A **memória de longo prazo** é como o **disco**: persiste entre sessões, e o agente vai lá buscar a informação quando precisa — preferências, fatos do usuário, dados de contexto.

### O que vive na memória de longo prazo

Preferências do usuário, fatos sobre ele, dados usados para chamar serviços, informação isolada por usuário ou por tenant. Aqui o exemplo é **um único usuário**, com fatos em texto livre persistidos num arquivo `memory.json`.

### Tipos de memória (panorama)

Como panorama, costuma-se dividir em três tipos: **semantic** (fatos), **episodic** (exemplos de interações passadas) e **procedural** (instruções de como agir). Este projeto usa uma memória **genérica de fatos** para manter a demonstração simples — a construção real (onde persistir, como recuperar em escala) é tema dos módulos de agentes.

## Requisitos

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) instalado
- Chave de API do Google (Gemini)

## Como Executar

1. Configure a variável de ambiente `GOOGLE_API_KEY` no arquivo `.env` na raiz do repositório:

```
GOOGLE_API_KEY=sua-chave-aqui
```

2. Instale as dependências e execute o dashboard com `uv`:

```bash
uv sync
uv run streamlit run main.py
```

## Estrutura de Arquivos

```
04-long-term-memory/
├── README.md          # Este arquivo
├── pyproject.toml     # Dependências (gerenciadas com uv)
├── main.py            # Código completo do dashboard
└── memory.json        # Fatos persistidos em disco (criado/atualizado em runtime)
```

## Experimentos Sugeridos

1. **Adicione fatos**: na barra lateral, adicione "Meu nome é Ana" e "Moro em São Paulo". Veja que `memory.json` é criado no disco.
2. **Memória ON**: no chat, pergunte "Qual é o meu nome? Onde eu moro?" — o agente responde corretamente, pois os fatos foram injetados na conversa.
3. **Limpar o chat (janela some)**: clique em **Limpar chat**, depois pergunte de novo. O agente ainda sabe — a janela foi esvaziada, mas a memória de longo prazo permaneceu no disco.
4. **Memória OFF**: limpe o chat, desligue o toggle e pergunte novamente — agora o agente não sabe, pois nem o histórico nem os fatos estão disponíveis.
5. **Persistência entre sessões**: encerre o app (`Ctrl+C`) e rode `uv run streamlit run main.py` novamente. Os fatos continuam lá — prova de que estavam no "disco", não na "RAM".
