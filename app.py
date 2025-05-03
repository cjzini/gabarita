from math import e
from PIL import Image
import streamlit as st
import services.supabase_client as supabase_client

im = Image.open("images/favicon.png")
st.set_page_config(
    page_title="Gabarita",
    page_icon=im,
    layout="wide"
)

supabase = supabase_client.get_supabase_connection()

# Inicialização das variáveis de sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None

# Inicializa o estado da sessão para contar questões aprovadas
if 'questoes_geradas' not in st.session_state:
    st.session_state.questoes_geradas = []  
# Indica se a geração de questões já foi realizada
if 'geracao_realizada' not in st.session_state:
    st.session_state.geracao_realizada = False   
# Armazena o número de questões selecionado
if 'num_questoes' not in st.session_state:
    st.session_state.num_questoes = 3
# Armazena o nível de dificuldade selecionado
if 'dificuldade' not in st.session_state:
    st.session_state.dificuldade = "médio"   
# Armazena os dados do arquivo em formato JSON
if 'json_data' not in st.session_state:
    st.session_state.json_data = None

# Função para logar o usuário
def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.user = response.user
        st.session_state.logged_in = True

        # Consultar a tabela profiles para obter o perfil do usuário
        user_id = response.user.id
        # Armazenar o ID do usuário na sessão para uso em outras partes do aplicativo
        st.session_state.user_id = user_id
        profile_response = supabase.table('profiles').select('*').eq('id', user_id).execute()
        # Definir o perfil do usuário na sessão
        if profile_response.data and len(profile_response.data) > 0:
            st.session_state.profile = profile_response.data[0]
            st.session_state.role = profile_response.data[0].get('role', 'user')
        else:
            # Se não houver perfil, definir o perfil padrão como 'user'
            st.session_state.profile = {}
            st.session_state.role = 'user'
        return True
    except Exception as e:
        st.error(f"Erro no login: {str(e)}")
        return False

def logout_user():
    supabase.auth.sign_out()
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.profile = None
    st.rerun()

# Interface de login
def login_page():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("images/logo_gabarita.png", width=300)
        st.subheader("🔐 Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")     
            if submit:
                if login_user(email, password):
                    st.success("Login realizado com sucesso!")
                    st.rerun()

# Interface principal após o login
def main_page():
    role = st.session_state.role
    dashboard = st.Page(
        "views/dashboard.py",
        title="Dashboard",
        icon=":material/dashboard:",
        default=(role == "admin"),
    )
    extracao = st.Page(
        "views/extracao.py",
        title="Gerar Questões",
        icon=":material/convert_to_text:",
    )
    settings = st.Page(
        "services/settings.py", 
        title="Configurações", 
        icon=":material/settings:")   
    logout_page = st.Page(
        logout_user, 
        title="Sair", 
        icon=":material/logout:")
    user_pages = [dashboard, extracao]
    #admin_pages = [admin]
    account_pages = [settings, logout_page]
    st.logo("images/logo_gabarita.png")
    page_dict = {}
    if st.session_state.role in ["integ", "admin"]:
        page_dict["Menu"] = user_pages
    if len(page_dict) > 0:
        pg = st.navigation(page_dict | {"Conta": account_pages})
    else:
        pg = st.navigation([st.Page(login_page)])
    pg.run()

# Fluxo principal da aplicação
if st.session_state.logged_in:
    main_page()
else:
    login_page()