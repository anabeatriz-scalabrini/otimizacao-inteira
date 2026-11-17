#!/usr/bin/env python3
"""
Visualiza as instâncias geradas por gerar_instancias.py.

Para cada instância, gera uma figura com dois painéis:
  1. Mapa: portos de coleta (círculos) e de entrega (quadrados), posição inicial
     de cada navio (triângulo) e as rotas do plano de referência. Trechos com
     carga em linha cheia; trechos vazios (indo buscar a próxima carga) tracejados.
  2. Janelas de tempo: uma barra por carga com a janela [a, b]. Sobre ela, a
     chegada nominal (círculo) e a pior chegada com até Γ atrasos (losango),
     calculadas para o plano de referência pela programação dinâmica do artigo.

Também imprime no terminal um resumo da instância (navios, cargas, atrasos).

Uso:
  # uma instância (salva o PNG ao lado do JSON)
  python visualizar_instancia.py dados/inst_c08_n2_s42.json

  # escolher o Γ da pior chegada e abrir a janela do gráfico
  python visualizar_instancia.py dados/inst_c08_n2_s42.json --gama 2 --mostrar

  # todas as instâncias de uma pasta (PNGs em dados/figuras/)
  python visualizar_instancia.py dados/

Requer: matplotlib (pip install matplotlib).
"""

import argparse
import glob
import json
import math
import os

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# ---------------------------------------------------------------------------
# Paleta (cores por navio em ordem fixa; tons neutros para texto e fundo)
# ---------------------------------------------------------------------------
CORES_NAVIOS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                "#e87ba4", "#008300", "#6250d6", "#e34948"]
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
GRADE = "#e4e2dc"
JANELA = "#d9d6cf"
PORTO = "#8a877f"
FUNDO = "#fcfcfb"

plt.rcParams.update({
    "font.size": 10,
    "axes.edgecolor": GRADE,
    "axes.labelcolor": TEXTO_2,
    "xtick.color": TEXTO_2,
    "ytick.color": TEXTO_2,
    "axes.titlecolor": TEXTO,
    "figure.facecolor": FUNDO,
    "axes.facecolor": FUNDO,
})


def cor_navio(k):
    return CORES_NAVIOS[k % len(CORES_NAVIOS)]


# ---------------------------------------------------------------------------
# Cálculos sobre o plano de referência
# ---------------------------------------------------------------------------

def indexar_arcos(inst):
    return {(a["navio"], str(a["de"]), str(a["para"])): a for a in inst["arcos"]}


def chegadas(inst, gama):
    """Chegada nominal e pior chegada (com até Γ atrasos) para cada carga do plano.

    Pior chegada: a(j, g) = max{ a_j, a(j-1, g) + t_barra, a(j-1, g-1) + t_barra + t_chapeu }
    (programação dinâmica da Proposição 10 de Agra et al., 2013).
    """
    arcos = indexar_arcos(inst)
    cargas = {c["id"]: c for c in inst["cargas"]}
    res = {}
    for rota in inst["plano_referencia"]:
        k, seq = rota["navio"], rota["sequencia"]
        if not seq:
            continue
        nominal = 0.0
        pior = [0.0] * (gama + 1)
        anterior = "o"
        for j in seq:
            arco = arcos[(k, str(anterior), str(j))]
            tb, tc = arco["t_barra"], arco["t_chapeu"]
            a_j = cargas[j]["janela_inicio"]
            nominal = max(a_j, nominal + tb)
            novo = []
            for g in range(gama + 1):
                sem = pior[g] + tb
                com = pior[g - 1] + tb + tc if g > 0 else -math.inf
                novo.append(max(a_j, sem, com))
            pior = novo
            res[j] = {"navio": k, "nominal": nominal, "pior": pior[gama]}
            anterior = j
    return res


# ---------------------------------------------------------------------------
# Resumo no terminal
# ---------------------------------------------------------------------------

