"""
================================================================================
💰 FINANK - CARTEIRA INTELIGENTE
================================================================================
Esta é a página mais complexa e poderosa do sistema. Ela funciona como um "Cofre".
Aqui nós não apenas guardamos o que você comprou, mas também calculamos quanto
o seu dinheiro rendeu hoje.

O GRANDE TRUQUE (A LÓGICA HÍBRIDA):
1. Ações/Cripto/FIIs: Buscamos o preço atual no Yahoo Finance.
2. Tesouro Direto: Buscamos o preço no site oficial do Tesouro (API JSON).
3. Renda Fixa/Outros: Se não acharmos o preço, usamos Matemática Financeira
   (Juros Compostos) para projetar quanto vale hoje baseado na taxa que você contratou.

Ninguém fica para trás. Todo ativo tem seu valor atualizado.
"""

import streamlit as st
import pandas as pd
import os
import plotly.express as px
import yfinance as yf
import requests
import numpy as np
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
st.set_page_config(page_title="Minha Carteira", layout="wide", page_icon="💰")

# Defino o nome do nosso "Banco de Dados" (que na verdade é um arquivo de texto simples)
ARQUIVO_DB = "carteira.csv"

# ==============================================================================
# 2. MOTOR DE DADOS & CÁLCULOS (O CÉREBRO)
# ==============================================================================

# Função 1: Carregar o Banco de Dados
# Se o arquivo não existir, eu crio um vazio. Se existir, eu leio.
def carregar_dados():
    if not os.path.exists(ARQUIVO_DB):
        # Cria as colunas que precisamos
        df = pd.DataFrame(columns=["Data", "Ativo", "Tipo", "Operacao", "Quantidade", "Preco", "Taxa"])
        df.to_csv(ARQUIVO_DB, index=False)
        return df
    try:
        df = pd.read_csv(ARQUIVO_DB)
        # Garante que a coluna 'Taxa' existe (para compatibilidade com versões antigas)
        if "Taxa" not in df.columns: df["Taxa"] = 0.0
        return df
    except: return pd.DataFrame()

# Função 2: Salvar uma Nova Compra/Venda
# Pega o que você digitou no formulário e adiciona uma nova linha no CSV.
def salvar_operacao(data, ativo, tipo, operacao, qtd, preco, taxa):
    df = carregar_dados()
    novo = pd.DataFrame({
        "Data": [data], "Ativo": [ativo.upper()], "Tipo": [tipo], 
        "Operacao": [operacao], "Quantidade": [qtd], "Preco": [preco], "Taxa": [taxa]
    })
    # Concatena (junta) o antigo com o novo e salva
    pd.concat([df, novo], ignore_index=True).to_csv(ARQUIVO_DB, index=False)
    st.success("✅ Operação salva com sucesso!")
    st.rerun() # Recarrega a página para mostrar os dados novos

# Função 3: Calcular a Posição Atual (A Matemática)
# Transforma o histórico "Comprei 10, Vendi 2" em "Tenho 8".
def calcular_posicao_atual(df):
    if df.empty: return pd.DataFrame()
    carteira = df.copy()
    
    carteira['Data'] = pd.to_datetime(carteira['Data'])
    
    # Se for VENDA, transformo a quantidade em negativo para subtrair
    carteira['Qtd_Sinal'] = carteira.apply(lambda x: x['Quantidade'] * -1 if x['Operacao'] == 'Venda' else x['Quantidade'], axis=1)
    carteira['Financeiro'] = carteira['Qtd_Sinal'] * carteira['Preco']

    # Agrupo tudo por Ativo (Ex: Soma todas as compras de PETR4)
    resumo = carteira.groupby(['Tipo', 'Ativo']).agg({
        'Qtd_Sinal': 'sum',      # Quantas sobraram
        'Financeiro': 'sum',     # Quanto gastei no total
        'Taxa': 'mean',          # Média da taxa contratada
        'Data': 'min'            # Data da primeira compra (para calcular o tempo)
    }).reset_index()
    
    # Renomeio para ficar bonito
    resumo.rename(columns={'Qtd_Sinal': 'Qtd_Atual', 'Financeiro': 'Total_Investido', 'Data': 'Data_Inicial'}, inplace=True)
    
    # Filtro só o que eu ainda tenho (Qtd > 0)
    resumo = resumo[resumo['Qtd_Atual'] > 0]
    
    # Calculo o Preço Médio (PM) -> Total Gasto / Quantidade
    resumo['PM'] = resumo['Total_Investido'] / resumo['Qtd_Atual']
    return resumo

