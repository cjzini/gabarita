import streamlit as st
import pandas as pd
import time
import csv
import io
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

# Função para converter questões para formato Excel completo (com todas as colunas)
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
        # Obter metadados
        metadados = questao.get('metadados', {})
        # Preparar a linha de dados
        linha = {
            'codigo': metadados.get('codigo', ''),
            'materia': metadados.get('materia', ''),
            'tema': metadados.get('tema', ''),
            'subtema': metadados.get('subtema', ''),
            'assunto': metadados.get('assunto', ''),
            'enunciado': questao.get('enunciado', ''),
            'alternativa1': alternativa1,
            'alternativa2': alternativa2,
            'alternativa3': alternativa3,
            'alternativa4': alternativa4,
            'alternativa5': alternativa5,
            'gabarito': questao.get('gabarito', ''),
            'resolucao': questao.get('resolucao', '')
        }
        dados.append(linha)
    # Criar um DataFrame com os dados
    df = pd.DataFrame(dados)
    # Criar um buffer para armazenar o arquivo Excel
    output = io.BytesIO()
    # Escrever o DataFrame no arquivo Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Questões')
    # Obter o conteúdo do Excel como bytes
    excel_data = output.getvalue()
    output.close()
    return excel_data

# Função para converter questões não aprovadas para Excel simplificado (apenas metadados)
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

# Função para converter questões para formato CSV
def converter_questoes_para_csv(questoes):
    """
    Converte questões do formato JSON para CSV com as colunas especificadas. 
    Args:
        questoes (list): Lista de questões no formato JSON
    Returns:
        str: String contendo dados CSV
    """
    # Criar um buffer de string para armazenar o CSV
    output = io.StringIO()
    # Definir as colunas do CSV
    fieldnames = [
        'codigo', 'materia', 'tema', 'subtema', 'assunto', 
        'enunciado', 'alternativa1', 'alternativa2', 'alternativa3', 
        'alternativa4', 'alternativa5', 'gabarito', 'resolucao'
    ]
    # Criar o escritor CSV
    writer = csv.DictWriter(output, fieldnames=fieldnames)  
    # Escrever o cabeçalho
    writer.writeheader()
    # Para cada questão, extrair os dados e escrever no CSV
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
        # Obter metadados
        metadados = questao.get('metadados', {})
        # Preparar a linha do CSV
        linha = {
            'codigo': metadados.get('codigo', ''),
            'materia': metadados.get('materia', ''),
            'tema': metadados.get('tema', ''),
            'subtema': metadados.get('subtema', ''),
            'assunto': metadados.get('assunto', ''),
            'enunciado': questao.get('enunciado', ''),
            'alternativa1': alternativa1,
            'alternativa2': alternativa2,
            'alternativa3': alternativa3,
            'alternativa4': alternativa4,
            'alternativa5': alternativa5,
            'gabarito': questao.get('gabarito', ''),
            'resolucao': questao.get('resolucao', '')
        }
        # Escrever a linha no CSV
        writer.writerow(linha)
    # Obter o conteúdo do CSV como string
    csv_string = output.getvalue()
    output.close()
    return csv_string
 
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
        progress_container.text(f"Processando item {i+1} de {len(json_data_selecionado)} - {item.get('materia', 'N/A')} - {item.get('assunto', 'N/A')}")        
        try:
            questao = gerar_lista_questoes([item])[0]
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
        # Salvar os dados no estado da sessão
        st.session_state.json_data = json_data
    if json_data:
        # Determinar o número máximo de questões com base no número de registros no arquivo
        max_registros = len(json_data)
        valor_padrao = min(3, max_registros)  # Valor padrão é 3 ou o número máximo de registros, o que for menor      
        st.success(f"Arquivo analisado com sucesso! {max_registros} registros encontrados.")       
        # Adiciona um controle deslizante para selecionar o número de questões
        # e salva o valor no estado da sessão
        st.session_state.num_questoes = st.slider(
            "Selecione o número de questões a gerar:", 
            min_value=1, 
            max_value=max_registros, 
            value=valor_padrao, 
            help="Quanto mais questões, mais tempo levará para gerar."
        )
        # Botão para gerar questões
        if st.button("Gerar Questões", key="btn_gerar_questoes"):
            # Chamar a função para gerar questões (não precisa de spinner, já tem barra de progresso)
            num_geradas = gerar_questoes()
            if num_geradas > 0:
                st.success(f"{num_geradas} questões geradas com sucesso!")
            st.session_state.geracao_realizada = True