def imprimir_resumo(inst, cheg, gama):
    p = inst["parametros"]
    print(f"\n=== {inst['nome']} ===")
    print(f"Cargas: {p['cargas']} | Navios: {p['navios']} | Arcos: {len(inst['arcos'])} "
          f"| Viável garantido até Γ = {p['gama_max_garantido']}")

    print("\nNavios")
    print(f"  {'navio':<6}{'vel (nós)':>10}{'custo/dia':>11}{'porto ini':>11}{'cargas no plano':>18}")
    plano = {r["navio"]: r["sequencia"] for r in inst["plano_referencia"]}
    for n in inst["navios"]:
        seq = " → ".join(str(j) for j in plano.get(n["id"], [])) or "(parado)"
        print(f"  {n['nome']:<6}{n['velocidade_nos']:>10}{n['custo_dia_kusd']:>11}"
              f"{'P%02d' % n['porto_inicial']:>11}   {seq}")

    print(f"\nCargas (chegadas do plano de referência, Γ = {gama})")
    print(f"  {'carga':<6}{'janela [a, b]':>18}{'navio':>7}{'nominal':>9}{'pior':>8}{'folga':>8}")
    for c in sorted(inst["cargas"], key=lambda c: c["janela_inicio"]):
        ch = cheg[c["id"]]
        folga = c["janela_fim"] - ch["pior"]
        print(f"  {c['id']:<6}{'[%.1f, %.1f]' % (c['janela_inicio'], c['janela_fim']):>18}"
              f"{inst['navios'][ch['navio']]['nome']:>7}{ch['nominal']:>9.1f}{ch['pior']:>8.1f}{folga:>8.1f}")

    ativos = [a for a in inst["arcos"] if a["t_barra"] > 0]
    razoes = sorted(a["t_chapeu"] / a["t_barra"] for a in ativos)
    med = razoes[len(razoes) // 2]
    print(f"\nAtraso máximo / tempo nominal nos arcos: mín {razoes[0]:.0%}, "
          f"mediana {med:.0%}, máx {razoes[-1]:.0%}")
    custo = sum(indexar_arcos(inst)[(r["navio"], str(de), str(para))]["custo"]
                for r in inst["plano_referencia"] if r["sequencia"]
                for de, para in zip(["o"] + r["sequencia"], r["sequencia"] + ["d"]))
    print(f"Custo do plano de referência: {custo:.1f} kUSD (viável, não necessariamente ótimo)")


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

def desenhar_mapa(ax, inst):
    portos = {p["id"]: p for p in inst["portos"]}
    cargas = {c["id"]: c for c in inst["cargas"]}

    # portos
    for p in inst["portos"]:
        marca = "o" if p["tipo"] == "coleta" else "s"
        ax.scatter(p["x"], p["y"], marker=marca, s=70, facecolor="white",
                   edgecolor=PORTO, linewidth=1.5, zorder=3)
        ax.annotate(p["nome"], (p["x"], p["y"]), xytext=(6, 6), textcoords="offset points",
                    fontsize=8, color=TEXTO_2, zorder=4)

    # rotas do plano de referência
    for rota in inst["plano_referencia"]:
        k, seq = rota["navio"], rota["sequencia"]
        cor = cor_navio(k)
        nav = inst["navios"][k]
        atual = portos[nav["porto_inicial"]]
        ax.scatter(atual["x"], atual["y"], marker="^", s=150, color=cor,
                   edgecolor="white", linewidth=1.5, zorder=5)
        for j in seq:
            col = portos[cargas[j]["porto_coleta"]]
            ent = portos[cargas[j]["porto_entrega"]]
            # trecho vazio até a coleta
            ax.annotate("", xy=(col["x"], col["y"]), xytext=(atual["x"], atual["y"]),
                        arrowprops=dict(arrowstyle="-|>", color=cor, lw=1.5,
                                        linestyle=(0, (4, 3)), shrinkA=6, shrinkB=6), zorder=2)
            # trecho carregado coleta -> entrega
            ax.annotate("", xy=(ent["x"], ent["y"]), xytext=(col["x"], col["y"]),
                        arrowprops=dict(arrowstyle="-|>", color=cor, lw=2.2,
                                        shrinkA=6, shrinkB=6), zorder=2)
            mx, my = (col["x"] + ent["x"]) / 2, (col["y"] + ent["y"]) / 2
            ax.text(mx, my, f"C{j}", fontsize=8, color=TEXTO, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=cor, lw=1), zorder=6)
            atual = ent

    ax.set_title("Mapa: portos e rotas do plano de referência", loc="left", fontsize=11)
    ax.set_xlabel("x (milhas náuticas)")
    ax.set_ylabel("y (milhas náuticas)")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(color=GRADE, linewidth=0.6)
    ax.set_axisbelow(True)

    legenda = [
        Line2D([], [], marker="o", ls="", mfc="white", mec=PORTO, mew=1.5, ms=8, label="Porto de coleta"),
        Line2D([], [], marker="s", ls="", mfc="white", mec=PORTO, mew=1.5, ms=8, label="Porto de entrega"),
        Line2D([], [], marker="^", ls="", color=TEXTO_2, ms=10, label="Posição inicial do navio"),
        Line2D([], [], color=TEXTO_2, lw=2.2, label="Com carga"),
        Line2D([], [], color=TEXTO_2, lw=1.5, ls=(0, (4, 3)), label="Vazio"),
    ] + [Line2D([], [], color=cor_navio(n["id"]), lw=3, label=n["nome"]) for n in inst["navios"]]
    ax.legend(handles=legenda, loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=8.5)