# --- MOTOR DO TESOURO DIRETO (API OFICIAL) ---
# Aqui eu acesso o "backstage" do site do Tesouro para pegar os preços reais.
@st.cache_data(ttl=3600) # Cache de 1 hora para não sobrecarregar
def buscar_dados_tesouro_direto():
    url = "https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json"
    try:
        response = requests.get(url, verify=False, timeout=5)
        dados = response.json()
        mapa_precos = {}
        
        # O JSON é complexo, então eu navego até achar a lista de títulos
        lista_titulos = dados['response']['TrsrBdTradgList']
        for item in lista_titulos:
            titulo = item['TrsrBd']
            nome = titulo['nm'].upper() 
            # Tento pegar o preço de Venda (Resgate). Se não tiver, pego o de Compra.
            preco = titulo.get('untrRedVal') 
            if not preco or preco == 0:
                preco = titulo.get('untrInvstmtVal')
            
            if preco: mapa_precos[nome] = float(preco)
        return mapa_precos
    except: return {}

# Função 4: O Grande Orquestrador de Preços
# Essa função decide de onde vem o preço de cada ativo.
@st.cache_data(ttl=300)
def buscar_precos_online(df_posicao):
    if df_posicao.empty: return df_posicao
    
    # 1. Pego os dados do Tesouro
    mapa_tesouro = buscar_dados_tesouro_direto()
    
    # 2. Preparo a lista para o Yahoo Finance (Ações, FIIs, Cripto)
    tickers_map = {}
    for idx, row in df_posicao.iterrows():
        t_yahoo = None
        # Regra para saber se é Brasil (.SA) ou EUA
        if row['Tipo'] in ["Ação", "FII", "ETF", "BDR"]:
            ativo = row['Ativo']
            if "." in ativo: t_yahoo = ativo
            elif any(char.isdigit() for char in ativo): t_yahoo = ativo + ".SA" # Tem número? É Brasil.
            else: t_yahoo = ativo # Só letras? É EUA.
                
        elif row['Tipo'] == "Cripto":
            t_yahoo = row['Ativo'] + "-USD" if not "-" in row['Ativo'] else row['Ativo']
            
        if t_yahoo: tickers_map[t_yahoo] = row['Ativo']

    # 3. Baixo tudo do Yahoo de uma vez
    cotacoes_yahoo = {}
    if tickers_map:
        lista_download = list(tickers_map.keys())
        try:
            dados = yf.download(lista_download, period="1d", progress=False)['Close']
            # Tratamento de erro se vier só 1 ativo ou vários
            if len(lista_download) == 1:
                cotacoes_yahoo[tickers_map[lista_download[0]]] = float(dados.iloc[-1])
            else:
                for t_y in lista_download:
                    try: cotacoes_yahoo[tickers_map[t_y]] = float(dados[t_y].iloc[-1])
                    except: pass
        except: pass

    # 4. Aplico o preço correto linha por linha
    def get_price(row):
        ativo_nome = row['Ativo']
        tipo = row['Tipo']
        
        # Estratégia A: É Tesouro Direto?
        if tipo == "Tesouro Direto":
            # Tenta achar o nome exato ou parecido na lista oficial
            if ativo_nome in mapa_tesouro: return mapa_tesouro[ativo_nome]
            for nome_oficial, preco in mapa_tesouro.items():
                if ativo_nome in nome_oficial: return preco
            
        # Estratégia B: É Ação/FII/Cripto? (Veio do Yahoo)
        if ativo_nome in cotacoes_yahoo: return cotacoes_yahoo[ativo_nome]
        
        # Estratégia C: É Renda Fixa sem cotação? (Juros Compostos)
        # Se o usuário informou uma TAXA, eu calculo quanto rendeu matematicamente.
        if row['Taxa'] > 0:
            hoje = datetime.now()
            anos_passados = (hoje - row['Data_Inicial']).days / 365.25
            if anos_passados <= 0: return row['PM'] # Acabou de comprar
            
            # Fórmula: Valor Futuro = Valor Presente * (1 + taxa)^tempo
            taxa_decimal = row['Taxa'] / 100
            preco_calculado = row['PM'] * ((1 + taxa_decimal) ** anos_passados)
            return preco_calculado
        
        # Se nada der certo, assume que o preço não mudou (Preço Médio)
        return row['PM']

    # Aplica a lógica e calcula os lucros
    df_posicao['Preco_Atual'] = df_posicao.apply(get_price, axis=1)
    df_posicao['Saldo_Atual'] = df_posicao['Qtd_Atual'] * df_posicao['Preco_Atual']
    df_posicao['Lucro_R$'] = df_posicao['Saldo_Atual'] - df_posicao['Total_Investido']
    df_posicao['Var_%'] = ((df_posicao['Preco_Atual'] / df_posicao['PM']) - 1) * 100
    
    # Função para dar o veredito (Emoji)
    def recomendar(var):
        if var > 20: return "🚀 Lucro Forte"
        if var > 5: return "🟢 No Azul"
        if var >= -0.01: return "⚪ Estável"
        if var > -15: return "🟡 Queda Leve"
        return "🔴 Desconto"
        
    df_posicao['Status'] = df_posicao['Var_%'].apply(recomendar)
    return df_posicao

