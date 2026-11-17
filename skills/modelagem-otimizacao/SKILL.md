---
name: modelagem-otimizacao
description: >-
  Use esta skill sempre que for formular ou modificar um modelo de Programação Linear
  Inteira Mista (MIP) ou Otimização Robusta. Garante rigor matemático, definição precisa
  de conjuntos e parâmetros, e cálculo de Big-M justos.
---

# Skill: Modelagem Matemática em Otimização Inteira

Esta skill orienta a criação de modelos matemáticos claros, corretos e eficientes para solvers (como HiGHS, Gurobi, CPLEX, PuLP ou Pyomo).

---

## 1. Estrutura Padrão da Formulação

Toda especificação e documentação de modelo deve seguir rigorosamente a estrutura:

1. **Índices e Conjuntos:**
   * Descreva o significado físico de cada conjunto (ex: $K$ navios, $C$ cargas, $A$ arcos).
2. **Parâmetros:**
   * Nome, unidade de medida e limites físicos conhecidos (ex: custo em kUSD, tempo em dias).
3. **Variáveis de Decisão:**
   * Nome, domínio matemático ($\{0, 1\}$, $\mathbb{Z}_{\ge 0}$, $\mathbb{R}_{\ge 0}$) e interpretação prática.
4. **Função Objetivo:**
   * Deixar explícito se é minimização ou maximização.
5. **Restrições:**
   * Agrupar por função lógica (ex: conservação de fluxo, acoplamento de variáveis, janelas de tempo).

---

## 2. Regra Fundamental: Big-M Justo (Tight Big-M)

Ao modelar precedências temporais ou desativação de restrições condicionais:
$$w_j \ge w_i + s_i + t_{ij} - M_{ij} (1 - x_{ij})$$

* ❌ **NUNCA faça:** $M = 10^9$ ou $M = 999999$.
* ✅ **SEMPRE calcule o menor valor válido:**
  $$M_{ij} = \max(0, b_i + s_i + t_{ij}^{\max} - a_j)$$
  onde:
  * $b_i$: limite superior da janela do nó $i$;
  * $s_i$: tempo de serviço no nó $i$;
  * $t_{ij}^{\max}$: tempo máximo de viagem entre $i$ e $j$;
  * $a_j$: limite inferior da janela do nó $j$.

---

## 3. Checklist de Validação do Modelo

Antes de submeter para a **Aprovação 1 (Documental)**:
- [ ] Todos os somatórios têm índices e conjuntos bem definidos?
- [ ] O modelo evita não-linearidades (como produto de variáveis binárias por contínuas) ou as lineariza adequadamente?
- [ ] Os limites inferiores e superiores das variáveis foram declarados para auxiliar o pré-processamento do solver?
- [ ] As restrições de subciclo ou fluxo foram contempladas?
