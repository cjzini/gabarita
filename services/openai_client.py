import streamlit as st
from openai import OpenAI
import json

openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

def gerar_questao(item_json, dificuldade):
    """
    Gera questões de múltipla escolha baseadas nos dados fornecidos.  
    Args:
        item_json (dict): Um dicionário contendo 'codigo', 'materia', 'tema', 'subtema' e 'assunto'
        dificuldade (str): Nível de dificuldade da questão ('fácil', 'médio' ou 'difícil')
    Returns:
        dict: Questão gerada em formato JSON
    """
    try:
        # Extrai informações do item
        codigo = item_json.get('codigo', '')
        materia = item_json.get('materia', '')
        tema = item_json.get('tema', '')
        subtema = item_json.get('subtema', '')
        assunto = item_json.get('assunto', '')     
        # Cria o prompt para a API
        prompt = f"""
        1. Objetivos
        Você é um gerador de questões para que alunos que estão em fase pré-vestibular possam usar essa questão para ajudá-los a estudar. 
        Vou apresentar a você: matéria, tema, subtema e assunto. 
        Com isso você deverá elaborar uma questão (enunciado) de múltipla escolha, com 5 alternativas possíveis. 
        Também deverá apresentar a alternativa correta (gabarito) e uma descrição da resolução da questão.
        A questão poderá ter 3 níveis de dificuldade: fácil, médio e difícil. Abaixo vou apresentar qual o nível de dificuldade da questão.

        Matéria: {materia}
        Tema: {tema}
        Subtema: {subtema}
        Assunto: {assunto}

        Nível de dificuldade: {dificuldade}

        2. Como deve ser a resposta
        A resposta deverá ser no seguinte formato JSON:
        {{
            "enunciado":"[enunciado]" 
            "alternativa1":"[alternativa 1]"
            "alternativa2":"[alternativa 2]"
            "alternativa3":"[alternativa 3]"
            "alternativa4":"[alternativa 4]"
            "alternativa5":"[alternativa 5]"
            "gabarito":"[gabarito]"
            "resolucao":"[resolucao]"
        }} 
        
        3. Alertas e avisos
        Certifique-se de que a resposta apontada da questão esteja correta. Se necessário faça várias checagens para que a resposta apontada seja a correta, isso é MUITO IMPORTANTE.
        O formato da exibição da alternativa deverá ser no seguinte formato: A) Descrição da alternativa 1
        O gabarito deverá ser apresentado na alternativa na forma literal, ou seja, repetindo a descrição da alternativa correta.
        Um exemplo do formato do gabarito: Descrição da alternativa 4
        A resolução deverá ser elaborada de maneira clara e interessante, de maneira que o aluno possa entender e aprender o conteúdo da questão.
        Quando houver fórmulas matemáticas, utilize o formato LaTeX para apresentá-las, ou seja, use sempre o símbolo $ para delimitar a fórmula matemática.
        É muito importante que todas as fórmulas estejam no formato LaTeX, se preciso faça uma checagem dupla para certificar-se disso.
        Exemplo de como apresentar o teorema de pitágoras: $a^2 + b^2 = c^2$.
        
        4. Contexto
        Elabore a questão e suas alternativas cuidadosamente, de maneira original e interessante para despertar a curiosidade e engajar o aluno a pensar para responder.       
        """     
        # Faz a chamada para a API da OpenAI
        # O modelo gpt-4o é o mais recente da OpenAI (lançado após seu conhecimento de corte)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}  # Garante que a resposta seja em formato JSON
        )
        # Extrai e retorna o JSON da resposta
        resultado = json.loads(response.choices[0].message.content)
        # Adiciona metadados do conteúdo original
        resultado["metadados"] = {
            "codigo": codigo,
            "materia": materia,
            "tema": tema,
            "subtema": subtema,
            "assunto": assunto,
            "dificuldade": dificuldade    
        }  
        return resultado
    except Exception as e:
        print(f"Erro ao gerar questão: {str(e)}")
        # Em caso de erro, definir valores padrão para evitar problemas de referência
        if not 'codigo' in locals(): codigo = "N/A" 
        if not 'materia' in locals(): materia = "N/A"
        if not 'tema' in locals(): tema = "N/A"
        if not 'subtema' in locals(): subtema = "N/A"
        if not 'assunto' in locals(): assunto = "N/A"            
        return {
            "erro": f"Não foi possível gerar uma questão: {str(e)}",
            "metadados": {
                "codigo": codigo,
                "materia": materia,
                "tema": tema,
                "subtema": subtema,
                "assunto": assunto
            }
        }

def gerar_lista_questoes(lista_json, dificuldade):
    """
    Gera questões de múltipla escolha para uma lista de itens JSON.  
    Args:
        lista_json (list): Lista de dicionários com os dados para geração de questões
    Returns:
        list: Lista de questões geradas em formato JSON
    """
    resultados = []
    for item in lista_json:
        questao = gerar_questao(item, dificuldade)
        resultados.append(questao)      
    return resultados