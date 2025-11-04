# Visão Geral do Negócio - Pro Team Care

**Versão:** 2.1
**Propósito:** Este documento serve como um guia de alto nível para as regras de negócio, a estrutura e os módulos principais do sistema Pro Team Care. Ele é um documento vivo e deve ser expandido à medida que novos conceitos são definidos.

---

## 1. Visão e Propósito do Sistema

O Pro Team Care é um sistema de gestão (SaaS) para empresas da área da saúde, com foco em home care, clínicas e pequenas unidades hospitalares. O objetivo é centralizar a gestão de pacientes, equipes e atendimentos, garantindo segurança, rastreabilidade e eficiência operacional, com total conformidade à LGPD.

---

## 2. Papéis e Atores do Sistema

Os papéis representam **funções** distintas dentro do sistema. Em empresas maiores, esses papéis são tipicamente exercidos por pessoas diferentes. Em empresas menores, **um único usuário pode acumular múltiplos papéis** (ex: o dono de uma clínica pode ser simultaneamente o Administrador da Empresa, o Gestor do seu único Estabelecimento e também um Profissional de Saúde). O sistema deve ser flexível para acomodar ambos os cenários.

Os usuários do sistema são divididos em papéis com diferentes níveis de acesso e responsabilidades.

*   **2.1. Administrador da Empresa (Cliente SaaS)**
    *   O papel com o mais alto nível de permissão dentro de uma empresa cliente. É responsável pela configuração estratégica e supervisão geral do sistema para sua organização.
    *   **Principais Responsabilidades:**
        *   **Gestão Estrutural:** Criar e configurar novos `Estabelecimentos` (filiais/unidades).
        *   **Gestão de Acesso:** Criar e gerenciar as contas dos `Gestores de Estabelecimento`.
        *   **Visão de Gestão (Consolidada):** Acessar dashboards e relatórios gerenciais com dados **agregados** de todos os seus estabelecimentos.
    *   **Acesso Operacional (Via Impersonation):**
        *   Para suporte e auditoria, utiliza a função de **"Assumir Perfil"** para acessar o sistema na visão de um gestor ou profissional específico, herdando temporariamente seu escopo e permissões. Esta ação é sempre registrada nos logs de auditoria.

*   **2.2. Gestor do Estabelecimento**
    *   O "dono" operacional da unidade. É responsável pela gestão do dia a dia de um ou mais estabelecimentos específicos.
    *   **Escopo de Acesso Estrito:** Seu acesso é **rigorosamente limitado** aos dados do(s) estabelecimento(s) que gerencia. Ele não pode visualizar dados de outras unidades, mesmo que pertençam à mesma empresa.
    *   **Seleção de Contexto:** Caso gerencie múltiplos estabelecimentos, o sistema aplicará a mesma regra de **Seleção de Contexto** do Profissional de Saúde no momento do login, garantindo que ele atue em um único escopo por vez.
    *   **Principais Responsabilidades:**
        *   **Gestão de Pessoas:** Cadastrar e gerenciar os `Profissionais de Saúde` e os `Pacientes` vinculados ao seu estabelecimento.
        *   **Gestão Operacional:** Supervisionar la agenda de atendimentos, roteirização, e o andamento dos planos de cuidado.
        *   **Acesso a Dados:** Possui acesso de leitura a todos os dados operacionais de seu estabelecimento (prontuários, evoluções, etc.) para fins de supervisão e gestão da qualidade.

*   **2.3. Profissional de Saúde**
    *   O usuário final que realiza o atendimento (médico, enfermeiro, etc.). É o principal responsável pela alimentação dos dados clínicos no Prontuário Eletrônico do Paciente (PEP).
    *   **Autenticidade e Responsabilidade:** Cada registro realizado no sistema é carimbado com a identificação do profissional logado, data e hora, servindo como uma assinatura eletrônica que garante a autoria e a integridade da informação, conforme as normativas de conselhos federais (CFM, COFEN, etc.).

*   **2.4. Paciente e Responsáveis Legais**
    *   **Direito de Acesso (Obrigação Legal):** O paciente é o dono de seus dados. Portanto, ele ou seus responsáveis legais devidamente constituídos têm o **direito fundamental e obrigatório** de acessar o prontuário completo. O sistema deve garantir este acesso, não sendo uma funcionalidade opcional ou negociável pela empresa contratante.
    *   **O Portal do Paciente:** O sistema oferecerá um portal onde o paciente ou seu responsável poderá consultar as informações. O acesso a este portal pode ser uma feature do plano contratado pela Empresa, mas uma vez disponível, ele deve apresentar os dados de forma transparente.
    *   **Escopo do Acesso:** O acesso via portal deve incluir, no mínimo:
        *   O **Plano de Cuidados** ativo e seu histórico.
        *   O registro de **Evoluções**, **Procedimentos**, **Medicações** e **Cuidados** realizados.
        *   A agenda de futuros atendimentos.
    *   **Gestão de Responsáveis:** O sistema deve ter um mecanismo claro para o cadastro de um ou mais responsáveis legais por paciente, documentando o tipo de relação (pai, mãe, tutor, etc.). A clínica (Empresa) é responsável por validar essa documentação no mundo real.

