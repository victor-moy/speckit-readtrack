# Feature Specification: ReadTrack Core

**Feature Branch**: `001-readtrack-core`

**Created**: 2026-06-21

**Status**: Draft

**Input**: User description: "Construir o ReadTrack, uma aplicação de linha de comando pessoal para controlar os livros que estou lendo. Quero poder cadastrar livros com título e autor, marcá-los como 'quero ler', 'lendo' ou 'lido', avaliar com 1 a 5 estrelas os livros que terminei, adicionar notas pessoais, listar/filtrar/buscar minha coleção, e ver estatísticas simples sobre meus hábitos de leitura (total de livros lidos, livros lidos neste ano, nota média). Todos os dados devem ficar armazenados localmente, sem dependência de rede."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cadastrar e listar livros (Priority: P1)

Como leitor, quero adicionar um livro à minha coleção informando título e autor, e
ver a lista de todos os livros cadastrados, para começar a organizar minha leitura
em um único lugar.

**Why this priority**: É a funcionalidade mínima sem a qual nenhuma outra parte do
sistema tem dados para operar. Sem isso não há produto.

**Independent Test**: Pode ser testado isoladamente executando o comando de
cadastro e em seguida o comando de listagem, confirmando que o livro cadastrado
aparece na saída.

**Acceptance Scenarios**:

1. **Given** a coleção está vazia, **When** o usuário cadastra um livro com título
   e autor, **Then** o livro passa a existir com status padrão "quero ler" e é
   exibido na listagem.
2. **Given** existem livros cadastrados, **When** o usuário lista a coleção,
   **Then** todos os livros são exibidos com título, autor e status atuais.
3. **Given** o usuário tenta cadastrar um livro sem título, **When** o comando é
   executado, **Then** o sistema rejeita a operação com uma mensagem de erro clara
   e nenhum livro é criado.

---

### User Story 2 - Atualizar o status de leitura (Priority: P2)

Como leitor, quero mudar o status de um livro entre "quero ler", "lendo" e "lido",
para refletir o progresso real da minha leitura ao longo do tempo.

**Why this priority**: É o que transforma uma lista estática em um rastreador de
leitura; depende apenas da User Story 1 já existir.

**Independent Test**: Pode ser testado cadastrando um livro e em seguida alterando
seu status, confirmando que a listagem reflete o novo status e a data de transição
correspondente (ex.: data de início de leitura, data de conclusão).

**Acceptance Scenarios**:

1. **Given** um livro com status "quero ler", **When** o usuário marca o livro como
   "lendo", **Then** o status é atualizado e a data de início de leitura é
   registrada.
2. **Given** um livro com status "lendo", **When** o usuário marca o livro como
   "lido", **Then** o status é atualizado e a data de conclusão é registrada.
3. **Given** um identificador de livro inexistente, **When** o usuário tenta
   atualizar seu status, **Then** o sistema retorna um erro claro informando que o
   livro não foi encontrado.

---

### User Story 3 - Avaliar e anotar livros lidos (Priority: P3)

Como leitor, quero atribuir uma nota de 1 a 5 estrelas e escrever notas pessoais
sobre um livro que já terminei, para registrar minhas impressões e poder consultá-
-las depois.

**Why this priority**: Agrega valor qualitativo à coleção, mas só faz sentido após
o livro existir e estar marcado como lido (depende das Stories 1 e 2).

**Independent Test**: Pode ser testado marcando um livro como "lido" e em seguida
atribuindo uma nota e uma nota pessoal, confirmando que ambos aparecem nos detalhes
do livro.

**Acceptance Scenarios**:

1. **Given** um livro com status "lido", **When** o usuário atribui uma nota de 1 a
   5, **Then** a nota é salva e exibida nos detalhes do livro.
2. **Given** um livro com status "quero ler" ou "lendo", **When** o usuário tenta
   atribuir uma nota, **Then** o sistema impede a ação e explica que apenas livros
   "lidos" podem ser avaliados.
3. **Given** um livro qualquer, **When** o usuário adiciona uma nota pessoal em
   texto livre, **Then** a nota é salva e pode ser lida posteriormente nos detalhes
   do livro.

---

### User Story 4 - Buscar, filtrar e ver estatísticas (Priority: P4)

