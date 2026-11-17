#!/usr/bin/env python3
"""
Gerador de instâncias para o VRPTW robusto com tempos de viagem incertos,
inspirado na seção 5.2 de Agra et al. (2013), "The robust vehicle routing
problem with time windows", Computers & Operations Research 40, 856–866.

Cada instância representa um problema de navegação industrial:
  - cada nó é uma CARGA (coleta + entrega juntas: o navio leva uma carga por vez);
  - não há depósito central: cada navio parte de onde está (nó "o") e termina
    num nó artificial ("d");
  - a frota é heterogênea (velocidades e custos diferentes) e alguns navios não
    podem atender algumas cargas (porte/calado);
  - cada arco (i, j) do navio k tem custo c, tempo nominal t_barra e atraso
    máximo t_chapeu (usado no conjunto de incerteza com orçamento Γ).

Garantia de viabilidade: o gerador primeiro sorteia um plano de referência
(qual navio atende quais cargas e em que ordem) e só depois cria as janelas de
tempo em volta desse plano. Assim, toda instância tem pelo menos uma solução
viável para qualquer Γ <= --gama-max. O plano de referência é salvo no arquivo
para conferência, mas NÃO é necessariamente ótimo.

Unidades: distância em milhas náuticas, velocidade em nós, tempo em dias,
custo em milhares de dólares (kUSD).

Uso:
  # uma instância com 8 cargas e 2 navios
  python gerar_instancias.py --cargas 8 --navios 2

  # um lote: 5, 10 e 15 cargas; 1, 2 e 3 navios; 3 réplicas de cada
  python gerar_instancias.py --cargas 5 10 15 --navios 1 2 3 --replicas 3 --saida dados

Requer apenas a biblioteca padrão do Python (3.8+).
"""

import argparse
import csv
import json
import math
import os
import random

VERSAO = "1.0"


# --------------------------------------------------------------------------
# Geração dos elementos básicos
# --------------------------------------------------------------------------

def gerar_portos(rng, n_coleta, n_entrega, largura, altura):
    """Sorteia portos de coleta e de entrega em conjuntos disjuntos.

    Cada porto recebe um fator de atraso: portos em regiões de mau tempo
    atrasam mais (seção 5.2 do artigo).
    """
    portos = []
    for idx in range(n_coleta + n_entrega):
        tipo = "coleta" if idx < n_coleta else "entrega"
        portos.append({
            "id": idx,
            "nome": f"P{idx:02d}",
            "tipo": tipo,
            "x": round(rng.uniform(0, largura), 1),
            "y": round(rng.uniform(0, altura), 1),
            "fator_atraso": round(rng.uniform(0.5, 1.5), 2),
        })
    return portos


def distancia(p, q):
    return math.hypot(p["x"] - q["x"], p["y"] - q["y"])


def gerar_navios(rng, n_navios, portos_entrega, vel_min, vel_max):
    """Navios heterogêneos: velocidade, custo diário e posição inicial."""
    navios = []
    for k in range(n_navios):
        velocidade = rng.uniform(vel_min, vel_max)
        # Navios mais rápidos custam mais por dia.
        custo_dia = 15 + 2.0 * (velocidade - vel_min) + rng.uniform(0, 5)
        inicio = rng.choice(portos_entrega)  # porto da última entrega
        navios.append({
            "id": k,
            "nome": f"N{k + 1}",
            "velocidade_nos": round(velocidade, 1),
            "custo_dia_kusd": round(custo_dia, 2),
            "porto_inicial": inicio["id"],
        })
    return navios


def gerar_cargas(rng, n_cargas, portos_coleta, portos_entrega, serv_min, serv_max):
    """Cada carga tem um porto de coleta, um de entrega e tempos de serviço."""
    cargas = []
    for i in range(n_cargas):
        cargas.append({
            "id": i + 1,  # cargas numeradas a partir de 1 (0 fica livre)
            "porto_coleta": rng.choice(portos_coleta)["id"],
            "porto_entrega": rng.choice(portos_entrega)["id"],
            "servico_coleta_dias": round(rng.uniform(serv_min, serv_max), 2),
            "servico_entrega_dias": round(rng.uniform(serv_min, serv_max), 2),
        })
    return cargas


# --------------------------------------------------------------------------
# Arcos: custo, tempo nominal e atraso máximo por navio
# --------------------------------------------------------------------------

