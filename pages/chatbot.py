import streamlit as st
from model.genai import get_response

def main():
    st.title("Chat Bot")

    # Inisialisasi riwayat chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Menampilkan riwayat chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Menanggapi input pengguna
    if prompt := st.chat_input("Halo ada apa??"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = f"{get_response(prompt)}"
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
    # Tombol Reset Chat
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []  # Hapus semua riwayat chat
        st.experimental_rerun()  # Refresh halaman

if __name__ == "__main__":
    main()