# Mostrar questões só se já foram geradas
if st.session_state.get('geracao_realizada', False) and st.session_state.questoes_geradas:
    # Mostrar todas as questões geradas
    st.subheader("Questões geradas")
    # Exibir cada questão
    for i, questao in enumerate(st.session_state.questoes_geradas):
        # Criar uma chave única para cada questão
        questao_key = f"questao_{i}"       
        # Container para toda a questão
        question_container = st.container()     
        with question_container:
            # Usar colunas para mostrar título e status de aprovação lado a lado
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### Questão {i+1}")
            with col2:
                # Mostrar status de aprovação
                if questao.get('aprovado', False):
                    st.success("✓ Aprovada")
                else:
                    st.info("Pendente")        
            st.markdown(f"**Questão:** {questao.get('enunciado', 'N/A')}")           
            # Mostrar alternativas
            st.markdown(f"{questao.get('alternativa1', 'N/A')}")
            st.markdown(f"{questao.get('alternativa2', 'N/A')}")
            st.markdown(f"{questao.get('alternativa3', 'N/A')}")
            st.markdown(f"{questao.get('alternativa4', 'N/A')}")
            st.markdown(f"{questao.get('alternativa5', 'N/A')}")
            # Mostrar resposta correta em destaque
            st.success(f"**Resposta correta:** {questao.get('gabarito', 'N/A')}")          
            # Mostrar explicação 
            st.info(f"**Resolução:** {questao.get('resolucao', 'N/A')}")            
            # Mostrar metadados
            st.markdown("**Metadados:**")
            meta = questao.get('metadados', {})
            st.markdown(f"**Código:** {meta.get('codigo', 'N/A')} | **Matéria:** {meta.get('materia', 'N/A')} | **Tema:** {meta.get('tema', 'N/A')} | **Subtema:** {meta.get('subtema', 'N/A')} | **Assunto:** {meta.get('assunto', 'N/A')}")
            
            # Adicionar botão de aprovação
            btn_col1, btn_col2 = st.columns([3, 1])
            with btn_col2:
                # Se já estiver aprovada, mostrar botão para cancelar aprovação
                if questao.get('aprovado', False):
                    if st.button("Cancelar aprovação", key=f"btn_cancelar_{questao_key}"):
                        # Chamar a função de callback
                        cancelar_aprovacao(i)
                        st.rerun()  # Recarregar apenas os componentes
                else:
                    # Se não estiver aprovada, mostrar botão de aprovar
                    if st.button("Aprovar questão", key=f"btn_aprovar_{questao_key}"):
                        # Chamar a função de callback
                        aprovar_questao(i)
                        st.rerun()  # Recarregar apenas os componentes
            
            # Adiciona uma linha de separação entre as questões
            st.markdown("---")
    # Resumo e botões de download
    st.subheader("Resumo e download")
    # Contar questões aprovadas
    questoes_aprovadas = contar_questoes_aprovadas()
    total_questoes = len(st.session_state.questoes_geradas)
    if total_questoes > 0:
        # Mostrar resumo de aprovação
        percentual = (questoes_aprovadas / total_questoes) * 100 if total_questoes > 0 else 0
        st.info(f"Status de aprovação: {questoes_aprovadas} de {total_questoes} questões aprovadas ({percentual:.1f}%).")  
        # Botões para download em duas colunas
        dl_col1, dl_col2, dl_col3 = st.columns(3)
        # Botão para baixar todas as questões
        with dl_col1:
            # Gerar dados em CSV para todas as questões
            # csv_data = converter_questoes_para_csv(st.session_state.questoes_geradas)
            # st.download_button(
            #     label="Baixar todas as questões (CSV)",
            #     data=csv_data,
            #     file_name="questoes_geradas.csv",
            #     mime="text/csv"
            # )
            # Gerar dados em Excel para todas as questões
            excel_data = converter_questoes_para_excel(st.session_state.questoes_geradas)
            st.download_button(
                label="Baixar todas as questões (Excel)",
                data=excel_data,
                file_name="questoes_geradas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )   
        # Botão para baixar apenas questões aprovadas
        with dl_col2:
            # Filtrar apenas questões aprovadas
            questoes_aprovadas_lista = [q for q in st.session_state.questoes_geradas if q.get('aprovado', False)]         
            if questoes_aprovadas_lista:
                # Gerar dados em CSV apenas para questões aprovadas
                # csv_aprovadas = converter_questoes_para_csv(questoes_aprovadas_lista)
                # st.download_button(
                #     label="Baixar apenas aprovadas (CSV)",
                #     data=csv_aprovadas,
                #     file_name="questoes_aprovadas.csv",
                #     mime="text/csv"
                # )
                # Gerar dados em Excel apenas para questões aprovadas
                excel_aprovadas = converter_questoes_para_excel(questoes_aprovadas_lista)
                st.download_button(
                    label="Baixar apenas aprovadas (Excel)",
                    data=excel_aprovadas,
                    file_name="questoes_aprovadas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.write("Nenhuma questão aprovada ainda")
        # Botão para baixar apenas questões NÃO aprovadas em CSV
        with dl_col3:
            # Filtrar apenas questões NÃO aprovadas
            questoes_nao_aprovadas_lista = [q for q in st.session_state.questoes_geradas if not q.get('aprovado', False)]      
            if questoes_nao_aprovadas_lista:
                # Gerar dados em CSV apenas para questões NÃO aprovadas
                # csv_nao_aprovadas = converter_questoes_para_csv(questoes_nao_aprovadas_lista)
                # st.download_button(
                #     label="Baixar apenas não aprovadas (CSV)",
                #     data=csv_nao_aprovadas,
                #     file_name="questoes_nao_aprovadas.csv",
                #     mime="text/csv"
                # )
                # Gerar dados em Excel apenas para metadados das questões NÃO aprovadas
                excel_nao_aprovadas = converter_questoes_nao_aprovadas_para_excel(questoes_nao_aprovadas_lista)
                st.download_button(
                    label="Baixar apenas não aprovadas (Excel)",
                    data=excel_nao_aprovadas,
                    file_name="questoes_nao_aprovadas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.write("Todas as questões já foram aprovadas")