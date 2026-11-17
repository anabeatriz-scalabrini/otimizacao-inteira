# Diretrizes do Projeto: Otimização Inteira (Spec-Driven Development)

Este repositório é um projeto acadêmico individual de **Pesquisa Operacional e Otimização Inteira**, desenvolvido por **Ana Beatriz**. O desenvolvimento é conduzido em branch única (`main`) com o apoio da IA em formato de *pair programmer*.

---

## 🚨 REGRA DE OURO: As 2 Aprovações Obrigatórias

Para qualquer nova funcionalidade, alteração no modelo matemático, novo script ou refatoração relevante, a IA **DEVE** seguir rigorosamente o ciclo de duas aprovações sequenciais:

```
[Demanda] 
   │
   ▼
[1. Elaborar/Atualizar Spec em specs/] ──► 🛑 AGUARDAR APROVAÇÃO 1 (DOCUMENTAL)
                                                       │ (Aprovado pela usuária)
                                                       ▼
[2. Implementar Código & Validar Testes] ──► 🛑 AGUARDAR APROVAÇÃO 2 (IMPLEMENTAÇÃO)
                                                       │ (Validado pela usuária)
                                                       ▼
                                            [Finalização / Commit]
```

### 1. Aprovação 1: Documental (Spec & Formulação Matemática)
* **O que a IA deve fazer:** Antes de alterar ou criar qualquer código de implementação, a IA deve redigir ou atualizar a especificação em `specs/` (ou apresentar o documento com formulação matemática detalhada, conjuntos, restrições, arquivos envolvidos e plano de testes).
* **Parada Obrigatória:** A IA **NÃO** deve escrever o código funcional nesta etapa. Deve pausar e perguntar:
  > *"Você aprova esta especificação/formulação documental para avançarmos para a implementação?"*
* **Condição:** Só avançar após a confirmação explícita da usuária.

### 2. Aprovação 2: Implementação (Código, Execução e Validação)
* **O que a IA deve fazer:** Após a aprovação documental, implementar o código, executar validações em instâncias pequenas e demonstrar o funcionamento (status do solver, viabilidade, tempos e logs).
* **Parada Obrigatória:** A IA deve apresentar o resultado e perguntar:
  > *"A implementação e os resultados atendem ao esperado? Você aprova a entrega desta etapa?"*
* **Condição:** Apenas após essa validação o trabalho daquela etapa é dado como concluído e pronto para ser commitado.

### 3. 🛑 Proibição Absoluta de Auto-Commit pela IA
* A IA está **TERMINANTEMENTE PROIBIDA** de executar `git commit` por conta própria.
* Os commits pertencem exclusivamente à **Ana Beatriz**. Você decide quando commitar, diretamente pela interface gráfica do VS Code ("Source Control") ou pelo terminal.
* A IA **só** pode rodar `git commit` se você emitir uma ordem direta e inequívoca como *"pode commitar"* ou *"faça o commit para mim"*. Em qualquer outra situação, a IA deve apenas deixar os arquivos prontos e aguardar.

---

## 📐 Boas Práticas para Otimização Inteira (Pesquisa Operacional)

Ao sugerir, modelar ou implementar soluções de otimização, a IA deve observar os seguintes padrões de engenharia matemática:

1. **Rigor Notacional:**
   * Sempre explicitar a notação formal: Conjuntos ($I, J, K$), Parâmetros ($c_{ij}, t_{ij}$), Variáveis e seus domínios ($x_{ij} \in \{0, 1\}$, $w_i \ge 0$).
   * Nunca omitir índices ou deixar somatórios ambíguos.

2. **Cuidado com constantes Big-M:**
   * **PROIBIDO** usar valores genéricos gigantescos (como $M = 10^9$ ou $M = 999999$). Isso causa instabilidade numérica, erros de arredondamento e relaxações lineares fracas.
   * Sempre calcular valores de $M$ justos (*tight Big-M*) baseados nos limites reais da instância (ex: $M_{ij} = b_i + t_{ij} - a_j$).

3. **Verificação de Status do Solver:**
   * Nunca assumir que o solver encontrou a solução ótima sem inspecionar explicitamente o status (`OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `TIME_LIMIT`).
   * Tratar devidamente casos inviáveis com mensagens claras.

4. **Tolerâncias Numéricas:**
   * Respeitar tolerâncias de integridade (ex: $10^{-5}$ ou $10^{-6}$). Em Python, use `round()` ou `abs(val) > 1e-5` ao invés de comparações diretas de igualdade (`val == 1`).

5. **Validador Independente de Viabilidade:**
   * Toda solução gerada por um solver ou heurística deve poder ser verificada por uma função independente que avalia se todas as restrições (janelas de tempo, capacidades, fluxo) são estritamente satisfeitas.

6. **Gradualismo nos Testes:**
   * Sempre testar primeiro em instâncias mínimas (ex: 5 cargas, 1 navio) antes de rodar instâncias grandes ou baterias completas de benchmark.

7. **Isolamento de Dependências:**
   * O código base do gerador e visualizador usa bibliotecas padrão + `matplotlib`. Para solvers, preferir solvers com interfaces limpas e gratuitas/acadêmicas (ex: `PuLP`, `Pyomo`, `HiGHS`, `OR-Tools`, ou `Gurobi` se licença disponível).
