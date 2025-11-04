#!/bin/bash
# Script de migração automática do frontend completo

echo "=========================================="
echo "  MIGRAÇÃO DE FRONTEND COMPLETO"
echo "=========================================="
echo ""

PROJECT_DIR="/home/juliano/Projetos/meu_projeto"
SOURCE_DIR="/home/juliano/Projetos/pro_team_care_16/frontend"

# Verificar se diretório fonte existe
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Erro: Diretório fonte não encontrado: $SOURCE_DIR"
    exit 1
fi

# 1. Backup do frontend atual
echo "📦 Passo 1/5: Fazendo backup do frontend atual..."
cd "$PROJECT_DIR"
if [ -d "frontend" ]; then
    BACKUP_NAME="frontend_backup_$(date +%Y%m%d_%H%M%S)"
    mv frontend "$BACKUP_NAME"
    echo "✅ Backup criado: $BACKUP_NAME"
else
    echo "⚠️  Nenhum frontend anterior encontrado"
fi
echo ""

# 2. Copiar frontend completo
echo "📋 Passo 2/5: Copiando frontend completo..."
cp -r "$SOURCE_DIR" "$PROJECT_DIR/"
echo "✅ Frontend copiado (30+ páginas, componentes, testes)"
echo ""

# 3. Ajustar .env
echo "🔧 Passo 3/5: Configurando .env..."
cd "$PROJECT_DIR/frontend"
cat > .env << 'EOF'
# API Backend
VITE_API_BASE_URL=http://192.168.11.83:8000/api/v1

# Ambiente
VITE_ENV=development
EOF
echo "✅ .env configurado com backend: http://192.168.11.83:8000"
echo ""

# 4. Limpar e preparar
echo "🧹 Passo 4/5: Limpando instalação anterior..."
rm -rf node_modules package-lock.json dist build
echo "✅ Limpeza concluída"
echo ""

# 5. Instalar dependências
echo "📦 Passo 5/5: Instalando dependências..."
echo "   (Isso pode levar alguns minutos...)"
npm install --silent
if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi
echo ""

echo "=========================================="
echo "  ✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=========================================="
echo ""
echo "📊 O que foi migrado:"
echo "   ✅ 30+ páginas completas"
echo "   ✅ Sistema de componentes robusto"
echo "   ✅ React Hook Form + Zod"
echo "   ✅ React Query (cache de dados)"
echo "   ✅ React Hot Toast (notificações)"
echo "   ✅ Lucide React (ícones)"
echo "   ✅ Charts (gráficos)"
echo "   ✅ Testes E2E (Playwright)"
echo "   ✅ Testes unitários (Jest)"
echo "   ✅ LGPD compliance"
echo ""
echo "⚠️  AJUSTES NECESSÁRIOS:"
echo ""
echo "1. Verificar campo de login (email_address):"
echo "   cd $PROJECT_DIR/frontend"
echo "   grep -r 'email:' src/services/ src/pages/Login*"
echo ""
echo "2. Se encontrar 'email:', mudar para 'email_address:'"
echo ""
echo "3. Iniciar frontend:"
echo "   cd $PROJECT_DIR/frontend"
echo "   npm run dev"
echo ""
echo "4. Testar login:"
echo "   URL: http://192.168.11.83:3000/login"
echo "   Email: admin@proteamcare.com.br"
echo "   Senha: admin123"
echo ""
echo "=========================================="
echo "🚀 Pronto para iniciar!"
echo "=========================================="
