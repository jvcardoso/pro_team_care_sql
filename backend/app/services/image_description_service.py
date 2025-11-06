"""
Serviço para gerar descrições automáticas de imagens usando Google Gemini Vision
"""

import os
import base64
from typing import Optional
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ImageDescriptionService:
    """Serviço para análise de imagens com IA"""
    
    def __init__(self):
        """Inicializa o serviço com API key do Gemini"""
        # Usar a mesma chave do GEMINI_API_KEY existente
        from app.core.config import settings
        api_key = settings.GEMINI_API_KEY

        if not api_key:
            logger.warning("GEMINI_API_KEY não configurada. Descrições automáticas desabilitadas.")
            self.enabled = False
            return

        genai.configure(api_key=api_key)
        # Usar o mesmo modelo configurado no settings
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.enabled = True
        logger.info(f"✅ Gemini Vision configurado com sucesso: {settings.GEMINI_MODEL}")
    
    def _generate_description_sync(
        self,
        image_path: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Método síncrono para gerar descrição (executado em thread pool)
        """
        if not self.enabled:
            logger.warning("Serviço de descrição de imagens desabilitado")
            return None

        try:
            # Ler imagem
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Preparar prompt
            prompt = self._build_prompt(context)

            # Enviar para Gemini
            logger.info(f"📸 Analisando imagem: {image_path}")
            response = self.model.generate_content([
                prompt,
                {"mime_type": self._get_mime_type(image_path), "data": image_data}
            ])

            description = response.text.strip()
            logger.info(f"✅ Descrição gerada: {description[:100]}...")

            return description

        except Exception as e:
            logger.error(f"❌ Erro ao gerar descrição: {str(e)}")
            return None

    async def generate_description(
        self,
        image_path: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Gera descrição automática de uma imagem (async wrapper)

        Args:
            image_path: Caminho para a imagem no servidor
            context: Contexto adicional (ex: "card de kanban sobre desenvolvimento")

        Returns:
            Descrição da imagem em português ou None se falhar
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        # Executar em thread pool para não bloquear o event loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self._generate_description_sync, image_path, context)

        # Executar em thread pool para não bloquear o event loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self._generate_description_sync, image_path, context)
        """
        Gera descrição automática de uma imagem
        
        Args:
            image_path: Caminho para a imagem no servidor
            context: Contexto adicional (ex: "card de kanban sobre desenvolvimento")
            
        Returns:
            Descrição da imagem em português ou None se falhar
        """
        if not self.enabled:
            logger.warning("Serviço de descrição de imagens desabilitado")
            return None
            
        try:
            # Ler imagem
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Preparar prompt
            prompt = self._build_prompt(context)
            
            # Enviar para Gemini
            logger.info(f"📸 Analisando imagem: {image_path}")
            response = self.model.generate_content([
                prompt,
                {"mime_type": self._get_mime_type(image_path), "data": image_data}
            ])
            
            description = response.text.strip()
            logger.info(f"✅ Descrição gerada: {description[:100]}...")
            
            return description
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar descrição: {str(e)}")
            return None
    
    def _generate_description_from_base64_sync(
        self,
        base64_image: str,
        mime_type: str = "image/jpeg",
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Método síncrono para gerar descrição de base64 (executado em thread pool)
        """
        if not self.enabled:
            return None

        try:
            # Remover prefixo data:image se existir
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]

            # Decodificar base64
            image_data = base64.b64decode(base64_image)

            # Preparar prompt
            prompt = self._build_prompt(context)

            # Enviar para Gemini
            logger.info("📸 Analisando imagem base64")
            response = self.model.generate_content([
                prompt,
                {"mime_type": mime_type, "data": image_data}
            ])

            description = response.text.strip()
            logger.info(f"✅ Descrição gerada: {description[:100]}...")

            return description

        except Exception as e:
            logger.error(f"❌ Erro ao gerar descrição: {str(e)}")
            return None

    async def generate_description_from_base64(
        self,
        base64_image: str,
        mime_type: str = "image/jpeg",
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Gera descrição de imagem em base64 (async wrapper)

        Args:
            base64_image: Imagem em base64 (com ou sem prefixo data:image)
            mime_type: Tipo MIME da imagem
            context: Contexto adicional

        Returns:
            Descrição da imagem ou None
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        # Executar em thread pool para não bloquear o event loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self._generate_description_from_base64_sync, base64_image, mime_type, context)
    
    def _build_prompt(self, context: Optional[str] = None) -> str:
        """Constrói prompt para o Gemini"""
        base_prompt = """
Analise esta imagem e forneça uma descrição clara e objetiva em português brasileiro.

A descrição deve:
- Ser concisa (máximo 2-3 frases)
- Descrever o conteúdo principal da imagem
- Mencionar elementos importantes visíveis
- Usar linguagem profissional

"""
        
        if context:
            base_prompt += f"\nContexto: {context}\n"
        
        base_prompt += "\nDescrição:"
        
        return base_prompt
    
    def _get_mime_type(self, file_path: str) -> str:
        """Detecta tipo MIME da imagem"""
        extension = file_path.lower().split('.')[-1]
        
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp'
        }
        
        return mime_types.get(extension, 'image/jpeg')


# Instância global do serviço
image_description_service = ImageDescriptionService()
