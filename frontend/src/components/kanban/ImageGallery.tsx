/**
 * Galeria de imagens do Kanban
 */

import React, { useState } from 'react';
import api from '../../services/api';

interface Image {
  CardImageID?: number;
  MovementImageID?: number;
  ImagePath: string;
  ImageType: string;
  Description: string;
  UploadedAt: string;
}

interface ImageGalleryProps {
  images: Image[];
  onDelete: () => void;
  type: 'card' | 'movement';
}

export const ImageGallery: React.FC<ImageGalleryProps> = ({ images, onDelete, type }) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<number | null>(null);

  const getImageUrl = (imagePath: string) => {
    // Extrair apenas o nome do arquivo
    const filename = imagePath.split('/').pop() || imagePath.split('\\').pop();
    return `http://192.168.11.83:8000/uploads/kanban/${filename}`;
  };

  const handleDelete = async (imageId: number) => {
    if (!confirm('Deseja realmente remover esta imagem?')) return;

    setDeleting(imageId);

    try {
      const endpoint = type === 'card' 
        ? `/api/v1/kanban/card-images/${imageId}`
        : `/api/v1/kanban/movement-images/${imageId}`;

      await api.delete(endpoint);
      onDelete();
    } catch (error) {
      console.error('Erro ao deletar imagem:', error);
      alert('Erro ao deletar imagem');
    } finally {
      setDeleting(null);
    }
  };

  if (!images || images.length === 0) {
    return (
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Nenhuma imagem anexada
      </p>
    );
  }

  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {images.map((image) => {
          const imageId = image.CardImageID || image.MovementImageID;
          if (!imageId) return null;

          return (
            <div
              key={imageId}
              className="relative group rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700"
            >
              {/* Image */}
              <img
                src={getImageUrl(image.ImagePath)}
                alt={image.Description || 'Imagem anexada'}
                className="w-full h-32 object-cover cursor-pointer hover:opacity-90 transition-opacity"
                onClick={() => setSelectedImage(getImageUrl(image.ImagePath))}
              />

              {/* Overlay */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity flex items-center justify-center">
                <button
                  onClick={() => handleDelete(imageId)}
                  disabled={deleting === imageId}
                  className="opacity-0 group-hover:opacity-100 bg-red-600 hover:bg-red-700 text-white rounded-full p-2 transition-opacity disabled:opacity-50"
                  title="Remover imagem"
                >
                  {deleting === imageId ? (
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  )}
                </button>
              </div>

              {/* Description */}
              {image.Description && (
                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-70 text-white text-xs p-2 truncate">
                  {image.Description}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Modal de visualização */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-4xl max-h-full">
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute top-4 right-4 text-white bg-black bg-opacity-50 rounded-full p-2 hover:bg-opacity-70"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <img
              src={selectedImage}
              alt="Visualização"
              className="max-w-full max-h-[90vh] object-contain"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>
      )}
    </>
  );
};
