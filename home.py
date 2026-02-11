import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA (SEM CSS PERSONALIZADO)
# ==============================================================================
st.set_page_config(page_title="Finank", layout="wide", page_icon="💰")

# ==============================================================================
# 2. FUNÇÕES DE DADOS (MANTIVEMOS A INTELIGÊNCIA IGUAL)
# ==============================================================================
@st.cache_data(ttl=300)
def buscar_dados_mercado():
    tickers = ['^BVSP', '^GSPC', 'USDBRL=X', 'EURBRL=X', 'CNYBRL=X', 'BTC-USD']
    dados = {}
    try:
        yf_tickers = yf.Tickers(" ".join(tickers))
        for t in tickers:
            hist = yf_tickers.tickers[t].history(period="2d")
            if len(hist) >= 2:
                fech_ontem = hist['Close'].iloc[-2]
                preco_atual = hist['Close'].iloc[-1]
                var = ((preco_atual - fech_ontem) / fech_ontem) * 100
                dados[t] = {'preco': preco_atual, 'var': var}
            elif len(hist) == 1:
                preco_atual = hist['Close'].iloc[-1]
                dados[t] = {'preco': preco_atual, 'var': 0.0}
    except: pass
    return dados

def analisar_sentimento(texto):
    texto_limpo = texto.lower()
    positivos = ["alta", "sobe", "subiu", "lucro", "dispara", "otimismo", "recorde", "superávit"]
    negativos = ["queda", "cai", "caiu", "prejuízo", "desaba", "crise", "pessimismo", "déficit"]
    score = 0
    for p in positivos: 
        if p in texto_limpo: score += 1
    for n in negativos: 
        if n in texto_limpo: score -= 1
    
    if score > 0: return "🟢 Otimista"
    elif score < 0: return "🔴 Cautela"
    else: return "⚪ Neutro"

@st.cache_data(ttl=600)
def buscar_noticias_topico(topico):
    termo_codificado = urllib.parse.quote(topico)
    url = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    headers = {'User-Agent': 'Mozilla/5.0'}
    noticias = []
    try:
        response = requests.get(url, headers=headers)
        try: soup = BeautifulSoup(response.content, features='xml')
        except: soup = BeautifulSoup(response.content, features='html.parser')
        
        items = soup.find_all('item')[:6]
        for item in items:
            titulo = item.title.text
            link = item.link.text
            fonte = item.source.text if item.source else "News"
            titulo_limpo = titulo.split(" - ")[0]
            sentimento = analisar_sentimento(titulo_limpo)
            noticias.append({'titulo': titulo_limpo, 'link': link, 'fonte': fonte, 'sentimento': sentimento})
    except: pass
    return noticias

# ==============================================================================
# 3. INTERFACE (AGORA USANDO COMPONENTES NATIVOS)
# ==============================================================================
st.title("💰 Finank")
st.markdown("Bem-vindo ao seu centro de comando financeiro.")
st.markdown("---")

# --- BLOCO 1: TERMÔMETRO DE MERCADO ---
st.subheader("🌍 Cotações do Dia")
mercado = buscar_dados_mercado()

# O Streamlit nativo empilha automaticamente no celular!
col1, col2, col3, col4, col5 = st.columns(5)

ibov = mercado.get('^BVSP')
val_ibov = f"{ibov['preco']/1000:.1f}k" if ibov else "--"
var_ibov = f"{ibov['var']:.2f}%" if ibov else "--"
col1.metric("🇧🇷 Ibovespa", val_ibov, var_ibov)

spx = mercado.get('^GSPC')
val_spx = f"{spx['preco']:.0f}" if spx else "--"
var_spx = f"{spx['var']:.2f}%" if spx else "--"
col2.metric("🇺🇸 S&P 500", val_spx, var_spx)

usd = mercado.get('USDBRL=X')
val_usd = f"R$ {usd['preco']:.3f}" if usd else "--"
var_usd = f"{usd['var']:.2f}%" if usd else "--"
col3.metric("💵 Dólar", val_usd, var_usd)

