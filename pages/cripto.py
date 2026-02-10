"""
================================================================================
🪙 FINANK - MÓDULO DE CRIPTOMOEDAS E BLOCKCHAIN
================================================================================
Este é o módulo mais volátil e emocionante do sistema.
Aqui monitoramos o mercado 24/7 de ativos digitais.

DIFERENCIAIS DESTE CÓDIGO:
1. Índice "Fear & Greed" (Medo e Ganância): Uma API especial que nos diz se o
   mercado está em pânico (hora de comprar?) ou euforia (hora de vender?).
2. Múltiplas Fontes de Dados: Usamos Yahoo Finance para gráficos históricos e
   CoinGecko para preços em tempo real, garantindo redundância.
3. Gráfico Comparativo Normalizado: Permite ver quem está rendendo mais (BTC, ETH ou SOL)
   colocando todos na mesma régua (%).
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from deep_translator import GoogleTranslator
from datetime import datetime
import pandas as pd # Importante para manipular os dados do gráfico

# ==============================================================================
# 1. CONFIGURAÇÃO VISUAL
# ==============================================================================
st.set_page_config(page_title="Módulo Cripto", layout="wide", page_icon="🪙")

st.markdown("""
    <style>
    /* Estilo para o Nome da Moeda e o Resumo Explicativo */
    .nome-completo { font-size: 1.5em; font-weight: bold; color: #b0b0b0; margin-bottom: 10px; }
    .resumo-box { background-color: #262730; padding: 15px; border-radius: 10px; border-left: 5px solid #F7931A; margin-bottom: 20px; }
    
    /* CARTÕES PERSONALIZADOS (Com setinhas de alta e baixa) */
    .custom-card {
        background-color: #1b1e23;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .card-label { font-size: 14px; color: #8b949e; margin-bottom: 5px; }
    .card-value { font-size: 22px; font-weight: bold; color: #ffffff; word-wrap: break-word; }
    .card-delta-pos { color: #00ff41; font-size: 14px; font-weight: bold; margin-top: 5px; } /* Verde */
    .card-delta-neg { color: #ff2b2b; font-size: 14px; font-weight: bold; margin-top: 5px; } /* Vermelho */
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. FUNÇÕES AUXILIARES (A INTELIGÊNCIA)
# ==============================================================================

# Função 1: Índice de Medo e Ganância (Fear & Greed Index)
# Busca na API "alternative.me" um número de 0 a 100.
# 0 = Medo Extremo (Ninguém quer comprar) | 100 = Ganância Extrema (Todo mundo quer)
@st.cache_data(ttl=300)
def buscar_medo_ganancia():
    url = "https://api.alternative.me/fng/?limit=1"
    try:
        response = requests.get(url).json()
        data = response['data'][0]
        valor = int(data['value'])
        texto_ingles = data['value_classification']
        
        # Traduz para o usuário brasileiro
        traducoes = {
            "Extreme Fear": "Medo Extremo 😱",
            "Fear": "Medo 😨",
            "Neutral": "Neutro 😐",
            "Greed": "Ganância 🤑",
            "Extreme Greed": "Ganância Extrema 🚀"
        }
        texto_pt = traducoes.get(texto_ingles, texto_ingles)
        return valor, texto_pt
    except:
        return 50, "Neutro" # Valor padrão se a API falhar

# Função 2: Cotação do Dólar
# Como cripto é dolarizada, precisamos saber o dólar para converter para Real.
@st.cache_data(ttl=600)
def obter_taxa_usd_brl():
    try:
        return yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
    except:
        return 5.80 # Fallback seguro

# Função 3: Top 3 Moedas (API CoinGecko)
# Essa API é ótima para pegar preços de várias moedas ao mesmo tempo.
@st.cache_data(ttl=60)
def buscar_top_3_coingecko(moeda_alvo):
    currency = "brl" if moeda_alvo == "BRL" else "usd"
    url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies={currency}&include_24hr_change=true"
    dados = []
    mapa_nomes = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}
    try:
        response = requests.get(url).json()
        for id_coin, info in response.items():
            preco = info[currency]
            var = info[f"{currency}_24h_change"]
            ticker = mapa_nomes.get(id_coin, id_coin.upper())
            dados.append({'ticker': ticker, 'preco': preco, 'var': var})
        # Ordena pelo preço (BTC primeiro)
        dados.sort(key=lambda x: x['preco'], reverse=True)
    except: pass
    return dados

# Função 4: Gráfico Comparativo (Normalizado)
# Mostra a performance de BTC, ETH e SOL nos últimos 30 dias.
# Normalizar significa fazer todos começarem em 0%, para ver quem cresceu mais proporcionalmente.
@st.cache_data(ttl=600)
def obter_dados_grafico_comparativo():
    tickers = {'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'SOL': 'SOL-USD'}
    df_final = pd.DataFrame()
    
    try:
        for nome, ticker in tickers.items():
            hist = yf.Ticker(ticker).history(period="1mo")['Close']
            if not hist.empty:
                # A Fórmula Mágica da Normalização:
                # (Preço Atual / Preço Inicial - 1) * 100
                df_final[nome] = (hist / hist.iloc[0] - 1) * 100
    except: pass
    return df_final

# Tradutor (Google Translator)
@st.cache_data
def traduzir_texto(texto, destino='pt'):
    try: return GoogleTranslator(source='auto', target=destino).translate(texto)
    except: return texto 

# Resumos Prontos (Didática)
# Se o usuário buscar BTC, eu mostro um texto educativo. Se buscar outra coisa, tento traduzir.
def obter_resumo_projeto(ticker, info_yahoo):
    dicionario_ideias = {
        "BTC": "O Ouro Digital. A primeira criptomoeda, criada para ser uma reserva de valor descentralizada e incensurável.",
        "ETH": "O Computador Mundial. Plataforma que permite criar Contratos Inteligentes e Aplicativos Descentralizados (dApps).",
        "SOL": "Velocidade e Baixo Custo. Blockchain de alta performance capaz de processar milhares de transações por segundo.",
        "DOGE": "A Moeda do Povo. Começou como meme, mas ganhou força pelo uso em microtransações e comunidade vibrante.",
        "ADA": "Blockchain Científica. Focada em segurança e sustentabilidade, desenvolvida através de pesquisas acadêmicas.",
        "XRP": "O Banco das Criptos. Focada em facilitar transferências internacionais instantâneas para instituições financeiras.",
        "USDT": "Dólar Digital. Stablecoin que mantém paridade com o dólar americano."
    }
    ticker_limpo = ticker.upper()
    if ticker_limpo in dicionario_ideias: return dicionario_ideias[ticker_limpo]
    
    resumo_yahoo = info_yahoo.get('description') or info_yahoo.get('longBusinessSummary')
    if resumo_yahoo: return traduzir_texto(resumo_yahoo)
    return "Projeto de ativo digital descentralizado baseada em tecnologia blockchain."

# Função para criar o HTML do cartão bonito
def exibir_card_html(label, valor, delta_pct=None):
    html_delta = ""
    if delta_pct is not None:
        if delta_pct >= 0: html_delta = f"<div class='card-delta-pos'>↑ {delta_pct:.2f}%</div>"
        else: html_delta = f"<div class='card-delta-neg'>↓ {delta_pct:.2f}%</div>"
    st.markdown(f"""
    <div class="custom-card">
        <div class="card-label">{label}</div>
        <div class="card-value">{valor}</div>
        {html_delta}
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. BARRA LATERAL
# ==============================================================================
with st.sidebar:
    st.header("₿ Configurações")
    moeda_ref = st.radio("Cotar em:", ["Real (BRL)", "Dólar (USD)"])
    sufixo_escolhido = "BRL" if "Real" in moeda_ref else "USD"
    simbolo = "R$" if "Real" in moeda_ref else "$"
    
    input_usuario = st.text_input("Criptomoeda:", value="", placeholder="Ex: BTC, ETH").upper().strip()
    valor_aporte = st.number_input("Simular Investimento:", value=1000.0)

# ==============================================================================
# 4. LÓGICA PRINCIPAL
# ==============================================================================

# CENÁRIO A: USUÁRIO DIGITOU UMA CRIPTO ESPECÍFICA
if input_usuario:
    st.title(f"₿ Análise: {input_usuario}")
    ticker_base = f"{input_usuario}-USD"
    try:
        cripto = yf.Ticker(ticker_base)
        hist = cripto.history(period="1mo")
        
        if hist.empty:
             st.error(f"Cripto '{input_usuario}' não encontrada. Tente o código padrão (Ex: BTC).")
        else:
            info = cripto.info
            nome_completo = info.get('name', input_usuario)
            
            # Exibe o resumo educativo
            st.markdown(f"<div class='nome-completo'>{nome_completo}</div>", unsafe_allow_html=True)
            resumo_projeto = obter_resumo_projeto(input_usuario, info)
            st.markdown(f"<div class='resumo-box'>💡 <b>O que é {input_usuario}?</b><br>{resumo_projeto}</div>", unsafe_allow_html=True)
            st.markdown("---")

            # Conversão Dólar -> Real se necessário
            taxa = obter_taxa_usd_brl() if sufixo_escolhido == "BRL" else 1.0
            preco_atual_usd = hist['Close'].iloc[-1]
            preco_exibicao = preco_atual_usd * taxa

            if len(hist) >= 2:
                fech_ontem = hist['Close'].iloc[-2]
                var_24h = ((preco_atual_usd - fech_ontem) / fech_ontem) * 100
            else: var_24h = 0.0

            qtd_moedas = valor_aporte / preco_exibicao

            # Cards de Dados
            c1, c2, c3, c4 = st.columns(4)
            with c1: exibir_card_html(f"Preço ({sufixo_escolhido})", f"{simbolo} {preco_exibicao:,.2f}")
            with c2: exibir_card_html("Variação (24h)", f"{var_24h:.2f}%", var_24h)
            with c3:
                mcap = info.get('marketCap', 0)
                if mcap > 1_000_000_000: mcap_fmt = f"$ {mcap/1_000_000_000:.2f} B"
                else: mcap_fmt = f"$ {mcap:,.0f}"
                exibir_card_html("Market Cap (USD)", mcap_fmt)
            with c4: exibir_card_html("Você compraria", f"{qtd_moedas:,.6f} {input_usuario}")

            st.markdown("---")

            # Gráficos
            tab_graf, tab_candle = st.tabs(["📈 Gráfico Linha", "🕯️ Velas (Candles)"])
            hist_plot = hist['Close'] * taxa
            
            with tab_graf:
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Scatter(x=hist.index, y=hist_plot, name="Preço", fill='tozeroy', line=dict(color='#F7931A', width=2)), secondary_y=True)
                fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name="Volume", opacity=0.3, marker_color='#808080'), secondary_y=False)
                fig.update_layout(height=450, template="plotly_dark", showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
                st.plotly_chart(fig, use_container_width=True)
                
            with tab_candle:
                fig_c = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                fig_c.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False, title=f"Estrutura (Base USD)")
                st.plotly_chart(fig_c, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")

# CENÁRIO B: NENHUMA CRIPTO SELECIONADA (DASHBOARD)
else:
    st.title("₿ Mercado Cripto")
    st.info("👈 **Digite o código da moeda** (BTC, ETH, SOL) na barra lateral.")
    st.markdown("---")
    
    col_fg, col_top = st.columns([1, 2])
    
    # 1. Relógio do Medo (Gauge Chart)
    with col_fg:
        st.subheader("🌡️ Sentimento Hoje")
        valor, classe = buscar_medo_ganancia()
        cor = "#00ff41" if valor > 55 else "#ff2b2b" if valor < 45 else "#ebc934"
        fig_g = go.Figure(go.Indicator(mode = "gauge+number", value = valor, title = {'text': f"<b>{classe}</b>"}, gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': cor}}))
        fig_g.update_layout(height=250, margin=dict(t=0,b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_g, use_container_width=True)
        st.markdown(f"""
        <div style="background-color: #262730; padding: 15px; border-radius: 10px; font-size: 0.9em;">
            <b>Como ler este relógio:</b>
            <br>🔴 <b>0-25 (Medo Extremo):</b> Pânico. Historicamente, bons momentos de compra (preço baixo).
            <br>🟡 <b>26-74 (Neutro/Medo):</b> Incerteza ou equilíbrio.
            <br>🟢 <b>75-100 (Ganância):</b> Euforia. Cuidado, o mercado pode estar caro (bolha).
        </div>
        """, unsafe_allow_html=True)

    # 2. Top 3 e Gráfico Comparativo
    with col_top:
        st.subheader(f"🔥 Top 3 ({sufixo_escolhido})")
        with st.spinner("Buscando dados na CoinGecko..."):
            top3 = buscar_top_3_coingecko(sufixo_escolhido)
        
        if top3:
            c1, c2, c3 = st.columns(3)
            if len(top3) >= 1: 
                with c1: exibir_card_html(top3[0]['ticker'], f"{simbolo} {top3[0]['preco']:,.2f}", top3[0]['var'])
            if len(top3) >= 2: 
                with c2: exibir_card_html(top3[1]['ticker'], f"{simbolo} {top3[1]['preco']:,.2f}", top3[1]['var'])
            if len(top3) >= 3: 
                with c3: exibir_card_html(top3[2]['ticker'], f"{simbolo} {top3[2]['preco']:,.2f}", top3[2]['var'])
            
            st.markdown("---")
            st.subheader("📊 Comparativo de Performance (30 Dias)")
            st.caption("Veja quem está crescendo mais percentualmente, independente do preço.")
            
            df_comp = obter_dados_grafico_comparativo()
            if not df_comp.empty:
                fig_comp = go.Figure()
                colors = {'BTC': '#F7931A', 'ETH': '#627EEA', 'SOL': '#14F195'}
                for coin in df_comp.columns:
                    fig_comp.add_trace(go.Scatter(
                        x=df_comp.index, 
                        y=df_comp[coin], 
                        mode='lines', 
                        name=coin,
                        line=dict(color=colors.get(coin, '#ffffff'), width=2)
                    ))
                
                fig_comp.update_layout(
                    height=350,
                    template="plotly_dark",
                    yaxis_title="Variação (%)",
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_comp, use_container_width=True)

        else:
            st.warning("CoinGecko indisponível no momento.")