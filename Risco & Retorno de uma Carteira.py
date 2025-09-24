# Risco & Retorno de uma Carteira (últimos 4 anos - análise mensal);
# Simular carteira com 100k, 3 ações (BBAS3.SA (Banco do Brasil), PETR4.SA (Petrobras) e VALE3.SA (Vale));
# Calcular risco, retorno e CAPM dos ativos (betas, retorno esperado pelo modelo em relação ao IBOV e taxa livre de risco);

# Requisitos: pip install yfinance matplotlib;
# Autora: Gabriela Isabel Cirene da Silva.
import pandas as pd
import math
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt
from collections import defaultdict

# -------- CONFIGURAÇÃO --------
TICKERS = ['BBAS3.SA', 'PETR4.SA', 'VALE3.SA'] 
ORCAMENTO_TOTAL = 100_000.00
MESES_ANO = 12
ANOS = 4  
HOJE = datetime.today().date()
START = datetime(HOJE.year - ANOS, HOJE.month, HOJE.day).date().isoformat()
END = HOJE.isoformat()

print(f"Baixando dados de {TICKERS} entre {START} e {END}...")

# -------- BAIXA DADOS (ajustados aautomaticamente no yfinance) --------
data = yf.download(TICKERS, start=START, end=END, progress=False, auto_adjust=True)['Close']

# Se só um ticker, yfinance retorna Series; adaptar para sempre dataframe-like
if isinstance(data, float) or isinstance(data, int):
    raise SystemExit("Erro no download dos dados.")
if isinstance(data, type(data.index.__class__)): 
    pass

# Convertemos os dados para dict: ticker -> list of (date, price) ordered by date
prices_by_ticker = {}
for t in TICKERS:
    if t not in data.columns:
        raise SystemExit(f"Ticker {t} não encontrado nos dados baixados.")
    series = []
    for dt, row in data[[t]].iterrows():
        price = row[t]
        if not math.isnan(price):
            series.append((dt.date(), float(price)))
    prices_by_ticker[t] = series

# -------- AGREGAR MENSAL (último preço de cada mês) - feito manualmente --------
def ultimo_preco_por_mes(series):
    by_ym = {}
    for dt, p in series:
        ym = (dt.year, dt.month)
        by_ym[ym] = (dt, p)
    ordered = sorted(by_ym.items(), key=lambda x: (x[0][0], x[0][1]))
    return [(ym, by_ym[ym][1]) for ym, _ in ordered]

precos_mensal = {}
for t, s in prices_by_ticker.items():
    precos_mensal[t] = ultimo_preco_por_mes(s) 

def meses_disponiveis(precos_mensal):
    sets = []
    for t, lst in precos_mensal.items():
        meses = [ym for ym, _ in lst]
        sets.append(set(meses))
    inters = set.intersection(*sets)
    return sorted(list(inters))

meses_comuns = meses_disponiveis(precos_mensal)
if len(meses_comuns) < 12:
    print("Atenção: poucos meses em comum entre os ativos. Verifique dados.")
precos_mensais_alinhados = {}
for t, lst in precos_mensal.items():
    mapa = {ym: price for ym, price in lst}
    precos_mensais_alinhados[t] = [mapa[ym] for ym in meses_comuns]

# -------- RETORNOS SIMPLES MENSAIS (manualmente) --------
retornos_mensais = {}
for t, prices in precos_mensais_alinhados.items():
    rets = []
    for i in range(1, len(prices)):
        p_prev = prices[i-1]
        p_now = prices[i]
        if p_prev == 0:
            r = 0.0
        else:
            r = (p_now / p_prev) - 1.0
        rets.append(r)
    retornos_mensais[t] = rets

# -------- FUNÇÕES ESTATÍSTICAS MANUAIS (média aritmética, desvio amostral, cov, corr) --------
def media(lista):
    return sum(lista) / len(lista) if len(lista) > 0 else 0.0

def desvio_padrao_amostral(lista):
    n = len(lista)
    if n <= 1:
        return 0.0
    mu = media(lista)
    var = sum((x - mu) ** 2 for x in lista) / (n - 1)
    return math.sqrt(var)