def dias_navegando(dist_nm, velocidade_nos):
    return dist_nm / (velocidade_nos * 24.0)


def construir_arcos(portos, navios, cargas, compat, frac_atraso):
    """Cria os arcos de cada navio, no formato do artigo.

    Arco (o, j): do porto inicial do navio até a coleta da carga j.
    Arco (i, j): coleta de i -> entrega de i -> coleta de j.
    Arco (i, d): coleta de i -> entrega de i (fim da programação).
    Arco (o, d): navio não usado (custo e tempo zero).

    O tempo do arco inclui o serviço na coleta e na entrega da carga i.
    O atraso máximo t_chapeu incide só sobre a navegação e depende do fator de
    atraso dos portos envolvidos.
    """
    P = {p["id"]: p for p in portos}
    C = {c["id"]: c for c in cargas}
    arcos = []

    for nav in navios:
        k, v, custo_dia = nav["id"], nav["velocidade_nos"], nav["custo_dia_kusd"]
        origem = P[nav["porto_inicial"]]
        atendiveis = [c["id"] for c in cargas if compat[(k, c["id"])]]

        def novo_arco(de, para, nav_dias, serv_dias, fator):
            t_barra = nav_dias + serv_dias
            t_chapeu = frac_atraso * nav_dias * fator
            arcos.append({
                "navio": k,
                "de": de,
                "para": para,
                "custo": round(custo_dia * t_barra, 3),
                "t_barra": round(t_barra, 3),
                "t_chapeu": round(t_chapeu, 3),
            })

        # o -> d: navio parado
        arcos.append({"navio": k, "de": "o", "para": "d",
                      "custo": 0.0, "t_barra": 0.0, "t_chapeu": 0.0})

        for j in atendiveis:
            cj = C[j]
            pj = P[cj["porto_coleta"]]
            # o -> j
            nav_dias = dias_navegando(distancia(origem, pj), v)
            fator = (origem["fator_atraso"] + pj["fator_atraso"]) / 2
            novo_arco("o", j, nav_dias, 0.0, fator)

        for i in atendiveis:
            ci = C[i]
            pi_col, pi_ent = P[ci["porto_coleta"]], P[ci["porto_entrega"]]
            perna_carga = dias_navegando(distancia(pi_col, pi_ent), v)
            serv_i = ci["servico_coleta_dias"] + ci["servico_entrega_dias"]
            fator_carga = (pi_col["fator_atraso"] + pi_ent["fator_atraso"]) / 2

            # i -> d: leva a carga i e encerra
            novo_arco(i, "d", perna_carga, serv_i, fator_carga)

            # i -> j: leva a carga i e segue para a coleta de j
            for j in atendiveis:
                if j == i:
                    continue
                pj = P[C[j]["porto_coleta"]]
                perna_vazio = dias_navegando(distancia(pi_ent, pj), v)
                fator = (fator_carga + (pi_ent["fator_atraso"] + pj["fator_atraso"]) / 2) / 2
                novo_arco(i, j, perna_carga + perna_vazio, serv_i, fator)

    return arcos


# --------------------------------------------------------------------------
# Plano de referência e janelas de tempo
# --------------------------------------------------------------------------

def pior_chegada(seq_arcos, janelas_inicio, gama):
    """Programação dinâmica da Prop. 10 do artigo.

    a(j, g) = chegada mais cedo no j-ésimo nó quando até g trechos estão no pico:
      a(j, g) = max{ a_j, a(j-1, g) + t_barra, a(j-1, g-1) + t_barra + t_chapeu }
    Retorna, para cada nó do caminho, a chegada no pior caso com até Γ atrasos.
    """
    linha = [0.0] * (gama + 1)  # saída da origem no instante 0
    piores = []
    for (t_barra, t_chapeu), a_j in zip(seq_arcos, janelas_inicio):
        nova = []
        for g in range(gama + 1):
            sem_atraso = linha[g] + t_barra
            com_atraso = linha[g - 1] + t_barra + t_chapeu if g > 0 else -math.inf
            nova.append(max(a_j, sem_atraso, com_atraso))
        linha = nova
        piores.append(linha[gama])
    return piores