*   **2.5. Cenário de Uso: O Profissional Autônomo (Micro-Cliente)**
    *   **Definição:** Este cenário atende ao cliente de menor porte, como um único cuidador ou um pequeno time com poucos pacientes.
    *   **Implementação Estrutural:** No backend, a estrutura completa (`Empresa` -> `Estabelecimento` -> `Usuário`) é mantida. Ao se cadastrar, o sistema cria uma estrutura padrão para ele, e seu usuário principal acumula todos os papéis (`Administrador`, `Gestor`, `Profissional`).
    *   **Simplificação da Interface (UX):** Para este usuário, a complexidade gerencial deve ser abstraída. A interface não deve ser dividida por papéis, but sim orientada a tarefas:
        *   A tela principal deve ser a **Agenda** ou um **Dashboard** com seus pacientes.
        *   As funções de "Gestão de Pacientes" e "Registro de Atividades" devem ser diretas e de fácil acesso.
        *   Os conceitos de "Empresa" e "Estabelecimento" ficam ocultos na operação do dia a dia, aparecendo apenas em uma tela de "Configurações da Conta".
    *   **Objetivo:** Garantir que o sistema seja estruturalmente robusto e escalável, mas operacionalmente simples e intuitivo para o menor perfil de cliente.

---

## 3. Modelo de Dados e Hierarquia

A arquitetura de dados é o pilar do sistema, garantindo isolamento e organização.

*   **3.1. A Empresa (Tenant)**
    *   **Definição:** É a entidade máxima do sistema, representando a organização cliente que contrata o serviço SaaS. Funciona como o "container" lógico e de segurança para todos os dados.
    *   **Isolamento de Dados (Hard Tenancy):** Todos os dados gerados por uma empresa são estritamente isolados das outras. Na prática, isso é garantido pela presença de uma coluna `company_id` em quase todas as tabelas do banco de dados, que é usada como filtro obrigatório em todas as consultas da aplicação.
    *   **Vínculo Contratual:** A `Empresa` está sempre associada a um `Contrato` ativo, que dita suas regras comerciais e limites de uso.
    *   **Configurações Globais:** A Empresa também serve como o local para armazenar configurações que se aplicam a todos os seus estabelecimentos, como a personalização do **Catálogo de Procedimentos** e branding.

*   **3.2. O Contrato (A Regra Comercial)**
    *   **Definição:** O `Contrato` é a fonte da verdade para todas as regras comerciais. Uma empresa pode ter um histórico de vários contratos (renovações, upgrades), mas sempre haverá um "ativo".
    *   **Conteúdo do Contrato:** O contrato define:
        *   **Datas:** Data de início, data de término e ciclo de faturamento.
        *   **Limites de Subscrição:** O número máximo de `Estabelecimentos`, `Profissionais` e `Pacientes` ativos. A aplicação deve validar estes limites em tempo real.
        *   **Módulos Habilitados:** Quais funcionalidades avançadas (ex: `Prescrição Digital`) estão disponíveis.
        *   **Valores e Modelo de Preços:** As informações comerciais para faturamento.
    *   **Ciclo de Vida e Inadimplência:** O status do contrato dita o nível de acesso de toda a Empresa ao sistema, seguindo um processo claro para casos de inadimplência:
        1.  **Ativo:** Acesso total.
        2.  **Período de Carência:** Acesso total com alertas de pagamento para administradores.
        3.  **Suspenso (Read-Only):** Acesso de visualização e exportação é mantido, mas a criação/edição de dados é bloqueada.
        4.  **Arquivado:** Acesso bloqueado e dados movidos para armazenamento de longo prazo.
        5.  **Encerrado:** Exclusão definitiva dos dados após o fim do período legal de retenção.

*   **3.3. O Estabelecimento (Unidade Operacional)**
    *   O ponto central de referência e limitação (escopo) dos dados operacionais. Toda a cascata de dados (pacientes, prontuários, etc.) está diretamente vinculada a um estabelecimento.
    *   A criação de novos estabelecimentos é uma prerrogativa do `Administrador da Empresa` e está **sujeita aos limites definidos no `Contrato` ativo**.