eur = mercado.get('EURBRL=X')
val_eur = f"R$ {eur['preco']:.3f}" if eur else "--"
var_eur = f"{eur['var']:.2f}%" if eur else "--"
col4.metric("💶 Euro", val_eur, var_eur)

btc = mercado.get('BTC-USD')
val_btc = f"$ {btc['preco']:,.0f}" if btc else "--"
var_btc = f"{btc['var']:.2f}%" if btc else "--"
col5.metric("🪙 Bitcoin", val_btc, var_btc)

st.markdown("---")

# --- BLOCO 2: CONVERSOR RÁPIDO ---
st.subheader("💱 Conversor Rápido")
st.caption("Compare o poder de compra instantaneamente.")

# Definição de Taxas
taxa_usd_brl = usd['preco'] if usd else 5.80
taxa_eur_brl = eur['preco'] if eur else 6.20
cny = mercado.get('CNYBRL=X')
taxa_cny_brl = cny['preco'] if cny else 0.80
taxa_btc_usd = btc['preco'] if btc else 0.0
taxa_btc_brl = taxa_btc_usd * taxa_usd_brl

info_moedas = {
    "Real (BRL)":    {"fator": 1.0,          "simbolo": "R$"},
    "Dólar (USD)":   {"fator": taxa_usd_brl, "simbolo": "$"},
    "Euro (EUR)":    {"fator": taxa_eur_brl, "simbolo": "€"},
    "Yuan (CNY)":    {"fator": taxa_cny_brl, "simbolo": "¥"},
    "Bitcoin (BTC)": {"fator": taxa_btc_brl, "simbolo": "₿"}
}

# Layout de Conversão Nativo
c_input, c_res = st.columns([1, 3])

with c_input:
    valor_base = st.number_input("Valor:", value=1.00, step=1.0, format="%.2f")
    moeda_origem = st.selectbox("Moeda:", list(info_moedas.keys()))

with c_res:
    # Lógica de conversão
    fator_origem = info_moedas[moeda_origem]["fator"]
    if fator_origem > 0:
        valor_em_reais = valor_base * fator_origem
        moedas_destino = [m for m in info_moedas.keys() if m != moeda_origem]
        
        # Exibe os resultados usando st.metric (NATIVO e SEGURO)
        cols_resultado = st.columns(len(moedas_destino))
        for i, moeda_alvo in enumerate(moedas_destino):
            dados = info_moedas[moeda_alvo]
            fator_destino = dados["fator"]
            
            if fator_destino > 0:
                val_final = valor_em_reais / fator_destino
                if "Bitcoin" in moeda_alvo:
                    txt = f"{dados['simbolo']} {val_final:.8f}"
                else:
                    txt = f"{dados['simbolo']} {val_final:,.2f}"
                
                cols_resultado[i].metric(moeda_alvo.split(" ")[0], txt)

st.markdown("---")

# --- BLOCO 3: NOTÍCIAS (USANDO EXPANDER NATIVO) ---
st.subheader("📰 Radar de Notícias")
tab_geral, tab_acoes, tab_cripto, tab_fiis = st.tabs(["🔥 Macro", "🏢 Ações", "₿ Cripto", "🏗️ FIIs"])

def renderizar_noticias(termo_busca):
    news = buscar_noticias_topico(termo_busca)
    if news:
        for n in news:
            # Título com Link e Sentimento
            texto_link = f"[{n['titulo']}]({n['link']})"
            st.markdown(f"{n['sentimento']} | **{n['fonte']}**: {texto_link}")
    else: st.info("Buscando atualizações...")

with tab_geral: renderizar_noticias("Mercado financeiro economia brasil hoje")
with tab_acoes: renderizar_noticias("Ações bolsa de valores empresas brasil")
with tab_cripto: renderizar_noticias("Mercado criptomoedas bitcoin hoje")
with tab_fiis: renderizar_noticias("Fundos imobiliários IFIX notícias")
