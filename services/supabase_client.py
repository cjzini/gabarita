import streamlit as st
import os
from supabase import create_client, Client

# Inicializar cliente Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_connection():
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

def salvar_questao(questao):
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
        
        # Processar alternativas (remover letras no início, se houver)
        alternativas_processadas = []
        for alt in questao.get('alternativas', []):
            # Remover prefixos como "A)", "B)", etc. se existirem
            if ') ' in alt:
                alternativas_processadas.append(alt.split(') ', 1)[1])
            else:
                alternativas_processadas.append(alt)
                
        # Preencher até 5 alternativas
        while len(alternativas_processadas) < 5:
            alternativas_processadas.append('')
        
        # Preparar o registro para inserção
        registro_questao = {
            "codigo": metadados.get('codigo', ''),
            "enunciado": questao.get('questao', ''),
            "alternativa1": alternativas_processadas[0],
            "alternativa2": alternativas_processadas[1],
            "alternativa3": alternativas_processadas[2],
            "alternativa4": alternativas_processadas[3],
            "alternativa5": alternativas_processadas[4],
            "resposta": questao.get('resposta_correta', ''),
            "explicacao": questao.get('explicacao', ''),
            "dificuldade": questao.get('dificuldade', 'médio'),
            "id_materia": id_materia
        }
        
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

def salvar_questoes_aprovadas(questoes):
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
        if salvar_questao(questao):
            questoes_salvas += 1
    
    return (questoes_salvas, total_questoes)