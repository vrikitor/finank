"""
================================================================================
🔍 FINANK - MÓDULO OLHEIRO DE AÇÕES
================================================================================
Este é o "Detetive" do sistema. A função dele é investigar um ativo a fundo.
Eu projetei essa página para ter dois modos:
1. Modo Visão Geral: Quando você não digita nada, ele mostra os TOP 3 do mercado.
2. Modo Detalhado: Quando você busca um código (ex: PETR4), ele puxa gráfico,
   notícias, variação e até diz se o clima está otimista ou pessimista.

TECNOLOGIAS USADAS AQUI:
- Plotly: Para desenhar os gráficos de velas (Candlestick) interativos.
- Requests + BeautifulSoup: Para "raspar" notícias do Google News.
- Deep Translator: Para traduzir a descrição das empresas americanas para português.
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from deep_translator import GoogleTranslator
import requests
from bs4 import BeautifulSoup
import urllib.parse

# ==============================================================================
# 1. CONFIGURAÇÃO VISUAL (CSS)
# ==============================================================================
st.set_page_config(page_title="Módulo Ações", layout="wide", page_icon="🔍")

# Aqui eu injeto CSS para criar as "caixinhas" coloridas de sentimento.
# Se a notícia for boa, fica verde. Se for ruim, vermelha.
st.markdown("""
    <style>
    .stMetric { background-color: #1b1e23; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    .sentimento-positivo { color: #00ff41; font-weight: bold; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; }
    .sentimento-negativo { color: #ff2b2b; font-weight: bold; border: 1px solid #ff2b2b; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; }
    .sentimento-neutro { color: #8b949e; border: 1px solid #8b949e; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; }
    .veredito-box { padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center; font-weight: bold; font-size: 1.2em; }
    .v-alta { background-color: rgba(0, 255, 65, 0.1); border: 1px solid #00ff41; color: #00ff41; }
    .v-baixa { background-color: rgba(255, 43, 43, 0.1); border: 1px solid #ff2b2b; color: #ff2b2b; }
    .v-neutro { background-color: rgba(139, 148, 158, 0.1); border: 1px solid #8b949e; color: #8b949e; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. INTELIGÊNCIA DE DADOS (O CÉREBRO)
# ==============================================================================

# --- LISTAS DE MONITORAMENTO ---
# Eu defini essas listas manualmente para o sistema ter o que mostrar na tela inicial.
# São as ações mais populares ("Blue Chips") e ETFs conhecidos.
CESTA_ACOES_BR = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'WEGE3.SA', 'BBAS3.SA', 'PRIO3.SA', 'B3SA3.SA', 'RENT3.SA', 'ELET3.SA', 'GGBR4.SA']
CESTA_ACOES_US = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC']

CESTA_ETFS = ['IVVB11.SA', 'BOVA11.SA', 'SMAL11.SA', 'HASH11.SA', 'NASD11.SA', 'XINA11.SA', 'EURP11.SA', 'GOLD11.SA']
CESTA_BDRS = ['AAPL34.SA', 'MSFT34.SA', 'GOGL34.SA', 'AMZO34.SA', 'TSLA34.SA', 'NVDA34.SA', 'MELI34.SA', 'COCA34.SA', 'DISB34.SA']

# Função Genérica de Ranking
# O que ela faz: Recebe uma lista de códigos, baixa o preço de ontem e de hoje,
# calcula quem subiu mais e me devolve o TOP 3.
@st.cache_data(ttl=300) 
def buscar_top_3_generico(lista_ativos):
    ranking = []
    try:
        # Baixa dados em lote para ser rápido
        tickers = yf.Tickers(" ".join(lista_ativos))
        for t in lista_ativos:
            try:
                hist = tickers.tickers[t].history(period="2d")
                if len(hist) >= 2:
                    fechamento_ontem = hist['Close'].iloc[-2]
                    fechamento_hoje = hist['Close'].iloc[-1]
                    
                    # Cálculo da porcentagem de variação
                    if fechamento_ontem > 0:
                        var_pct = ((fechamento_hoje - fechamento_ontem) / fechamento_ontem) * 100
                    else: var_pct = 0.0
                    
                    nome_limpo = t.replace('.SA', '')
                    ranking.append({'ticker': nome_limpo, 'var': var_pct, 'preco': fechamento_hoje})
            except: pass
    except: pass
    
    # Ordena do maior para o menor e pega os 3 primeiros
    ranking.sort(key=lambda x: x['var'], reverse=True)
    return ranking[:3]

# Função de Análise de Sentimento (NLP Simples)
# Eu criei um dicionário de palavras "boas" e "ruins".
# O sistema lê o título da notícia e conta quantas palavras de cada tipo aparecem.
def analisar_sentimento(texto):
    texto_limpo = texto.lower()
    positivos = ["alta", "sobe", "subiu", "lucro", "dispara", "ganhos", "otimismo", "valorização", "aprovado", "dividendo", "compra"]
    negativos = ["queda", "cai", "caiu", "prejuízo", "desaba", "perdas", "crise", "pessimismo", "desvalorização", "risco", "venda"]
    score = 0
    for p in positivos:
        if p in texto_limpo: score += 1
    for n in negativos:
        if n in texto_limpo: score -= 1
    
    if score > 0: return "🟢 Otimista", "sentimento-positivo"
    elif score < 0: return "🔴 Pessimista", "sentimento-negativo"
    else: return "⚪ Neutro", "sentimento-neutro"

# Função Auxiliar: Cria o termo de busca para o Google
# Ex: Se busco PETR4, ele pesquisa "Petrobras ações mercado financeiro"
def obter_contexto_busca(ticker, nome_empresa):
    t = ticker.upper()
    primeiro_nome = nome_empresa.split()[0] if nome_empresa else ""
    return f"{primeiro_nome} ações mercado financeiro"

# Web Scraping de Notícias (Google News RSS)
@st.cache_data(ttl=600)
def buscar_noticias_inteligentes(termo_busca):
    termo_codificado = urllib.parse.quote(termo_busca)
    # URL do feed RSS do Google News filtrado para o Brasil (pt-BR)
    url = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    headers = {'User-Agent': 'Mozilla/5.0'}
    noticias = []
    try:
        resposta = requests.get(url, headers=headers)
        # O BeautifulSoup organiza o XML bagunçado que o Google devolve
        try: soup = BeautifulSoup(resposta.content, features='xml')
        except: soup = BeautifulSoup(resposta.content, features='html.parser')
        itens = soup.find_all('item')
        
        vistos = set()
        for item in itens:
            titulo = item.title.text
            link = item.link.text
            if titulo not in vistos:
                vistos.add(titulo)
                titulo_limpo = titulo.split(" - ")[0]
                fonte = titulo.split(" - ")[-1] if " - " in titulo else "News"
                # Aqui aplicamos a análise de sentimento em cada manchete
                sentimento, css = analisar_sentimento(titulo_limpo)
                noticias.append({'titulo': titulo_limpo, 'link': link, 'sentimento': sentimento, 'css': css, 'fonte': fonte})
                if len(noticias) >= 12: break # Limite de 12 notícias
    except: pass
    return noticias

# Tradutor Automático
# Usado para traduzir a descrição de empresas americanas (que vem em inglês do Yahoo)
@st.cache_data
def traduzir_texto(texto, destino='pt'):
    try: return GoogleTranslator(source='auto', target=destino).translate(texto)
    except: return texto 

# Conversor de Moedas
# Pega a cotação do Dólar para calcular quanto custa uma ação americana em Reais
@st.cache_data
def obter_taxa_cambio(origem, destino):
    if origem == destino: return 1.0
    try:
        par = f"{origem}{destino}=X"
        return yf.Ticker(par).history(period="1d")['Close'].iloc[-1]
    except: return 1.0

# ==============================================================================
# 3. BARRA LATERAL (ENTRADA DO USUÁRIO)
# ==============================================================================
with st.sidebar:
    st.header("🔍 Configurações")
    mercado = st.radio("Mercado:", ["🇧🇷 Nacional (B3)", "🇺🇸 Internacional (NY/NASDAQ)"])
    
    input_usuario = st.text_input("Código do Ativo:", value="", placeholder="Ex: PETR4 ou GOOGL").upper().strip()
    valor_aporte = st.number_input("Investimento:", value=1000.0)
    st.markdown("---")
    moeda_base = st.selectbox("Minha Moeda:", ["BRL", "USD", "EUR"])
    moeda_analise = st.selectbox("Analisar em:", ["BRL", "USD", "EUR"])

# ==============================================================================
# 4. LÓGICA PRINCIPAL (DASHBOARD vs DETALHES)
# ==============================================================================

# CENÁRIO A: USUÁRIO DIGITOU UM CÓDIGO (MODO DETETIVE)
if input_usuario:
    # Ajuste de sufixo (.SA) se for Brasil
    if "Nacional" in mercado:
        if not input_usuario.endswith(".SA") and len(input_usuario) > 3:
            ticker_yfinance = f"{input_usuario}.SA"
        else:
            ticker_yfinance = input_usuario
    else:
        ticker_yfinance = input_usuario
        
    ticker_visual = input_usuario.replace(".SA", "")

    st.title(f"🔍 Olheiro: {ticker_visual}")
    st.markdown("---")

    try:
        # Busca os dados no Yahoo Finance
        ativo = yf.Ticker(ticker_yfinance)
        info = ativo.info
        hist = ativo.history(period="5d")

        if hist.empty:
            st.error(f"Ativo '{ticker_visual}' não encontrado no mercado selecionado ({mercado}).")
        else:
            # Cálculos de conversão de moeda e quantidade possível de compra
            moeda_ativo = info.get('currency', 'BRL')
            preco_nativo = info.get('currentPrice', hist['Close'].iloc[-1])
            taxa_origem = obter_taxa_cambio(moeda_base, moeda_ativo)
            qtd_acoes = (valor_aporte * taxa_origem) // preco_nativo
            taxa_destino = obter_taxa_cambio(moeda_ativo, moeda_analise)
            preco_final = preco_nativo * taxa_destino
            
            # Cálculo manual da variação do dia
            if len(hist) >= 2:
                fechamento_ontem = hist['Close'].iloc[-2]
                fechamento_hoje = hist['Close'].iloc[-1]
                if fechamento_ontem > 0:
                    var_dia = ((fechamento_hoje - fechamento_ontem) / fechamento_ontem) * 100
                else: var_dia = 0.0
            else: var_dia = 0.0

            # Exibe os Cards com os dados
            m1, m2, m3, m4 = st.columns(4)
            simbolo_moeda = "R$" if "BRL" in moeda_analise else "$"
            m1.metric(f"Preço ({moeda_analise})", f"{simbolo_moeda} {preco_final:.2f}")
            m2.metric("Ações Possíveis", f"{int(qtd_acoes)}")
            m3.metric("Variação (Dia)", f"{var_dia:.2f}%", delta=f"{var_dia:.2f}%")
            m4.metric("Setor", info.get('sector', 'N/A'))
            st.markdown("---")

            # Layout: Gráfico na Esquerda, Detalhes na Direita
            col_grafico, col_resumo = st.columns([2.5, 1])

            with col_grafico:
                # Abas para diferentes tipos de análise
                tab1, tab2, tab3 = st.tabs(["📈 Gráfico Pro", "🕯️ Velas", "📰 Radar & Veredito"])
                
                with tab1:
                    # Gráfico de Linha com Área (Estilo moderno)
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="Preço", fill='tozeroy', line=dict(color='#00ff41', width=2)), secondary_y=True)
                    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name="Volume", opacity=0.3, marker_color='#808080'), secondary_y=False)
                    fig.update_layout(height=450, template="plotly_dark", showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
                    st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    # Gráfico de Velas (Candlestick) tradicional
                    fig_v = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                    fig_v.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_v, use_container_width=True)
                
                with tab3:
                    # Aqui acontece a mágica do Sentimento de Mercado
                    termo = obter_contexto_busca(ticker_visual, info.get('longName', ticker_visual))
                    news = buscar_noticias_inteligentes(termo)
                    
                    if news:
                        # Conta quantas notícias boas vs ruins
                        qtd_pos = sum(1 for n in news if "Otimista" in n['sentimento'])
                        qtd_neg = sum(1 for n in news if "Pessimista" in n['sentimento'])
                        
                        # Gera o "Veredito" final
                        if qtd_pos > qtd_neg:
                            msg, cls, ico = f"🔥 Veredito: CLIMA OTIMISTA ({qtd_pos} pos)", "v-alta", "🚀"
                        elif qtd_neg > qtd_pos:
                            msg, cls, ico = f"❄️ Veredito: CLIMA CAUTELOSO ({qtd_neg} neg)", "v-baixa", "⚠️"
                        else:
                            msg, cls, ico = "⚖️ Veredito: MERCADO NEUTRO", "v-neutro", "😐"
                        
                        st.markdown(f'<div class="veredito-box {cls}">{ico} {msg}</div>', unsafe_allow_html=True)
                        for n in news:
                            st.markdown(f"<span class='{n['css']}'>{n['sentimento']}</span> <small>[{n['fonte']}]</small> [{n['titulo']}]({n['link']})", unsafe_allow_html=True)
                    else: st.warning("Sem notícias recentes.")

            with col_resumo:
                # Descrição da empresa traduzida
                st.markdown("### Sobre")
                with st.expander("Ver descrição", expanded=True):
                    st.write(traduzir_texto(info.get('longBusinessSummary', 'Sem resumo disponível.')))

    except Exception as e:
        st.error(f"Erro: {e}")

# CENÁRIO B: NENHUM CÓDIGO DIGITADO (MODO DASHBOARD)
else:
    st.title("🔍 Módulo Olheiro de Ações")
    st.info("👈 **Escolha o mercado e digite o código** na barra lateral.")
    st.markdown("---")
    
    # 1. RANKING DE AÇÕES (Top 3 que mais subiram)
    titulo_ranking = "🇧🇷 Top 3 Altas do Dia (Ações B3)" if "Nacional" in mercado else "🇺🇸 Top 3 Altas do Dia (S&P 500 / NASDAQ)"
    st.subheader(titulo_ranking)
    
    lista_acoes = CESTA_ACOES_BR if "Nacional" in mercado else CESTA_ACOES_US
    
    with st.spinner("Analisando o mercado..."):
        top3_acoes = buscar_top_3_generico(lista_acoes)
        
        # Se for Brasil, busca também os rankings de ETFs e BDRs
        if "Nacional" in mercado:
            top3_etfs = buscar_top_3_generico(CESTA_ETFS)
            top3_bdrs = buscar_top_3_generico(CESTA_BDRS)
    
    # Exibe Cards das Ações
    col1, col2, col3 = st.columns(3)
    if len(top3_acoes) >= 3:
        moeda_simbolo = "R$" if "Nacional" in mercado else "$"
        col1.metric(top3_acoes[0]['ticker'], f"{moeda_simbolo} {top3_acoes[0]['preco']:.2f}", f"{top3_acoes[0]['var']:.2f}%")
        col2.metric(top3_acoes[1]['ticker'], f"{moeda_simbolo} {top3_acoes[1]['preco']:.2f}", f"{top3_acoes[1]['var']:.2f}%")
        col3.metric(top3_acoes[2]['ticker'], f"{moeda_simbolo} {top3_acoes[2]['preco']:.2f}", f"{top3_acoes[2]['var']:.2f}%")
    else: st.warning("Mercado fechado ou dados indisponíveis.")

    # 2. RANKING DE ETFs (Só aparece se for Brasil)
    if "Nacional" in mercado:
        st.markdown("---")
        st.subheader("🌎 Top 3 ETFs (Índices e Cripto)")
        
        c1, c2, c3 = st.columns(3)
        if len(top3_etfs) >= 3:
            c1.metric(top3_etfs[0]['ticker'], f"R$ {top3_etfs[0]['preco']:.2f}", f"{top3_etfs[0]['var']:.2f}%")
            c2.metric(top3_etfs[1]['ticker'], f"R$ {top3_etfs[1]['preco']:.2f}", f"{top3_etfs[1]['var']:.2f}%")
            c3.metric(top3_etfs[2]['ticker'], f"R$ {top3_etfs[2]['preco']:.2f}", f"{top3_etfs[2]['var']:.2f}%")
        else: st.info("Carregando ETFs...")

    # 3. RANKING DE BDRs (Só aparece se for Brasil)
    if "Nacional" in mercado:
        st.markdown("---")
        st.subheader("🇺🇸 Top 3 BDRs (Empresas Americanas na B3)")
        
        c1, c2, c3 = st.columns(3)
        if len(top3_bdrs) >= 3:
            c1.metric(top3_bdrs[0]['ticker'], f"R$ {top3_bdrs[0]['preco']:.2f}", f"{top3_bdrs[0]['var']:.2f}%")
            c2.metric(top3_bdrs[1]['ticker'], f"R$ {top3_bdrs[1]['preco']:.2f}", f"{top3_bdrs[1]['var']:.2f}%")
            c3.metric(top3_bdrs[2]['ticker'], f"R$ {top3_bdrs[2]['preco']:.2f}", f"{top3_bdrs[2]['var']:.2f}%")
        else: st.info("Carregando BDRs...")