# ==============================================================================
# 3. INTERFACE LATERAL (BARRA DE CONTROLE)
# ==============================================================================
st.sidebar.header("📝 Lançar Ordem")
tipo_op = st.sidebar.selectbox("Categoria", ["Ação", "FII", "Cripto", "Tesouro Direto", "Renda Fixa", "ETF", "BDR"])

with st.sidebar.form("form_operacao"):
    data_op = st.date_input("Data", datetime.today())
    operacao_op = st.radio("Ação", ["Compra", "Venda"], horizontal=True)
    
    # Configuração dinâmica dos campos (Placeholder e Taxa)
    lbl_cod, txt_ex = "Código", "Ex: WEGE3"
    exibir_taxa = False 

    if tipo_op == "FII": lbl_cod, txt_ex = "Código", "Ex: MXRF11"
    elif tipo_op == "ETF": lbl_cod, txt_ex = "Código", "Ex: BOVA11"
    elif tipo_op == "BDR": lbl_cod, txt_ex = "Código", "Ex: AAPL34"
    elif tipo_op == "Cripto": lbl_cod, txt_ex = "Símbolo", "Ex: BTC"
    elif tipo_op == "Tesouro Direto": 
        lbl_cod, txt_ex = "Nome (Use a lupa abaixo)", "Ex: Tesouro IPCA+ 2045"
        exibir_taxa = True
    elif tipo_op == "Renda Fixa": 
        lbl_cod, txt_ex = "Nome do Produto", "Ex: CDB Banco Inter"
        exibir_taxa = True

    # --- CAMPOS DE ENTRADA ---
    # Se for Ação/FII, usa quantidade inteira. Se for Cripto, usa decimal.
    if tipo_op in ["Ação", "FII", "ETF", "BDR"]:
        ativo_op = st.text_input(f"{lbl_cod} ({txt_ex})", max_chars=10).upper()
        c1, c2 = st.columns(2)
        qtd_op = c1.number_input("Qtd", min_value=1, step=1, value=100)
        preco_op = c2.number_input("Preço (R$)", min_value=0.01, format="%.2f", value=10.00)
        taxa_op = 0.0
    
    elif tipo_op == "Cripto":
        ativo_op = st.text_input(f"{lbl_cod} ({txt_ex})").upper()
        c1, c2 = st.columns(2)
        qtd_op = c1.number_input("Qtd", min_value=0.00000001, step=0.001, format="%.8f")
        preco_op = c2.number_input("Preço (R$)", min_value=0.01, format="%.2f", value=100.00)
        taxa_op = 0.0

    elif tipo_op in ["Tesouro Direto", "Renda Fixa"]:
        ativo_op = st.text_input(f"{lbl_cod} ({txt_ex})").upper()
        c1, c2 = st.columns(2)
        qtd_op = c1.number_input("Qtd", min_value=0.01, step=0.1, format="%.2f", value=1.0)
        preco_op = c2.number_input("Aporte (PU)", min_value=0.01, format="%.2f", value=1000.00)
        
        if exibir_taxa:
            taxa_op = st.number_input("Rentabilidade Contratada (% a.a.)", value=10.0, step=0.1, format="%.2f")
        else: taxa_op = 0.0
    
    else:
        # Fallback genérico
        ativo_op = st.text_input(f"{lbl_cod}").upper()
        qtd_op = st.number_input("Qtd", min_value=1, value=1)
        preco_op = st.number_input("Valor", min_value=0.01, value=100.00)
        taxa_op = 0.0

    if st.form_submit_button("💾 Executar Ordem"):
        if ativo_op: salvar_operacao(data_op, ativo_op, tipo_op, operacao_op, qtd_op, preco_op, taxa_op)
        else: st.warning("Preencha o ativo!")

