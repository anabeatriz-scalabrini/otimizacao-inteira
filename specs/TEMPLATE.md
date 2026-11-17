# Template de Especificação (Spec-Driven Development)

> Use este template antes de qualquer nova implementação no projeto.
> **Lembre-se da Regra de 2 Aprovações:** Nenhuma linha de código deve ser escrita antes da **Aprovação 1 (Documental)** desta especificação.

---

## 1. Contexto e Motivação
* Breve descrição do problema ou funcionalidade a ser adicionada.
* Referência bibliográfica ou teórica (se aplicável).
* Qual a dor ou necessidade acadêmica/prática que essa spec resolve?

---

## 2. Modelo Matemático (Se aplicável)

### 2.1 Conjuntos e Índices
* $N = \{0, 1, \dots, n\}$: Conjunto de nós/cargas...
* $K = \{1, \dots, m\}$: Conjunto de navios/veículos...
* $A$: Conjunto de arcos viáveis $(i, j)$...

### 2.2 Parâmetros
* $c_{ij}^k$: Custo de deslocamento...
* $\bar{t}_{ij}^k$: Tempo nominal de viagem...
* $\hat{t}_{ij}^k$: Desvio/atraso máximo...
* $[a_i, b_i]$: Janela de tempo no nó $i$...
* $\Gamma_k$: Orçamento de incerteza do navio $k$...

### 2.3 Variáveis de Decisão
* $x_{ij}^k \in \{0, 1\}$: Se o navio $k$ percorre o arco $(i, j)$...
* $w_i^k \ge 0$: Horário de início de atendimento do nó $i$ pelo navio $k$...
* Variáveis de linearização / duais robustas (se houver)...

### 2.4 Função Objetivo
$$\min \sum_{k \in K} \sum_{(i,j) \in A} c_{ij}^k x_{ij}^k + \dots$$

### 2.5 Restrições
* Conservação de fluxo...
* Atendimento único de cada carga...
* Respeito às janelas de tempo...
* Robustez contra atrasos sob orçamento $\Gamma$...
* Domínio das variáveis...

---

## 3. Arquitetura e Estrutura de Código
* **Arquivos a criar/modificar:**
  * `exemplo_solver.py`
* **Entradas esperadas:** Estrutura dos dados (ex: instâncias JSON em `dados/`).
* **Saídas esperadas:** Formato do resultado (JSON de solução, logs, gaps, etc.).
* **Solvers / Bibliotecas utilizadas:** (ex: PuLP, Pyomo, Gurobi, HiGHS, OR-Tools).

---

## 4. Plano de Validação e Testes
* Como comprovar que a implementação está matematicamente correta?
* Testes com instâncias triviais (ex: 2 cargas, 1 navio).
* Verificação de viabilidade (checagem manual de restrições violadas).
* Critérios de parada e limites de tempo (ex: `time_limit=60s`).

---

## 5. Histórico de Aprovações

| Etapa | Responsável | Status | Data |
| :--- | :--- | :--- | :--- |
| **Aprovação 1: Documental (Spec & Modelo)** | Aluna (Ana Beatriz) | `[Pendente / Aprovado]` | DD/MM/AAAA |
| **Aprovação 2: Implementação (Código & Resultados)** | Aluna (Ana Beatriz) | `[Pendente / Aprovado]` | DD/MM/AAAA |
