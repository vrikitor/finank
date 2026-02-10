# 💰 Finank: central financeira pessoal (100% Python)

> *"O mercado financeiro não precisa ser um monstro de 7 cabeças."*

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-green)

## A Motivação
Muitas pessoas deixam de investir ou de buscar a liberdade financeira porque o mercado parece complicado, cheio de siglas e taxas. A ideia da **Finank** nasceu de dois desejos:
1.  **Desmistificar os Investimentos:** Criar uma plataforma intuitiva onde qualquer pessoa possa gerenciar seu patrimônio sem medo.
2.  **Me Desafiar com o Python:** Provar para mim mesmo que é possível construir uma aplicação complexas, completas, robustas e visualmente ricas usando **100% Python**, testando os limites da linguagem para entregar soluções reais e aprender mais sobre ela no processo.

## Para Quem é Este Projeto?
O Finank foi desenhado para ser democrático. Ele é ideal para:
* **Iniciantes:** Que se perdem nas sopas de letrinhas (CDB, LCI, BDR).
* **Investidores Independentes:** Que não querem pagar mensalidades caras em apps de consolidação de carteira.
* **Curiosos de Tecnologia:** Que querem entender como Python se conecta ao mercado financeiro real.

---

## As Killer Features 

O sistema vai além de uma simples planilha. Ele possui inteligência embutida:

### 1. Motor Híbrido de Cotação 
O grande diferencial técnico. O sistema não depende de uma única fonte:
* **Renda Variável (Ações/EUA/Cripto):** Conecta-se ao **Yahoo Finance** para dados em tempo real.
* **Renda Fixa (Tesouro Direto):** Conecta-se via **API JSON Oficial do Tesouro Nacional** para buscar preços de resgate atualizados.
* **Matemática Financeira:** Se a API falhar, o sistema assume um cálculo de **Juros Compostos (Pro Rata)** baseado na taxa contratada pelo usuário. Nada fica sem valor.

### 2. Carteira Inteligente & Visual 
* **Gráfico Sunburst (Explosão Solar):** Visualização hierárquica (Categoria -> Ativo) interativa.
* **Cálculo Automático:** O sistema entende a diferença entre comprar uma Ação (preço de mercado) e um CDB (curva de juros).
* **Suporte Global:** Aceita ativos do Brasil (B3), Estados Unidos (Stocks/REITs) e Criptomoedas.

### 3. Comparador de Ativos (Arena) 
Uma ferramenta para colocar ativos "batalhando" lado a lado. Compara rentabilidade histórica, volatilidade e retorno acumulado em gráficos de linha.

### 4. Educação Integrada 
O sistema não apenas mostra números, ele ensina.
* **Glossários Contextuais:** Ao selecionar "Renda Fixa", o sistema explica o que é CDI, CDB, LCI, etc.
* **Sugestões de Tickers:** Listas integradas de ETFs e BDRs populares para quem não sabe os códigos de cabeça.

---

## Stack Tecnológica (A Engenharia por Trás)

Este projeto utiliza uma arquitetura moderna de Data Science aplicada à Web.

### Linguagem & Framework
* **Python 3.10+:** A base de todo o projeto.
* **Streamlit:** Framework para criação da interface web interativa, gerenciamento de estado (Session State) e cacheamento de dados.

### Manipulação de Dados
* **Pandas:** O "cérebro" do sistema. Utilizado para criar DataFrames, manipular o arquivo CSV (banco de dados local), realizar agragação de carteira (`groupby`), tratamento de datas e cálculos financeiros.
* **NumPy:** Utilizado para operações numéricas vetoriais e cálculos de juros compostos.

### Visualização de Dados
* **Plotly Express & Graph Objects:** Biblioteca para gráficos interativos de alta performance.
    * *Sunburst Chart:* Para alocação de carteira.
    * *Candlestick Chart:* Para análise técnica de velas (OHLC).
    * *Line Chart:* Para comparação de rentabilidade histórica.
    * *Area Chart:* Para o simulador de juros compostos.

### APIs & Conexões
* **yfinance:** Wrapper para consumo de dados históricos e cotações da bolsa mundial.
* **Requests:** Utilizado para consumir a API REST não-documentada do Tesouro Direto (`treasurybondsinfo.json`).
* **BeautifulSoup (BS4):** Utilizado para Web Scraping de notícias e sentimento de mercado (Google News).

### Persistência de Dados
* **CSV (Flat File Database):** Banco de dados local, leve e portátil.
* **OS Module:** Gerenciamento de sistema de arquivos para criação automática e leitura segura dos dados.

---

##  Instalação e Uso

Siga os passos abaixo para rodar o Finank na sua máquina:

### 1. Clone o Repositório
```bash
git clone [https://github.com/vrikitor/finank.git](https://github.com/vrikitor/finank.git)
cd finank
2. Crie um Ambiente Virtual (Recomendado)
Isso evita conflitos com outras bibliotecas do seu PC.

Bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
3. Instale as Dependências
Bash
pip install streamlit pandas plotly yfinance requests beautifulsoup4 deep-translator
4. Execute a Aplicação
Bash
streamlit run Home.py
📂 Sobre o Arquivo carteira.csv
Ao iniciar o sistema pela primeira vez, você notará que um arquivo chamado carteira.csv será criado automaticamente na pasta do projeto.

O que é: É o seu banco de dados pessoal. Todas as suas compras e vendas ficam salvas ali.

Privacidade: Seus dados financeiros ficam apenas no seu computador. Nada vai para a nuvem.

Compatibilidade: Como é um CSV padrão, você pode abrir esse mesmo arquivo no Excel, LibreOffice ou Google Sheets se quiser fazer análises externas.

Segurança: Se você apagar esse arquivo, perderá seu histórico de lançamentos. Faça backup!

## Contribuição
Este é um projeto de código aberto focado em aprendizado. Sinta-se à vontade para abrir Issues, sugerir melhorias ou fazer um Fork!







