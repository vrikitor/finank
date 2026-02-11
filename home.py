"""
================================================================================
💰 FINANK - HOME (PÁGINA INICIAL)
================================================================================
Olá! Aqui é onde tudo começa. Este arquivo é o "cartão de visitas" do nosso sistema.
Eu projetei essa página para ser um Painel de Controle (Dashboard) que te dá um
resumo rápido de tudo o que está acontecendo no mercado agora.

TECNOLOGIAS USADAS AQUI:
1. Streamlit: Para criar toda a parte visual (botões, textos, layout).
2. Yfinance: Para buscar o preço do Dólar, Bitcoin e Ibovespa em tempo real.
3. BeautifulSoup (BS4): Para "raspar" (ler) as notícias do Google News.
4. Pandas: Para organizar os dados em tabelas (se precisar).
"""

import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CSS (A MAQUIAGEM)
# ==============================================================================
# Aqui eu digo para o navegador: "O nome da aba é Finank Home e quero usar a tela toda (wide)"
st.set_page_config(page_title="Finank Home", layout="wide", page_icon="💰")

# Agora vou injetar um pouco de CSS (Estilo) para deixar tudo bonito.
# Eu queria que os cartões de notícias tivessem um visual moderno e escuro.
st.markdown("""
    <style>
    /* --- ESTILOS GERAIS (DESKTOP) --- */
    .stMetric { background-color: #1b1e23; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .news-card { background-color: #262730; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #00D4FF; }
    .news-title { font-weight: bold; font-size: 1.1em; color: #fff; text-decoration: none; }
    .news-source { font-size: 0.8em; color: #b0b0b0; }
    
    .sentimento-positivo { color: #00ff41; font-weight: bold; border: 1px solid #00ff41; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; }
    .sentimento-negativo { color: #ff2b2b; font-weight: bold; border: 1px solid #ff2b2b; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; }
    .sentimento-neutro { color: #8b949e; border: 1px solid #8b949e; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; }

    .custom-card {
        background-color: #1b1e23;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 100px;
    }
    .card-label { font-size: 14px; color: #8b949e; margin-bottom: 5px; }
    .card-value { font-size: 20px; font-weight: bold; color: #ffffff; word-wrap: break-word; line-height: 1.2; }
    
    .seta-centro {
        display: flex; align-items: center; justify-content: center; height: 100%;
        font-size: 24px; color: #00D4FF; margin-top: 25px;
    }

    /* --- 📱 O SEGREDO DO MOBILE (RESPONSIVIDADE) --- */
    @media (max-width: 768px) {
        /* Força as colunas a ficarem uma embaixo da outra */
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 auto !important;
            min-width: 100% !important;
        }
        
        /* Ajusta a setinha do conversor para girar 90 graus no celular */
        .seta-centro { margin-top: 5px; margin-bottom: 5px; transform: rotate(90deg); }
        
        /* Ajusta margens para não grudar */
        .stMetric { margin-bottom: 10px; }
        .custom-card { margin-bottom: 10px; min-height: auto; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. FUNÇÕES DE DADOS (O MOTOR DO SISTEMA)
# ==============================================================================

# Função 1: Buscar Dados do Mercado (Cotações)
# Eu uso @st.cache_data(ttl=300) para o sistema não ficar lento.
# Ele baixa os dados e guarda na memória por 300 segundos (5 minutos).
@st.cache_data(ttl=300)
def buscar_dados_mercado():
    # Lista de códigos que o Yahoo Finance entende:
    # ^BVSP = Ibovespa (Brasil)
    # ^GSPC = S&P 500 (EUA)
    # USDBRL=X = Dólar para Real
    tickers = ['^BVSP', '^GSPC', 'USDBRL=X', 'EURBRL=X', 'CNYBRL=X', 'BTC-USD']
    dados = {}
    try:
        # Baixa tudo de uma vez para ser rápido
        yf_tickers = yf.Tickers(" ".join(tickers))
        for t in tickers:
            # Pego os últimos 2 dias para comparar Hoje vs Ontem e saber se subiu ou caiu
            hist = yf_tickers.tickers[t].history(period="2d")
            
            if len(hist) >= 2:
                fech_ontem = hist['Close'].iloc[-2]
                preco_atual = hist['Close'].iloc[-1]
                # Fórmula da variação: ((Hoje - Ontem) / Ontem) * 100
                var = ((preco_atual - fech_ontem) / fech_ontem) * 100
                dados[t] = {'preco': preco_atual, 'var': var}
            elif len(hist) == 1:
                # Se só tiver dados de hoje (feriado?), variação é zero
                preco_atual = hist['Close'].iloc[-1]
                dados[t] = {'preco': preco_atual, 'var': 0.0}
    except: pass
    return dados

# Função 2: Analisar Sentimento (O "Psicólogo" do Robô)
# O computador lê o título da notícia e tenta adivinhar se é Boa ou Ruim.
def analisar_sentimento(texto):
    texto_limpo = texto.lower() # Transforma tudo em minúsculo
    
    # Palavras-chave que indicam coisa boa
    positivos = ["alta", "sobe", "subiu", "lucro", "dispara", "otimismo", "recorde", "superávit", "aprovado", "dividendos"]
    # Palavras-chave que indicam coisa ruim
    negativos = ["queda", "cai", "caiu", "prejuízo", "desaba", "crise", "pessimismo", "déficit", "risco", "medo"]
    
    score = 0
    for p in positivos: 
        if p in texto_limpo: score += 1
    for n in negativos: 
        if n in texto_limpo: score -= 1
    
    # Se Score > 0 é Otimista, se < 0 é Pessimista
    if score > 0: return "🟢 Otimista", "sentimento-positivo"
    elif score < 0: return "🔴 Cautela", "sentimento-negativo"
    else: return "⚪ Neutro", "sentimento-neutro"

# Função 3: Buscar Notícias (Web Scraping)
# Eu vou lá no Google News e pego as manchetes mais recentes sobre o tópico.
@st.cache_data(ttl=600) # Atualiza a cada 10 min
def buscar_noticias_topico(topico):
    termo_codificado = urllib.parse.quote(topico)
    # URL mágica do Google News em RSS (formato fácil de ler por robôs)
    url = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    headers = {'User-Agent': 'Mozilla/5.0'} # Finge que sou um navegador comum
    noticias = []
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, features='xml') # O BS4 organiza a bagunça do HTML
        items = soup.find_all('item')[:6] # Pega só as 6 primeiras
        
        for item in items:
            titulo = item.title.text
            link = item.link.text
            fonte = item.source.text if item.source else "News"
            
            # Limpa o título (tira o nome do jornal do final)
            titulo_limpo = titulo.split(" - ")[0]
            
            # Chama o "Psicólogo" para ver se a notícia é boa
            sentimento, css = analisar_sentimento(titulo_limpo)
            
            noticias.append({'titulo': titulo_limpo, 'link': link, 'fonte': fonte, 'sentimento': sentimento, 'css': css})
    except: pass
    return noticias

# Função Auxiliar: Criar o HTML do cartãozinho do conversor
def exibir_card_conversor(label, valor):
    st.markdown(f"""
    <div class="custom-card">
        <div class="card-label">{label}</div>
        <div class="card-value">{valor}</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFACE (O QUE VOCÊ VÊ NA TELA)
# ==============================================================================
st.title("💰 Finank ")
st.markdown("Bem-vindo ao seu centro de comando financeiro.")
st.markdown("---")

# --- BLOCO 1: TERMÔMETRO DE MERCADO (OS NÚMEROS GRANDES) ---
# Aqui eu busco os dados e distribuo em 5 colunas lado a lado
with st.container():
    st.subheader("🌍 Cotações do Dia")
    mercado = buscar_dados_mercado()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Ibovespa (Brasil)
    ibov = mercado.get('^BVSP')
    val_ibov = f"{ibov['preco']/1000:.1f}k" if ibov else "--"
    var_ibov = f"{ibov['var']:.2f}%" if ibov else "--"
    col1.metric("🇧🇷 Ibovespa", val_ibov, var_ibov)
    
    # S&P 500 (EUA)
    spx = mercado.get('^GSPC')
    val_spx = f"{spx['preco']:.0f}" if spx else "--"
    var_spx = f"{spx['var']:.2f}%" if spx else "--"
    col2.metric("🇺🇸 S&P 500", val_spx, var_spx)
    
    # Dólar
    usd = mercado.get('USDBRL=X')
    val_usd = f"R$ {usd['preco']:.3f}" if usd else "--"
    var_usd = f"{usd['var']:.2f}%" if usd else "--"
    col3.metric("💵 Dólar", val_usd, var_usd)
    
    # Euro
    eur = mercado.get('EURBRL=X')
    val_eur = f"R$ {eur['preco']:.3f}" if eur else "--"
    var_eur = f"{eur['var']:.2f}%" if eur else "--"
    col4.metric("💶 Euro", val_eur, var_eur)
    
    # Bitcoin
    btc = mercado.get('BTC-USD')
    val_btc = f"$ {btc['preco']:,.0f}" if btc else "--"
    var_btc = f"{btc['var']:.2f}%" if btc else "--"
    col5.metric("🪙 Bitcoin", val_btc, var_btc)

st.markdown("---")

# --- BLOCO 2: CONVERSOR RÁPIDO ---
# Uma ferramenta útil para saber quanto vale R$ 100 em Dólar, Euro e Bitcoin ao mesmo tempo.
st.subheader("💱 Conversor Rápido")
st.caption("Compare o poder de compra instantaneamente.")

with st.container():
    # 1. Defino as taxas manuais caso a API falhe (Fallback)
    taxa_usd_brl = usd['preco'] if usd else 5.80
    taxa_eur_brl = eur['preco'] if eur else 6.20
    
    cny = mercado.get('CNYBRL=X')
    taxa_cny_brl = cny['preco'] if cny else 0.80
    
    taxa_btc_usd = btc['preco'] if btc else 0.0
    # Bitcoin é cotado em Dólar, então converto para Real: (Preço BTC em $) * (Preço Dólar)
    taxa_btc_brl = taxa_btc_usd * taxa_usd_brl

    # 2. Mapa de Inteligência: Digo ao sistema quanto vale cada moeda em relação ao Real
    info_moedas = {
        "Real (BRL)":    {"fator": 1.0,          "simbolo": "R$", "label": "🇧🇷 Real"},
        "Dólar (USD)":   {"fator": taxa_usd_brl, "simbolo": "$",  "label": "🇺🇸 Dólar"},
        "Euro (EUR)":    {"fator": taxa_eur_brl, "simbolo": "€",  "label": "🇪🇺 Euro"},
        "Yuan (CNY)":    {"fator": taxa_cny_brl, "simbolo": "¥",  "label": "🇨🇳 Yuan"},
        "Bitcoin (BTC)": {"fator": taxa_btc_brl, "simbolo": "₿",  "label": "₿ Bitcoin"}
    }

    # Layout: Input (Esquerda) + Seta + 4 Resultados (Direita)
    c_input, c_seta, c_res1, c_res2, c_res3, c_res4 = st.columns([1.5, 0.2, 1, 1, 1, 1])
    
    with c_input:
        col_v, col_m = st.columns([1, 1.5])
        valor_base = col_v.number_input("Valor:", value=1.00, step=1.0, format="%.2f")
        moeda_origem = col_m.selectbox("Moeda:", list(info_moedas.keys()))

    with c_seta:
        st.markdown("<div class='seta-centro'>➔</div>", unsafe_allow_html=True)
        
    # A Lógica Matemática da Conversão:
    # Passo 1: Converter tudo para Real (Moeda Base)
    fator_origem = info_moedas[moeda_origem]["fator"]
    
    if fator_origem > 0:
        valor_em_reais = valor_base * fator_origem
        
        # Passo 2: Converter do Real para as outras moedas
        # Excluo a moeda que o usuário escolheu (não faz sentido converter Dólar para Dólar)
        moedas_destino = [m for m in info_moedas.keys() if m != moeda_origem]
        
        colunas_res = [c_res1, c_res2, c_res3, c_res4]
        
        for i, moeda_alvo in enumerate(moedas_destino):
            dados = info_moedas[moeda_alvo]
            fator_destino = dados["fator"]
            
            # Cálculo final: (Valor em Reais) / (Cotação da Moeda Alvo)
            if fator_destino > 0:
                val_final = valor_em_reais / fator_destino
            else:
                val_final = 0.0
            
            # Formatação bonita (Bitcoin precisa de mais casas decimais)
            if "Bitcoin" in moeda_alvo:
                texto_valor = f"{dados['simbolo']} {val_final:.8f}"
            else:
                texto_valor = f"{dados['simbolo']} {val_final:,.2f}"
            
            # Desenha o cartão na tela
            with colunas_res[i]:
                exibir_card_conversor(dados["label"], texto_valor)

    else:
        st.error("Erro nas taxas de conversão.")

st.markdown("---")

# --- BLOCO 3: CENTRAL DE NOTÍCIAS (O RADAR) ---
st.subheader("📰 Radar de Notícias")
# Crio abas para organizar o conteúdo
tab_geral, tab_acoes, tab_cripto, tab_fiis = st.tabs(["🔥 Destaques Macro", "🏢 Ações & Empresas", "₿ Cripto & Web3", "🏗️ Fundos Imobiliários"])

def renderizar_noticias(termo_busca):
    # Chama minha função de buscar no Google News
    news = buscar_noticias_topico(termo_busca)
    if news:
        for n in news:
            # Cria um cartão HTML para cada notícia
            st.markdown(f"""
            <div class="news-card">
                <span class="{n['css']}">{n['sentimento']}</span> 
                <span class="news-source"> | {n['fonte']}</span>
                <br>
                <a href="{n['link']}" class="news-title" target="_blank">{n['titulo']}</a>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("Buscando atualizações...")

# Aqui eu defino o que buscar em cada aba
with tab_geral: renderizar_noticias("Mercado financeiro economia brasil hoje")
with tab_acoes: renderizar_noticias("Ações bolsa de valores empresas brasil")
with tab_cripto: renderizar_noticias("Mercado criptomoedas bitcoin hoje")

with tab_fiis: renderizar_noticias("Fundos imobiliários IFIX notícias")
