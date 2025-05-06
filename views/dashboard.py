import streamlit as st

st.title("Dashboard")
st.write("Bem-vindo ao Dashboard do Gerador de Questões!")
st.write("Utilize a barra lateral para navegar entre as funcionalidades da aplicação.")

# Estatísticas (placeholder para futura implementação)
st.subheader("Estatísticas")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Questões Geradas", "--")

with col2:
    st.metric("Questões Aprovadas", "--")

with col3:
    st.metric("Questões no Banco", "--")
    
st.info("Esta é a página inicial do aplicativo. Use a funcionalidade 'Gerar Questões' para começar a criar questões de múltipla escolha.")