# --- AJUDA INTELIGENTE (COLA PARA O USUÁRIO) ---
if tipo_op == "Renda Fixa":
    st.markdown("---")
    st.caption("🎓 **Mini-Glossário de Renda Fixa**")
    st.info("""
    * **CDB:** Empréstimo p/ Banco. Tem FGC.
    * **LCI/LCA:** Isento de IR. Setor Imob/Agro.
    * **CDI:** Taxa base (segue a Selic).
    * **Pré:** Taxa fixa (ex: 12%).
    * **Pós:** Segue o CDI ou IPCA.
    
    ⚠️ *Consulte seu banco para investir.*
    """)

elif tipo_op == "Tesouro Direto":
    with st.sidebar.expander("🔍 Ver Nomes Oficiais (Tesouro)"):
        st.caption("Se a lista não carregar, use os nomes do site do Tesouro.")
        try:
            mapa_oficial = buscar_dados_tesouro_direto()
            if mapa_oficial:
                for nome in mapa_oficial.keys():
                    st.code(nome, language=None)
            else:
                st.warning("API Off. Tente: TESOURO SELIC 2029")
        except: st.error("Erro na API.")

elif tipo_op == "ETF":
    with st.sidebar.expander("🔍 ETFs Populares"):
        st.write("**Bolsa Brasileira (B3):**")
        st.code("IVVB11", language=None) # S&P 500
        st.code("BOVA11", language=None) # Ibovespa
        st.code("SMAL11", language=None) # Small Caps
        st.code("HASH11", language=None) # Cripto

elif tipo_op == "BDR":
    with st.sidebar.expander("🔍 BDRs Populares (EUA na B3)"):
        st.write("**Tech Giants:**")
        st.code("AAPL34", language=None) # Apple
        st.code("MSFT34", language=None) # Microsoft
        st.code("NVDA34", language=None) # Nvidia
        st.code("TSLA34", language=None) # Tesla

# ==============================================================================
# 4. PAINEL PRINCIPAL (DASHBOARD)
# ==============================================================================
st.title("💰 Gestão de Patrimônio")

df_historico = carregar_dados()

