import streamlit as st
import time
import pandas as pd
import io
from services.openai_client import gerar_lista_questoes
from services.supabase_client import salvar_questoes_aprovadas


# Função para aprovar uma questão
def aprovar_questao(indice):
    """Marca uma questão como aprovada"""
    if 0 <= indice < len(st.session_state.questoes_geradas):
        st.session_state.questoes_geradas[indice]['aprovado'] = True

# Função para cancelar aprovação
def cancelar_aprovacao(indice):
    if 0 <= indice < len(st.session_state.questoes_geradas):
        st.session_state.questoes_geradas[indice]['aprovado'] = False

# Função para aprovar todas as questões de uma vez
def aprovar_todas_questoes():
    for i in range(len(st.session_state.questoes_geradas)):
        st.session_state.questoes_geradas[i]['aprovado'] = True

# Função para contar questões aprovadas
def contar_questoes_aprovadas():
    return sum(1 for q in st.session_state.questoes_geradas if q.get('aprovado', False))

def editar_questao(indice, dados_editados):
    """
    Atualiza uma questão com os dados editados.  
    Args:
        indice (int): Índice da questão a ser editada
        dados_editados (dict): Dicionário com os novos dados da questão
    """
    if 'questoes_geradas' not in st.session_state or indice >= len(st.session_state.questoes_geradas):
        return False  
    # Atualizar os campos da questão com os dados editados
    questao = st.session_state.questoes_geradas[indice]
    questao['enunciado'] = dados_editados['enunciado']
    questao['alternativa1'] = dados_editados['alternativa1']
    questao['alternativa2'] = dados_editados['alternativa2']
    questao['alternativa3'] = dados_editados['alternativa3']
    questao['alternativa4'] = dados_editados['alternativa4']
    questao['alternativa5'] = dados_editados['alternativa5']
    questao['gabarito'] = dados_editados['gabarito']
    questao['resolucao'] = dados_editados['resolucao']
    # Atualizar metadados se necessário
    if 'metadados' in dados_editados:
        questao['metadados'] = dados_editados['metadados']
    # Salvar a questão atualizada de volta na lista
    st.session_state.questoes_geradas[indice] = questao
    return True

def regenerar_questao(indice):
    """
    Regenera uma única questão mantendo as demais inalteradas.
    Args:
        indice (int): Índice da questão a ser regenerada
    Returns:
        bool: True se a questão foi regenerada com sucesso, False caso contrário
    """
    # Verificar se o índice é válido
    if indice < 0 or indice >= len(st.session_state.questoes_geradas):
        return False
    # Obter o item original do JSON dos dados carregados
    if not st.session_state.json_data or indice >= len(st.session_state.json_data):
        return False   
    # Obter o item correspondente do JSON
    item = st.session_state.json_data[indice]
    # Criar um container para mostrar o progresso
    progress_container = st.empty()
    try:
        # Informar que estamos regenerando
        progress_container.info(f"Regenerando questão {indice+1}...")
        # Usar o nível de dificuldade atual da sessão
        questao = gerar_lista_questoes([item], st.session_state.dificuldade)[0]
        # Substituir a questão antiga pela nova
        st.session_state.questoes_geradas[indice] = questao
        # Pequena pausa para não sobrecarregar a API
        time.sleep(0.5)
        # Limpar indicador de progresso
        progress_container.empty()
        return True
    except Exception as e:
        progress_container.error(f"Erro ao regenerar questão: {str(e)}")
        time.sleep(2)  # Mostrar o erro por alguns segundos
        progress_container.empty()
        return False
    
def converter_questoes_para_excel(questoes):
    """
    Converte questões do formato JSON para Excel com as colunas completas.    
    Args:
        questoes (list): Lista de questões no formato JSON
    Returns:
        bytes: Arquivo Excel em formato bytes
    """
    # Criar listas para armazenar os dados
    dados = []
    # Para cada questão, extrair os dados
    for questao in questoes:
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
        # Obter metadados
        metadados = questao.get('metadados', {})
        # Preparar a linha de dados
        linha = {
            'codigo': metadados.get('codigo', ''),
            'materia': metadados.get('materia', ''),
            'tema': metadados.get('tema', ''),
            'subtema': metadados.get('subtema', ''),
            'assunto': metadados.get('assunto', ''),
            'dificuldade': metadados.get('dificuldade', ''),
            'enunciado': questao.get('enunciado', ''),
            'alternativa1': alternativa1,
            'alternativa2': alternativa2,
            'alternativa3': alternativa3,
            'alternativa4': alternativa4,
            'alternativa5': alternativa5,
            'gabarito': gabarito,
            'resolucao': questao.get('resolucao', '')
        }
        dados.append(linha)
    # Criar um DataFrame com os dados
    df = pd.DataFrame(dados)
    # Escapes the unicode characters if they exist
    #df = df.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
    #df = df.apply(lambda col: col.map(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x))
    # Criar um buffer para armazenar o arquivo Excel
    output = io.BytesIO()
    # Escrever o DataFrame no arquivo Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Questões')
    # Obter o conteúdo do Excel como bytes
    excel_data = output.getvalue()
    output.close()
    return excel_data