def criar_plano_e_janelas(rng, navios, cargas, compat, arcos, gama_max,
                          folga_antes, folga_depois):
    """Sorteia um plano viável e cria as janelas de tempo em volta dele.

    Para cada carga do plano:
      - a (abertura) = chegada nominal menos uma folga aleatória;
      - b (fechamento) = pior chegada com Γ_max atrasos mais uma folga aleatória.
    Isso garante que o plano de referência é robusto para todo Γ <= Γ_max.
    """
    idx = {(a["navio"], a["de"], a["para"]): a for a in arcos}

    # Distribui as cargas entre navios compatíveis.
    rotas = {nav["id"]: [] for nav in navios}
    ordem = [c["id"] for c in cargas]
    rng.shuffle(ordem)
    for j in ordem:
        opcoes = [nav["id"] for nav in navios if compat[(nav["id"], j)]]
        rotas[rng.choice(opcoes)].append(j)

    janelas = {}
    for k, seq in rotas.items():
        if not seq:
            continue
        nos = ["o"] + seq
        seq_arcos, inicios = [], []
        chegada_nominal = 0.0
        for de, para in zip(nos[:-1], nos[1:]):
            arco = idx[(k, de, para)]
            chegada_nominal += arco["t_barra"]
            a_j = max(0.0, chegada_nominal - rng.uniform(0, folga_antes))
            seq_arcos.append((arco["t_barra"], arco["t_chapeu"]))
            inicios.append(a_j)
            # Sem espera no plano nominal: a_j <= chegada nominal.
        piores = pior_chegada(seq_arcos, inicios, gama_max)
        for j, a_j, w in zip(seq, inicios, piores):
            b_j = w + rng.uniform(0, folga_depois)
            # Arredonda para o lado seguro: abertura para baixo, fechamento para cima.
            janelas[j] = (math.floor(a_j * 1000) / 1000, math.ceil(b_j * 1000) / 1000)

    plano = [{"navio": k, "sequencia": seq} for k, seq in rotas.items()]
    return plano, janelas


def verificar_plano(plano, janelas, arcos, gama):
    """Confere, pela programação dinâmica, se o plano respeita as janelas."""
    idx = {(a["navio"], a["de"], a["para"]): a for a in arcos}
    for rota in plano:
        k, seq = rota["navio"], rota["sequencia"]
        if not seq:
            continue
        nos = ["o"] + seq
        seq_arcos = [(idx[(k, de, para)]["t_barra"], idx[(k, de, para)]["t_chapeu"])
                     for de, para in zip(nos[:-1], nos[1:])]
        inicios = [janelas[j][0] for j in seq]
        piores = pior_chegada(seq_arcos, inicios, gama)
        for j, w in zip(seq, piores):
            if w > janelas[j][1] + 1e-6:
                return False
    return True


# --------------------------------------------------------------------------
# Montagem de uma instância
# --------------------------------------------------------------------------

def gerar_instancia(n_cargas, n_navios, semente, args):
    rng = random.Random(semente)

    n_coleta = max(2, math.ceil(n_cargas * 0.6))
    n_entrega = max(2, math.ceil(n_cargas * 0.6))
    portos = gerar_portos(rng, n_coleta, n_entrega, args.largura, args.altura)
    portos_coleta = [p for p in portos if p["tipo"] == "coleta"]
    portos_entrega = [p for p in portos if p["tipo"] == "entrega"]

    navios = gerar_navios(rng, n_navios, portos_entrega, args.vel_min, args.vel_max)
    cargas = gerar_cargas(rng, n_cargas, portos_coleta, portos_entrega,
                          args.servico_min, args.servico_max)

    # Compatibilidade navio x carga (porte/calado). Toda carga tem ao menos um navio.
    compat = {}
    for c in cargas:
        for nav in navios:
            compat[(nav["id"], c["id"])] = rng.random() >= args.prob_incompat
        if not any(compat[(nav["id"], c["id"])] for nav in navios):
            compat[(rng.choice(navios)["id"], c["id"])] = True

    arcos = construir_arcos(portos, navios, cargas, compat, args.frac_atraso)
    plano, janelas = criar_plano_e_janelas(
        rng, navios, cargas, compat, arcos, args.gama_max,
        args.folga_antes, args.folga_depois)

    for c in cargas:
        c["janela_inicio"], c["janela_fim"] = janelas[c["id"]]
        c["navios_compativeis"] = [nav["id"] for nav in navios if compat[(nav["id"], c["id"])]]

    assert verificar_plano(plano, janelas, arcos, args.gama_max), \
        "Plano de referência inviável: erro no gerador"

    nome = f"inst_c{n_cargas:02d}_n{n_navios}_s{semente}"
    return {
        "nome": nome,
        "versao_gerador": VERSAO,
        "semente": semente,
        "parametros": {
            "cargas": n_cargas,
            "navios": n_navios,
            "gama_max_garantido": args.gama_max,
            "frac_atraso": args.frac_atraso,
            "prob_incompat": args.prob_incompat,
            "unidades": {"distancia": "milhas nauticas", "velocidade": "nos",
                         "tempo": "dias", "custo": "kUSD"},
        },
        "portos": portos,
        "navios": navios,
        "cargas": cargas,
        "arcos": arcos,
        "plano_referencia": plano,
    }


