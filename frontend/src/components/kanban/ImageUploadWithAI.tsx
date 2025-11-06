/**
 * Upload de imagem com descrição automática por IA
 */

import React, { useState } from 'react';
import { Upload, Sparkles, Loader2, Check, X } from 'lucide-react';
import { api } from '../../services/api';
import toast from 'react-hot-toast';
import { RichTextEditor } from '../common/RichTextEditor';

interface ImageUploadWithAIProps {
  cardId?: number;
  onImageProcessed: (movementId: number, imageUrl: string, userDescription: string, aiAnalysis: string) => void;
  context?: string; // Contexto para IA (ex: "card de desenvolvimento")
}

export const ImageUploadWithAI: React.FC<ImageUploadWithAIProps> = ({
  cardId,
  onImageProcessed,
  context
}) => {
  const [processing, setProcessing] = useState(false);
  const [userDescription, setUserDescription] = useState('');
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validar tipo
    if (!file.type.startsWith('image/')) {
      toast.error('Arquivo deve ser uma imagem');
      return;
    }

    // Validar tamanho (máx 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Imagem muito grande (máx 10MB)');
      return;
    }

    // Preview da imagem
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handlePaste = async (event: React.ClipboardEvent) => {
    const items = event.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        event.preventDefault();
        const file = items[i].getAsFile();
        if (file) {
          // Criar evento sintético para reutilizar lógica
          const fakeEvent = {
            target: {
              files: [file]
            }
          } as any;
          await handleFileSelect(fakeEvent);
        }
      }
    }
  };

  const handleUploadAndProcess = async () => {
    if (!imagePreview) {
      toast.error('Selecione uma imagem primeiro');
      return;
    }

    if (!userDescription.trim()) {
      toast.error('Adicione uma descrição para a imagem');
      return;
    }

    try {
      setProcessing(true);
      toast.loading('Enviando imagem e processando com IA...', { id: 'upload-ai' });

      // Converter base64 para File
      const response = await fetch(imagePreview);
      const blob = await response.blob();
      const file = new File([blob], 'image.jpg', { type: 'image/jpeg' });

      // 1. Upload da imagem
      const formData = new FormData();
      formData.append('file', file);

      const uploadEndpoint = `/api/v1/kanban/cards/${cardId}/images?image_type=reference&description=${encodeURIComponent(userDescription)}`;

      console.log('📤 1/2: Fazendo upload da imagem...');
      const uploadResponse = await api.post(uploadEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const imageId = uploadResponse.data.image_id;
      console.log('✅ Upload concluído! Image ID:', imageId);

      // 2. Processar com IA
      console.log('🤖 2/2: Processando com IA...');
      const processEndpoint = `/api/v1/kanban/cards/${cardId}/process-image`;
      const payload = {
        image_id: imageId,
        user_description: userDescription
      };

      const processResponse = await api.post(processEndpoint, payload);
      console.log('✅ Processamento concluído:', processResponse.data);

      toast.success('✨ Imagem processada com IA e movimento criado!', { id: 'upload-ai' });

      // Callback com dados
      onImageProcessed(
        processResponse.data.movement_id,
        imagePreview,
        userDescription,
        processResponse.data.ai_analysis
      );

      // Limpar formulário
      setImagePreview(null);
      setUserDescription('');

    } catch (error: any) {
      console.error('❌ Erro:', error);
      toast.error(error.response?.data?.detail || 'Erro ao processar imagem', { id: 'upload-ai' });
    } finally {
      setProcessing(false);
    }
  };


  const handleCancel = () => {
    setImagePreview(null);
    setUserDescription('');
  };

  return (
    <div className="space-y-4" onPaste={handlePaste}>
      {/* Upload Area */}
      {!imagePreview && (
        <div
          className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center hover:border-blue-500 dark:hover:border-blue-400 transition-colors cursor-pointer"
        >
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
            id="image-upload-ai"
            disabled={processing}
          />
          <label htmlFor="image-upload-ai" className="cursor-pointer">
            <div className="flex flex-col items-center gap-3">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-full">
                <Upload className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900 dark:text-white">
                  Clique para fazer upload ou cole uma imagem
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  JPG, PNG, GIF, WebP (máx 10MB)
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400">
                <Sparkles className="w-4 h-4" />
                <span>Descrição automática com IA</span>
              </div>
            </div>
          </label>
        </div>
      )}

      {/* Preview e Processamento */}
      {imagePreview && (
        <div className="space-y-4 bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          {/* Preview da Imagem */}
          <div className="relative">
            <img
              src={imagePreview}
              alt="Preview"
              className="w-full h-auto max-h-96 object-contain rounded-lg border border-gray-200 dark:border-gray-700"
            />
            <button
              onClick={handleCancel}
              disabled={processing}
              className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors disabled:opacity-50"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Descrição do Usuário */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              📝 Descrição da Imagem
            </label>
            <RichTextEditor
              value={userDescription}
              onChange={setUserDescription}
              placeholder="Descreva o conteúdo da imagem para contextualizar a análise da IA..."
              disabled={processing}
              minHeight="120px"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              ✨ A IA usará esta descrição para gerar uma análise detalhada da imagem
            </p>
          </div>

          {/* Botões */}
          <div className="flex gap-2">
            <button
              onClick={handleCancel}
              disabled={processing}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleUploadAndProcess}
              disabled={!userDescription.trim() || processing}
              className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-md text-sm font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg"
            >
              {processing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processando com IA...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Enviar e Processar com IA
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
