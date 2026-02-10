"""
================================================================================
🏛️ FINANK - MÓDULO TESOURO DIRETO
================================================================================
Este módulo conecta você ao investimento mais seguro do Brasil.
A engenharia aqui é focada em RESILIÊNCIA. O site do Tesouro Nacional costuma
cair ou bloquear robôs, então criei um sistema de "Plano B".

FUNCIONAMENTO:
1. Tenta acessar a API JSON oficial do Tesouro Direto (b3/tesourodireto).
2. Se conseguir, mostra as taxas reais em tempo real (ex: IPCA + 6.20%).
3. Se falhar (erro 403 ou timeout), ativa o "Modo Contingência" e carrega uma
   lista interna de títulos com taxas de referência, para o usuário não ficar na mão.
"""

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAÇÃO VISUAL
# ==============================================================================
st.set_page_config(page_title="Tesouro Direto", layout="wide", page_icon="🏛️")

# CSS para criar os cartões dos títulos (estilo "Bond Card")
st.markdown("""
    <style>
    .stMetric { background-color: #1b1e23; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    
    /* Cartão do Título */
    .bond-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00D4FF; /* Azul Tesouro */
        margin-bottom: 15px;
    }
    .bond-title { font-size: 1.2em; font-weight: bold; color: #ffffff; }
    .bond-detail { font-size: 0.9em; color: #b0b0b0; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. INTELIGÊNCIA DE DADOS (COM PLANO B)
# ==============================================================================

# Função Principal: Buscar Taxas
@st.cache_data(ttl=3600) # Cache de 1h
def buscar_dados_tesouro():
    # URL Secreta que alimenta o site oficial
    url = "https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/balcao/precos-taxas.json"
    
    # Cabeçalho para fingir ser um navegador Google Chrome (Evita bloqueio 403)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Tenta conectar com timeout curto (5 segundos)
        response = requests.get(url, headers=headers, verify=True, timeout=5).json()
        titulos = response['response']['TrsrBdTradgList']
        
        lista_final = []
        for t in titulos:
            nome = t['TrsrBd']['nm']
            taxa = t['TrsrBd']['anulInvstmtRate']
            invest_min = t['TrsrBd']['minInvstmtAmt']
            vencimento = t['TrsrBd']['mtrtyDt']
            
            # Categorização para as Abas
            tipo = "Outros"
            if "Selic" in nome: tipo = "Selic (Pós-fixado)"
            elif "IPCA" in nome: tipo = "IPCA+ (Inflação)"
            elif "Prefixado" in nome: tipo = "Prefixado (Fixo)"
            
            lista_final.append({
                "Nome": nome,
                "Taxa Anual": taxa,
                "Invest. Mínimo": invest_min,
                # Formata a data de YYYY-MM-DD para DD/MM/YYYY
                "Vencimento": datetime.strptime(vencimento.split('T')[0], '%Y-%m-%d').strftime('%d/%m/%Y'),
                "Tipo": tipo,
                "Offline": False # Marca que veio da API oficial
            })
            
        return pd.DataFrame(lista_final)

    except Exception as e:
        # --- PLANO B: DADOS DE CONTINGÊNCIA (SE O SITE CAIR) ---
        # Isso garante que a tela nunca fique vazia/vermelha com erro.
        # São dados aproximados de mercado para referência.
        dados_fallback = [
            {"Nome": "Tesouro Selic 2029", "Taxa Anual": 10.75, "Invest. Mínimo": 150.00, "Vencimento": "01/03/2029", "Tipo": "Selic (Pós-fixado)", "Offline": True},
            {"Nome": "Tesouro Selic 2026", "Taxa Anual": 10.75, "Invest. Mínimo": 150.00, "Vencimento": "01/03/2026", "Tipo": "Selic (Pós-fixado)", "Offline": True},
            {"Nome": "Tesouro IPCA+ 2029", "Taxa Anual": 6.20, "Invest. Mínimo": 32.00, "Vencimento": "15/05/2029", "Tipo": "IPCA+ (Inflação)", "Offline": True},
            {"Nome": "Tesouro IPCA+ 2035", "Taxa Anual": 6.35, "Invest. Mínimo": 40.00, "Vencimento": "15/05/2035", "Tipo": "IPCA+ (Inflação)", "Offline": True},
            {"Nome": "Tesouro IPCA+ 2045", "Taxa Anual": 6.45, "Invest. Mínimo": 35.00, "Vencimento": "15/05/2045", "Tipo": "IPCA+ (Inflação)", "Offline": True},
            {"Nome": "Tesouro Prefixado 2027", "Taxa Anual": 11.80, "Invest. Mínimo": 35.00, "Vencimento": "01/01/2027", "Tipo": "Prefixado (Fixo)", "Offline": True},
            {"Nome": "Tesouro Prefixado 2031", "Taxa Anual": 12.10, "Invest. Mínimo": 38.00, "Vencimento": "01/01/2031", "Tipo": "Prefixado (Fixo)", "Offline": True}
        ]
        return pd.DataFrame(dados_fallback)

# Função Simuladora: Quanto meu dinheiro vai render?
def calcular_retorno_bruto(valor_investido, taxa_anual, data_vencimento):
    try:
        hoje = datetime.now()
        venc = datetime.strptime(data_vencimento, '%d/%m/%Y')
        dias = (venc - hoje).days
        anos = dias / 365
        if anos < 0: anos = 0.1 # Evita erro se o título já venceu
        
        # Juros Compostos: Valor * (1 + taxa)^anos
        taxa_dec = taxa_anual / 100
        montante_final = valor_investido * ((1 + taxa_dec) ** anos)
        lucro = montante_final - valor_investido
        return montante_final, lucro
    except:
        return valor_investido, 0

# ==============================================================================
# 3. BARRA LATERAL
# ==============================================================================
with st.sidebar:
    st.header("🏛️ Simulador")
    valor_aporte = st.number_input("Vou investir hoje:", value=1000.0, step=100.0)
    st.markdown("---")
    st.info("ℹ️ **Dica:** O Tesouro Selic é o ideal para sua Reserva de Emergência pois tem liquidez diária.")

# ==============================================================================
# 4. PAINEL PRINCIPAL
# ==============================================================================
st.title("🏛️ Tesouro Direto & Renda Fixa")
st.markdown("Investimentos garantidos pelo Tesouro Nacional.")

df_tesouro = buscar_dados_tesouro()

# Aviso inteligente: Só mostra alerta se estiver no Plano B
if df_tesouro['Offline'].iloc[0]:
    st.warning("⚠️ O site do Tesouro Nacional está instável. Exibindo taxas de referência estimadas.")
else:
    st.success("🟢 Conectado ao Tesouro Nacional em tempo real.")

st.markdown("---")

# Abas organizadoras
tab1, tab2, tab3 = st.tabs(["🔒 Prefixados", "⚖️ IPCA+ (Inflação)", "💰 Selic (Reserva)"])

# Função que desenha a tela
def exibir_titulos(tipo_filtro):
    # Filtra o DataFrame pelo tipo (ex: só mostra Selic)
    filtrado = df_tesouro[df_tesouro['Tipo'].str.contains(tipo_filtro)]
    
    if filtrado.empty:
        st.info("Nenhum título disponível nesta categoria.")
        return

    for index, row in filtrado.iterrows():
        # Calcula a simulação para cada título
        final, lucro = calcular_retorno_bruto(valor_aporte, row['Taxa Anual'], row['Vencimento'])
        
        with st.container():
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.markdown(f"""
                <div class="bond-card">
                    <div class="bond-title">{row['Nome']}</div>
                    <div class="bond-detail">Vence em: {row['Vencimento']} • Mínimo: R$ {row['Invest. Mínimo']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2: st.metric("Rentabilidade Anual", f"{row['Taxa Anual']:.2f}%")
            with c3: st.metric("Retorno Bruto", f"R$ {final:,.2f}", f"+ R$ {lucro:,.2f}")
            
            # Gráfico de Barras Horizontal (Hoje vs Futuro)
            with st.expander(f"📈 Ver projeção para {row['Nome']}"):
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=['Hoje', 'No Vencimento'], x=[valor_aporte, final],
                    text=[f"R$ {valor_aporte:,.0f}", f"R$ {final:,.0f}"],
                    textposition='auto', orientation='h', marker_color=['#808080', '#00D4FF']
                ))
                fig.update_layout(height=200, template="plotly_dark", margin=dict(l=0,r=0,t=30,b=0))
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")

# Renderiza cada aba
with tab1: exibir_titulos("Prefixado")
with tab2: exibir_titulos("IPCA")
with tab3: exibir_titulos("Selic")