import streamlit as st
import os
from supabase import create_client, Client

# Inicializar cliente Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"] if "SUPABASE_URL" in st.secrets else os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"] if "SUPABASE_KEY" in st.secrets else os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = st.secrets["SUPABASE_SERVICE_KEY"] if "SUPABASE_SERVICE_KEY" in st.secrets else os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_connection(admin=False):
    """Retorna uma conexão com o Supabase real
    
    Args:
        admin (bool, optional): Se True, usará a chave de serviço para operações administrativas.
        
    Returns:
        Client: Cliente de conexão com o Supabase
    """
    if admin:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    else:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def obter_materia_id(materia, tema, subtema, assunto):
    """
    Verifica se a matéria já existe e retorna seu ID.
    Caso não exista, cria um novo registro e retorna o ID criado.
    
    Args:
        materia (str): Nome da matéria
        tema (str): Nome do tema
        subtema (str): Nome do subtema
        assunto (str): Nome do assunto
        
    Returns:
        int: ID da matéria encontrada ou criada
    """
    # Primeiro, verificar se já existe uma matéria com esses dados
    try:
        # Realizar a consulta para verificar se a matéria existe
        query = (
            supabase.table("materias")
            .select("id")
            .eq("materia", materia)
            .eq("tema", tema)
            .eq("subtema", subtema)
            .eq("assunto", assunto)
        )
        
        resultado = query.execute()
        
        # Se encontrou pelo menos um registro
        if resultado.data and len(resultado.data) > 0:
            return resultado.data[0]["id"]
            
        # Se não encontrou, criar um novo registro
        novo_registro = {
            "materia": materia,
            "tema": tema,
            "subtema": subtema,
            "assunto": assunto
        }
        
        resultado_insercao = (
            supabase.table("materias")
            .insert(novo_registro)
            .execute()
        )
        
        # Retornar o ID do registro inserido
        if resultado_insercao.data and len(resultado_insercao.data) > 0:
            return resultado_insercao.data[0]["id"]
        else:
            raise Exception("Falha ao inserir novo registro de matéria")
            
    except Exception as e:
        # Registrar o erro e propagar a exceção
        print(f"Erro ao obter ou criar matéria: {str(e)}")
        raise e

