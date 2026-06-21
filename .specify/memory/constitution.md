<!--
Sync Impact Report
- Version change: (none) → 1.0.0
- Modified principles: N/A (initial ratification)
- Added sections:
  - Core Principles: I. Simplicidade em Primeiro Lugar (CLI-First); II. Test-First (TDD, NÃO NEGOCIÁVEL);
    III. Consistência de Experiência na CLI; IV. Dados Locais e Privacidade; V. Performance Instantânea
  - Qualidade de Código
  - Fluxo de Desenvolvimento e Quality Gates
  - Governance
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (already generic, references "Constitution Check" gate by file path)
  - .specify/templates/spec-template.md ✅ (no constitution-specific placeholders to sync)
  - .specify/templates/tasks-template.md ✅ (already supports test-first task ordering)
- Follow-up TODOs: none
-->

# ReadTrack Constitution

## Core Principles

### I. Simplicidade em Primeiro Lugar (CLI-First)
ReadTrack é uma aplicação de linha de comando para uso pessoal. Toda funcionalidade
DEVE ser exposta como um comando CLI com entrada por argumentos/flags e saída em
texto (stdout para resultados, stderr para erros), com um modo `--json` opcional
para saída estruturada. Não é permitido adicionar interface gráfica, servidor web,
ou camadas de abstração (plugins, frameworks de injeção de dependência, etc.) que
não sejam estritamente necessárias para os requisitos atuais. YAGNI é a regra:
nenhuma funcionalidade especulativa "para o futuro" deve ser implementada antes de
ser explicitamente requisitada na especificação.

**Razão**: um app de uso pessoal de baixa complexidade não justifica overhead
arquitetural; cada camada extra é custo de manutenção sem benefício comprovado.

### II. Test-First (TDD, NÃO NEGOCIÁVEL)
Todo comportamento de negócio (adicionar livro, mudar status de leitura, avaliar,
buscar, gerar estatísticas) DEVE ter testes escritos antes da implementação,
seguindo o ciclo Red-Green-Refactor. Nenhum Pull Request pode ser mesclado com
testes falhando ou com cobertura de regras de negócio reduzida. Testes de
contrato/CLI (entrada → saída esperada) são obrigatórios para cada comando novo
ou alterado.

**Razão**: é a única garantia de que o comportamento documentado na especificação
continua válido conforme o código evolui, especialmente em um projeto mantido por
uma única pessoa sem revisão de pares constante.

### III. Consistência de Experiência na CLI
Todos os comandos DEVEM seguir convenções previsíveis: verbos no infinitivo
(`add`, `list`, `update`, `remove`, `stats`), mensagens de erro claras e
acionáveis (nunca apenas stack traces), códigos de saída consistentes (`0` sucesso,
`!=0` erro), e textos de ajuda (`--help`) completos para cada comando. Mudanças que
quebrem a compatibilidade de um comando existente (nome, flags, formato de saída)
exigem justificativa explícita e atualização da documentação de uso.

**Razão**: previsibilidade reduz a carga cognitiva de quem usa a ferramenta no
dia a dia e evita scripts/automação do usuário quebrarem silenciosamente.

### IV. Dados Locais e Privacidade
ReadTrack NÃO DEVE depender de serviços externos, contas, autenticação ou rede
para operar. Todos os dados (livros, status, notas, avaliações) são armazenados
localmente (arquivo SQLite ou JSON no diretório do usuário). Nenhuma telemetria
ou coleta de dados é permitida. Importação/exportação de dados (ex.: JSON, CSV)
DEVE ser suportada para que o usuário nunca fique preso ao formato interno.

**Razão**: é uma ferramenta pessoal de produtividade; dependências de rede ou
serviços de terceiros introduzem pontos de falha e riscos de privacidade
desproporcionais ao valor entregue.

### V. Performance Instantânea
Qualquer comando DEVE responder em menos de 200ms para acervos de até 10.000
livros em hardware comum, já que é uma ferramenta de uso interativo no terminal.
Otimizações prematuras são desencorajadas (Princípio I), mas qualquer escolha de
estrutura de dados ou índice DEVE ser justificada quando o acervo de testes
ultrapassar esse limite de performance.

**Razão**: ferramentas de CLI que "travam" perceptivelmente quebram o fluxo de
uso e fazem o usuário abandonar a ferramenta.

## Qualidade de Código

- Código Python deve seguir PEP 8 e ser formatado com uma ferramenta automática
  (ex.: `black`/`ruff format`); lint (`ruff`) deve passar sem erros antes do merge.
- Funções e módulos devem ter responsabilidade única; lógica de domínio (regras de
  status de leitura, validações) deve ser separada da camada de CLI (parsing de
  argumentos e formatação de saída).
- Type hints são obrigatórios em funções públicas/de domínio.
- Dependências externas (bibliotecas de terceiros) só podem ser adicionadas se
  resolverem um problema não trivial coberto pela biblioteca padrão do Python;
  cada nova dependência deve ser justificada no `plan.md` da feature.

## Fluxo de Desenvolvimento e Quality Gates

- Toda feature nasce de uma especificação (`/speckit.specify`) e um plano
  (`/speckit.plan`) antes de qualquer código ser escrito.
- `/speckit.tasks` deve gerar tarefas com testes antes da implementação
  correspondente (ordem test-first).
- Nenhuma tarefa de implementação é considerada concluída sem os testes
  associados passando localmente (`pytest`).
- Mudanças na constituição exigem nova versão e devem ser propagadas para
  `plan-template.md`, `spec-template.md` e `tasks-template.md` quando afetarem
  os gates ali descritos.

## Governance

Esta constituição tem precedência sobre qualquer outra prática, convenção ou
preferência individual de implementação. Qualquer plano técnico (`plan.md`) que
viole um princípio aqui definido DEVE registrar a violação explicitamente na
seção "Complexity Tracking" do plano, com justificativa, ou ser redesenhado para
estar em conformidade.

**Processo de emenda**: alterações a esta constituição são feitas via
`/speckit.constitution`, exigem descrição da motivação da mudança, e seguem
versionamento semântico:
- **MAJOR**: remoção ou redefinição incompatível de um princípio existente.
- **MINOR**: adição de novo princípio ou expansão material de uma seção.
- **PATCH**: correções de redação, clarificações sem mudança de regra.

Toda emenda deve incluir um "Sync Impact Report" (comentário HTML no topo deste
arquivo) listando o que mudou e quais templates dependentes foram revisados.

**Version**: 1.0.0 | **Ratified**: 2026-06-21 | **Last Amended**: 2026-06-21
