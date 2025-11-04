/**
 * Componente de upload de imagens para Kanban
 */

import React, { useState, useRef } from 'react';
import api from '../../services/api';

interface ImageUploadProps {
  cardId?: number;
  movementId?: number;
  onUploadSuccess: () => void;
  imageType?: string;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  cardId,
  movementId,
  onUploadSuccess,
  imageType = 'reference'
}) => {
  const [uploading, setUploading] = useState(false);
  const [description, setDescription] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Listener para colar imagem (SEMPRE ATIVO)
  React.useEffect(() => {
    const handlePaste = async (e: ClipboardEvent) => {
      // Ignorar se estiver digitando em um input/textarea
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
        return;
      }

      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          e.preventDefault();
          const blob = items[i].getAsFile();
          if (blob) {
            await uploadFile(blob);
          }
          break;
        }
      }
    };

    document.addEventListener('paste', handlePaste);

    return () => {
      document.removeEventListener('paste', handlePaste);
    };
  }, []);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validar tipo de arquivo
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert('Tipo de arquivo não permitido. Use: JPG, PNG, GIF ou WebP');
      return;
    }

    // Validar tamanho (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Arquivo muito grande. Tamanho máximo: 5MB');
      return;
    }

    await uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      let endpoint = '';
      if (cardId) {
        endpoint = `/api/v1/kanban/cards/${cardId}/images?image_type=${imageType}&description=${encodeURIComponent(description)}`;
      } else if (movementId) {
        endpoint = `/api/v1/kanban/movements/${movementId}/images?image_type=${imageType}&description=${encodeURIComponent(description)}`;
      }

      await api.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setDescription('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      onUploadSuccess();
    } catch (error: any) {
      console.error('Erro ao fazer upload:', error);
      alert(error.response?.data?.detail || 'Erro ao fazer upload da imagem');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-3">
      <h4 className="font-medium text-gray-900 dark:text-white">
        📎 Anexar Imagem
        <span className="ml-2 text-xs text-blue-600 dark:text-blue-400">
          (Ctrl+V para colar)
        </span>
      </h4>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Descrição (opcional)
        </label>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Ex: Print do erro, Solução aplicada..."
          className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      {/* File Input */}
      <div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
          onChange={handleFileSelect}
          disabled={uploading}
          className="block w-full text-sm text-gray-500 dark:text-gray-400
            file:mr-4 file:py-2 file:px-4
            file:rounded-md file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100
            dark:file:bg-blue-900 dark:file:text-blue-200
            dark:hover:file:bg-blue-800
            disabled:opacity-50"
        />
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          JPG, PNG, GIF ou WebP. Máximo 5MB.
        </p>
      </div>

      {uploading && (
        <div className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400">
          <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Enviando imagem...
        </div>
      )}
    </div>
  );
};
