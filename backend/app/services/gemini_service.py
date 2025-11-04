"""
Serviço de integração com Gemini API para análise de atividades.

Responsável por:
- Analisar texto e imagens
- Extrair entidades (pessoas, sistemas)
- Identificar datas e prazos
- Sugerir tags e categorias
- Detectar pendências e impedimentos
"""
import json
import logging
import asyncio
import hashlib
from typing import Dict, Optional
from app.core.config import settings

# Importação obrigatória do Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.error("ERRO CRÍTICO: google-generativeai não instalado. Instale com: pip install google-generativeai")
    raise ImportError("google-generativeai é obrigatório para o funcionamento do módulo de atividades")

logger = logging.getLogger(__name__)


class GeminiService:
    """Serviço de análise de atividades usando Gemini API"""

    def __init__(self):
        """Inicializa o serviço Gemini - OBRIGATÓRIO para dados reais"""
        if not GEMINI_AVAILABLE:
            raise RuntimeError("ERRO CRÍTICO: google-generativeai não está instalado")

        if not settings.GEMINI_API_KEY:
            raise RuntimeError("ERRO CRÍTICO: GEMINI_API_KEY não configurada no .env")

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"✅ Gemini inicializado com sucesso: {settings.GEMINI_MODEL}")

            # Cache simples para otimizar uso da API gratuita
            self._cache = {}
            self._max_cache_size = 50  # Limitar cache para não crescer indefinidamente

        except Exception as e:
            logger.error(f"ERRO CRÍTICO: Falha ao inicializar Gemini: {e}")
            raise RuntimeError(f"Não foi possível inicializar Gemini API: {e}")

    async def analyze_activity(
        self,
        title: str,
        status: str,
        raw_text: Optional[str] = None,
        raw_image_path: Optional[str] = None
    ) -> Dict:
        """
        Analisa conteúdo de uma atividade e retorna sugestões estruturadas.
        Usa dados reais da IA com otimizações para plano gratuito.

        Args:
            title: Título da atividade
            status: Status atual
            raw_text: Texto colado pelo usuário
            raw_image_path: Caminho da imagem (se houver)

        Returns:
            Dict com sugestões: pessoas, sistemas, datas, tags, pendencias

        Raises:
            RuntimeError: Se houver erro na análise da IA
        """
        if not self.model:
            raise RuntimeError("Gemini não está inicializado")

        # Verificar cache primeiro
        cache_key = self._get_cache_key(title, status, raw_text)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            logger.info(f"✅ Resultado obtido do cache para: {title}")
            return cached_result

        # Otimização para plano gratuito: reduzir tamanho do prompt se necessário
        if raw_text and len(raw_text) > 1000:
            raw_text = raw_text[:1000] + "..."
            logger.info("Texto truncado para otimizar uso da API gratuita")

        try:
            prompt = self._build_prompt(title, status, raw_text)

            # Análise com retry e backoff
            if raw_image_path:
                response = await self._retry_with_backoff(self._analyze_with_image, prompt, raw_image_path)
            else:
                response = await self._retry_with_backoff(self._analyze_text_only, prompt)

            # Parse e retorno
            result = self._parse_ai_response(response.text)

            # Armazenar em cache
            self._cache_result(cache_key, result)

            logger.info(f"✅ Análise IA concluída para: {title}")
            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Erro na análise Gemini: {error_msg}")

            # Se for erro de quota, fornecer orientação específica
            if "429" in error_msg or "Resource exhausted" in error_msg:
                raise RuntimeError(
                    "Limite da API gratuita atingido. Aguarde alguns minutos ou considere upgrade para plano pago. "
                    "Limites gratuitos: ~60 requests/minuto, quota diária baixa."
                )
            else:
                raise RuntimeError(f"Falha na análise da IA: {error_msg}")

    def _get_cache_key(self, title: str, status: str, raw_text: Optional[str]) -> str:
        """Gera chave de cache baseada no conteúdo"""
        content = f"{title}|{status}|{raw_text or ''}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Verifica se há resultado em cache"""
        return self._cache.get(cache_key)

    def _cache_result(self, cache_key: str, result: Dict):
        """Armazena resultado em cache"""
        if len(self._cache) >= self._max_cache_size:
            # Remove entrada mais antiga (FIFO simples)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[cache_key] = result

    async def _retry_with_backoff(self, func, *args, max_retries=3):
        """Executa função com retry e backoff exponencial"""
        for attempt in range(max_retries):
            try:
                return await func(*args)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Backoff exponencial: 1s, 2s, 4s
                    logger.warning(f"Tentativa {attempt + 1} falhou (429). Aguardando {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise e

    def _build_prompt(self, title: str, status: str, raw_text: Optional[str]) -> str:
        """Constrói o prompt otimizado para a IA (modelo Kanban)"""
        return f"""
Você é um assistente especializado em análise de atividades de TI para um sistema Kanban Board.

**CONTEXTO DO CARD:**
- Título: {title}
- Status: {status}

**CONTEÚDO ORIGINAL:**
{raw_text or "Sem texto adicional"}

**TAREFA:**
Analise o conteúdo e extraia informações estruturadas para um card de Kanban. Retorne um JSON com:

1. **"description"**: (string) Descrição melhorada e profissional do card, em 2-3 frases, destacando:
   - O que precisa ser feito
   - Contexto técnico relevante
   - Impacto/urgência se houver

2. **"assignees"**: (array) Pessoas responsáveis/mencionadas (apenas nomes próprios)

3. **"systems"**: (array) Sistemas/aplicações/tecnologias mencionados
   - Ex: "SAP", "Jira", "PSCD", "RDM", "SQL Server", "React", "FastAPI"

4. **"tags"**: (array) 3-5 tags para categorização
   - Ex: ["Gestão de Mudanças", "Performance", "Deploy", "Bug Fix", "Aprovação"]

5. **"priority"**: (string) Prioridade estimada: "Baixa", "Média", "Alta", ou "Urgente"
   - Baseie-se em palavras como: urgente, crítico, bloqueador, ASAP

6. **"sub_status"**: (string ou null) Se houver impedimento, retorne:
   - "Bloqueado - Depende de outro" (se aguarda outra pessoa/equipe)
   - "Bloqueado - Depende de mim" (se você deve fazer algo primeiro)
   - "Aguardando aprovação" (se aguarda aprovação/validação)
   - null (se não há impedimento)

7. **"due_date"**: (string ou null) Data de prazo se identificada (formato YYYY-MM-DD)

8. **"movements"**: (array) Lista de sub-tarefas/movimentos identificados. Cada objeto com:
   - "subject": Título curto da sub-tarefa (ex: "CHG0076721 - Deploy Sprint 10")
   - "description": Descrição detalhada
   - "estimated_time": Tempo estimado em minutos (se identificável, senão null)
   - "assignee": Responsável específico (se identificável, senão null)

**REGRAS CRÍTICAS:**
✅ Retorne APENAS o JSON válido, sem markdown, sem texto adicional
✅ **SEMPRE preserve IDs de tickets** (CHG, INC, REQ, TASK, RITM) no início do subject
✅ Cada ticket/change diferente = movimento separado
✅ Use null para valores não identificados
✅ Seja conservador: só inclua informações claras no texto
✅ Na description do card, resuma o objetivo geral (não liste todos os tickets)

**EXEMPLO DE RESPOSTA:**
{{
  "description": "Realizar aprovações de mudanças da Sprint 10 do sistema PSCD. Inclui deploy de demandas homologadas, manutenção de performance e reconstrução de réplicas. Aguardando aprovação do gestor Ray.",
  "assignees": ["Ray", "Juliano"],
  "systems": ["PSCD", "RDM"],
  "tags": ["Gestão de Mudanças", "Deploy", "Performance", "Aprovação"],
  "priority": "Alta",
  "sub_status": "Aguardando aprovação",
  "due_date": "2025-11-10",
  "movements": [
    {{
      "subject": "CHG0076721 - Deploy de Demandas Homologadas Sprint 10",
      "description": "Realizar deploy das demandas homologadas da Sprint 10 no ambiente de produção do PSCD",
      "estimated_time": 120,
      "assignee": "Juliano"
    }},
    {{
      "subject": "CHG0076643 - Manutenção de Performance PSCD",
      "description": "Aplicar otimizações de performance no banco de dados do PSCD",
      "estimated_time": 60,
      "assignee": null
    }},
    {{
      "subject": "CHG0076697 - Reconstrução de Réplicas PSCD",
      "description": "Reconstruir réplicas do banco de dados para melhorar disponibilidade",
      "estimated_time": 90,
      "assignee": null
    }}
  ]
}}

Agora analise o conteúdo fornecido e retorne o JSON:
"""

    async def _analyze_text_only(self, prompt: str):
        """Análise apenas de texto"""
        return self.model.generate_content(prompt)

    async def _analyze_with_image(self, prompt: str, image_path: str):
        """Análise de texto + imagem"""
        try:
            image = genai.upload_file(image_path)
            return self.model.generate_content([prompt, image])
        except Exception as e:
            logger.warning(f"Erro ao processar imagem, usando apenas texto: {e}")
            return await self._analyze_text_only(prompt)

    def _parse_ai_response(self, response_text: str) -> Dict:
        """
        Faz parse da resposta da IA para JSON.

        Remove markdown code blocks se existirem e tenta parsear.
        """
        try:
            # Limpar markdown
            clean_text = response_text.strip()

            # Remover ```json ou ```
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:]

            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            # Parse JSON
            result = json.loads(clean_text.strip())

            # Validar estrutura mínima
            if not isinstance(result, dict):
                raise ValueError("Resposta não é um objeto JSON")

            # Garantir campos obrigatórios (novo modelo Kanban)
            result.setdefault("description", "")
            result.setdefault("assignees", [])
            result.setdefault("systems", [])
            result.setdefault("tags", [])
            result.setdefault("priority", "Média")
            result.setdefault("sub_status", None)
            result.setdefault("due_date", None)
            result.setdefault("movements", [])
            
            # Manter compatibilidade com modelo antigo (temporário)
            result.setdefault("pessoas", result.get("assignees", []))
            result.setdefault("sistemas", result.get("systems", []))
            result.setdefault("pendencias", result.get("movements", []))

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON da IA: {e}")
            logger.debug(f"Resposta bruta: {response_text}")
            return {
                "error": "Falha ao parsear resposta da IA",
                "raw_response": response_text[:500],
                # Novo modelo
                "description": "",
                "assignees": [],
                "systems": [],
                "tags": [],
                "priority": "Média",
                "sub_status": None,
                "due_date": None,
                "movements": [],
                # Compatibilidade
                "pessoas": [],
                "sistemas": [],
                "pendencias": []
            }




# Instância global (singleton)
gemini_service = GeminiService()
