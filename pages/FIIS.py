"""
================================================================================
🏢 FINANK - MÓDULO DE FUNDOS IMOBILIÁRIOS (FIIs)
================================================================================
Bem-vindo ao mundo da Renda Passiva!
Este módulo foi desenhado especificamente para o investidor que ama receber
aluguéis (dividendos) todos os meses na conta.

DIFERENCIAIS DESTE CÓDIGO:
1. Calculadora do "Número Mágico": Descobre quantas cotas você precisa ter para
   que os dividendos comprem uma nova cota sozinhos (o efeito Bola de Neve).
2. Simulador de Renda Futura: Projeta quanto você vai receber de "salário" do fundo.
3. Análise de Preço Justo (P/VP): Diz se o fundo está caro ou barato.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
import math
import plotly.graph_objects as go
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAÇÃO VISUAL
# ==============================================================================
st.set_page_config(page_title="Módulo FIIs", layout="wide", page_icon="🏢")

# CSS para destacar o valor da Renda Mensal (o número mais importante para quem gosta de FIIs)
st.markdown("""
    <style>
    .stMetric { background-color: #1b1e23; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    .destaque-calc { color: #00ff41; font-weight: bold; font-size: 1.3em; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. FUNÇÕES AUXILIARES (AS FERRAMENTAS)
# ==============================================================================

# Função 1: Buscar Notícias Específicas de FIIs
# O Google News é ótimo, então filtramos a busca para trazer apenas notícias do setor imobiliário.
def buscar_noticias_fii(ticker_limpo):
    termo = f"{ticker_limpo} fundos imobiliários"
    termo_codificado = urllib.parse.quote(termo)
    url = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    noticias = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(url, headers=headers)
        soup = BeautifulSoup(resposta.content, features='xml')
        itens = soup.find_all('item')
        # Pego só as 5 primeiras para não poluir a tela
        for item in itens[:5]:
            noticias.append({'titulo': item.title.text, 'link': item.link.text, 'data': item.pubDate.text})
    except: pass
    return noticias

# Função 2: Tradutor
# Às vezes o resumo do fundo vem em inglês na API, então garantimos a tradução.
@st.cache_data
def traduzir_texto(texto):
    try: return GoogleTranslator(source='auto', target='pt').translate(texto)
    except: return texto

# ==============================================================================
# 3. BARRA LATERAL (ENTRADA DE DADOS)
# ==============================================================================
with st.sidebar:
    st.header("🏢 Configurações")
    
    # Campo de busca: Começa vazio para não gastar API à toa
    input_usuario = st.text_input("Código do Fundo:", value="").upper().strip()
    
    # Inputs para simulação financeira
    valor_aporte = st.number_input("Aporte Inicial (R$):", value=5000.0)
    aporte_mensal = st.number_input("Aporte Mensal (R$):", value=500.0)
    
    st.markdown("---")
    st.caption("🔧 Ajustes Manuais")
    # Às vezes a API falha no valor patrimonial, então deixo o usuário corrigir se quiser
    pvp_manual = st.number_input("Forçar P/VP (Opcional):", value=0.0, step=0.01)

# ==============================================================================
# 4. LÓGICA PRINCIPAL
# ==============================================================================

if input_usuario:
    # Tratamento: Se o usuário esquecer o ".SA" (sufixo da bolsa brasileira), a gente coloca.
    if not input_usuario.endswith(".SA"):
        ticker_yfinance = f"{input_usuario}.SA"
        ticker_visual = input_usuario
    else:
        ticker_yfinance = input_usuario
        ticker_visual = input_usuario.replace(".SA", "")

    st.title(f"🏢 Analisador: {ticker_visual}")
    st.markdown("---")

    try:
        # Busca os dados no Yahoo Finance
        fii = yf.Ticker(ticker_yfinance)
        hist = fii.history(period="1y")

        if hist.empty:
            st.error(f"Fundo '{ticker_visual}' não encontrado. Verifique o código.")
        else:
            # Dados fundamentais
            info = fii.info
            preco_atual = hist['Close'].iloc[-1]
            
            # --- CÁLCULO DE DIVIDENDOS (A PARTE CRÍTICA) ---
            # O Yahoo nem sempre dá o Yield anual pronto, então eu calculo na mão.
            # Eu somo todos os dividendos pagos nos últimos 12 meses.
            dy_anual_decimal = 0
            media_mensal = 0
            minimo_12m = 0

            try:
                dividendos = fii.dividends
                # Filtra apenas o último ano
                um_ano_atras = pd.Timestamp.now(tz=dividendos.index.tz) - pd.DateOffset(days=365)
                divs_12m = dividendos[dividendos.index >= um_ano_atras]
                
                total_div_12m = divs_12m.sum()
                if not divs_12m.empty: minimo_12m = divs_12m.min()
                
                # Se achou dividendos no histórico, usa o cálculo real
                if total_div_12m > 0:
                    dy_anual_decimal = total_div_12m / preco_atual
                    media_mensal = total_div_12m / 12
                # Se não achou (bug da API?), tenta pegar o dado pronto do resumo
                else:
                    dy_info = info.get('dividendYield', 0)
                    dy_anual_decimal = dy_info if dy_info and dy_info < 1 else (dy_info/100 if dy_info else 0)
                    media_mensal = (dy_anual_decimal * preco_atual) / 12
            except: pass

            # --- CÁLCULO DO P/VP (PREÇO SOBRE VALOR PATRIMONIAL) ---
            # Indica se está barato (<1) ou caro (>1)
            pvp_api = info.get('priceToBook', 0)
            pvp_final = pvp_manual if pvp_manual > 0 else pvp_api
            
            # --- CÁLCULO DO NÚMERO MÁGICO ---
            # Quantas cotas preciso ter para ganhar 1 cota nova de presente todo mês?
            # Fórmula: Preço da Cota / Dividendo Mensal Médio
            magic_number = math.ceil(preco_atual / media_mensal) if media_mensal > 0 else 0

            # --- EXIBIÇÃO DOS CARDS (TOPO) ---
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Preço Atual", f"R$ {preco_atual:.2f}")
            
            # Coloração dinâmica do P/VP
            delta_pvp = "Justo"
            if pvp_final > 0:
                delta_pvp = "Caro" if pvp_final > 1.05 else "Barato" if pvp_final < 0.95 else "Justo"
                c2.metric("P/VP", f"{pvp_final:.2f}", delta=delta_pvp, delta_color="inverse")
            else: c2.metric("P/VP", "--")
                
            c3.metric("Dividend Yield (12m)", f"{dy_anual_decimal*100:.2f}%")
            c4.metric("Número Mágico ❄️", f"{magic_number} Cotas" if magic_number > 0 else "--")
            c5.metric("Menor Div. (12m)", f"R$ {minimo_12m:.2f}")

            st.markdown("---")

            # --- ABAS DE ANÁLISE ---
            tab_calc, tab_sim, tab_graf, tab_news = st.tabs(["🧮 Calculadora & Resumo", "❄️ Simulador Bola de Neve", "📈 Gráficos", "📰 Notícias"])

            with tab_calc:
                col_calc, col_resumo = st.columns([1, 1.5], gap="large")
                
                # Calculadora de Renda Passiva
                with col_calc:
                    st.subheader("🧮 Quanto vou receber?")
                    invest_simulado = st.number_input("Valor a investir (R$):", value=valor_aporte, step=100.0)
                    if preco_atual > 0:
                        cotas_possiveis = int(invest_simulado // preco_atual)
                        renda_mensal = cotas_possiveis * media_mensal
                        
                        # Cartão bonito com o resultado
                        st.markdown(f"""
                        <div style="background-color: #262730; padding: 20px; border-radius: 10px;">
                            <p>Com <b>R$ {invest_simulado:,.2f}</b> você compra:</p>
                            <h2>{cotas_possiveis} Cotas</h2>
                            <hr>
                            <p>💰 Renda Mensal Estimada:</p>
                            <h2 class="destaque-calc">R$ {renda_mensal:,.2f}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                        
                with col_resumo:
                    st.subheader(f"📖 Sobre {ticker_visual}")
                    with st.spinner("Traduzindo..."):
                        resumo = info.get('longBusinessSummary')
                        if resumo: st.write(traduzir_texto(resumo))
                        else: st.info("Descrição não disponível.")

            with tab_sim:
                # Simulador de Longo Prazo (Bola de Neve)
                col1, col2 = st.columns([1, 2])
                with col1:
                    anos = st.slider("Anos:", 1, 30, 10)
                    dy_proj = st.slider("DY Projetado (%):", 0.0, 20.0, dy_anual_decimal*100) / 100
                    taxa = (1 + dy_proj)**(1/12) - 1 # Taxa mensal equivalente
                
                with col2:
                    # Loop de projeção mês a mês
                    lista_pat = []
                    lista_inv = []
                    saldo = valor_aporte
                    inv = valor_aporte
                    for m in range(anos * 12):
                        rend = saldo * taxa # O dinheiro rende
                        saldo += rend + aporte_mensal # Reinvisto o lucro + Aporte novo
                        inv += aporte_mensal # Apenas o que saiu do bolso
                        lista_pat.append(saldo)
                        lista_inv.append(inv)
                    
                    df = pd.DataFrame({"Mês": range(anos*12), "Total": lista_pat, "Bolso": lista_inv})
                    
                    # Gráfico de Área (Verde = Lucro, Cinza = Esforço)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df["Mês"], y=df["Total"], fill='tozeroy', name='Total', line=dict(color='#00ff41')))
                    fig.add_trace(go.Scatter(x=df["Mês"], y=df["Bolso"], fill='tozeroy', name='Bolso', line=dict(color='#808080')))
                    fig.update_layout(template="plotly_dark", title="Evolução Patrimonial")
                    st.plotly_chart(fig, use_container_width=True)

            with tab_graf:
                st.line_chart(hist['Close'])
                # Gráfico de barras para mostrar histórico de pagamento de dividendos
                if not fii.dividends.empty: st.bar_chart(fii.dividends, color="#00ff41")

            with tab_news:
                news = buscar_noticias_fii(ticker_visual)
                if news: 
                    for n in news: st.markdown(f"- [{n['titulo']}]({n['link']})")
                else: st.warning("Sem notícias.")

    except Exception as e:
        st.error(f"Erro: {e}")

else:
    # --- TELA DE BOAS-VINDAS (QUANDO NÃO TEM CÓDIGO) ---
    st.title("🏢 Módulo de Fundos Imobiliários (FIIs)")
    st.markdown("Invista em imóveis e gere renda passiva mensal isenta de Imposto de Renda.")
    st.markdown("---")
    
    st.info("👈 **Comece por aqui:** Digite o código do fundo na barra lateral (Ex: MXRF11, HGLG11) para ver a análise.")
    st.markdown("---")
    
    st.markdown("### 🔥 Fundos Populares")
    c1, c2, c3 = st.columns(3)
    c1.metric("MXRF11", "Híbrido / Papel")
    c2.metric("HGLG11", "Tijolo / Logística")
    c3.metric("KNRI11", "Tijolo / Renda")