def converter_questoes_nao_aprovadas_para_excel(questoes):
    """
    Converte questões não aprovadas para Excel com apenas os campos de metadados.
    Args:
        questoes (list): Lista de questões não aprovadas no formato JSON
    Returns:
        bytes: Arquivo Excel em formato bytes
    """
    # Criar listas para armazenar os dados
    dados = []
    # Para cada questão, extrair apenas os metadados
    for questao in questoes:
        # Obter metadados
        metadados = questao.get('metadados', {})
        # Preparar a linha de dados
        linha = {
            'codigo': metadados.get('codigo', ''),
            'materia': metadados.get('materia', ''),
            'tema': metadados.get('tema', ''),
            'subtema': metadados.get('subtema', ''),
            'assunto': metadados.get('assunto', '')
        }
        
        dados.append(linha)
    # Criar um DataFrame com os dados
    df = pd.DataFrame(dados)
    # Criar um buffer para armazenar o arquivo Excel
    output = io.BytesIO()
    # Escrever o DataFrame no arquivo Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Questões não aprovadas')
    # Obter o conteúdo do Excel como bytes
    excel_data = output.getvalue()
    output.close()    
    return excel_data

# Função para gerar questões
def gerar_questoes():
    # Marcar que a geração foi realizada
    st.session_state.geracao_realizada = True   
    # Limitar o número de questões ao selecionado pelo usuário
    json_data_selecionado = st.session_state.json_data[:st.session_state.num_questoes]   
    # Limpar questões anteriores
    st.session_state.questoes_geradas = []    
    # Criar um container para mostrar o progresso
    progress_container = st.empty()
    progress_bar = st.progress(0)   
    # Gerar as questões
    for i, item in enumerate(json_data_selecionado):
        # Atualizar progresso
        progresso = (i + 1) / len(json_data_selecionado)
        progress_bar.progress(progresso)
        progress_container.text(f"Processando item {i+1} de {len(json_data_selecionado)} - {item.get('materia', 'N/A')} - {item.get('assunto', 'N/A')}  - Dificuldade: {st.session_state.dificuldade}")        
        try:
            questao = gerar_lista_questoes([item], st.session_state.dificuldade)[0]
            st.session_state.questoes_geradas.append(questao)
            # Pequena pausa para não sobrecarregar a API
            time.sleep(0.5)
        except Exception as e:
            st.error(f"Erro ao gerar questão para o item {i+1}: {str(e)}")   
    # Limpar indicadores de progresso
    progress_container.empty()
    progress_bar.empty()            
    # Retornar o número de questões geradas
    return len(st.session_state.questoes_geradas)

def process_file(file):
    try:
        # Detect file type and read accordingly
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        elif file.name.endswith('.csv'):
            # Try to read with different encodings and delimiters
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file, encoding='latin1')
                except:
                    df = pd.read_csv(file, encoding='ISO-8859-1')           
            # If semicolon is the delimiter, parse again
            if len(df.columns) == 1 and df.columns[0].count(';') > 0:
                file.seek(0)  # Go back to the beginning of the file
                df = pd.read_csv(file, sep=';')
        else:
            st.error("Formato de arquivo não suportado.")
            return None
        # Expected column names
        expected_columns = ['codigo', 'materia', 'tema', 'subtema', 'assunto']
        # Check if file has the required columns or if we need to rename columns
        if not all(col in df.columns for col in expected_columns):
            # If the file has the right number of columns but wrong names
            if len(df.columns) >= len(expected_columns):
                # Rename the first 5 columns to the expected names
                column_mapping = {df.columns[i]: expected_columns[i] for i in range(min(len(df.columns), len(expected_columns)))}
                df = df.rename(columns=column_mapping)
            else:
                st.error(f"O arquivo não contém todas as colunas necessárias. Colunas esperadas: {', '.join(expected_columns)}")
                return None                
        # Convert DataFrame to list of dictionaries (JSON-like format)
        result = df.to_dict(orient='records')
        return result
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
        return None