import streamlit as st
import pandas as pd

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

