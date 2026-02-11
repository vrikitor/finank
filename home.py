import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuração Simples
st.set_page_config(page_title="Finank Lite", layout="wide", page_icon="💰")

# 2. Título
st.title("💰 Finank (Modo de Teste Mobile)")
st.info("Se você está vendo isso no celular, o teste funcionou!")

# 3. Teste de Colunas (O vilão)
st.subheader("Teste de Colunas")
col1, col2, col3 = st.columns(3)
col1.metric("Teste 1", "R$ 100", "10%")
col2.metric("Teste 2", "R$ 200", "-5%")
col3.metric("Teste 3", "R$ 300", "0%")

# 4. Teste de Biblioteca Externa (yfinance)
st.subheader("Teste de API (Yahoo Finance)")
try:
    ticker = yf.Ticker("PETR4.SA")
    preco = ticker.history(period="1d")['Close'].iloc[-1]
    st.success(f"API Funcionando! Petrobras: R$ {preco:.2f}")
except Exception as e:
    st.error(f"Erro na API: {e}")
