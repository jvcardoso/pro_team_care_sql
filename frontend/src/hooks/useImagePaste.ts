/**
 * Hook para capturar imagens coladas (Ctrl+V) e gerenciar preview
 */

import { useState, useCallback } from 'react';

export interface PastedImage {
  id: string;
  file: File;
  preview: string; // data URL para preview
  name: string;
  size: number;
}

export const useImagePaste = () => {
  const [images, setImages] = useState<PastedImage[]>([]);

  /**
   * Handler para evento de paste
   */
  const handlePaste = useCallback((e: ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    // Procurar por imagens no clipboard
    for (const item of Array.from(items)) {
      if (item.type.startsWith('image/')) {
        e.preventDefault(); // Prevenir comportamento padrão

        const file = item.getAsFile();
        if (!file) continue;

        // Validar tamanho (máximo 5MB)
        const maxSize = 5 * 1024 * 1024; // 5MB
        if (file.size > maxSize) {
          alert(`Imagem muito grande (${(file.size / 1024 / 1024).toFixed(1)}MB). Máximo: 5MB`);
          continue;
        }

        // Gerar ID único
        const id = `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Ler arquivo e criar preview
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

  /**
   * Remover imagem por ID
   */
  const removeImage = useCallback((id: string) => {
    setImages(prev => prev.filter(img => img.id !== id));
  }, []);

  /**
   * Limpar todas as imagens
   */
  const clearImages = useCallback(() => {
    setImages([]);
  }, []);

  /**
   * Adicionar imagem via file input
   */
  const addImageFromFile = useCallback((file: File) => {
    // Validar tipo
    if (!file.type.startsWith('image/')) {
      alert('Apenas imagens são permitidas');
      return;
    }

    // Validar tamanho (máximo 5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      alert(`Imagem muito grande (${(file.size / 1024 / 1024).toFixed(1)}MB). Máximo: 5MB`);
      return;
    }

    const id = `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const preview = event.target?.result as string;
      
      setImages(prev => [...prev, {
        id,
        file,
        preview,
        name: file.name,
        size: file.size
      }]);
    };
    
    reader.readAsDataURL(file);
  }, []);

  return {
    images,
    handlePaste,
    removeImage,
    clearImages,
    addImageFromFile
  };
};
