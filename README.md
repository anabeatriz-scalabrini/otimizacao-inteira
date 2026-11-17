# Otimização Inteira: Roteamento Robusto de Navios com Janelas de Tempo (VRPTW Robusto)

Repositório acadêmico de **Pesquisa Operacional e Otimização Inteira**, desenvolvido por **Ana Beatriz Scalabrini**. O projeto aborda o problema de roteamento de veículos com janelas de tempo e tempos de viagem incertos sob condições climáticas adversas na navegação industrial de cabotagem, inspirado na formulação de **Agra et al. (2013)** (*"The robust vehicle routing problem with time windows"*, *Computers & Operations Research*).

---

## 🎯 Metodologia: Spec-Driven Development (SDD)

Este repositório adota estritamente o paradigma **Spec-Driven Development** em conjunto com a assistência de Inteligência Artificial. 

### Regra de Ouro: As 2 Aprovações Obrigatórias

Mesmo sendo um projeto individual conduzido em branch única (`main`), nenhuma alteração de código é executada sem passar pelo protocolo de duas etapas:

```text
[Nova Demanda/Etapa]
        │
        ▼
┌──────────────────────────────────────────────┐
│ 1. Especificação em specs/                   │
│    (Definição formal, conjuntos e modelo)    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
          🛑 APROVAÇÃO 1: DOCUMENTAL
          (Aluna revisa e aprova a spec)
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 2. Implementação e Testes                    │
│    (Código, execução e validação)            │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
        🛑 APROVAÇÃO 2: IMPLEMENTAÇÃO
        (Aluna valida os testes e resultados)
                       │
                       ▼
              [Commit / Entrega]
```

1. **Aprovação 1 (Documental):** A IA redige ou atualiza a especificação em [`specs/`](specs/) detalhando conjuntos, variáveis, restrições e casos de teste. O código **só** começa a ser escrito após aprovação formal da aluna.
2. **Aprovação 2 (Implementação):** O código é implementado e submetido a baterias de testes e validação independente de viabilidade. Apenas após a confirmação e validação pela aluna a etapa é finalizada.

---

## 📂 Estrutura do Repositório

```text
Otimização Inteira/
├── GEMINI.md                  # Regras de projeto, diretrizes da IA e boas práticas
├── AGENTS.md                  # Padrões para agentes e assistentes de código
├── README.md                  # Documentação principal do projeto
├── .gitignore                 # Arquivos ignorados pelo Git (venv, logs de solvers, etc.)
│
├── gerar_instancias.py        # Gerador sintético de instâncias do problema
├── visualizar_instancia.py    # Visualizador de mapas de rotas e janelas de tempo
│
├── specs/                     # Especificações funcionais e modelos matemáticos
│   ├── TEMPLATE.md            # Modelo padrão para novas especificações
│   └── 001-vrptw-robusto...   # Formalização do problema e instâncias base
│
├── skills/                    # Módulo de habilidades e boas práticas de modelagem
│   ├── modelagem-otimizacao/  # Rigor notacional, conjuntos e Big-M justo
│   ├── validacao-solucao/     # Checagem independente de restrições e pior caso Γ
│   └── benchmark-experimentos/# Métricas de CPU, Gap, limites duais e logs
│
└── dados/                     # Instâncias de teste geradas e gráficos
    ├── resumo.csv             # Tabela com métricas consolidadas das instâncias
    ├── inst_*.json            # Arquivos de instâncias em JSON
    └── figuras/               # Gráficos com mapas de rotas e janelas de tempo
```

---

## 🚀 Como Executar o Projeto

### 1. Clonar e Acessar o Repositório
```bash
git clone https://github.com/anabeatriz-scalabrini/otimizacao-inteira.git
cd "otimizacao-inteira"
```

### 2. Configurar o Ambiente Virtual (`.venv`)
No Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Instale as dependências visuais:
```powershell
pip install matplotlib
```

### 3. Gerar Novas Instâncias
O gerador calcula previamente um plano de referência viável, garantindo que toda instância possua solução viável sob incerteza $\Gamma$:
```powershell
# Gerar uma instância com 8 cargas e 2 navios:
python gerar_instancias.py --cargas 8 --navios 2

# Gerar uma bateria completa de instâncias:
python gerar_instancias.py --cargas 5 10 15 --navios 1 2 3 --replicas 3 --saida dados
```

### 4. Visualizar Rotas e Janelas de Tempo
Gera figuras em PNG com o mapa dos portos (origem/destino/lastro) e o gráfico de janelas de tempo nominais vs. pior caso sob incerteza:
```powershell
# Visualizar uma instância específica e exibir na tela:
python visualizar_instancia.py dados/inst_c08_n2_s42.json --gama 2 --mostrar

# Gerar imagens para todas as instâncias da pasta:
python visualizar_instancia.py dados/
```

---

## 📚 Referência Bibliográfica
* **Agra, A., Christiansen, M., Figueiredo, R., Hvattum, L. M., Lagergren, M., & Neves, R. (2013).** *The robust vehicle routing problem with time windows.* Computers & Operations Research, 40(3), 856–866.
