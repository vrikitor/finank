# 💰 Finank: Central Financeira Pessoal (100% Python)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-green)

> *"O mercado financeiro não precisa ser um monstro de 7 cabeças."*

## Visão Geral do Projeto

O **Finank** é uma plataforma intuitiva desenvolvida para democratizar o gerenciamento de patrimônio. A ideia nasceu de dois desejos principais:
1.  **Desmistificar os Investimentos:** Criar um ambiente onde iniciantes e investidores independentes possam gerenciar seus ativos sem medo de siglas complicadas.
2.  **Desafio Python Puro:** Provar que é possível construir uma aplicação financeira robusta, completa e visualmente rica utilizando **100% Python**, explorando os limites da linguagem para entregar soluções reais.

### Screenshots

![Dashboard Overview](<img width="1918" height="877" alt="Home_finank" src="https://github.com/user-attachments/assets/edd49518-68dd-4ad8-9f05-95603ecb04a5" />)



![Análise de Carteira](<img width="1919" height="1079" alt="Carteira" src="https://github.com/user-attachments/assets/2fc252f7-5c5f-4196-bbc8-71c9ec85a753" />)


---

## Killer Features

O sistema vai além de uma simples planilha digital. Ele possui inteligência de mercado embutida:

### 1. Motor Híbrido de Cotação
O grande diferencial técnico do backend. O sistema não depende de uma única fonte:
* **Renda Variável (Ações/Stocks/Cripto):** Conexão em tempo real via **Yahoo Finance**.
* **Renda Fixa (Tesouro Direto):** Conexão via **API JSON Oficial do Tesouro Nacional** para buscar preços de resgate atualizados.
* **Fallback Matemático:** Se a API falhar, o sistema assume automaticamente um cálculo de **Juros Compostos (Pro Rata)** baseado na taxa contratada. Nada fica sem valor.

### 2. arteira Inteligente & Visual
* **Sunburst Chart (Explosão Solar):** Visualização hierárquica interativa (Categoria -> Ativo).
* **Lógica de Mercado:** O sistema entende a diferença técnica entre comprar uma Ação (preço de mercado/volatilidade) e um CDB (curva de juros contratada).
* **Suporte Global:** Aceita ativos da B3 (Brasil), Stocks/REITs (EUA) e Criptomoedas.

### 3. Area de Comparação
Uma ferramenta para colocar ativos "batalhando" lado a lado. Compara rentabilidade histórica, volatilidade e retorno acumulado em gráficos de linha interativos.

### 4. Educação Integrada
O sistema não apenas mostra números, ele ensina:
* **Glossários Contextuais:** Explicações automáticas sobre termos como CDI, CDB, LCI ao navegar.
* **Sugestões de Tickers:** Listas integradas de ETFs e BDRs populares para auxiliar quem não sabe os códigos de cabeça.

---

## Stack Tecnológica

Este projeto utiliza uma arquitetura moderna de Data Science aplicada à Web.

* **Linguagem:** `Python 3.10+` (Base de todo o projeto).
* **Interface (Frontend):** `Streamlit` (Gerenciamento de estado, cacheamento e UI).
* **Manipulação de Dados:**
    * `Pandas`: O "cérebro" do sistema (DataFrames, GroupBy, tratamento de datas).
    * `NumPy`: Operações vetoriais e cálculos financeiros de juros compostos.
* **Visualização:** `Plotly Express` & `Graph Objects` (Gráficos interativos de alta performance: Sunburst, Candlestick, Line e Area Charts).
* **Conectividade (APIs):**
    * `yfinance`: Wrapper para dados de bolsas mundiais.
    * `Requests`: Consumo da API REST do Tesouro Direto.
    * `BeautifulSoup4`: Web Scraping de notícias e sentimento.
* **Persistência:** `CSV` (Flat File Database) gerenciado via módulo `OS`.

---

## Instalação e Uso

Siga os passos abaixo para rodar o Finank na sua máquina:

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/vrikitor/finank.git](https://github.com/vrikitor/finank.git)
    cd finank
    ```

2.  **Crie um Ambiente Virtual (Recomendado):**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install streamlit pandas plotly yfinance requests beautifulsoup4 deep-translator
    ```

4.  **Execute a Aplicação:**
    ```bash
    streamlit run Home.py
    ```

---

## Sobre a Privacidade dos Dados (`carteira.csv`)

Ao iniciar o sistema pela primeira vez, um arquivo chamado `carteira.csv` será criado automaticamente na pasta do projeto.

* **O que é:** É o seu banco de dados pessoal. Todas as suas transações ficam salvas aqui.
* **Privacidade:** Seus dados ficam 100% locais no seu computador. Nada é enviado para a nuvem.
* **Portabilidade:** Como é um CSV padrão, você pode abrir no Excel ou Google Sheets para análises externas.
* ⚠️ **Atenção:** Se você apagar este arquivo, perderá seu histórico. Faça backups regulares!

---

## Autor

Desenvolvido por **Victor Godoi Souza**
* [LinkedIn](https://www.linkedin.com/in/vicotr/)
* [GitHub](http://github.com/vrikitor)

---
