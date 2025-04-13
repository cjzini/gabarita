import streamlit as st
import pandas as pd
import time
from services.openai_client import gerar_lista_questoes

# Inicializa o estado da sessão para contar questões aprovadas
if 'questoes_geradas' not in st.session_state:
    st.session_state.questoes_geradas = []  
# Indica se a geração de questões já foi realizada
if 'geracao_realizada' not in st.session_state:
    st.session_state.geracao_realizada = False   
# Armazena o número de questões selecionado
if 'num_questoes' not in st.session_state:
    st.session_state.num_questoes = 3   
# Armazena os dados do arquivo em formato JSON
if 'json_data' not in st.session_state:
    st.session_state.json_data = None

# Função para atualizar o status de aprovação de uma questão
def aprovar_questao(indice):
    if 0 <= indice < len(st.session_state.questoes_geradas):
        st.session_state.questoes_geradas[indice]['aprovado'] = True 

# Função para cancelar aprovação
def cancelar_aprovacao(indice):
    if 0 <= indice < len(st.session_state.questoes_geradas):
        st.session_state.questoes_geradas[indice]['aprovado'] = False 

# Função para contar questões aprovadas
def contar_questoes_aprovadas():
    return sum(1 for q in st.session_state.questoes_geradas if q.get('aprovado', False))
 
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
        progress_container.text(f"Processando item {i+1} de {len(json_data_selecionado)} - {item.get('matéria', 'N/A')} - {item.get('assunto', 'N/A')}")        
        try:
            questao = gerar_questoes_para_lista([item])[0]
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

st.title('Geração de Questões')
st.write("Faça o upload de um arquivo Excel (.xlsx) ou CSV (.csv)")

# Armazena o número de questões selecionado
if 'num_questoes' not in st.session_state:
    st.session_state.num_questoes = 3

# File upload component
uploaded_file = st.file_uploader("Escolha um arquivo", type=["xlsx", "csv"])

# Function to process the uploaded file
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
    
# Display content based on uploaded file
if uploaded_file is not None:
    st.write("Arquivo carregado com sucesso!") 
    # Add button to process file
    with st.spinner("Processando Arquivo..."):
        json_data = process_file(uploaded_file)
    if json_data:
        # Determinar o número máximo de questões com base no número de registros no arquivo
        max_registros = len(json_data)
        valor_padrao = min(3, max_registros)  # Valor padrão é 3 ou o número máximo de registros, o que for menor      
        st.success(f"Arquivo analisado com sucesso! {max_registros} registros encontrados.")
        # Adiciona um controle deslizante para selecionar o número de questões
        num_questoes = st.slider("Selecione o número de questões a gerar:", 
                                min_value=1, max_value=max_registros, value=valor_padrao, 
                                help="Quanto mais questões, mais tempo levará para gerar.")
        # Add button to process file and generate questions
        if st.button("Gerar Questões"):     
            # Limitar o número de questões ao selecionado pelo usuário
            json_data_selecionado = json_data[:num_questoes]
            # Gerar questões usando a API da OpenAI
            # st.subheader("Gerando questões...")
            # Criar um container para mostrar o progresso
            progress_container = st.empty()
            progress_bar = st.progress(0)           
            # Processar itens um por um para mostrar progresso
            questoes_geradas = []
            for i, item in enumerate(json_data_selecionado):
                # Atualizar progresso
                progresso = (i + 1) / len(json_data_selecionado)
                progress_bar.progress(progresso)
                progress_container.text(f"Processando item {i+1} de {len(json_data_selecionado)} - {item.get('materia', 'N/A')} - {item.get('assunto', 'N/A')}")               
                # Gerar questão para este item
                try:
                    questao = gerar_lista_questoes([item])[0]
                    questoes_geradas.append(questao)                   
                    # Mostrar a questão que acabou de ser gerada
                    st.markdown(f"### Questão {i+1}")
                    st.markdown(f"**Enunciado:** {questao.get('enunciado', 'N/A')}")                  
                    # Mostrar alternativas
                    st.markdown(f"A) {questao.get('alternativa1', 'N/A')}")
                    st.markdown(f"B) {questao.get('alternativa2', 'N/A')}")
                    st.markdown(f"C) {questao.get('alternativa3', 'N/A')}")
                    st.markdown(f"D) {questao.get('alternativa4', 'N/A')}")
                    st.markdown(f"E) {questao.get('alternativa5', 'N/A')}")
                    # alternativas = questao.get('alternativas', [])
                    # for alt in alternativas:
                    #     st.markdown(f"{alt}")                      
                    # Mostrar resposta correta em destaque
                    st.success(f"**Resposta correta:** {questao.get('gabarito', 'N/A')}")                   
                    # Mostrar explicação 
                    st.info(f"**Resolução:** {questao.get('resolucao', 'N/A')}")                    
                    # Mostrar metadados
                    st.markdown("**Metadados:**")
                    meta = questao.get('metadados', {})
                    st.markdown(f"**Código:** {meta.get('codigo', 'N/A')} | **Matéria:** {meta.get('materia', 'N/A')} | **Tema:** {meta.get('tema', 'N/A')} | **Subtema:** {meta.get('subtema', 'N/A')} | **Assunto:** {meta.get('assunto', 'N/A')}")                    
                    # Adiciona uma linha de separação entre as questões
                    st.markdown("---")               
                    # Pequena pausa para não sobrecarregar a API
                    time.sleep(0.5)                 
                except Exception as e:
                    st.error(f"Erro ao gerar questão para o item {i+1}: {str(e)}")           
            # Limpar indicadores de progresso
            progress_container.empty()
            progress_bar.empty()
            st.success(f"Processo concluído! {len(questoes_geradas)} questões foram geradas com sucesso.")       
else:
    st.info("Por favor, faça o upload de um arquivo Excel (.xlsx) ou CSV (.csv).")