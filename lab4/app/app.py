import streamlit as st
from openai import OpenAI, APIError

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

st.set_page_config(page_title="MacBook AI", page_icon="🍎", layout="centered")
st.title("Локальний AI")

with st.sidebar:
    st.header("Налаштування моделі")
    
    selected_model = st.selectbox("Оберіть модель", ["llama3.1", "llama3.2"])
    
    # Повзунок температури (0.0 - логічно, 1.0 - креативно)
    temperature = st.slider("Температура (креативність)", 0.0, 1.0, 0.7, 0.1)
    
    max_tokens = st.number_input("Максимум токенів", min_value=100, max_value=2000, value=800)
    
    st.markdown("---")
    st.markdown("💡 **Ідея для тесту:** Попроси написати код гри 'Змійка' на Python, або пояснити квантову фізику 5-річній дитині.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Ти корисний і розумний AI-асистент. Завжди відповідай українською мовою, використовуй форматування Markdown."}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("Про що поговоримо?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=selected_model,
                messages=st.session_state.messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌") 
            
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except APIError as e:
            st.error(f"❌ Помилка API. Переконайтеся, що Ollama працює. Деталі: {e}")
        except Exception as e:
            st.error(f"❌ Виникла неочікувана помилка: {e}")