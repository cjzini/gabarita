import streamlit as st
import utils.question_utils as qu
from services.supabase_client import salvar_questoes_aprovadas

st.title('Geração de Questões')
st.write("Faça o upload de um arquivo Excel (.xlsx) ou CSV (.csv)")

# Armazena o número de questões selecionado
if 'num_questoes' not in st.session_state:
    st.session_state.num_questoes = 3

# File upload component
uploaded_file = st.file_uploader("Escolha um arquivo", type=["xlsx", "csv"])
    
# Display content based on uploaded file
if uploaded_file is not None:
    st.write("Arquivo carregado com sucesso!") 
    # Add button to process file
    with st.spinner("Processando Arquivo..."):
        json_data = qu.process_file(uploaded_file)
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
        # Seletor de nível de dificuldade usando radio buttons
        st.write("Selecione o nível de dificuldade:")
        st.session_state.dificuldade = st.radio(
            "Nível de dificuldade",
            options=["fácil", "médio", "difícil"],
            index=1,  # médio como padrão
            help="Escolha o nível de complexidade das questões geradas.",
            horizontal=True,  # Mostra os botões horizontalmente
            label_visibility="collapsed"  # Oculta o rótulo principal pois já temos um título acima
        )
        # Botão para gerar questões
        if st.button("Gerar Questões", key="btn_gerar_questoes"):
            # Chamar a função para gerar questões (não precisa de spinner, já tem barra de progresso)
            num_geradas = qu.gerar_questoes()
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
            st.markdown(f"**Código:** {meta.get('codigo', 'N/A')} | **Matéria:** {meta.get('materia', 'N/A')} | **Tema:** {meta.get('tema', 'N/A')} | **Subtema:** {meta.get('subtema', 'N/A')} | **Assunto:** {meta.get('assunto', 'N/A')} | **Dificuldade:** {meta.get('dificuldade', 'N/A')}")
            
            # Estado de edição para esta questão
            if f"edit_mode_{i}" not in st.session_state:
                st.session_state[f"edit_mode_{i}"] = False
            # Estado para armazenar os dados da questão durante a edição
            if f"edit_data_{i}" not in st.session_state:
                st.session_state[f"edit_data_{i}"] = {
                    'enunciado': questao.get('enunciado', ''),
                    'alternativa1': questao.get('alternativa1', ''),
                    'alternativa2': questao.get('alternativa2', ''),
                    'alternativa3': questao.get('alternativa3', ''),
                    'alternativa4': questao.get('alternativa4', ''),
                    'alternativa5': questao.get('alternativa5', ''),
                    'gabarito': questao.get('gabarito', ''),
                    'resolucao': questao.get('resolucao', '')
                }
            # Modo de edição
            if st.session_state[f"edit_mode_{i}"]:
                # Formulário de edição
                with st.form(key=f"edit_form_{i}"):
                    st.subheader("Editar Questão")                 
                    # Campo para editar o enunciado
                    enunciado_editado = st.text_area(
                        "Enunciado da questão",
                        value=st.session_state[f"edit_data_{i}"]['enunciado'],
                        key=f"edit_enunciado_{i}"
                    )               
                    # Campos para editar alternativas
                    alternativa1_editada = st.text_input(
                        "Alternativa A", 
                        value=st.session_state[f"edit_data_{i}"]['alternativa1'],
                        key=f"edit_alt1_{i}"
                    )
                    alternativa2_editada = st.text_input(
                        "Alternativa B", 
                        value=st.session_state[f"edit_data_{i}"]['alternativa2'],
                        key=f"edit_alt2_{i}"
                    )
                    alternativa3_editada = st.text_input(
                        "Alternativa C", 
                        value=st.session_state[f"edit_data_{i}"]['alternativa3'],
                        key=f"edit_alt3_{i}"
                    )
                    alternativa4_editada = st.text_input(
                        "Alternativa D", 
                        value=st.session_state[f"edit_data_{i}"]['alternativa4'],
                        key=f"edit_alt4_{i}"
                    )
                    alternativa5_editada = st.text_input(
                        "Alternativa E", 
                        value=st.session_state[f"edit_data_{i}"]['alternativa5'],
                        key=f"edit_alt5_{i}"
                    )      
                    # Campo para editar a resposta correta
                    gabarito_editado = st.text_input(
                        "Gabarito",
                        value=st.session_state[f"edit_data_{i}"]['gabarito'],
                        key=f"edit_gabarito_{i}"
                    )
                    # Campo para editar a explicação
                    resolucao_editada = st.text_area(
                        "Resolução",
                        value=st.session_state[f"edit_data_{i}"]['resolucao'],
                        key=f"edit_resolucao_{i}"
                    )              
                    edt_col1, edt_col2, edt_col3 = st.columns([1, 2, 2])
                    # Coluna para os botões de ação
                    with edt_col1:
                        # Botões de salvar e cancelar
                        col1, col2 = st.columns(2)
                        with col1:
                            submit_button = st.form_submit_button("Salvar alterações")
                        with col2:
                            cancel_button = st.form_submit_button("Cancelar")               
                        if submit_button:
                            # Atualizar os dados da questão com os valores editados
                            dados_editados = {
                                'enunciado': enunciado_editado,
                                'alternativa1': alternativa1_editada,
                                'alternativa2': alternativa2_editada,
                                'alternativa3': alternativa3_editada,
                                'alternativa4': alternativa4_editada,
                                'alternativa5': alternativa5_editada,
                                'gabarito': gabarito_editado,
                                'resolucao': resolucao_editada
                            }
                            # Chamar a função para atualizar a questão
                            qu.editar_questao(i, dados_editados)
                            # Sair do modo de edição
                            st.session_state[f"edit_mode_{i}"] = False
                            st.rerun()
                        if cancel_button:
                            # Sair do modo de edição sem salvar
                            st.session_state[f"edit_mode_{i}"] = False
                            st.rerun()           
            else:
                dsg_col1, dsg_col2, dsg_col3, dsg_col4, dsg_col5, dsg_col6 = st.columns([2, 1, 1, 1, 1, 1])
                # Coluna para os botões de ação
                with dsg_col1:
                    # Adicionar botões de ação (editar e aprovar/cancelar aprovação)
                    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
                    # Botão de edição
                    with btn_col1:
                        if st.button(" Editar questão ", key=f"btn_editar_{questao_key}"):
                            # Atualizar os dados de edição com os valores atuais da questão
                            st.session_state[f"edit_data_{i}"] = {
                                'enunciado': questao.get('enunciado', ''),
                                'alternativa1': questao.get('alternativa1', ''),
                                'alternativa2': questao.get('alternativa2', ''),
                                'alternativa3': questao.get('alternativa3', ''),
                                'alternativa4': questao.get('alternativa4', ''),
                                'alternativa5': questao.get('alternativa5', ''),
                                'gabarito': questao.get('gabarito', ''),
                                'resolucao': questao.get('resolucao', '')
                            }
                            st.session_state[f"edit_mode_{i}"] = True
                            st.rerun()
                    # Botão para regenerar a questão
                    with btn_col2:
                        if st.button("🔄 Regenerar", key=f"btn_regenerar_{questao_key}"):
                            # Chamar a função para regenerar a questão
                            if qu.regenerar_questao(i):
                                st.success(f"Questão {i+1} regenerada com sucesso!")
                                st.rerun()          
                    # Botão de aprovação
                    with btn_col3:
                        # Se já estiver aprovada, mostrar botão para cancelar aprovação
                        if questao.get('aprovado', False):
                            if st.button("Cancelar aprovação", key=f"btn_cancelar_{questao_key}"):
                                # Chamar a função de callback
                                qu.cancelar_aprovacao(i)
                                st.rerun()  # Recarregar apenas os componentes
                        else:
                            # Se não estiver aprovada, mostrar botão de aprovar
                            if st.button("Aprovar questão", key=f"btn_aprovar_{questao_key}"):
                                # Chamar a função de callback
                                qu.aprovar_questao(i)
                                st.rerun()  # Recarregar apenas os componentes
            # Adiciona uma linha de separação entre as questões
            st.markdown("---")

    # -----------------------  Resumo e botões de download ---------------------------
    st.subheader("Resumo e download")
    # Contar questões aprovadas
    questoes_aprovadas = qu.contar_questoes_aprovadas()
    total_questoes = len(st.session_state.questoes_geradas)
    if total_questoes > 0:
        # Mostrar resumo de aprovação
        percentual = (questoes_aprovadas / total_questoes) * 100 if total_questoes > 0 else 0
        st.info(f"Status de aprovação: {questoes_aprovadas} de {total_questoes} questões aprovadas ({percentual:.1f}%).")  
        # Adicionar um botão para salvar no Supabase
        if questoes_aprovadas > 0:
            if st.button("💾 Salvar questões aprovadas no banco de dados", use_container_width=True):
                # Filtrar apenas questões aprovadas
                questoes_aprovadas_lista = [q for q in st.session_state.questoes_geradas if q.get('aprovado', False)]      
                # Tentar salvar no Supabase
                with st.spinner("Salvando questões no banco de dados..."):
                    try:
                        # Obter o ID do usuário atual da sessão
                        user_id = st.session_state.get('user_id')
                        # Chamar a função para salvar questões aprovadas
                        questoes_salvas, total = salvar_questoes_aprovadas(questoes_aprovadas_lista, user_id)       
                        if questoes_salvas > 0:
                            st.success(f"{questoes_salvas} de {total} questões foram salvas no banco de dados com sucesso!")
                        else:
                            st.error("Não foi possível salvar nenhuma questão no banco de dados.")   
                    except Exception as e:
                        st.error(f"Erro ao salvar no banco de dados: {str(e)}")
        else:
            st.warning("Aprove pelo menos uma questão para poder salvar no banco de dados.")
        # Botões para download em três colunas
        dl_col1, dl_col2, dl_col3 = st.columns(3)
        # Botão para aprovar todas as questões
        with dl_col1:
            dlb_col1, dlb_col2, dlb_col3 = st.columns(3)
            with dlb_col1:
                # Contar quantas questões não estão aprovadas
                questoes_nao_aprovadas = total_questoes - questoes_aprovadas
                if questoes_nao_aprovadas > 0:
                    if st.button(f"Aprovar todas as questões ({questoes_nao_aprovadas} pendentes)"):
                        # Chamar a função para aprovar todas as questões
                        qu.aprovar_todas_questoes()
                        st.success("Todas as questões foram aprovadas!")
                        st.rerun()
                else:
                    st.success("Todas as questões já estão aprovadas!")
            with dlb_col2:
                # Filtrar apenas questões aprovadas
                questoes_aprovadas_lista = [q for q in st.session_state.questoes_geradas if q.get('aprovado', False)]         
                if questoes_aprovadas_lista:
                    # Gerar dados em Excel apenas para questões aprovadas
                    excel_aprovadas = qu.converter_questoes_para_excel(questoes_aprovadas_lista)
                    st.download_button(
                        label="Baixar apenas aprovadas (Excel)",
                        data=excel_aprovadas,
                        file_name="questoes_aprovadas.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.write("Nenhuma questão aprovada ainda")
            with dlb_col3:
                # Filtrar apenas questões NÃO aprovadas
                questoes_nao_aprovadas_lista = [q for q in st.session_state.questoes_geradas if not q.get('aprovado', False)]      
                if questoes_nao_aprovadas_lista:
                    # Gerar dados em Excel apenas para metadados das questões NÃO aprovadas
                    excel_nao_aprovadas = qu.converter_questoes_nao_aprovadas_para_excel(questoes_nao_aprovadas_lista)
                    st.download_button(
                        label="Baixar apenas não aprovadas (Excel)",
                        data=excel_nao_aprovadas,
                        file_name="questoes_nao_aprovadas.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.write("Todas as questões já foram aprovadas")  
        