def covariancia_amostral(x, y):
    n = len(x)
    if n <= 1:
        return 0.0
    mu_x = media(x)
    mu_y = media(y)
    return sum((xi - mu_x) * (yi - mu_y) for xi, yi in zip(x, y)) / (n - 1)

def correlacao(x, y):
    denom = desvio_padrao_amostral(x) * desvio_padrao_amostral(y)
    if denom == 0:
        return 0.0
    return covariancia_amostral(x, y) / denom

# -------- RETORNO DO PERÍODO (fórmula "preço final/preço inicial - 1") --------
retorno_periodo = {}
for t in TICKERS:
    prices = precos_mensais_alinhados[t]
    if len(prices) < 2:
        retorno_periodo[t] = 0.0
    else:
        p_i = prices[0]
        p_f = prices[-1]
        retorno_periodo[t] = (p_f / p_i - 1.0) * 100  # em %

# -------- ESTATÍSTICAS DOS ATIVOS (médias e desvios anualizados a partir de mensal) --------
estatisticas = {}
for t in TICKERS:
    lista = retornos_mensais[t]
    mu_m = media(lista)
    mu_a = mu_m * MESES_ANO
    sigma_m = desvio_padrao_amostral(lista)
    sigma_a = sigma_m * math.sqrt(MESES_ANO)
    estatisticas[t] = {
        'RetornoMedio_m': mu_m,
        'RetornoMedio_a': mu_a,
        'DesvioPadrao_m': sigma_m,
        'DesvioPadrao_a': sigma_a
    }

# -------- MATRIZ DE COVARIÂNCIA E CORRELAÇÃO (anualizada) --------
cov_matrix = {t: {u: 0.0 for u in TICKERS} for t in TICKERS}
corr_matrix = {t: {u: 0.0 for u in TICKERS} for t in TICKERS}

for i in range(len(TICKERS)):
    for j in range(len(TICKERS)):
        a = TICKERS[i]
        b = TICKERS[j]
        x = retornos_mensais[a]
        y = retornos_mensais[b]
        cov_ij_m = covariancia_amostral(x, y)  # mensal
        cov_ij_a = cov_ij_m * MESES_ANO        # anualizar covariância
        cov_matrix[a][b] = cov_ij_a
        corr_matrix[a][b] = correlacao(x, y)

# -------- CARTEIRA (pesos iguais por padrão) --------
N = len(TICKERS)
pesos = [1.0 / N] * N

# retorno esperado da carteira (anual)
mu_port = sum(pesos[i] * estatisticas[TICKERS[i]]['RetornoMedio_a'] for i in range(N))

# variância da carteira 
var_port = 0.0
for i in range(N):
    for j in range(N):
        var_port += pesos[i] * pesos[j] * cov_matrix[TICKERS[i]][TICKERS[j]]
sigma_port = math.sqrt(var_port)

# retorno da carteira no período (ponderado pelos pesos) - usando retorno_periodo (%) dos ativos
retorno_carteira_periodo = sum(pesos[i] * retorno_periodo[TICKERS[i]] for i in range(N))

