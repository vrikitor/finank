"""
================================================================================
⚔️ FINANK - ARENA DE BATALHA (COMPARADOR DE ATIVOS)
================================================================================
Bem-vindo ao Coliseu dos Investimentos! 🏟️
Aqui colocamos dois ativos frente a frente para ver quem entregou mais resultado.

O QUE ESTE CÓDIGO FAZ:
1. Normalização: Ajusta os preços para que ambos comecem do ponto 0%.
   Isso permite comparar coisas de preços diferentes (ex: Ação de R$ 10 vs Ação de R$ 100).
2. Correlação: Calcula estatisticamente se os ativos "andam juntos" ou não.
3. Fundamentos: Busca dados como P/L e Dividendos para uma comparação técnica.

É a ferramenta perfeita para decidir entre "Ativo A" ou "Ativo B".
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==============================================================================
# 1. CONFIGURAÇÃO VISUAL & CSS (O ESTILO DA ARENA)
# ==============================================================================
st.set_page_config(page_title="Batalha de Ativos", layout="wide", page_icon="⚔️")

st.markdown("""
    <style>
    /* Estilo dos números principais */
    .stMetric { background-color: #1b1e23; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    
    /* Aquele "VS" gigante e laranja no meio da tela */
    .vs-badge { font-size: 40px; font-weight: bold; color: #F7931A; text-align: center; display: flex; align-items: center; justify-content: center; height: 100%; }
    
    /* Cartões de Fundamentos (Tale of the Tape) */
    .card-fundamentos { background-color: #262730; padding: 20px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #00D4FF; }
    .card-fundamentos-b { border-left: 4px solid #F7931A; } /* Cor Laranja para o Desafiante */
    .metric-row { display: flex; justify-content: space-between; border-bottom: 1px solid #30363d; padding: 8px 0; }
    .metric-label { color: #b0b0b0; font-size: 0.9em; }
    .metric-value { color: #fff; font-weight: bold; }
    
    /* BARRA DE CORRELAÇÃO (O TERMÔMETRO) */
    /* Cria aquela barra degradê que mostra se os ativos são amigos ou inimigos */
    .corr-container { background-color: #262730; padding: 20px; border-radius: 10px; margin-top: 20px; text-align: center; border: 1px solid #30363d; }
    .corr-bar-bg { width: 100%; height: 20px; background: linear-gradient(90deg, #00D4FF 0%, #30363d 50%, #ff2b2b 100%); border-radius: 10px; position: relative; margin-top: 15px; margin-bottom: 10px; }
    .corr-marker { width: 6px; height: 26px; background-color: #fff; position: absolute; top: -3px; box-shadow: 0 0 10px white; transition: left 0.5s; border-radius: 2px; }
    .corr-labels { display: flex; justify-content: space-between; color: #b0b0b0; font-size: 0.8em; }
    
    /* CARDS DE DESTAQUES DO DIA (TOP 5) */
    .top-card { background-color: #21262d; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #30363d; margin-bottom: 5px; }
    .top-ticker { font-weight: bold; color: #fff; font-size: 1.1em; }
    .top-val { font-weight: bold; font-size: 1em; }
    .sobe { color: #00ff41; }
    .desce { color: #ff2b2b; }
    
    /* LINHA VERTICAL DIVISÓRIA */
    .vertical-line { border-left: 1px solid #30363d; height: 120px; margin: auto; width: 1px; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LISTAS UNIVERSAIS (PARA O SCANNER)
# ==============================================================================
# O sistema monitora esses ativos automaticamente na tela inicial
UNIV_ACOES = [
    "VALE3.SA", "PETR4.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "WEGE3.SA", "PRIO3.SA", 
    "ELET3.SA", "RENT3.SA", "SUZB3.SA", "GGBR4.SA", "JBSS3.SA", "RADL3.SA", "CSAN3.SA",
    "MGLU3.SA", "LREN3.SA", "HAPV3.SA", "B3SA3.SA", "CMIG4.SA", "TAEE11.SA"
]

UNIV_FIIS = [
    "MXRF11.SA", "HGLG11.SA", "KNRI11.SA", "XPLG11.SA", "XPML11.SA", "VISC11.SA", "HGRU11.SA",
    "BCFF11.SA", "BRCO11.SA", "IRDM11.SA", "CPTS11.SA", "HFOF11.SA", "KNCR11.SA", "JSRE11.SA",
    "VILG11.SA", "MALL11.SA", "HGBS11.SA", "LVBI11.SA", "RECR11.SA", "SNAG11.SA"
]

# ==============================================================================
# 3. MOTOR DE DADOS (O CÉREBRO)
# ==============================================================================

# Função Auxiliar: Garante que o código está certo (põe .SA se for Brasil)
def tratar_nome(t):
    t = t.upper().strip()
    if "-" in t: return t # Cripto
    usa_vip = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "AMD", "NFLX", "DIS", "KO", "MCD", "V", "JPM"]
    if t in usa_vip: return t # Ações EUA
    if "." in t: return t # Já tem ponto
    return f"{t}.SA" # Assume Brasil

# Função 1: Buscar Destaques (Top 5)
# Olha a lista de ativos e vê quem subiu mais hoje.
@st.cache_data(ttl=1800)
def buscar_destaques(lista_ativos):
    try:
        dados = yf.download(lista_ativos, period="2d", progress=False)['Close']
        if len(dados) >= 2:
            # Pega o último dia e calcula a variação percentual
            variacao = dados.pct_change().iloc[-1] * 100
            # Ordena e pega os top 5
            top5 = variacao.sort_values(ascending=False).head(5)
            return top5
        return None
    except: return None

# Função 2: Dados para o Gráfico de Batalha e Correlação
# Aqui acontece a mágica da "Normalização".
@st.cache_data(ttl=3600)
def obter_dados_grafico_corr(ticker1, ticker2, periodo_selecionado):
    t1_code = tratar_nome(ticker1)
    t2_code = tratar_nome(ticker2)
    try:
        # Baixa os dados históricos
        ativo_a = yf.Ticker(t1_code).history(period=periodo_selecionado, auto_adjust=False)['Close']
        ativo_b = yf.Ticker(t2_code).history(period=periodo_selecionado, auto_adjust=False)['Close']
        
        if ativo_a.empty or ativo_b.empty: return None, None, 0, t1_code, t2_code
        
        # Limpa o fuso horário para não dar erro
        ativo_a.index = ativo_a.index.tz_localize(None)
        ativo_b.index = ativo_b.index.tz_localize(None)
        
        # Junta os dois em uma tabela só
        df = pd.concat([ativo_a, ativo_b], axis=1)
        df.columns = [t1_code, t2_code]
        df = df.ffill().dropna()
        
        # NORMALIZAÇÃO: (Preço / Preço Inicial - 1) * 100
        # Isso faz os dois começarem em 0%, permitindo comparar a rentabilidade justa.
        df_norm = (df / df.iloc[0] - 1) * 100
        
        # CÁLCULO DE ESTATÍSTICAS
        retornos = df.pct_change().dropna()
        # Volatilidade anualizada (Risco)
        vol1 = retornos[t1_code].std() * (252 ** 0.5)
        vol2 = retornos[t2_code].std() * (252 ** 0.5)
        
        # Correlação (de -1 a +1)
        try:
            corr = retornos[t1_code].corr(retornos[t2_code])
            if np.isnan(corr): corr = 0.0
        except: corr = 0.0
        
        return df_norm, (vol1, vol2), corr, t1_code, t2_code
    except: return None, None, 0, t1_code, t2_code

# Função 3: Buscar Fundamentos (P/L, PVP, DY)
@st.cache_data(ttl=3600)
def obter_fundamentos(ticker):
    try: return yf.Ticker(ticker).info
    except: return {}

# Formatação bonita dos números (Bilhões, Porcentagem, Moeda)
def formatar_dado(info, chaves, tipo="moeda"):
    valor = None
    if info:
        for k in chaves:
            if k in info and info[k] is not None:
                valor = info[k]
                break
    if valor is None: return "--"
    try:
        if tipo == "moeda": return f"{valor:,.2f}"
        if tipo == "pct": 
            if isinstance(valor, (int, float)):
                if valor > 5: valor = valor / 100 
                return f"{valor*100:.2f}%"
            return "--"
        if tipo == "num": return f"{valor:.2f}"
        if tipo == "bi": return f"{valor/1_000_000_000:.2f} B"
    except: return "--"
    return str(valor)

# ==============================================================================
# 3. INTERFACE (BARRA LATERAL)
# ==============================================================================
with st.sidebar:
    st.header("⚔️ Configurar Luta")
    # Campos de entrada para os lutadores
    input1 = st.text_input("Lutador 1", value="").upper()
    input2 = st.text_input("Lutador 2", value="").upper()
    
    mapa_tempo = {"1 Mês": "1mo", "6 Meses": "6mo", "1 Ano": "1y", "5 Anos": "5y"}
    tempo_user = st.selectbox("Round (Tempo):", list(mapa_tempo.keys()), index=2)

# ==============================================================================
# 4. PAINEL PRINCIPAL
# ==============================================================================

# --- SCANNER DE DESTAQUES (TOPO DA PÁGINA) ---
st.title("🔥 Destaques do Mercado Agora")

# Expander aberto por padrão para mostrar o pulso do mercado
with st.expander("Ver Top 5 do Dia (Ao Vivo)", expanded=True):
    col_acoes, col_div, col_fiis = st.columns([1, 0.1, 1])
    
    # Lado Esquerdo: Ações
    with col_acoes:
        st.subheader("📈 Ações em Alta")
        top_acoes = buscar_destaques(UNIV_ACOES)
        if top_acoes is not None:
            cols = st.columns(5)
            for i, (ticker, val) in enumerate(top_acoes.items()):
                nome_limpo = ticker.replace(".SA", "")
                cor = "sobe" if val >= 0 else "desce"
                with cols[i]:
                    st.markdown(f"""
                    <div class="top-card">
                        <div class="top-ticker">{nome_limpo}</div>
                        <div class="top-val {cor}">{val:+.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
        else: st.info("Carregando...")

    # Divisória vertical chique
    with col_div:
        st.markdown('<div class="vertical-line"></div>', unsafe_allow_html=True)

    # Lado Direito: FIIs
    with col_fiis:
        st.subheader("🏢 FIIs em Alta")
        top_fiis = buscar_destaques(UNIV_FIIS)
        if top_fiis is not None:
            cols = st.columns(5)
            for i, (ticker, val) in enumerate(top_fiis.items()):
                nome_limpo = ticker.replace(".SA", "")
                cor = "sobe" if val >= 0 else "desce"
                with cols[i]:
                    st.markdown(f"""
                    <div class="top-card">
                        <div class="top-ticker">{nome_limpo}</div>
                        <div class="top-val {cor}">{val:+.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
        else: st.info("Carregando...")

st.markdown("---")

# --- BATALHA PRINCIPAL (Só roda se tiver os dois lutadores) ---
if input1 and input2:
    st.header(f"⚔️ ARENA FINAL: {input1} vs {input2}")
    
    df_final, volatildade, corr, nome1, nome2 = obter_dados_grafico_corr(input1, input2, mapa_tempo[tempo_user])

    if df_final is not None and not df_final.empty:
        # Pega a rentabilidade acumulada final
        rent1 = df_final[nome1].iloc[-1]
        rent2 = df_final[nome2].iloc[-1]

        # Placar da Luta
        c1, c2, c3 = st.columns([1, 0.2, 1])
        c1.metric(nome1, f"{rent1:+.2f}%", delta="Vencedor" if rent1 > rent2 else None)
        c2.markdown("<div class='vs-badge'>VS</div>", unsafe_allow_html=True)
        c3.metric(nome2, f"{rent2:+.2f}%", delta="Vencedor" if rent2 > rent1 else None)

        # Gráfico Comparativo
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_final.index, y=df_final[nome1], mode='lines', name=nome1, line=dict(color='#00D4FF', width=3)))
        fig.add_trace(go.Scatter(x=df_final.index, y=df_final[nome2], mode='lines', name=nome2, line=dict(color='#F7931A', width=3)))
        fig.update_layout(title="Rentabilidade Normalizada (%)", template="plotly_dark", height=450, hovermode="x unified", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        
        # ANÁLISE DE CORRELAÇÃO (DIVERSIFICAÇÃO)
        if corr > 0.6: texto_corr, cor_texto = "⚠️ Alta Correlação (Andam Juntos)", "#ff2b2b"
        elif corr > 0.2: texto_corr, cor_texto = "😐 Correlação Moderada", "#F7931A"
        elif corr > -0.2: texto_corr, cor_texto = "✅ Baixa Correlação (Ótima Diversificação)", "#00ff41"
        else: texto_corr, cor_texto = "🛡️ Correlação Negativa (Hedge)", "#00D4FF"
        
        # Cálculo para mover a bolinha da barra
        posicao_marker = max(0, min(100, ((corr + 1) / 2) * 100))

        st.subheader("🔗 Análise de Diversificação")
        st.markdown(f"""
        <div class="corr-container">
            <h3>Coeficiente: {corr:.2f}</h3>
            <p style="color: {cor_texto}; font-weight: bold;">{texto_corr}</p>
            <div class="corr-bar-bg"><div class="corr-marker" style="left: {posicao_marker}%;"></div></div>
            <div class="corr-labels"><span>⬅️ Opostos</span><span>Independentes</span><span>Iguais ➡️</span></div>
        </div>
        """, unsafe_allow_html=True)

        # TALE OF THE TAPE (FUNDAMENTOS)
        st.markdown("---")
        st.subheader("📊 Tale of the Tape")
        
        with st.spinner("Carregando indicadores..."):
            info1 = obter_fundamentos(nome1)
            info2 = obter_fundamentos(nome2)
        
        col_f1, col_f2 = st.columns(2)
        metricas = [
            ("Preço Atual", ['currentPrice', 'regularMarketPrice'], 'moeda'),
            ("P/L", ['trailingPE'], 'num'),
            ("P/VP", ['priceToBook'], 'num'),
            ("DY (Anual)", ['dividendYield'], 'pct'),
            ("Valor Mercado", ['marketCap'], 'bi')
        ]

        def criar_card(nome, info, vol, classe_css):
            html = f'<div class="{classe_css}">'
            for label, keys, fmt in metricas:
                val = formatar_dado(info, keys, fmt)
                html += f'<div class="metric-row"><span class="metric-label">{label}</span> <span class="metric-value">{val}</span></div>'
            v_val = f"{vol*100:.2f}%" if vol else "--"
            html += f'<div class="metric-row"><span class="metric-label">⚠️ Volatilidade</span> <span class="metric-value">{v_val}</span></div></div>'
            st.markdown(f"### {nome}")
            st.markdown(html, unsafe_allow_html=True)

        with col_f1: criar_card(f"🟦 {nome1}", info1, volatildade[0], "card-fundamentos")
        with col_f2: criar_card(f"🟧 {nome2}", info2, volatildade[1], "card-fundamentos card-fundamentos-b")

    else:
        st.warning(f"Não conseguimos cruzar os dados de {nome1} e {nome2}.")
else:
    # MENSAGEM DE ESPERA (QUANDO TUDO ESTÁ VAZIO)
    st.info("👈 **Comece a Batalha:** Selecione dois ativos na barra lateral para ver o comparativo completo!")