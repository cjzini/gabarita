import streamlit as st
import pandas as pd
import json

st.title('Extração do Arquivo')
st.write("Faça o upload de um arquivo Excel (.xlsx) ou CSV (.csv)")

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
    if st.button("Processar Arquivo"):
        with st.spinner("Processando..."):
            json_data = process_file(uploaded_file)

        if json_data:
            # Display the JSON data
            st.subheader("Resultado em JSON:")
            
            # Convert to JSON string with proper indentation and formatting
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
            
            # Display the JSON in a code block
            st.json(json_data)
            
            # Add a download button for the JSON
            st.download_button(
                label="Baixar JSON",
                data=json_str,
                file_name="dados_convertidos.json",
                mime="application/json"
            )
            
            # Display information about the conversion
            st.success(f"Conversão concluída! {len(json_data)} registros encontrados.")
else:
    st.info("Por favor, faça o upload de um arquivo Excel (.xlsx) ou CSV (.csv).")
    
    # Example of expected format
    st.subheader("Formato esperado do arquivo:")
    
    # Create example data
    example_data = {
        "código": ["001", "002", "003"],
        "matéria": ["Matemática", "Português", "Ciências"],
        "tema": ["Álgebra", "Gramática", "Biologia"],
        "subtema": ["Equações", "Sintaxe", "Células"],
        "assunto": ["Equações do 2º grau", "Análise sintática", "Mitocôndria"]
    }
    
    example_df = pd.DataFrame(example_data)
    
    # Display as table
    st.table(example_df)