"""
================================================================================
🎓 FINANK - MÓDULO EDUCACIONAL (ESCOLA DE INVESTIDORES)
================================================================================
Olá! Bem-vindo à sala de aula.
Este módulo foi criado para que o usuário não apenas "aperte botões", mas entenda
o que está comprando. A educação é a melhor defesa contra prejuízos.

ESTRUTURA DA PÁGINA:
1. Navegação por Abas: Cada classe de ativo (Ações, FIIs, Cripto...) tem sua aba.
2. Explicações Simples: Nada de "economês". Usamos analogias do dia a dia.
3. Classificações: Ensinamos a diferença entre ON vs PN, Tijolo vs Papel, etc.
"""

import streamlit as st

# ==============================================================================
# 1. CONFIGURAÇÃO VISUAL
# ==============================================================================
st.set_page_config(page_title="Central de Aprendizado", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    /* Estilo para os Títulos das Aulas */
    .aula-titulo { color: #00D4FF; font-size: 1.8em; font-weight: bold; margin-bottom: 10px; }
    .aula-subtitulo { color: #b0b0b0; font-size: 1.1em; margin-bottom: 20px; }
    
    /* Caixas de Destaque (Conceitos Chave) */
    .conceito-box {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #F7931A; /* Laranja Bitcoin */
        margin-bottom: 15px;
    }
    
    /* Caixas de Alerta (Riscos) */
    .alerta-box {
        background-color: #3b1b1b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ff2b2b;
        color: #ffcccc;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CONTEÚDO EDUCACIONAL
# ==============================================================================

st.title("🎓 Central de Aprendizado Finank")
st.markdown("O mercado financeiro traduzido para o português claro. Escolha um tema abaixo:")
st.markdown("---")

# Navegação por temas
tab_acoes, tab_fiis, tab_rf, tab_tesouro, tab_cripto, tab_bdr, tab_etf = st.tabs([
    "🏢 Ações", 
    "🏗️ FIIs", 
    "💰 Renda Fixa", 
    "🏛️ Tesouro", 
    "₿ Cripto", 
    "🌎 BDRs", 
    "🧺 ETFs"
])

# --- MÓDULO 1: AÇÕES ---
with tab_acoes:
    st.markdown('<div class="aula-titulo">O que são Ações?</div>', unsafe_allow_html=True)
    st.markdown("""
    Imagine que uma empresa (como a Petrobras ou o Banco do Brasil) é uma pizza gigante. 
    Quando você compra uma **Ação**, você está comprando um **pequeno pedaço (fatia)** dessa empresa.
    
    Ao ter essa fatia, você se torna **Sócio**. Se a empresa lucra, você ganha parte desse lucro (Dividendos). 
    Se ela cresce, sua fatia vale mais.
    """)
    
    st.markdown("### 🧩 Os Tipos de Ações (A Sopa de Letrinhas)")
    
    with st.expander("🔵 Ações Ordinárias (ON) - Final 3", expanded=True):
        st.write("""
        * **Código:** Ex: `PETR3`, `VALE3`.
        * **O que é:** Dá direito a **VOTO** nas assembleias. É a ação dos donos de verdade.
        * **Vantagem:** Se a empresa for vendida, você tem direito a receber 100% do valor pago por ação aos controladores (Tag Along).
        """)
        
    with st.expander("🟡 Ações Preferenciais (PN) - Final 4"):
        st.write("""
        * **Código:** Ex: `PETR4`, `ITUB4`.
        * **O que é:** Você **NÃO vota**, mas tem **PREFERÊNCIA** para receber os lucros (dividendos).
        * **Vantagem:** Geralmente tem mais liquidez (são mais fáceis de comprar e vender) e pagam um pouco mais de dividendos.
        """)

    with st.expander("📦 Units - Final 11"):
        st.write("""
        * **Código:** Ex: `TAEE11`, `SANB11`.
        * **O que é:** É um "pacotinho" (Combo). Geralmente contém 1 ação ON + 2 ou mais ações PN misturadas.
        """)

# --- MÓDULO 2: FIIs ---
with tab_fiis:
    st.markdown('<div class="aula-titulo">Fundos Imobiliários (FIIs)</div>', unsafe_allow_html=True)
    st.markdown("""
    É como comprar um Shopping Center ou um Prédio de Escritórios junto com milhares de outras pessoas.
    Você compra uma **Cota** e todo mês cai o "aluguel" (rendimento) na sua conta, isento de Imposto de Renda.
    """)
    
    st.markdown("### 🏘️ Os 3 Tipos Principais")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**🧱 FII de Tijolo**")
        st.write("Dono de imóveis reais: Shoppings, Galpões Logísticos, Hospitais, Prédios. Ganha com o aluguel físico.")
        st.caption("Ex: HGLG11, VISC11")
        
    with col2:
        st.info("**📄 FII de Papel**")
        st.write("Não tem imóveis. Ele empresta dinheiro para construtoras (CRIs). Ganha com os Juros da dívida.")
        st.caption("Ex: KNCR11, MXRF11")
        
    with col3:
        st.info("**🚜 Fiagro**")
        st.write("Primo do FII, mas focado no Agronegócio. Investe em fazendas ou dívidas de produtores rurais.")
        st.caption("Ex: SNAG11, KNCA11")

# --- MÓDULO 3: RENDA FIXA PRIVADA ---
with tab_rf:
    st.markdown('<div class="aula-titulo">Renda Fixa Privada</div>', unsafe_allow_html=True)
    st.markdown("""
    Aqui você não é sócio. Você é **Banqueiro**.
    Ao investir em Renda Fixa, você está **emprestando dinheiro** para um Banco ou Empresa em troca de juros no futuro.
    """)
    
    st.markdown('<div class="conceito-box">💡 <b>Dica de Ouro:</b> O FGC (Fundo Garantidor de Créditos) devolve seu dinheiro (até R$ 250 mil) se o banco quebrar. Válido para CDB, LCI e LCA.</div>', unsafe_allow_html=True)
    
    with st.expander("🏦 CDB (Certificado de Depósito Bancário)"):
        st.write("Você empresta para o Banco. O banco usa seu dinheiro para emprestar para outras pessoas. Tem Imposto de Renda.")
        
    with st.expander("🏠 LCI e LCA (Letras de Crédito)"):
        st.write("""
        * **LCI:** Dinheiro usado para financiar imóveis.
        * **LCA:** Dinheiro usado para financiar o Agro.
        * **Grande Vantagem:** **ISENTO de Imposto de Renda** para pessoa física.
        """)
        
    with st.expander("🏭 Debêntures"):
        st.write("Você empresta dinheiro para uma EMPRESA (não banco) construir uma fábrica ou estrada. Risco maior, mas paga mais. Não tem garantia do FGC.")

# --- MÓDULO 4: TESOURO DIRETO ---
with tab_tesouro:
    st.markdown('<div class="aula-titulo">Tesouro Direto</div>', unsafe_allow_html=True)
    st.markdown("O investimento mais seguro do país. Aqui você empresta dinheiro para o **Governo Federal**.")
    
    st.table({
        "Título": ["Tesouro Selic", "Tesouro IPCA+", "Tesouro Prefixado", "RendA+ / Educa+"],
        "Como funciona?": [
            "Acompanha a taxa básica de juros (Selic). Sempre cresce.",
            "Garante ganho acima da inflação. Protege seu poder de compra.",
            "Taxa fixa combinada hoje (ex: 12%). Você sabe exatamente quanto vai receber.",
            "Focados em aposentadoria ou faculdade. Pagam renda mensal no futuro."
        ],
        "Ideal para": [
            "Reserva de Emergência (Curto Prazo)",
            "Aposentadoria / Longo Prazo",
            "Metas de Médio Prazo (ex: Comprar carro em 3 anos)",
            "Previdência Complementar"
        ]
    })

# --- MÓDULO 5: CRIPTO ---
with tab_cripto:
    st.markdown('<div class="aula-titulo">Criptomoedas</div>', unsafe_allow_html=True)
    st.markdown("Dinheiro digital descentralizado. Não depende de bancos ou governos.")
    
    st.markdown("### 🪙 O Vocabulário Cripto")
    st.markdown("""
    * **Bitcoin (BTC):** O ouro digital. Escasso, seguro e a primeira cripto criada.
    * **Altcoins:** Qualquer moeda que não seja o Bitcoin (Ethereum, Solana, etc). Geralmente mais arriscadas e voláteis.
    * **Stablecoins:** Moedas digitais pareadas com dinheiro real (Ex: USDT vale sempre 1 Dólar). Usadas para proteção.
    """)
    
    st.markdown('<div class="alerta-box">⚠️ <b>Cuidado:</b> Criptos podem subir 100% ou cair 90% em dias. Só invista o dinheiro da "pinga", nunca o do "leite".</div>', unsafe_allow_html=True)

# --- MÓDULO 6: BDRs ---
with tab_bdr:
    st.markdown('<div class="aula-titulo">BDRs (Brazilian Depositary Receipts)</div>', unsafe_allow_html=True)
    st.markdown("""
    Quer investir na **Apple, Disney ou Coca-Cola** sem abrir conta no exterior? Use BDRs.
    
    BDRs são "recibos" negociados na bolsa do Brasil (em Reais) que representam ações de empresas gringas.
    """)
    st.info("Exemplo: Ao comprar `AAPL34`, você compra um recibo que vale uma fração da ação da Apple nos EUA. Se o dólar sobe, seu BDR valoriza também.")

# --- MÓDULO 7: ETFs ---
with tab_etf:
    st.markdown('<div class="aula-titulo">ETFs (Exchange Traded Funds)</div>', unsafe_allow_html=True)
    st.markdown("""
    Imagine uma **Cesta de Compras** pronta. Em vez de escolher fruta por fruta (Ação por Ação), você compra a cesta inteira de uma vez.
    Isso é um ETF: um fundo que copia um índice.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 🇧🇷 BOVA11")
        st.write("Cesta com as maiores empresas do Brasil (Vale, Petrobras, Itaú...). Segue o Ibovespa.")
        
    with col2:
        st.write("### 🇺🇸 IVVB11")
        st.write("Cesta com as 500 maiores empresas dos EUA (S&P 500). Você investe no Google, Facebook e Amazon de uma só vez.")