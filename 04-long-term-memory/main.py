import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MEMORY_FILE = Path(__file__).parent / "memory.json"


def validate_environment():
    """Valida se a API key do Google está configurada."""
    google_key = os.getenv("GOOGLE_API_KEY")

    if not google_key:
        return False

    if google_key.startswith("your-"):
        return False

    return True


def create_model():
    """Cria instância do modelo Gemini."""
    api_key = os.getenv("GOOGLE_API_KEY")
    return ChatGoogleGenerativeAI(
        model="gemini-3-pro-preview",
        google_api_key=api_key,
    )


def load_memory():
    """Lê os fatos persistidos no disco. Retorna lista vazia se não existir."""
    if not MEMORY_FILE.exists():
        return []
    try:
        with open(MEMORY_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_memory(facts):
    """Grava a lista de fatos no disco (JSON legível, UTF-8)."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=2)


def build_system_prompt(facts):
    """Monta o system prompt com os fatos da memória de longo prazo."""
    fatos = "\n".join(f"- {fato}" for fato in facts)
    return (
        "Você é um assistente que conhece o usuário através da memória de longo prazo. "
        "Use os fatos abaixo, recuperados de sessões anteriores, para personalizar suas "
        "respostas. Se a pergunta for sobre o usuário, baseie-se exclusivamente nesses fatos.\n\n"
        f"Fatos conhecidos sobre o usuário:\n{fatos}"
    )


def normalize_content(content):
    """Normaliza o content da resposta, que pode vir como lista de blocos."""
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return content


def main():
    st.set_page_config(
        page_title="Memória de Longo Prazo",
        page_icon="🧠",
        layout="wide",
    )

    st.title("Memória de Longo Prazo")
    st.markdown(
        "O **chat** é a janela: como a RAM, é rápido e volátil — some ao limpar a conversa "
        "ou reiniciar. A **memória de longo prazo** é como o disco: persiste entre sessões e "
        "o agente vai lá buscar quando precisa. Adicione fatos sobre você, ligue/desligue a "
        "memória e converse para observar a diferença."
    )

    if not validate_environment():
        st.error(
            "**GOOGLE_API_KEY** não configurada. "
            "Crie um arquivo `.env` na raiz do repositório com sua chave: "
            "`GOOGLE_API_KEY=sua-chave-aqui`"
        )
        st.stop()

    # Carrega os fatos do disco a cada execução (prova de persistência entre sessões).
    facts = load_memory()

    # --- Sidebar ---
    with st.sidebar:
        st.header("🧠 Memória de Longo Prazo")

        memory_on = st.toggle("Memória ativada", value=True)

        with st.expander("RAM vs. Disco — o que está acontecendo?"):
            st.markdown(
                "Com a memória **ligada**, os fatos salvos no disco (`memory.json`) são "
                "injetados no chat — o agente 'conhece' você mesmo numa conversa nova. "
                "Com a memória **desligada**, o agente só enxerga o histórico do chat atual; "
                "ao limpar a conversa, esquece tudo.\n\n"
                "Tipos de memória de longo prazo (panorama): **semantic** (fatos), "
                "**episodic** (exemplos de interações) e **procedural** (instruções). "
                "Aqui usamos uma memória genérica de fatos."
            )

        st.divider()

        st.subheader("Adicionar fato à memória")
        new_fact = st.text_input(
            "Novo fato/preferência:",
            placeholder="Ex: Meu nome é Ana e moro em São Paulo",
            label_visibility="collapsed",
        )
        if st.button("Adicionar à memória", type="primary"):
            if new_fact.strip():
                facts.append(new_fact.strip())
                save_memory(facts)
                st.rerun()
            else:
                st.warning("Digite um fato antes de adicionar.")

        st.divider()

        st.subheader("Fatos salvos no disco")
        if facts:
            for i, fato in enumerate(facts):
                col_text, col_btn = st.columns([5, 1])
                col_text.markdown(f"- {fato}")
                if col_btn.button("🗑️", key=f"del_{i}", help="Remover este fato"):
                    facts.pop(i)
                    save_memory(facts)
                    st.rerun()

            if st.button("Limpar toda a memória"):
                save_memory([])
                st.rerun()
        else:
            st.caption("Nenhum fato salvo ainda. O disco está vazio.")

    # --- Área principal (chat) ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    header_col, btn_col = st.columns([4, 1])
    with header_col:
        if memory_on and facts:
            st.success(f"🧠 Memória **ativada** — {len(facts)} fato(s) injetados no chat.")
        elif memory_on and not facts:
            st.info("🧠 Memória ativada, mas o disco está vazio. Adicione fatos na barra lateral.")
        else:
            st.warning("💨 Memória **desligada** — o agente conversa sem nenhum fato do disco.")
    with btn_col:
        if st.button("🧹 Limpar chat", help="Esvazia a janela (histórico). Os fatos no disco permanecem."):
            st.session_state.messages = []
            st.rerun()

    st.caption(
        "O histórico abaixo é a **janela** (volátil): some ao limpar o chat ou reiniciar. "
        "Os fatos da barra lateral são a **memória de longo prazo** (persistem no disco)."
    )

    # Renderiza o histórico da conversa (a janela).
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Converse com o agente..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        model = create_model()

        # Monta as mensagens: fatos (memória) + histórico da conversa (janela).
        messages = []
        if memory_on and facts:
            messages.append(SystemMessage(content=build_system_prompt(facts)))
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        with st.chat_message("assistant"):
            with st.spinner("Gerando resposta..."):
                try:
                    response = model.invoke(messages)
                    answer = normalize_content(response.content)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Erro ao gerar resposta: {e}")

    # --- Conteúdo do disco (reforça a metáfora) ---
    with st.expander("📀 Conteúdo do disco (`memory.json`)"):
        st.json(facts)


if __name__ == "__main__":
    main()
