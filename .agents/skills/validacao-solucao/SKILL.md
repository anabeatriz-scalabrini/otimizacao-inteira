---
name: validacao-solucao
description: >-
  Use esta skill para inspecionar, auditar e validar soluções geradas por solvers ou
  heurísticas de roteamento. Avalia viabilidade de janelas de tempo, capacidades e
  robustez sob o orçamento de atrasos Gamma.
---

# Skill: Validação Independente de Soluções

Esta skill define o protocolo para testar se uma solução encontrada por um solver é realmente viável e respeita as regras do negócio sem confiar cegamente na saída do solver.

---

## 1. Princípio da Verificação Independente

Nunca confie apenas no retorno do solver (`OPTIMAL`). Sempre passe a rota gerada por um algoritmo validador em Python puro que:
1. Reconstrói a sequência de visitas de cada navio/veículo.
2. Calcula os tempos acumulados de chegada.
3. Checa a janela de tempo de cada carga: $a_i \le \text{chegada}_i \le b_i$.
4. Avalia a pior chegada sob o orçamento de atrasos $\Gamma$.

---

## 2. Algoritmo de Pior Caso para Incerteza $\Gamma$ (Programação Dinâmica)

Para cada navio $k$ com rota $(v_0, v_1, \dots, v_m)$ e orçamento $\Gamma$:
* Seja $T(\ell, \gamma)$ o menor tempo para concluir a etapa $\ell$ tendo sofrido $\gamma$ atrasos:
  $$T(\ell, \gamma) = \max \left( a_{v_\ell}, \min \Big( T(\ell-1, \gamma) + \bar{t}_{v_{\ell-1}, v_\ell}, \; T(\ell-1, \gamma-1) + \bar{t}_{v_{\ell-1}, v_\ell} + \hat{t}_{v_{\ell-1}, v_\ell} \Big) \right)$$
* Se para qualquer nó $v_\ell$, o valor $T(\ell, \Gamma) > b_{v_\ell}$, a solução é **inviável** sob incerteza.

---

## 3. Checklist de Aprovação 2 (Implementação)

Antes de solicitar a **Aprovação 2**:
- [ ] O status do solver foi verificado (`OPTIMAL` ou `FEASIBLE`)?
- [ ] A função objetivo calculada pelo solver confere com a soma real dos custos dos arcos utilizados?
- [ ] Todas as cargas foram atendidas exatamente uma vez (sem duplicatas ou omissões)?
- [ ] O tempo de início em cada carga respeita a janela $[a_i, b_i]$ tanto no cenário nominal quanto no pior cenário $\Gamma$?