if not df_historico.empty:
    df_base = calcular_posicao_atual(df_historico)
    
    with st.spinner("Atualizando preços de mercado..."):
        df_final = buscar_precos_online(df_base)
    
    if not df_final.empty:
        # Cálculos de KPI (Key Performance Indicators)
        patrimonio_bruto = df_final['Total_Investido'].sum()
        saldo_atual_total = df_final['Saldo_Atual'].sum()
        lucro_total = df_final['Lucro_R$'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Valor Investido", f"R$ {patrimonio_bruto:,.2f}")
        c2.metric("📈 Saldo Atual", f"R$ {saldo_atual_total:,.2f}", delta=f"{lucro_total:,.2f}")
        c3.metric("📦 Ativos", len(df_final))

        st.markdown("---")

        col_grafico, col_resumo = st.columns([1.5, 1])
        
        # Cores para deixar o gráfico bonito e organizado
        mapa_cores = {
            "Ação":"#00D4FF", 
            "FII":"#9b59b6", 
            "Cripto":"#F7931A", 
            "Tesouro Direto":"#2ecc71", 
            "Renda Fixa":"#D4AC0D", # Amarelo Escuro/Ouro
            "ETF":"#95a5a6", 
            "BDR":"#0077b6"
        }
        
        with col_grafico:
            st.subheader("🎨 Alocação")
            # Gráfico de Explosão Solar (Sunburst)
            # Mostra o Tipo no centro e os Ativos na borda
            fig = px.sunburst(
                df_final, path=['Tipo', 'Ativo'], values='Saldo_Atual', color='Tipo',
                color_discrete_map=mapa_cores, hover_data={'Saldo_Atual': ':,.2f'}
            )
            # Forço a fonte a ser branca para leitura melhor no fundo escuro
            fig.update_traces(textinfo="label+percent entry", textfont=dict(color='white'))
            fig.update_layout(height=400, margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        with col_resumo:
            st.subheader("📋 Posição Detalhada")
            # Tabela resumida com barras de progresso
            st.dataframe(
                df_final[['Tipo', 'Ativo', 'Saldo_Atual']].sort_values(by="Saldo_Atual", ascending=False),
                column_config={
                    "Saldo_Atual": st.column_config.ProgressColumn("Valor (R$)", format="R$ %.2f", min_value=0, max_value=saldo_atual_total),
                },
                hide_index=True,
                use_container_width=True,
                height=400
            )

        st.markdown("---")
        # A Super Tabela com todos os detalhes (Lucro, PM, Taxas)
        st.subheader("🚀 Monitor de Rentabilidade")
        
        colunas_ordem = ["Status", "Tipo", "Ativo", "Taxa", "Qtd_Atual", "PM", "Preco_Atual", "Var_%", "Lucro_R$"]
        
        st.dataframe(
            df_final.sort_values(by="Var_%", ascending=False),
            column_order=colunas_ordem,
            column_config={
                "Status": st.column_config.TextColumn("Status"),
                "Taxa": st.column_config.NumberColumn("Taxa", format="%.2f %%"),
                "PM": st.column_config.NumberColumn("PM", format="R$ %.2f"),
                "Preco_Atual": st.column_config.NumberColumn("Valor Hoje", format="R$ %.2f"),
                "Var_%": st.column_config.NumberColumn("Var %", format="%.2f %%"),
                "Lucro_R$": st.column_config.NumberColumn("Lucro", format="R$ %.2f"),
                "Qtd_Atual": st.column_config.NumberColumn("Qtd", format="%.4f"),
            },
            hide_index=True,
            use_container_width=True
        )

    else: st.warning("Saldo zerado.")

    with st.expander("Ver Extrato de Lançamentos"):
        st.dataframe(df_historico.sort_values("Data", ascending=False), use_container_width=True)
        if st.button("🗑️ Resetar Tudo"):
            os.remove(ARQUIVO_DB)
            st.rerun()
else: st.info("👋 Lance sua primeira operação na barra lateral!")