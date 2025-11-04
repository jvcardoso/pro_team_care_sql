# 📋 Plano: Upload de Imagens via Cola (Paste) no Formulário de Atividades

**Data:** 2025-11-03  
**URL:** http://192.168.11.83:3000/admin/activities/new

---

## 🎯 Objetivo

Permitir que o usuário **cole prints de tela diretamente no formulário** de atividades, e essas imagens sejam:
1. Exibidas como preview
2. Enviadas ao backend
3. Analisadas pela IA (Gemini Vision)
4. Anexadas à atividade

---

## 📊 Análise da Estrutura Atual

### Frontend

**Arquivo:** `ActivityForm.tsx`
- ✅ Já tem campo `RawText` (textarea)
- ❌ Não tem área para colar imagens
- ❌ Não tem preview de imagens
- ❌ Não tem upload de arquivos

**Interface:** `ActivityCreateData`
```typescript
{
  Title: string;
  Status: string;
  DueDate?: string | null;
  RawText?: string;
  RawImagePath?: string;  // ✅ Já existe, mas não é usado
}
```

### Backend

**Schema:** `ActivityCreate`
```python
RawImagePath: Optional[str] = Field(None, max_length=512)
```
- ✅ Campo já existe
- ❌ Atualmente espera PATH, não arquivo
- ❌ Não tem endpoint de upload

**Banco de Dados:**
- ✅ Tabela `ActivityContents` tem campo `RawImagePath`
- ✅ Suporta múltiplas imagens? **NÃO** (apenas 1 path)

---

## 🏗️ Arquitetura Proposta

### Fluxo Completo

```
1. Usuário cola imagem (Ctrl+V)
   ↓
2. JavaScript captura evento paste
   ↓
3. Extrai arquivo de imagem do clipboard
   ↓
4. Converte para base64 OU envia para upload
   ↓
5. Exibe preview na tela
   ↓
6. Ao submeter formulário:
   - Envia texto + imagens para backend
   ↓
7. Backend:
   - Salva imagens no disco/S3
   - Envia para Gemini Vision API
   - Extrai texto/dados das imagens
   - Combina com análise do texto
   ↓
8. Retorna sugestões da IA
```

---

## 🔧 Implementação Detalhada

### Fase 1: Frontend - Captura de Imagens

#### 1.1. Criar Hook `useImagePaste`

**Arquivo:** `frontend/src/hooks/useImagePaste.ts`

```typescript
import { useState, useCallback } from 'react';

export interface PastedImage {
  id: string;
  file: File;
  preview: string; // data URL
  name: string;
  size: number;
}

export const useImagePaste = () => {
  const [images, setImages] = useState<PastedImage[]>([]);

  const handlePaste = useCallback((e: ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (const item of Array.from(items)) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (!file) continue;

        const id = `img-${Date.now()}-${Math.random()}`;
        const reader = new FileReader();
        
        reader.onload = (event) => {
          const preview = event.target?.result as string;
          setImages(prev => [...prev, {
            id,
            file,
            preview,
            name: `screenshot-${Date.now()}.png`,
            size: file.size
          }]);
        };
        
        reader.readAsDataURL(file);
      }
    }
  }, []);

  const removeImage = useCallback((id: string) => {
    setImages(prev => prev.filter(img => img.id !== id));
  }, []);

  const clearImages = useCallback(() => {
    setImages([]);
  }, []);

  return {
    images,
    handlePaste,
    removeImage,
    clearImages
  };
};
```

#### 1.2. Atualizar `ActivityForm.tsx`

**Adicionar:**
1. Hook de paste
2. Área de preview de imagens
3. Botão para adicionar imagem via file input
4. Envio de imagens no submit

