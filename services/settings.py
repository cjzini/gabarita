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

latex_expr = "a^2 + b^2 = c^2"
st.write(f"O teorema de pitágoras é dado pela seguinte equação: ${latex_expr}$.")

st.write(f"O teorema de pitágoras é dado pela seguinte equação: $a^2 + b^2 = c^2$.")

st.write(st.session_state.get('user_id'))