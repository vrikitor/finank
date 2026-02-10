"""
================================================================================
💻 FINANK - SIMULADOR DE LIBERDADE FINANCEIRA
================================================================================
Este é o módulo da esperança! 🚀
Aqui nós usamos a matemática para projetar o futuro financeiro do usuário.

A FÓRMULA MÁGICA: Juros Compostos
M = C * (1 + i)^t
Traduzindo: O seu dinheiro cresce de forma exponencial ao longo do tempo.

O QUE ESTE CÓDIGO FAZ:
1. Pega quanto você tem hoje e quanto vai investir por mês.
2. Calcula mês a mês o crescimento do patrimônio.
3. Gera um gráfico "Bola de Neve" mostrando a diferença entre o que saiu do seu
   bolso (esforço) e o que veio dos juros (dinheiro grátis).
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ==============================================================================
# 1. CONFIGURAÇÃO VISUAL
# ==============================================================================
st.set_page_config(page_title="Simulador de Liberdade", layout="wide", page_icon="💽")

st.markdown("""
<style>
    /* Estilos para deixar os números grandes e bonitos */
    .big-font { font-size: 24px !important; font-weight: bold; }
    .success-text { color: #00ff41; }
    .metric-card { background-color: #1b1e23; padding: 20px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. BARRA LATERAL (PAINEL DE CONTROLE)
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Parâmetros da Simulação")
    
    # Inputs numéricos: O usuário define a estratégia dele aqui
    valor_inicial = st.number_input("Já tenho guardado (R$):", min_value=0.0, value=10000.0, step=100.0)
    aporte_mensal = st.number_input("Vou investir por mês (R$):", min_value=0.0, value=1000.0, step=50.0)
    
    # Tempo: O fator mais importante dos juros compostos
    anos = st.slider("Por quanto tempo? (Anos)", min_value=1, max_value=50, value=20)
    
    # Rentabilidade: A taxa de crescimento do dinheiro
    st.markdown("---")
    st.caption("Taxa de Rentabilidade Anual Estimada")
    taxa_anual = st.number_input("% ao Ano (Ex: 10% = Média Histórica Bolsa):", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
    
    st.info(f"💡 Dica: A Bolsa (Ibovespa) rendeu historicamente ~10% a 12% ao ano. A Renda Fixa hoje paga ~11%.")

# ==============================================================================
# 3. MOTOR DE CÁLCULO (A MATEMÁTICA)
# ==============================================================================

# Passo 1: Converter tudo para MÊS, pois o aporte é mensal
meses = anos * 12
# Fórmula para converter taxa anual em mensal equivalente
taxa_mensal = (1 + taxa_anual / 100) ** (1/12) - 1

# Listas para guardar o histórico (usadas para desenhar o gráfico depois)
lista_meses = []
lista_patrimonio = []
lista_investido = [] # Só o dinheiro que saiu do bolso
lista_juros = []     # Só o lucro

# Variáveis de controle
saldo_atual = valor_inicial
total_investido_bolso = valor_inicial

# Loop: Calcula o crescimento mês a mês
for m in range(1, meses + 1):
    # 1. O dinheiro rende primeiro (Juros sobre o saldo anterior)
    rendimento = saldo_atual * taxa_mensal
    saldo_atual += rendimento
    
    # 2. O aporte novo entra depois
    saldo_atual += aporte_mensal
    total_investido_bolso += aporte_mensal
    
    # 3. Salva os dados na memória
    lista_meses.append(m)
    lista_patrimonio.append(saldo_atual)
    lista_investido.append(total_investido_bolso)
    lista_juros.append(saldo_atual - total_investido_bolso)

# Transforma as listas em uma Tabela (DataFrame) para o Streamlit usar
df_simulacao = pd.DataFrame({
    "Mês": lista_meses,
    "Patrimônio Total": lista_patrimonio,
    "Total Investido (Seu Bolso)": lista_investido,
    "Juros Acumulados (Lucro)": lista_juros
})

# Regra dos 4% (Adaptada para o Brasil como 0.6% ao mês ou ~7% a.a.)
# Essa é a renda segura que você pode sacar para sempre sem o dinheiro acabar.
renda_passiva = saldo_atual * 0.006

# ==============================================================================
# 4. PAINEL PRINCIPAL (RESULTADOS)
# ==============================================================================
st.title("💻 Simulador da Liberdade Financeira")
st.markdown("Veja o poder dos juros compostos trabalhando para você.")
st.markdown("---")

# --- BLOCO 1: O RESUMO DO FUTURO ---
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Patrimônio Final", f"R$ {saldo_atual:,.2f}")
col2.metric("💼 Saiu do seu Bolso", f"R$ {total_investido_bolso:,.2f}")
# Delta mostra o lucro separado
col3.metric("📈 Juros Ganhos (Grátis)", f"R$ {saldo_atual - total_investido_bolso:,.2f}", delta="O Dinheiro trabalhando")
col4.metric("🏖️ Renda Mensal Vitalícia", f"R$ {renda_passiva:,.2f}", help="Quanto você pode sacar todo mês para viver de renda.")

# Efeito Confete: Se a pessoa ficar rica, damos parabéns!
if renda_passiva > 5000:
    st.success(f"🎉 **Parabéns!** Com esse plano, você poderá viver de renda ganhando **R$ {renda_passiva:,.2f}** todo mês sem trabalhar!")

st.markdown("---")

# --- BLOCO 2: O GRÁFICO (BOLA DE NEVE) ---
st.subheader("📊 A Curva da Riqueza")

fig = go.Figure()

# Linha 1: O Esforço (Linear)
fig.add_trace(go.Scatter(
    x=df_simulacao["Mês"], 
    y=df_simulacao["Total Investido (Seu Bolso)"],
    mode='lines',
    name='O que você guardou (Esforço)',
    line=dict(color='#3498db', width=2, dash='dash') # Azul tracejado para diferenciar
))

# Linha 2: O Resultado (Exponencial)
fig.add_trace(go.Scatter(
    x=df_simulacao["Mês"], 
    y=df_simulacao["Patrimônio Total"],
    mode='lines',
    name='Patrimônio Total (Bola de Neve)',
    fill='tonexty', # Pinta a área entre as linhas (representa os juros)
    line=dict(color='#2ecc71', width=4) # Verde grosso para destacar
))

fig.update_layout(
    title="Efeito Bola de Neve: Juros Compostos vs. Esforço Próprio",
    xaxis_title="Meses",
    yaxis_title="Reais (R$)",
    template="plotly_dark",
    hovermode="x unified",
    height=500,
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

st.plotly_chart(fig, use_container_width=True)

# --- BLOCO 3: TABELA DETALHADA ---
with st.expander("📋 Ver Tabela Detalhada (Ano a Ano)"):
    # Agrupa por ano para a tabela não ficar com 360 linhas (30 anos x 12 meses)
    df_simulacao['Ano'] = df_simulacao['Mês'] // 12
    # Pega só o último mês de cada ano
    df_anual = df_simulacao.groupby('Ano').last().reset_index()
    
    st.dataframe(
        df_anual[['Ano', 'Total Investido (Seu Bolso)', 'Juros Acumulados (Lucro)', 'Patrimônio Total']],
        column_config={
            "Patrimônio Total": st.column_config.ProgressColumn("Evolução", format="R$ %.2f", min_value=0, max_value=saldo_atual),
            "Total Investido (Seu Bolso)": st.column_config.NumberColumn("Investido", format="R$ %.2f"),
            "Juros Acumulados (Lucro)": st.column_config.NumberColumn("Juros", format="R$ %.2f"),
        },
        use_container_width=True,
        hide_index=True
    )