**Estrutura:**
```tsx
export const ActivityForm: React.FC<ActivityFormProps> = ({
  onSubmit,
  loading = false
}) => {
  const [formData, setFormData] = useState<ActivityCreateData>({...});
  const { images, handlePaste, removeImage, clearImages } = useImagePaste();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Adicionar listener de paste
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.addEventListener('paste', handlePaste);
      return () => textarea.removeEventListener('paste', handlePaste);
    }
  }, [handlePaste]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      ...formData,
      images // Adicionar imagens
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* ... campos existentes ... */}

      {/* Área de Imagens */}
      <div>
        <label className="block text-sm font-medium">
          Imagens (Cole com Ctrl+V)
        </label>
        
        {/* Preview de Imagens */}
        {images.length > 0 && (
          <div className="grid grid-cols-3 gap-4 mt-2">
            {images.map(img => (
              <div key={img.id} className="relative">
                <img 
                  src={img.preview} 
                  alt={img.name}
                  className="w-full h-32 object-cover rounded"
                />
                <button
                  type="button"
                  onClick={() => removeImage(img.id)}
                  className="absolute top-1 right-1 bg-red-600 text-white rounded-full w-6 h-6"
                >
                  ×
                </button>
                <p className="text-xs text-gray-500 mt-1">
                  {(img.size / 1024).toFixed(0)} KB
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Dica */}
        <p className="text-sm text-gray-500 mt-2">
          💡 Pressione Print Screen e cole aqui (Ctrl+V) para adicionar imagens
        </p>
      </div>

      {/* ... botão submit ... */}
    </form>
  );
};
```

---

### Fase 2: Backend - Upload e Armazenamento

#### 2.1. Criar Endpoint de Upload

**Arquivo:** `backend/app/api/v1/uploads.py` (NOVO)

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = Path("uploads/activities")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/images")
async def upload_images(
    files: List[UploadFile] = File(...)
) -> dict:
    """Upload de múltiplas imagens"""
    uploaded_paths = []
    
    for file in files:
        # Validar tipo
        if not file.content_type.startswith("image/"):
            raise HTTPException(400, "Apenas imagens são permitidas")
        
        # Gerar nome único
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = UPLOAD_DIR / filename
        
        # Salvar arquivo
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        
        uploaded_paths.append(str(filepath))
    
    return {
        "paths": uploaded_paths,
        "count": len(uploaded_paths)
    }
```

#### 2.2. Atualizar Schema `ActivityCreate`

```python
class ActivityCreate(ActivityBase):
    """Schema para criação de activity"""
    RawText: Optional[str] = None
    RawImagePaths: Optional[List[str]] = None  # ✅ Múltiplas imagens
```

#### 2.3. Atualizar Banco de Dados

**Opção 1: Múltiplas Imagens (Recomendado)**

Criar tabela `ActivityImages`:
```sql
CREATE TABLE [core].[ActivityImages] (
    ImageID INT IDENTITY(1,1) PRIMARY KEY,
    ActivityID INT NOT NULL,
    ImagePath NVARCHAR(512) NOT NULL,
    ImageOrder INT NOT NULL DEFAULT 0,
    UploadedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (ActivityID) REFERENCES [core].[Activities](ActivityID)
);
```

**Opção 2: JSON no Campo Existente**

Usar `RawImagePath` como JSON:
```json
{
  "images": [
    "/uploads/activities/abc123.png",
    "/uploads/activities/def456.png"
  ]
}
```

---

### Fase 3: Integração com IA (Gemini Vision)

#### 3.1. Atualizar `GeminiService`

**Arquivo:** `backend/app/services/gemini_service.py`

```python
async def analyze_with_images(
    self,
    text: str,
    image_paths: List[str]
) -> Dict[str, Any]:
    """Analisa texto + imagens com Gemini Vision"""
    
    if not self.api_key:
        return self._mock_response()
    
    # Carregar imagens
    images_data = []
    for path in image_paths:
        with open(path, "rb") as f:
            images_data.append({
                "mime_type": "image/png",
                "data": f.read()
            })
    
    # Prompt combinado
    prompt = f"""
    Analise o seguinte texto e as imagens anexadas:
    
    TEXTO:
    {text}
    
    IMAGENS: {len(images_data)} anexadas
    
    Extraia:
    - Pessoas mencionadas (no texto e visíveis nas imagens)
    - Sistemas/aplicações (no texto e nas telas capturadas)
    - Datas e prazos
    - Tags relevantes
    - Pendências identificadas
    
    Retorne em JSON.
    """
    
    response = await self.model.generate_content([
        prompt,
        *images_data
    ])
    
    return json.loads(response.text)