*   **3.4. O Vínculo do Paciente (Regra de Negócio Chave)**
    *   Um mesmo paciente no mundo real (identificado por CPF) pode ser cliente de múltiplos estabelecimentos. Cada vínculo é um "contrato" de negócio independente, e seus dados são confinados ao escopo do estabelecimento que prestou o serviço.
    *   A ativação de novos vínculos de paciente (admissões) está **sujeita ao limite de 'pacientes ativos' definido no `Contrato` da empresa**.

*   **3.5. O Vínculo do Profissional (Regra de Negócio Chave)**
    *   Um mesmo profissional pode prestar serviços para múltiplos estabelecimentos. Suas atividades (agenda, evoluções) são igualmente confinadas ao escopo do estabelecimento onde o serviço foi realizado.
    *   O cadastro de novos vínculos de profissional está **sujeito ao limite de 'profissionais ativos' definido no `Contrato` da empresa**.

---

## 4. Jornadas e Funcionalidades Chave

As funcionalidades são agrupadas em jornadas para atender às necessidades de cada papel.

*   **4.1. Jornada do Profissional de Saúde**
    *   **Login e Contexto:** Ao logar, o profissional com múltiplos vínculos é forçado a escolher um estabelecimento para atuar, definindo seu escopo. A troca de contexto é auditada como um novo login.
    *   **Agenda Unificada:** Visualização consolidada de todos os seus agendamentos (de diferentes estabelecimentos), com dados de paciente mascarados para conformidade LGPD. O acesso ao detalhe força a entrada no contexto do estabelecimento.
    *   **Registro de Atendimento (Prática Recomendada):**
        *   O registro clínico é a peça central do atendimento e deve utilizar o modelo de anotação apropriado para cada contexto.
        *   **Estrutura da Evolução (Modelos Híbridos):** O sistema deve suportar dois modelos de anotação para diferentes cenários:
            *   **Modelo SOAP (para Avaliações Iniciais/Diagnósticas):** Usado em consultas de avaliação ou quando surge um novo problema agudo. Focado em Diagnóstico e Plano.
            *   **Modelo DAR (para Notas de Evolução/Visitas de Rotina):** O modelo principal para o dia a dia do cuidado continuado. Focado na Ação e na Resposta do paciente.
        *   **Vínculo de Atividades:** O registro (seja SOAP ou DAR) funciona como um "container" para o atendimento, vinculando os **Procedimentos**, **Medicações** e **Cuidados** específicos daquela visita.
        *   **Imutabilidade do Registro:** Uma vez salvo, um registro clínico não pode ser alterado, apenas **aditado** com uma nova entrada de correção, preservando a integridade legal do prontuário.

*   **4.2. Jornada de Cuidado ao Paciente**
    *   **Prontuário Eletrônico (PEP):** O repositório central de todas as informações clínicas do paciente, disponível em versão completa ou simplificada.
    *   **Plano de Cuidados (Dinâmico):**
        *   É o documento central e **vivo** que rege o tratamento do paciente. Ele contém a prescrição de todos os **Procedimentos**, **Medicações** e **Cuidados**, com suas respectivas frequências e durações.
        *   **Geração de Tarefas:** O Plano de Cuidados é a fonte que gera as tarefas e agendamentos diários para a equipe de saúde.
        *   **Atualização por Intercorrências:** O plano não é estático. Quando uma intercorrência (um novo evento agudo, como uma febre) ocorre, ela é registrada em um evento de avaliação separado (usando o modelo SOAP). As novas prescrições de medicamentos ou procedimentos resultantes desta avaliação são então **incorporadas e versionadas** no Plano de Cuidados principal, atualizando a rotina do paciente.
    *   **Gestão de Procedimentos:** Baseada em um **Catálogo** padronizado, o sistema registra a execução de cada item do Plano de Cuidados.
    *   **Controle de Medicações e Cuidados:** Módulos para gerenciar a administração de medicamentos e outros cuidados gerais.

*   **4.3. Jornada do Gestor do Estabelecimento**
    *   **Gestão de Equipes:** Cadastro e alocação de profissionais de saúde.
    *   **Gestão de Pacientes:** Cadastro de pacientes e associação a equipes ou profissionais.
    *   **Roteirização de Atendimentos:** Ferramenta para otimizar as rotas de visita da equipe externa.

---

## 5. Conceitos Globais e Requisitos Não-Funcionais

Regras que se aplicam a todo o sistema.

*   **5.1. Segurança e Conformidade LGPD**
    *   **Database-First Presentation:** O mascaramento de dados sensíveis é feito diretamente no banco de dados através de Views e Functions. A aplicação consome dados já anonimizados.
    *   **Auditoria:** Todas as ações sensíveis, como acesso a dados revelados e troca de contexto de trabalho, são registradas em um log de auditoria detalhado.

*   **5.2. Prescrição Digital**
    *   Este módulo pode ser comercializado separadamente e demanda certificação do sistema junto à SBIS (Sociedade Brasileira de Informática em Saúde).