Como leitor, quero buscar livros por título/autor, filtrar minha coleção por
status, e ver estatísticas simples (total lidos, lidos neste ano, nota média),
para entender meus hábitos de leitura ao longo do tempo.

**Why this priority**: É um refinamento de produtividade sobre uma coleção que já
tem dados reais; tem o menor impacto se ausente no MVP, mas agrega valor analítico.

**Independent Test**: Pode ser testado com uma coleção povoada por livros em
diferentes status e notas, executando os comandos de busca, filtro e estatísticas
isoladamente e validando os resultados contra os dados esperados.

**Acceptance Scenarios**:

1. **Given** uma coleção com múltiplos livros, **When** o usuário busca por um
   termo presente no título ou autor, **Then** apenas os livros correspondentes são
   exibidos.
2. **Given** uma coleção com livros em status variados, **When** o usuário filtra
   por um status específico, **Then** apenas livros naquele status são exibidos.
3. **Given** uma coleção com livros lidos em anos diferentes e com notas
   atribuídas, **When** o usuário solicita as estatísticas, **Then** o sistema
   exibe corretamente o total de livros lidos, quantos foram lidos no ano atual, e
   a nota média entre os livros avaliados.

---

### User Story 5 - Backup e restauração de dados (Priority: P5)

Como leitor, quero exportar minha coleção inteira para um arquivo e poder
restaurá-la a partir desse arquivo, para não ficar preso ao formato interno de
armazenamento e poder recuperar meus dados em caso de perda ou troca de máquina.

**Why this priority**: É uma rede de segurança sobre dados que já existem; não
bloqueia o uso diário da ferramenta (Stories 1-4), por isso tem a prioridade mais
baixa, mas é exigida pelo princípio de privacidade/portabilidade de dados do
projeto.

**Independent Test**: Pode ser testado populando uma coleção, exportando para um
arquivo, apagando a base local e importando o arquivo de volta, confirmando que
todos os livros e seus dados retornam idênticos.

**Acceptance Scenarios**:

1. **Given** uma coleção com um ou mais livros, **When** o usuário exporta a
   coleção, **Then** um arquivo é gerado contendo todos os livros com todos os
   seus campos.
2. **Given** um arquivo previamente exportado, **When** o usuário importa esse
   arquivo em uma base vazia, **Then** todos os livros são restaurados com os
   mesmos identificadores, status, datas, nota e nota pessoal.
3. **Given** um arquivo de importação inexistente ou malformado, **When** o
   usuário tenta importar, **Then** o sistema rejeita a operação com uma mensagem
   de erro clara, sem alterar a base local existente.

---

### Edge Cases

- O que acontece se o usuário tentar cadastrar dois livros com título e autor
  idênticos? (Permitido — podem existir edições/cópias diferentes; cada cadastro
  recebe um identificador próprio.)
- Como o sistema se comporta ao calcular a nota média quando nenhum livro lido
  possui avaliação ainda? (Deve indicar "sem avaliações" em vez de erro ou divisão
  por zero.)
- O que acontece se o usuário tentar marcar um livro como "lido" diretamente a
  partir de "quero ler" (sem passar por "lendo")? (Permitido — a transição de
  status é livre entre os três estados; apenas as datas correspondentes ao novo
  estado são preenchidas.)