```

---

### Fase 4: Frontend - Envio de Imagens

#### 4.1. Atualizar `activityService.ts`

```typescript
export const activityService = {
  async create(data: ActivityCreateData, images: File[]): Promise<ActivityWithAI> {
    // 1. Upload de imagens (se houver)
    let imagePaths: string[] = [];
    
    if (images.length > 0) {
      const formData = new FormData();
      images.forEach(img => formData.append('files', img));
      
      const uploadResponse = await api.post('/uploads/images', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      imagePaths = uploadResponse.data.paths;
    }
    
    // 2. Criar atividade com paths das imagens
    const response = await api.post<ActivityWithAI>('/activities', {
      ...data,
      RawImagePaths: imagePaths
    });
    
    return response.data;
  }
};
```

---

## 📝 Checklist de Implementação

### Frontend
- [ ] Criar hook `useImagePaste.ts`
- [ ] Atualizar `ActivityForm.tsx` com área de imagens
- [ ] Adicionar preview de imagens
- [ ] Adicionar botão de remover imagem
- [ ] Atualizar `activityService.ts` para upload
- [ ] Adicionar loading durante upload
- [ ] Validar tamanho máximo de imagem (ex: 5MB)
- [ ] Validar tipos permitidos (png, jpg, jpeg)

### Backend
- [ ] Criar endpoint `/uploads/images`
- [ ] Criar diretório `uploads/activities/`
- [ ] Atualizar schema `ActivityCreate`
- [ ] Decidir: tabela separada ou JSON?
- [ ] Implementar `GeminiService.analyze_with_images()`
- [ ] Atualizar `ActivityService.create_with_ai_analysis()`
- [ ] Adicionar validação de tamanho
- [ ] Adicionar limpeza de arquivos antigos

### Banco de Dados
- [ ] Criar tabela `ActivityImages` (se opção 1)
- [ ] Criar model `ActivityImage`
- [ ] Criar repository `ActivityImageRepository`

---

## 🎨 UI/UX Proposta

### Área de Cole de Imagens

```
┌─────────────────────────────────────────┐
│ Conteúdo da Atividade *                 │
│ ┌─────────────────────────────────────┐ │
│ │ Cole aqui o texto ou pressione      │ │
│ │ Ctrl+V para adicionar imagens...    │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Imagens Anexadas (2)                    │
│ ┌───────┐ ┌───────┐                     │
│ │ [IMG] │ │ [IMG] │                     │
│ │  [X]  │ │  [X]  │                     │
│ │ 245KB │ │ 312KB │                     │
│ └───────┘ └───────┘                     │
│                                         │
│ 💡 Cole prints com Ctrl+V              │
│ 📎 Ou clique para selecionar arquivos  │
└─────────────────────────────────────────┘
```

---

## ⚠️ Considerações Importantes

### Segurança
- ✅ Validar tipo de arquivo (apenas imagens)
- ✅ Validar tamanho máximo (5MB por imagem)
- ✅ Sanitizar nomes de arquivo
- ✅ Usar UUIDs para evitar conflitos
- ✅ Verificar permissões de escrita

### Performance
- ✅ Comprimir imagens grandes (opcional)
- ✅ Limitar número de imagens (ex: máximo 5)
- ✅ Upload assíncrono
- ✅ Progress bar durante upload

### Armazenamento
- **Opção 1:** Disco local (`/uploads/activities/`)
- **Opção 2:** S3/MinIO (produção)
- **Opção 3:** Base64 no banco (NÃO recomendado)

### Limpeza
- Criar job para deletar imagens de atividades excluídas
- Manter por 30 dias após exclusão

---

## 🚀 Ordem de Implementação

### Sprint 1: Básico (2-3 horas)
1. ✅ Hook `useImagePaste`
2. ✅ Preview de imagens no form
3. ✅ Endpoint de upload básico
4. ✅ Salvar paths no banco

### Sprint 2: IA (2-3 horas)
5. ✅ Integrar Gemini Vision
6. ✅ Combinar análise texto + imagens
7. ✅ Testar com prints reais

### Sprint 3: Melhorias (1-2 horas)
8. ✅ Validações
9. ✅ Progress bar
10. ✅ Compressão de imagens
11. ✅ Limpeza automática

---

## 📊 Estimativa de Esforço

| Tarefa | Tempo | Prioridade |
|--------|-------|------------|
| Frontend - Paste + Preview | 2h | Alta |
| Backend - Upload | 1h | Alta |
| Backend - Gemini Vision | 2h | Alta |
| Banco - Estrutura | 1h | Média |
| Testes | 1h | Alta |
| **TOTAL** | **7h** | - |

---

## ✅ Próximos Passos

1. **Confirmar arquitetura** (tabela separada ou JSON?)
2. **Implementar hook de paste**
3. **Criar endpoint de upload**
4. **Testar com Gemini Vision API**
5. **Validar fluxo completo**

---

**Pronto para começar a implementação?**
