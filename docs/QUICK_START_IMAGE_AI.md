# 🚀 Quick Start: IA para Descrição de Imagens

## ⚡ Configuração Rápida (5 minutos)

### 1️⃣ Obter API Key (2 minutos)

1. Acesse: https://aistudio.google.com
2. Faça login com Google
3. Clique em **"Get API key"**
4. Copie a chave gerada

### 2️⃣ Configurar Backend (1 minuto)

Edite `.env` no backend:

```bash
# Adicione ou atualize:
GOOGLE_GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 3️⃣ Reiniciar Servidor (1 minuto)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4️⃣ Testar (1 minuto)

```bash
# Verificar se está ativo:
curl http://localhost:8000/api/v1/image-analysis/status \
  -H "Authorization: Bearer SEU_TOKEN"

# Deve retornar:
{
  "enabled": true,
  "model": "gemini-2.5-flash",
  "message": "Serviço ativo"
}
```

---

## 🎨 Como Usar (Já Integrado!)

### ✅ **JÁ IMPLEMENTADO NO SISTEMA**

O componente `ImageUploadWithAI` já está integrado no modal de detalhes do card do Kanban Board.

**Para usar:**

1. **Abra um card** no quadro Kanban
2. **Clique no botão editar** (ícone de lápis)
3. **Role para a seção "Imagens do Card"**
4. **Clique na área de upload** ou **cole uma imagem** (Ctrl+V)
5. **A IA gera a descrição automaticamente**
6. **Edite se necessário** e clique **"Adicionar Imagem"**

### 🎯 **Funcionalidades Ativas:**

- ✅ Upload por clique ou paste
- ✅ Preview da imagem antes de salvar
- ✅ Descrição automática em português
- ✅ Possibilidade de editar descrição
- ✅ Contexto do card considerado pela IA
- ✅ Integração completa com backend

---

## ✅ Funcionalidades

- ✅ **Upload de arquivo**: Clique para selecionar
- ✅ **Paste (Ctrl+V)**: Cole imagem do clipboard
- ✅ **Preview**: Veja antes de salvar
- ✅ **IA automática**: Descrição gerada em 2 segundos
- ✅ **Editável**: Pode ajustar descrição
- ✅ **Contexto**: IA considera título/prioridade do card

---

## 💰 Custo

### FREE (Recomendado):
- 1500 imagens/dia
- **$0/mês**

### PAID (Se precisar):
- Ilimitado
- ~$0.58/mês para 1000 imagens/dia

---

## 🐛 Troubleshooting

### "Serviço desabilitado"
→ Verifique se `GOOGLE_GEMINI_API_KEY` está no `.env`

### "API key inválida"
→ Gere nova chave em https://aistudio.google.com

### "Descrição não gerada"
→ Verifique logs do backend: `tail -f logs/app.log`

---

## 📊 Exemplo Real

**Antes (sem IA):**
```
1. Upload imagem ✅
2. Digitar: "Captura de tela do código Python..." ⏱️ 30s
3. Salvar ✅
```

**Depois (com IA):**
```
1. Upload imagem ✅
2. IA gera: "Captura de tela mostrando código Python..." ⚡ 2s
3. Confirmar ✅
```

**Economia: 28 segundos por imagem!**

---

## 🎯 Pronto para Usar!

**A funcionalidade está COMPLETAMENTE implementada e pronta para uso!** 🚀

### 📍 **Onde Encontrar:**
- Abra qualquer card no **Kanban Board**
- Na seção **"Imagens do Card"**
- Use o componente com **ícone de ✨ (brilho)**

### 💡 **Dica:**
A IA gera descrições em português brasileiro, considerando o contexto do card (título, prioridade, etc.).

---

**Para documentação técnica completa, veja:** `GEMINI_VISION_SETUP.md`