- Como o sistema se comporta se o arquivo de dados local estiver corrompido ou
  ilegível na inicialização? (Deve falhar com uma mensagem clara orientando o
  usuário, em vez de apagar ou sobrescrever os dados silenciosamente.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir cadastrar um livro informando, no mínimo,
  título e autor.
- **FR-002**: O sistema DEVE atribuir a todo livro cadastrado um identificador
  único e um status inicial de "quero ler".
- **FR-003**: O sistema DEVE rejeitar o cadastro de um livro sem título, exibindo
  uma mensagem de erro acionável.
- **FR-004**: O sistema DEVE permitir listar todos os livros cadastrados com seus
  respectivos título, autor e status.
- **FR-005**: O sistema DEVE permitir atualizar o status de um livro entre "quero
  ler", "lendo" e "lido".
- **FR-006**: O sistema DEVE registrar a data em que um livro passa a "lendo"
  (início de leitura) e a data em que passa a "lido" (conclusão).
- **FR-007**: O sistema DEVE retornar um erro claro ao tentar atualizar, avaliar ou
  remover um livro com identificador inexistente.
- **FR-008**: O sistema DEVE permitir atribuir uma nota de 1 a 5 estrelas a um
  livro, exclusivamente quando esse livro estiver no status "lido".
- **FR-009**: O sistema DEVE permitir adicionar e editar uma nota pessoal em texto
  livre a qualquer livro, independentemente do status.
- **FR-010**: O sistema DEVE permitir buscar livros por substring (sem diferenciar
  maiúsculas/minúsculas) presente no título ou no autor.
- **FR-011**: O sistema DEVE permitir filtrar a listagem de livros por status.
- **FR-012**: O sistema DEVE calcular e exibir estatísticas de leitura: total de
  livros lidos, total de livros lidos no ano corrente, e nota média entre os livros
  avaliados (exibindo "sem avaliações" quando não houver nenhuma).
- **FR-013**: O sistema DEVE permitir remover um livro da coleção.
- **FR-014**: O sistema DEVE persistir todos os dados localmente, sem depender de
  rede, conta de usuário ou serviço externo.
- **FR-015**: O sistema DEVE preservar os dados existentes entre execuções
  (persistência), permitindo que o usuário encerre e reabra a aplicação sem perda
  de informação.
- **FR-016**: O sistema DEVE permitir exportar toda a coleção para um arquivo JSON
  legível por humanos, contendo todos os campos de cada livro, para que o usuário
  nunca fique preso ao formato interno de armazenamento.
- **FR-017**: O sistema DEVE permitir restaurar uma coleção a partir de um arquivo
  previamente exportado (backup/restore), preservando identificadores, status,
  datas, notas e avaliações.

### Key Entities *(include if feature involves data)*

- **Book (Livro)**: Representa um item da coleção. Atributos: identificador único,
  título, autor, status de leitura (quero ler / lendo / lido), data de início de
  leitura (opcional), data de conclusão (opcional), nota de 1 a 5 (opcional, apenas
  quando lido), nota pessoal em texto livre (opcional), data de cadastro.
- **ReadingStatus (Status de Leitura)**: Enumeração fechada com os valores "quero
  ler", "lendo" e "lido", que determina quais ações (avaliar, registrar datas) são
  permitidas sobre um livro.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um usuário consegue cadastrar um novo livro e vê-lo refletido na
  listagem em menos de 10 segundos de interação (incluindo digitação do comando).
- **SC-002**: 100% das tentativas de atribuir nota a um livro que não esteja "lido"
  são bloqueadas com mensagem explicativa, sem exceção não tratada.
- **SC-003**: Para uma coleção de até 10.000 livros, qualquer comando de listagem,
  busca, filtro ou estatística retorna resultado percebido como instantâneo pelo
  usuário (sem espera perceptível no terminal).
- **SC-004**: Um usuário consegue encontrar um livro específico por busca de
  título/autor em uma única tentativa de comando, sem precisar saber o
  identificador interno do livro.
- **SC-005**: As estatísticas de leitura exibidas (total lido, lido no ano, nota
  média) correspondem exatamente ao estado real da coleção em 100% dos casos
  testados, incluindo o caso de coleção sem nenhuma avaliação.
- **SC-006**: Após encerrar e reabrir a aplicação, 100% dos livros e seus dados
  (status, notas, avaliações) cadastrados anteriormente continuam disponíveis.
- **SC-007**: Um usuário consegue exportar a coleção inteira e restaurá-la em uma
  instalação nova do ReadTrack sem perda de nenhum dado (título, autor, status,
  datas, nota e nota pessoal).

## Assumptions

- A aplicação é de uso pessoal e single-user; não há conceito de múltiplas contas,
  permissões ou compartilhamento de coleção entre pessoas nesta fase.
- O usuário interage exclusivamente via terminal (linha de comando); não há
  interface gráfica nesta fase.
- "Ano corrente" para fins estatísticos é definido pela data do sistema operacional
  em que o ReadTrack é executado.
- Identificadores de livros podem ser apresentados ao usuário em formato curto e
  legível (não é necessário expor UUIDs longos na interação cotidiana), desde que
  sejam estáveis e únicos por livro.
- Não há requisito de importação de catálogos externos (ex.: ISBN, APIs de livros)
  nesta fase; o cadastro é manual. O requisito de import/export (FR-016, FR-017)
  cobre apenas backup/restore do próprio formato do ReadTrack, não integração com
  catálogos de terceiros.