def salvar_questao(questao, user_id=None):
    """
    Salva uma questão no banco de dados.
    
    Args:
        questao (dict): Dicionário com os dados da questão
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    try:
        # Obter metadados
        metadados = questao.get('metadados', {})
        
        # Primeiro inserir ou obter o ID da matéria
        id_materia = obter_materia_id(
            metadados.get('materia', ''),
            metadados.get('tema', ''),
            metadados.get('subtema', ''),
            metadados.get('assunto', '')
        )
        
        # Extrair alternativas (remover a letra do início, ex: "A) Alternativa 1" -> "Alternativa 1")
        alternativa1 = questao.get('alternativa1', '')
        if len(alternativa1) > 3 and alternativa1[0].isalpha() and alternativa1[1:3] == ") ":
            alternativa1 = alternativa1[3:]
        alternativa2 = questao.get('alternativa2', '')
        if len(alternativa2) > 3 and alternativa2[0].isalpha() and alternativa2[1:3] == ") ":
            alternativa2 = alternativa2[3:]
        alternativa3 = questao.get('alternativa3', '')
        if len(alternativa3) > 3 and alternativa3[0].isalpha() and alternativa3[1:3] == ") ":
            alternativa3 = alternativa3[3:]
        alternativa4 = questao.get('alternativa4', '')
        if len(alternativa4) > 3 and alternativa4[0].isalpha() and alternativa4[1:3] == ") ":
            alternativa4 = alternativa4[3:]
        alternativa5 = questao.get('alternativa5', '')
        if len(alternativa5) > 3 and alternativa5[0].isalpha() and alternativa5[1:3] == ") ":
            alternativa5 = alternativa5[3:]
        gabarito = questao.get('gabarito', '')
        if len(gabarito) > 3 and gabarito[0].isalpha() and gabarito[1:3] == ") ":
            gabarito = gabarito[3:] 

        # Preparar o registro para inserção
        registro_questao = {
            "codigo": metadados.get('codigo', ''),
            "enunciado": questao.get('enunciado', ''),
            "alternativa1": alternativa1,
            "alternativa2": alternativa2,
            "alternativa3": alternativa3,
            "alternativa4": alternativa4,
            "alternativa5": alternativa5,
            "gabarito": gabarito,
            "resolucao": questao.get('resolucao', ''),
            "dificuldade": metadados.get('dificuldade', ''),
            "id_materia": id_materia
        }
        # Adicionar o ID do usuário que está criando a questão, se fornecido
        if user_id:
            registro_questao["id_user"] = user_id
        
        # Inserir na tabela questoes
        resultado = (
            supabase.table("questoes")
            .insert(registro_questao)
            .execute()
        )

        # Verificar se a inserção foi bem-sucedida
        if resultado.data and len(resultado.data) > 0:
            return True
        else:
            return False  
           
    except Exception as e:
        # Registrar o erro
        print(f"Erro ao salvar questão: {str(e)}")
        return False

def salvar_questoes_aprovadas(questoes, user_id=None):
    """
    Salva uma lista de questões aprovadas no banco de dados.

    Args:
        questoes (list): Lista de questões aprovadas 
    Returns:
        tuple: (número de questões salvas com sucesso, número total de questões)
    """
    # Contar questões salvas com sucesso
    questoes_salvas = 0
    total_questoes = len(questoes)

    # Para cada questão, tentar salvar
    for questao in questoes:
        if salvar_questao(questao, user_id):
            questoes_salvas += 1

    return (questoes_salvas, total_questoes)

def is_admin_user(user_id):
    """
    Verifica se o usuário tem perfil de administrador na tabela profiles.
    
    Args:
        user_id (str): ID do usuário   
    Returns:
        bool: True se o usuário for admin, False caso contrário
    """
    try:
        # Conectar ao Supabase
        client = get_supabase_connection()
        
        # Consultar a tabela profiles para o usuário especificado
        response = client.table('profiles').select('role').eq('id', user_id).execute()
        
        # Verificar se o usuário tem role de admin
        if response.data and len(response.data) > 0:
            return response.data[0].get('role') == 'admin'
        return False
    except Exception as e:
        print(f"Erro ao verificar perfil admin: {str(e)}")
        return False

def listar_usuarios():
    """
    Lista todos os usuários cadastrados no sistema, combinando informações da
    tabela de autenticação e da tabela de perfis.
    
    Returns:
        list: Lista de usuários com seus dados
    """
    # Conectar ao Supabase com permissões de admin
    client = get_supabase_connection(admin=True)
    
    # Método 1: Tentar obter a lista de usuários diretamente via API Admin do Supabase
    try:
        # Obter todos os usuários do sistema
        auth_users = client.auth.admin.list_users()
        
        # Obter os perfis dos usuários
        profiles_response = client.table('profiles').select('*').execute()
        profiles_by_id = {profile['id']: profile for profile in profiles_response.data}
        
        # Combinar os dados
        usuarios = []
        # Verificar o formato do resultado (pode ser um objeto com propriedade 'users' ou uma lista direta)
        if hasattr(auth_users, 'users'):
            user_list = auth_users.users
        else:
            user_list = auth_users
            
        for user in user_list:
            user_id = user.id
            profile = profiles_by_id.get(user_id, {})
            
            usuarios.append({
                "id": user_id,
                "nome": profile.get("full_name", "Não informado"),
                "username": profile.get("username", "Não informado"),
                "email": user.email,
                "perfil": profile.get("role", "user"),
                "avatar_url": profile.get("avatar_url"),
                "criado_em": user.created_at,
                "confirmado": user.email_confirmed_at is not None
            })
            
        return usuarios
    except Exception as api_error:
        print(f"Erro ao listar usuários via API: {str(api_error)}")

def criar_usuario(nome, email, senha, perfil="user", username=None):
    """
    Cria um novo usuário usando o Supabase Auth e insere seus dados na tabela profiles.
    Se o usuário já existir, atualiza seus dados de perfil.
    
    Args:
        nome (str): Nome completo do usuário
        email (str): Endereço de email do usuário
        senha (str): Senha para o novo usuário
        perfil (str): Perfil do usuário ('admin' ou 'user')
        username (str, optional): Nome de usuário (se não for fornecido, usa a parte local do email)
        
    Returns:
        tuple: (sucesso, mensagem)
    """
    try:
        # Conectar ao Supabase com permissões de admin
        client = get_supabase_connection(admin=True)
        
        # Se o nome de usuário não for fornecido, use a parte local do email
        if not username:
            username = email.split('@')[0]
        
        # Verificar se o usuário já existe
        user_exists = False
        existing_user = None
        
        # Método 1: Tentar obter todos os usuários e filtrar por email
        try:
            all_users = client.auth.admin.list_users()
            user_list = all_users.users if hasattr(all_users, 'users') else all_users
            
            for user in user_list:
                if user.email == email:
                    existing_user = [user]
                    user_exists = True
                    break
        except Exception as verify_error:
            # Se houver erro na verificação, vamos tentar o método alternativo
            print(f"Erro ao verificar usuário: {str(verify_error)}")

        # Processar a criação ou atualização do usuário
        if user_exists and existing_user:
            # Atualizar o usuário existente
            user_id = existing_user[0].id
            
            # Atualizar a senha se foi fornecida
            if senha:
                client.auth.admin.update_user_by_id(
                    user_id,
                    {"password": senha}
                )
                
            mensagem = "Usuário existente atualizado."
        else:
            # Criar um novo usuário com o método de convite
            # Este método cria o usuário e já envia o email de confirmação
            user_response = client.auth.admin.invite_user_by_email(email)
            user_id = user_response.user.id
            
            # Definir a senha do usuário
            client.auth.admin.update_user_by_id(
                user_id,
                {"password": senha}
            )
            
            mensagem = "Novo usuário criado e email de confirmação enviado."
        
        # Verificar se o perfil já existe
        profile_check = client.table('profiles').select('*').eq('id', user_id).execute()
        
        # Preparar os dados do perfil
        profile_data = {
            "username": username,
            "full_name": nome,
            "role": perfil,
            "avatar_url": None  # Valor padrão para avatar_url
        }
        
        if profile_check.data and len(profile_check.data) > 0:
            # Atualizar o perfil existente
            profile_response = client.table('profiles').update(profile_data).eq('id', user_id).execute()
            mensagem += " Perfil atualizado."
        else:
            # Criar um novo perfil
            profile_data["id"] = user_id  # Adicionar o ID apenas para inserção
            profile_response = client.table('profiles').insert(profile_data).execute()
            mensagem += " Perfil criado."
        
        return True, mensagem
    except Exception as e:
        error_msg = str(e)
        print(f"Erro ao criar usuário: {error_msg}")
        return False, f"Erro ao criar usuário: {error_msg}"