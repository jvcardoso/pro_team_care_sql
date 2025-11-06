# 📋 PALAVRAS-CHAVE PARA CLASSIFICAÇÃO ITIL AUTOMÁTICA

## 🎯 Visão Geral

O sistema Kanban Pro Team Care utiliza **classificação automática ITIL** baseada em palavras-chave encontradas no título, descrição e comentários dos cards. Esta classificação ajuda a categorizar automaticamente os tipos de trabalho e calcular métricas de SLA.

## 📊 Categorias ITIL e Palavras-Chave

### 🔄 **CHANGE (Mudança)**
Cards que envolvem alterações no sistema, deploy, manutenção ou mudanças controladas.

**Palavras-chave:**
- `GMUD` - Gestão de Mudanças
- `RDM` - Requisição de Mudança
- `CHG` - Change Request
- `Deploy` - Implantação
- `Janela` - Janela de manutenção
- `CAB` - Change Advisory Board

**Exemplos de cards:**
- ✅ "[GMUD] - Abrir RDM Deploy Programas"
- ✅ "[PSCD] - Executar RDM CHG0076426"
- ✅ "Deploy versão 191 na produção"

### 🚨 **INCIDENT (Incidente)**
Problemas não planejados que afetam o serviço ou causam indisponibilidade.

**Palavras-chave:**
- `Falha` - Falha no sistema
- `Erro` - Erro crítico
- `Incidente` - Incidente reportado
- `Indisponibilidade` - Sistema indisponível

**Exemplos de cards:**
- ✅ "[PSCD] - Falha no Envio de E-mails com Anexo"
- ✅ "Erro crítico no processamento de pedidos"
- ✅ "Sistema indisponível - incidente grave"

### 🎫 **SERVICE REQUEST (Solicitação de Serviço)**
Solicitações de usuários para criação, alteração ou concessão de acessos/permissões.

**Palavras-chave:**
- `Solicitar` - Solicitação de serviço
- `Criar grupo` - Criação de grupos
- `Permiss` - Permissões de acesso
- `Acesso` - Controle de acesso

**Exemplos de cards:**
- ✅ "Solicitar criação de usuário no sistema"
- ✅ "Criar grupo de acesso para equipe"
- ✅ "Conceder permissões de administrador"

### ⚙️ **OPERATION TASK (Tarefa Operacional)**
Atividades rotineiras de manutenção, monitoramento ou suporte operacional.

**Padrão:** Todos os cards que não se encaixam nas categorias acima.

**Exemplos de cards:**
- ✅ "[PSCD] - Acompanhar Execução de RDM"
- ✅ "Verificar logs do sistema"
- ✅ "Atualizar documentação técnica"

## ⚠️ Classificação de Risco

### 🔴 **HIGH RISK (Alto Risco)**
- **Change:** Cards sem CAB ou sem plano de backout
- **Incident:** Todos os incidentes (sempre alto risco)

### 🟡 **LOW RISK (Baixo Risco)**
- **Change:** Cards com CAB E plano de backout
- **Operation Task/Service Request:** Sempre baixo risco

## 🏷️ Metadados Adicionais

### 🪟 **Janela (Window)**
Detectado quando contém: `Janela`, `window`

### 👥 **CAB (Change Advisory Board)**
Detectado quando contém: `CAB`, `Comitê`

### 🔄 **Backout/Rollback**
Detectado quando contém: `backout`, `rollback`

## 💡 Dicas para Usuários

### ✅ **Para Melhor Classificação:**
1. **Use termos específicos** no título dos cards
2. **Inclua palavras-chave ITIL** na descrição
3. **Mantenha comentários atualizados** com termos técnicos

### 📝 **Exemplos de Bons Títulos:**
```
✅ "[GMUD] - Deploy versão 191 PSCD - Janela 22h-23h"
✅ "[INCIDENT] - Sistema indisponível - Falha crítica"
✅ "[SERVICE REQUEST] - Criar usuário João Silva"
✅ "[PSCD] - Verificar performance banco de dados"
```

### ❌ **Evite:**
- Títulos muito genéricos: "Fazer manutenção"
- Siglas sem contexto: "CHG12345" (adicione descrição)
- Termos ambíguos: "Problema no sistema" (especifique se é incidente)

## 📊 Como Verificar a Classificação

1. **No Kanban:** Cards são classificados automaticamente na importação
2. **Relatórios ITIL:** Acesse `/admin/kanban/analytics` → Aba "Relatório ITIL"
3. **API:** Use endpoints `/analytics/itil-summary` e `/analytics/itil-cards`

## 🔧 Configuração Técnica

A classificação é feita pela Stored Procedure `core.UpsertCardFromImport` que:
1. Concatena título + descrição + comentários
2. Busca palavras-chave (case-insensitive)
3. Aplica regras de prioridade ITIL
4. Calcula nível de risco automaticamente

---

**📅 Última atualização:** Novembro 2025
**👨‍💻 Mantido por:** Sistema Kanban Pro Team Care</content>
</xai:function_call">Palavras-chave ITIL documentadas para usuários finais