def desenhar_janelas(ax, inst, cheg, gama):
    cargas = sorted(inst["cargas"], key=lambda c: c["janela_inicio"], reverse=True)
    for y, c in enumerate(cargas):
        a, b = c["janela_inicio"], c["janela_fim"]
        ax.barh(y, b - a, left=a, height=0.5, color=JANELA, edgecolor="none", zorder=1)
        ch = cheg[c["id"]]
        cor = cor_navio(ch["navio"])
        ax.plot([ch["nominal"], ch["pior"]], [y, y], color=cor, lw=2, zorder=2)
        ax.scatter(ch["nominal"], y, marker="o", s=55, color=cor, edgecolor="white", linewidth=1.5, zorder=3)
        ax.scatter(ch["pior"], y, marker="D", s=50, color=cor, edgecolor="white", linewidth=1.5, zorder=3)

    ax.set_yticks(range(len(cargas)))
    ax.set_yticklabels([f"C{c['id']} · {inst['navios'][cheg[c['id']]['navio']]['nome']}" for c in cargas])
    ax.set_xlabel("tempo (dias)")
    ax.set_title(f"Janelas de tempo e chegadas do plano (Γ = {gama})", loc="left", fontsize=11)
    ax.grid(axis="x", color=GRADE, linewidth=0.6)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(axis="y", length=0)

    legenda = [
        Patch(facecolor=JANELA, label="Janela [a, b]"),
        Line2D([], [], marker="o", ls="", color=TEXTO_2, ms=7, label="Chegada nominal"),
        Line2D([], [], marker="D", ls="", color=TEXTO_2, ms=6, label=f"Pior chegada (até Γ = {gama} atrasos)"),
    ]
    ax.legend(handles=legenda, loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=8.5)


def visualizar(caminho, gama, mostrar):
    with open(caminho, encoding="utf-8") as f:
        inst = json.load(f)
    if gama is None:
        gama = inst["parametros"]["gama_max_garantido"]
    cheg = chegadas(inst, gama)
    imprimir_resumo(inst, cheg, gama)

    n = len(inst["cargas"])
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7 + 0.28 * n),
                                   gridspec_kw={"height_ratios": [1.35, max(0.6, 0.12 * n)]})
    p = inst["parametros"]
    fig.suptitle(f"{inst['nome']}  ·  {p['cargas']} cargas, {p['navios']} navio(s), "
                 f"{len(inst['arcos'])} arcos", x=0.02, ha="left", fontsize=13, color=TEXTO)
    desenhar_mapa(ax1, inst)
    desenhar_janelas(ax2, inst, cheg, gama)
    fig.tight_layout(rect=(0, 0, 1, 0.97))

    saida = os.path.splitext(caminho)[0] + ".png"
    fig.savefig(saida, dpi=150)
    print(f"\nFigura salva em {saida}")
    if mostrar:
        plt.show()
    plt.close(fig)
    return saida


def main():
    ap = argparse.ArgumentParser(description="Visualiza instâncias do VRPTW robusto.")
    ap.add_argument("caminho", help="arquivo JSON de uma instância ou pasta com várias")
    ap.add_argument("--gama", type=int, default=None,
                    help="Γ usado na pior chegada (padrão: o Γ máximo garantido da instância)")
    ap.add_argument("--mostrar", action="store_true", help="abre a janela do gráfico")
    args = ap.parse_args()

    if os.path.isdir(args.caminho):
        arquivos = sorted(glob.glob(os.path.join(args.caminho, "*.json")))
        if not arquivos:
            raise SystemExit(f"Nenhum JSON em {args.caminho}")
        pasta_fig = os.path.join(args.caminho, "figuras")
        os.makedirs(pasta_fig, exist_ok=True)
        for arq in arquivos:
            png = visualizar(arq, args.gama, mostrar=False)
            os.replace(png, os.path.join(pasta_fig, os.path.basename(png)))
        print(f"\n{len(arquivos)} figura(s) em {pasta_fig}/")
    else:
        visualizar(args.caminho, args.gama, args.mostrar)


if __name__ == "__main__":
    main()