---
name: benchmark-experimentos
description: >-
  Use esta skill ao planejar e executar testes computacionais, experimentos de desempenho
  ou comparações de solvers. Garante rigor na coleta de métricas e reprodutibilidade.
---

# Skill: Benchmark e Testes Computacionais

Esta skill padroniza os experimentos computacionais do projeto, facilitando a confecção de tabelas e gráficos para artigos, monografias ou relatórios da faculdade.

---

## 1. Métricas Essenciais a Coletar

Para cada execução de instância, sempre registre:
* `instancia`: Nome do arquivo JSON testado.
* `n_cargas`, `n_navios`, `gama`: Parâmetros da instância.
* `status`: `OPTIMAL`, `TIME_LIMIT`, `INFEASIBLE`, etc.
* `tempo_cpu_s`: Tempo total de resolução em segundos.
* `valor_fo`: Valor da função objetivo (custo total).
* `melhor_limite`: Melhor limite dual (lower bound no caso de minimização).
* `gap_percentual`: Gap de otimalidade relativo:
  $$\text{Gap} = \frac{|\text{FO} - \text{Limite Dual}|}{|\text{FO}| + 10^{-10}} \times 100\%$$
* `nos_branch_and_bound`: Quantidade de nós explorados na árvore do solver.

---

## 2. Boas Práticas de Execução

1. **Definir sempre um Time Limit (ex: 60s ou 300s):**
   * Modelos NP-difíceis podem travar o computador em instâncias maiores se não houver tempo limite configurado.
2. **Fixar a Semente Aleatória:**
   * Qualquer componente estocástico deve ter semente (`seed`) declarada para garantia de reprodutibilidade.
3. **Exportar Resultados:**
   * Salvar os resultados consolidados em formato CSV ou JSON em pasta de resultados dedicada (ex: `resultados/`).
