# 🧪 Plataforma de Testes Automatizados - Guia Completo

## 📋 Visão Geral

Esta plataforma implementa testes automatizados para o módulo de empresas, seguindo o fluxo completo de CRUD com validações LGPD, APIs externas e cenários de erro.

## 🎯 Fluxo de Testes Implementado

### 1. **Listagem Inicial** 
- ✅ GET `/api/v1/companies`
- ✅ Validação de estrutura de resposta
- ✅ Contagem inicial de empresas

### 2. **Inclusão de Nova Empresa**
- ✅ **2.1** - Consulta CNPJ via API externa
- ✅ **2.2** - Preenchimento automático + dados fictícios
- ✅ **2.3** - Salvamento da empresa
- ✅ **2.4** - Geocodificação automática

### 3. **Validação na Lista**
- ✅ Verificação se empresa aparece na listagem
- ✅ Validação de incremento na contagem

### 4. **Consulta Detalhada e LGPD**
- ✅ **4.1** - Validação de dados cadastrais
- ✅ **4.2** - Verificação de mascaramento LGPD
- ✅ **4.3** - Revelação de dados sensíveis
- ✅ **4.4** - Validação de logs LGPD

### 5. **Alteração de Cadastro**
- ✅ Atualização de campos não-chave
- ✅ Proteção de campos críticos (CNPJ)

### 6. **Validação de Alterações**
- ✅ Verificação na listagem após update

### 7. **Inativação/Ativação**
- ✅ Inativação de empresa
- ✅ Validação de filtros de status
- ✅ Reativação de empresa

## 🔧 Configuração do Ambiente

### Pré-requisitos
```bash
# 1. Python 3.8+
# 2. SQL Server com bancos de teste
# 3. Dependências instaladas
pip install pytest pytest-asyncio httpx pytest-cov
```

### Variáveis de Ambiente
```bash
export TEST_DATABASE_URL="mssql+pyodbc://sa:SuaSenha@IP_SERVIDOR/pro_team_care_test?driver=ODBC+Driver+17+for+SQL+Server&timeout=30"
export TEST_ADMIN_EMAIL="admin@proteancare.com"
export TEST_ADMIN_PASSWORD="admin123"
```

## 🚀 Execução dos Testes

### Método 1: Script Automatizado (Recomendado)
```bash
cd /home/juliano/Projetos/meu_projeto/backend
python tests/setup_test_environment.py
```

### Método 2: Execução Manual
```bash
# Fluxo completo
pytest tests/api/test_company_complete_flow.py -v -s

# Testes específicos
pytest tests/api/test_auth.py -v
pytest tests/api/test_company*.py -v --tb=short
```

## 📊 Interpretação dos Resultados

### Taxa de Sucesso
- **≥ 80%**: 🎉 Plataforma viável - Excelente
- **60-79%**: ⚠️ Parcialmente viável - Ajustes necessários  
- **< 60%**: 🚨 Não viável - Correções críticas

### Relatórios Gerados
- **Console**: Resumo executivo em tempo real
- **JSON**: Relatório detalhado em `test_report_YYYYMMDD_HHMMSS.json`

## 🔍 Principais Correções Implementadas

### 1. **Conexão com Banco**
- ✅ Configuração para banco remoto
- ✅ Timeout otimizado (30s)
- ✅ Pool de conexões configurado

### 2. **Loop de Eventos**
- ✅ Fixture de sessão para event loop
- ✅ Cliente assíncrono otimizado
- ✅ Gerenciamento correto de recursos

### 3. **CNPJs Válidos**
- ✅ Lista de CNPJs testados e válidos
- ✅ Dados realistas por região
- ✅ Mocks configurados corretamente

### 4. **Autenticação**
- ✅ Login real com credenciais válidas
- ✅ Token de sessão reutilizado
- ✅ Headers padronizados

## 🎯 Cenários de Teste Cobertos

### ✅ Casos de Sucesso
- Fluxo completo CRUD
- Consultas com dados válidos
- Mascaramento/revelação LGPD
- Filtros e paginação

### ✅ Casos de Erro
- CNPJs inválidos
- Empresas inexistentes
- Dados incompletos
- Permissões insuficientes

### ✅ Casos Limite
- Timeouts de API
- Falhas de geocodificação
- Dados parciais

## 🔧 Troubleshooting

### Erro: "Login timeout expired"
```bash
# Verificar conectividade
telnet IP_SERVIDOR 1433

# Testar credenciais
sqlcmd -S IP_SERVIDOR -U sa -P SuaSenha -Q "SELECT 1"
```

### Erro: "Event loop is closed"
```bash
# Usar o conftest_fixed.py
cp tests/conftest_fixed.py tests/conftest.py
```

### Erro: "CNPJ inválido"
```bash
# Usar apenas CNPJs da lista validada
# Ver VALID_TEST_CNPJS em conftest.py
```

## 📈 Métricas de Qualidade

### Cobertura Esperada
- **Endpoints**: 100% dos endpoints CRUD
- **Cenários**: 90% dos casos de uso
- **Erros**: 80% dos cenários de falha

### Performance
- **Tempo por teste**: < 30s
- **Tempo total**: < 5min
- **Paralelização**: Suportada

## 🔄 Integração Contínua

### GitHub Actions (Futuro)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: python tests/setup_test_environment.py
```

## 📞 Suporte

### Em caso de problemas:
1. **Verificar logs**: `test_report_*.json`
2. **Validar ambiente**: Variáveis e conectividade
3. **Executar individualmente**: Isolar problemas
4. **Consultar documentação**: Este README

---

**Última atualização**: 2025-10-28  
**Versão**: 1.0  
**Autor**: Sistema de Testes Automatizados
