# 📈 Simulação de Carteira de Investimentos  

Este projeto implementa uma **simulação de carteira de R$100.000,00** distribuída igualmente em ações de três empresas brasileiras listadas na B3:  

- **BBAS3.SA** (Banco do Brasil)  
- **PETR4.SA** (Petrobras)  
- **VALE3.SA** (Vale)  

A análise considera os **últimos 4 anos de dados mensais** (via Yahoo Finance) e aplica fórmulas estatísticas implementadas manualmente, sem uso de bibliotecas para cálculos.  

## 🔎 Funcionalidades
- Importação automática de preços históricos (Yahoo Finance).  
- Agregação mensal dos preços.  
- Cálculo manual de:
  - Retornos simples mensais e no período;  
  - Retorno médio esperado (anualizado);  
  - Volatilidade (desvio padrão anualizado);  
  - Covariância e correlação entre os ativos;  
  - Retorno e risco da carteira (pesos iguais).  
- Simulação da alocação real em ações (quantidade comprada com 100k).  
- Geração de gráficos:
  - Preço normalizado (t0 = 1,0);  
  - Retorno acumulado mensal.  

## 🛠️ Tecnologias
- Python 3  
- [yfinance](https://pypi.org/project/yfinance/) (importação dos dados)  
- matplotlib (visualização)  
- pandas (manipulação de séries temporais)  

## 📂 Estrutura
- `Risco & Retorno de uma Carteira.py`: script principal com todos os cálculos e gráficos.   

## 📊 Resultados (exemplo)
- Retorno total da carteira em 4 anos: **+120,18%**  
- Retorno esperado anual: **20,50%**  
- Volatilidade anual: **17,83%**  

## 📌 Observação
Este projeto foi desenvolvido como atividade acadêmica na disciplina de **Fundamentos de Contabilidade e Gestão Financeira**.  
As fórmulas foram aplicadas conforme material de aula, **sem bibliotecas externas para cálculos estatísticos**.  
