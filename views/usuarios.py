import streamlit as st
from services import supabase_client

# Exibe a interface de gerenciamento de usuários (apenas para administradores).

# Verificar se o usuário é administrador
if st.session_state.role != 'admin':
    st.error("Acesso negado. Apenas administradores podem acessar esta página.")
    st.stop()

st.title("Gerenciamento de Usuários")
st.write("Gerencie os usuários do sistema. Crie novos usuários e defina seus perfis.")

# Dividir a página em abas
tab1, tab2 = st.tabs(["Usuários Cadastrados", "Novo Usuário"])

# Aba de usuários cadastrados
with tab1:
    st.subheader("Usuários Cadastrados")
    
    # Botão para atualizar a lista
    if st.button("Atualizar Lista", key="btn_atualizar_usuarios"):
        st.session_state.usuarios_cache = supabase_client.listar_usuarios()  # Limpar o cache
        st.rerun()
    
    # Carregar usuários (com cache)
    if 'usuarios_cache' not in st.session_state:
        with st.spinner("Carregando usuários..."):
            st.session_state.usuarios_cache = supabase_client.listar_usuarios()
    
    # Mostrar a lista de usuários
    if st.session_state.usuarios_cache:
        usuarios_df = {
            "Nome": [],
            "Usuário": [],
            "Email": [],
            "Perfil": [],
            "Status": [],
        }
        
        for user in st.session_state.usuarios_cache:
            usuarios_df["Nome"].append(user["nome"])
            usuarios_df["Usuário"].append(user["username"])
            usuarios_df["Email"].append(user["email"])
            usuarios_df["Perfil"].append(user["perfil"].upper() if user["perfil"] else "USER")
            status = "✅ Confirmado" if user["confirmado"] else "⏳ Pendente"
            usuarios_df["Status"].append(status)
        
        st.dataframe(usuarios_df, use_container_width=True)
    else:
        st.info("Nenhum usuário encontrado.")

# Aba de novo usuário
with tab2:
    st.subheader("Criar Novo Usuário")
    st.write("Preencha o formulário abaixo para criar um novo usuário. Um email de confirmação será enviado.")
    
    with st.form("criar_usuario_form"):
        # Campos do formulário
        nome = st.text_input("Nome completo", placeholder="Nome completo do usuário")
        username = st.text_input("Nome de usuário (opcional)", placeholder="username", 
                                help="Se não for fornecido, será usado a parte local do email")
        email = st.text_input("Email", placeholder="email@exemplo.com")
        senha = st.text_input("Senha temporária", type="password", help="O usuário poderá alterar após o primeiro acesso")
        perfil = st.selectbox("Perfil", options=["user", "admin"], index=0, 
                                format_func=lambda x: "Administrador" if x == "admin" else "Usuário comum")
        
        submit = st.form_submit_button("Criar Usuário")
        
        if submit:
            if not nome or not email or not senha:
                st.error("Os campos Nome, Email e Senha são obrigatórios.")
            else:
                # Tentar criar o usuário
                with st.spinner("Criando usuário e enviando email..."):
                    success, message = supabase_client.criar_usuario(nome, email, senha, perfil, username)
                    
                    if success:
                        st.success(message)
                        # Limpar o cache de usuários para forçar uma nova consulta
                        st.session_state.usuarios_cache = None
                    else:
                        st.error(message)