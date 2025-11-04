# Guia de Integração - Gemini API

**Responsável:** Dev Backend  
**Tempo Estimado:** 30 minutos

---

## 🔑 Obter API Key

1. Acesse: https://aistudio.google.com/app/apikey
2. Clique em "Get API Key"
3. Copie a chave (formato: `AIza...`)

---

## ⚙️ Configurar Backend

### 1. Instalar SDK
```bash
cd backend
pip install google-generativeai
```

### 2. Adicionar no `.env`
```bash
GEMINI_API_KEY=AIzaSy...your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Atualizar `core/config.py`
```python
class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"
```

---

## 🧪 Testar Integração

### `test_gemini.py`
```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = """
Analise: "Vania precisa dos testes. Daniel vai enviar amanhã."

Retorne JSON com:
- pessoas: lista de nomes
- pendencias: lista com descricao e responsavel
"""

response = model.generate_content(prompt)
print(response.text)
```

### Executar:
```bash
python test_gemini.py
```

---

## 💰 Custos

### `gemini-1.5-flash` (Recomendado)
- **Gratuito:** 15 req/min
- **Imagem:** $0.00025 cada
- **MVP:** < $10/mês

### `gemini-1.5-pro` (Futuro)
- **Texto:** $0.00125/req
- **Melhor qualidade**

---

## 🔒 Segurança

```bash
# .gitignore
.env
.env.local
```

**NUNCA** commitar chave API!

---

## 🐛 Troubleshooting

### "API key not valid"
- Verificar chave no .env
- Recarregar: `source .env`

### "Resource exhausted"
- Limite de 15 req/min atingido
- Aguardar 1 minuto

### "Invalid JSON"
- Melhorar prompt
- Adicionar retry logic

---

## 📚 Documentação

- API: https://ai.google.dev/docs
- Modelos: https://ai.google.dev/models/gemini
- Pricing: https://ai.google.dev/pricing