# -------- ALOCAÇÃO REAL (comprar número inteiro de lotes/ações) --------
ultimos_precos = {t: precos_mensais_alinhados[t][-1] for t in TICKERS}
qtd_shares = {}
investido_por_ativo = {}
for i, t in enumerate(TICKERS):
    orcamento_por_ativo = ORCAMENTO_TOTAL * pesos[i]
    preco = ultimos_precos[t]
    qtd = int(orcamento_por_ativo // preco)  # número inteiro de ações
    qtd_shares[t] = qtd
    investido_por_ativo[t] = qtd * preco

investido_total = sum(investido_por_ativo.values())
caixa_restante = ORCAMENTO_TOTAL - investido_total

# -------- RESULTADOS --------
print("\n=== ÚLTIMOS PREÇOS (mensal, último disponível) ===")
for t in TICKERS:
    print(f"{t}: R$ {ultimos_precos[t]:.2f}")

print("\n=== Retorno no período (4 anos) por ativo (%) ===")
for t, r in retorno_periodo.items():
    print(f"{t}: {r:.2f}%")

print("\n=== Estatísticas anuais (a partir de retornos mensais) ===")
for t in TICKERS:
    stats = estatisticas[t]
    print(f"{t}: Ret. médio anual={stats['RetornoMedio_a']*100:.2f}%, Desvio anual={stats['DesvioPadrao_a']*100:.2f}%")

print("\n=== Matriz de Correlação (mensal) ===")
for a in TICKERS:
    linha = " | ".join(f"{corr_matrix[a][b]:.3f}" for b in TICKERS)
    print(f"{a}: {linha}")

print("\n=== Resumo da Carteira ===")
print(f"Pesos: {dict(zip(TICKERS, pesos))}")
print(f"Retorno esperado da carteira (anual): {mu_port*100:.2f}%")
print(f"Volatilidade anual da carteira: {sigma_port*100:.2f}%")
print(f"Retorno da carteira no período (4 anos): {retorno_carteira_periodo:.2f}%")
print(f"Orçamento total: R$ {ORCAMENTO_TOTAL:,.2f}")
print("Investido por ativo (R$) e quantidade de ações:")
for t in TICKERS:
    print(f" {t}: Qtd={qtd_shares[t]}, Investido=R$ {investido_por_ativo[t]:,.2f}")
print(f"Caixa restante (não investido): R$ {caixa_restante:,.2f}")
# -------- CAPM --------
print("\n=== CAPM ===")

# Baixa IBOV para o mesmo período
ibov = yf.download("^BVSP", start=START, end=END, auto_adjust=True, progress=False)['Close']

# Garante que seja Series
if isinstance(ibov, pd.DataFrame):
    ibov = ibov.iloc[:,0]

ibov_mensal = ibov.resample("ME").last()
ret_ibov = ibov_mensal.pct_change().dropna().tolist()

# Retorno médio anual do mercado
mu_m_ibov = media(ret_ibov)
mu_a_ibov = mu_m_ibov * MESES_ANO

# Variância do mercado (mensal -> anualizada)
var_ibov_m = desvio_padrao_amostral(ret_ibov)**2
var_ibov_a = var_ibov_m * MESES_ANO

# Taxa livre de risco (Tesouro longo ~5% a.a.)
Rf = 0.05

for t in TICKERS:
    Ri = retornos_mensais[t]
    Rm = ret_ibov[:len(Ri)]
    beta = covariancia_amostral(Ri, Rm) / var_ibov_m
    retorno_capm = Rf + beta * (mu_a_ibov - Rf)
    print(f"{t}: Beta={beta:.3f} | Retorno esperado CAPM={retorno_capm*100:.2f}%")

print(f"\nMercado (IBOV): Retorno médio anual={mu_a_ibov*100:.2f}%, Variância anual={var_ibov_a:.4f}")
print(f"Taxa livre de risco (Rf): {Rf*100:.2f}%")
# -------- GRÁFICOS SIMPLES (preço normalizado e retorno acumulado) --------
plt.figure(figsize=(10,5))
for t in TICKERS:
    prices = precos_mensais_alinhados[t]
    norm = [p / prices[0] for p in prices]
    x = [f"{ym[0]}-{ym[1]:02d}" for ym in meses_comuns]
    plt.plot(x, norm, label=t)
plt.xticks(rotation=45)
plt.title("Preço Normalizado Mensal (t0=1)")
plt.xlabel("Mês")
plt.ylabel("Índice (x vezes)")
plt.legend()
plt.tight_layout()
plt.show()

# Retorno acumulado (produto dos 1+ret)
plt.figure(figsize=(10,5))
for t in TICKERS:
    rets = retornos_mensais[t]
    acum = []
    prod = 1.0
    for r in rets:
        prod = prod * (1 + r)
        acum.append(prod - 1.0)
    x = [f"{ym[0]}-{ym[1]:02d}" for ym in meses_comuns[1:]]  
    plt.plot(x, acum, label=t)
plt.xticks(rotation=45)
plt.title("Retorno Acumulado (mensal)")
plt.xlabel("Mês")
plt.ylabel("Retorno acumulado")
plt.legend()
plt.tight_layout()
plt.show()
