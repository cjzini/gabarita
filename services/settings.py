import streamlit as st

st.title('Configurações')
st.write('Testes de Fórmulas Matemáticas')

st.latex(r'''
    a^2 + b^2 = c^2
''')

st.write('**Configurações de Exibição**')
t = 'Teste de Fórmulas Matemáticas' + 'a^2 + b^2 = c^2'
st.latex(r'''\theta_b='''+ rf'''{t} ''')

st.write('**Configurações de Exibição**')
texto = 'Teste de Fórmulas Matemáticas'
a = 'a^2 + b^2 = c^2'
st.latex(r'''
    \text{variavel}'''+ rf'''{a}
''')

st.latex(rf'''\texttt{texto}'''+ rf'''{a}''')