# --------------------------------------------------------------------------
# Linha de comando
# --------------------------------------------------------------------------

def ler_argumentos():
    p = argparse.ArgumentParser(
        description="Gera instâncias do VRPTW robusto (navegação industrial).")
    p.add_argument("--cargas", type=int, nargs="+", default=[8],
                   help="número(s) de cargas, ex.: 5 10 15")
    p.add_argument("--navios", type=int, nargs="+", default=[2],
                   help="número(s) de navios, ex.: 1 2 3")
    p.add_argument("--replicas", type=int, default=1,
                   help="instâncias por combinação (sementes diferentes)")
    p.add_argument("--semente", type=int, default=42, help="semente inicial")
    p.add_argument("--saida", default="dados", help="pasta de saída")
    p.add_argument("--gama-max", dest="gama_max", type=int, default=3,
                   help="Γ máximo para o qual a viabilidade é garantida")
    p.add_argument("--frac-atraso", dest="frac_atraso", type=float, default=0.3,
                   help="atraso máximo como fração do tempo de navegação")
    p.add_argument("--prob-incompat", dest="prob_incompat", type=float, default=0.1,
                   help="probabilidade de um navio não poder atender uma carga")
    p.add_argument("--vel-min", dest="vel_min", type=float, default=13.0)
    p.add_argument("--vel-max", dest="vel_max", type=float, default=20.0)
    p.add_argument("--servico-min", dest="servico_min", type=float, default=0.5,
                   help="tempo mínimo de serviço por porto (dias)")
    p.add_argument("--servico-max", dest="servico_max", type=float, default=2.0)
    p.add_argument("--folga-antes", dest="folga_antes", type=float, default=5.0,
                   help="folga máxima antes da chegada nominal (dias)")
    p.add_argument("--folga-depois", dest="folga_depois", type=float, default=3.0,
                   help="folga máxima depois da pior chegada (dias)")
    p.add_argument("--largura", type=float, default=6000.0,
                   help="largura da região dos portos (milhas náuticas)")
    p.add_argument("--altura", type=float, default=3000.0)
    return p.parse_args()


def main():
    args = ler_argumentos()
    os.makedirs(args.saida, exist_ok=True)
    resumo = []
    semente = args.semente

    for n_c in args.cargas:
        for n_n in args.navios:
            if n_n > n_c:
                print(f"Pulando {n_c} cargas com {n_n} navios (mais navios que cargas).")
                continue
            for _ in range(args.replicas):
                inst = gerar_instancia(n_c, n_n, semente, args)
                caminho = os.path.join(args.saida, inst["nome"] + ".json")
                with open(caminho, "w", encoding="utf-8") as f:
                    json.dump(inst, f, ensure_ascii=False, indent=2)
                horizonte = max(c["janela_fim"] for c in inst["cargas"])
                resumo.append({
                    "arquivo": os.path.basename(caminho),
                    "cargas": n_c,
                    "navios": n_n,
                    "semente": semente,
                    "arcos": len(inst["arcos"]),
                    "horizonte_dias": round(horizonte, 1),
                })
                print(f"Gerada {caminho}  ({len(inst['arcos'])} arcos, "
                      f"horizonte {horizonte:.1f} dias)")
                semente += 1

    with open(os.path.join(args.saida, "resumo.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(resumo[0].keys()))
        w.writeheader()
        w.writerows(resumo)
    print(f"\n{len(resumo)} instância(s) em '{args.saida}/' (resumo em resumo.csv).")


if __name__ == "__main__":
    main()