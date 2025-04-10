import streamlit as st
from openai import OpenAI
from openai import OpenAIError

openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)