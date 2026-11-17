# SPEC-001: VRPTW Robusto para Navegação Industrial (Agra et al., 2013)

## 1. Contexto e Motivação
Este documento formaliza o problema de roteamento de veículos com janelas de tempo e tempos de viagem incertos (VRPTW Robusto) no contexto de navegação industrial de cabotagem/granel, conforme proposto por **Agra et al. (2013)**.

No transporte marítimo industrial:
* Não existe um depósito único central: cada navio $k$ inicia sua operação em um porto inicial $o(k)$ e finaliza em um porto destino artificial $d(k)$.
* Cada carga $i \in C$ é uma operação completa de coleta (porto de origem) e entrega (porto de destino). Como os navios transportam grandes lotes únicos por vez, o nó do grafo representa a carga inteira.
* A frota é heterogênea em capacidade, velocidade e custos operacionais diários.
* Condições climáticas e operações portuárias causam incertezas nos tempos de trânsito. O modelo utiliza o conceito de **orçamento de incerteza de Bertsimas & Simchi-Levi / Agra et al.**, onde no máximo $\Gamma_k$ trechos sofrerão seus piores atrasos ao longo da rota do navio $k$.

---

## 2. Elementos e Dados do Problema

### 2.1 Nós e Arcos
* $C = \{1, \dots, n\}$: Conjunto de cargas a serem transportadas.
* $K = \{1, \dots, m\}$: Conjunto de navios disponíveis.
* Para cada navio $k \in K$:
  * Nó de origem: $o(k)$ (porto inicial onde o navio está disponível).
  * Nó de término: $d(k)$ (nó artificial de encerramento).
  * Conjunto de nós do navio $k$: $V^k = C \cup \{o(k), d(k)\}$.
  * Conjunto de arcos viáveis $A^k \subseteq V^k \times V^k$ (respeitando compatibilidade navio-carga e precedências).

### 2.2 Parâmetros por Arco e Carga
* $c_{ij}^k$: Custo de deslocamento do navio $k$ entre a entrega da carga $i$ e a entrega da carga $j$ (inclui custo de lastro + viagem carregada).
* $\bar{t}_{ij}^k$: Tempo nominal de viagem em dias.
* $\hat{t}_{ij}^k$: Atraso máximo adicional esperado em dias.
* $[a_i, b_i]$: Janela de tempo para o início do atendimento da carga $i$.
* $\Gamma_k \in \mathbb{N}$: Orçamento máximo de arcos com atraso simultâneo na rota do navio $k$.

---

## 3. Estado Atual dos Módulos Implementados

1. **Gerador de Instâncias ([gerar_instancias.py](file:///c:/Users/anabe/OneDrive/Área%20de%20Trabalho/Otimização%20Inteira/gerar_instancias.py)):**
   * Sorteia posições geográficas de portos e navios.
   * Constrói previamente um **plano de referência viável** e dimensiona as janelas de tempo ao redor dele, garantindo que toda instância gerada possua solução viável para qualquer $\Gamma \le \Gamma_{\max}$.
   * Salva instâncias no formato JSON e metadados no arquivo `resumo.csv`.

2. **Visualizador ([visualizar_instancia.py](file:///c:/Users/anabe/OneDrive/Área%20de%20Trabalho/Otimização%20Inteira/visualizar_instancia.py)):**
   * Plota o mapa de atendimento com distinção de trecho carregado vs. lastro.
   * Plota o diagrama de janelas de tempo comparando chegada nominal vs. pior chegada sob $\Gamma$ atrasos calculada via programação dinâmica.

---

## 4. Próximos Passos (Aguardando Novas Specs)
* **SPEC-002 (Futura):** Formulação matemática exata do modelo MIP/Robust MIP (utilizando linearização por dualidade ou cortes de planos de corte) e resolução via solver (ex: HiGHS / PuLP / Gurobi).

---

## 5. Histórico de Aprovações

| Etapa | Responsável | Status | Data |
| :--- | :--- | :--- | :--- |
| **Aprovação 1: Documental (Estrutura e Conceito)** | Aluna (Ana Beatriz) | `Aprovado (Baseline)` | 17/11/2026 |
| **Aprovação 2: Implementação (Gerador e Visualizador)** | Aluna (Ana Beatriz) | `Aprovado (Baseline)` | 17/11/2026 |
