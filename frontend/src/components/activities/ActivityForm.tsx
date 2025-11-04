/**
 * Formulário de criação de atividades
 */

import React, { useState, useRef, useEffect } from 'react';
import { ActivityCreateData } from '../../services/activityService';
import { useImagePaste, PastedImage } from '../../hooks/useImagePaste';
import { ImageIcon, X, Upload } from 'lucide-react';

interface ActivityFormProps {
  onSubmit: (data: ActivityCreateData, images: File[]) => Promise<void>;
  loading?: boolean;
  initialData?: Partial<ActivityCreateData>;
  isEdit?: boolean;
}

export const ActivityForm: React.FC<ActivityFormProps> = ({
  onSubmit,
  loading = false,
  initialData,
  isEdit = false
}) => {
  const [formData, setFormData] = useState<ActivityCreateData>({
    Title: initialData?.Title || '',
    Status: initialData?.Status || 'Pendente',
    RawText: initialData?.RawText || '',
    DueDate: initialData?.DueDate || null
  });

  const { images, handlePaste, removeImage, clearImages, addImageFromFile } = useImagePaste();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Adicionar listener de paste no textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.addEventListener('paste', handlePaste);
      return () => textarea.removeEventListener('paste', handlePaste);
    }
  }, [handlePaste]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const imageFiles = images.map(img => img.file);
    await onSubmit(formData, imageFiles);
    if (!isEdit) {
      clearImages(); // Limpar imagens apenas na criação
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      Array.from(files).forEach(file => addImageFromFile(file));
    }
    // Limpar input para permitir selecionar o mesmo arquivo novamente
    e.target.value = '';
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value || null
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Título */}
      <div>
        <label htmlFor="Title" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Título/Assunto *
        </label>
        <input
          type="text"
          id="Title"
          name="Title"
          value={formData.Title}
          onChange={handleChange}
          required
          maxLength={255}
          className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          placeholder="Ex: Abertura RDM CHG0076721"
        />
      </div>

      {/* Status */}
      <div>
        <label htmlFor="Status" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Status *
        </label>
        <select
          id="Status"
          name="Status"
          value={formData.Status}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          <option value="Pendente">Pendente</option>
          <option value="Em Andamento">Em Andamento</option>
          <option value="Concluído">Concluído</option>
          <option value="Cancelado">Cancelado</option>
        </select>
      </div>

      {/* Prazo */}
      <div>
        <label htmlFor="DueDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Prazo (opcional)
        </label>
        <input
          type="datetime-local"
          id="DueDate"
          name="DueDate"
          value={formData.DueDate || ''}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      {/* Conteúdo */}
      <div>
        <label htmlFor="RawText" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Conteúdo da Atividade {!isEdit && '*'}
        </label>
        <textarea
          ref={textareaRef}
          id="RawText"
          name="RawText"
          value={formData.RawText || ''}
          onChange={handleChange}
          required={!isEdit}
          rows={6}
          className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm placeholder-gray-400 dark:placeholder-gray-500"
          placeholder={isEdit ? "Adicione novo conteúdo para reprocessar com IA (opcional)" : "Cole aqui o conteúdo da conversa, e-mail, ou descrição da atividade..."}
        />
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {isEdit 
            ? "Se adicionar conteúdo, a IA irá reprocessar e sugerir novas pessoas, sistemas e pendências."
            : "A IA analisará este conteúdo para sugerir pessoas, sistemas e pendências."
          }
        </p>
      </div>

      {/* Área de Imagens - Só mostrar na criação */}
      {!isEdit && (
        <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Imagens (Opcional)
        </label>

        {/* Preview de Imagens */}
        {images.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
            {images.map((img) => (
              <div
                key={img.id}
                className="relative group rounded-lg border-2 border-gray-200 dark:border-gray-700 overflow-hidden bg-gray-50 dark:bg-gray-800"
              >
                <img
                  src={img.preview}
                  alt={img.name}
                  className="w-full h-32 object-cover"
                />
                <button
                  type="button"
                  onClick={() => removeImage(img.id)}
                  className="absolute top-2 right-2 bg-red-600 hover:bg-red-700 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Remover imagem"
                >
                  <X className="w-4 h-4" />
                </button>
                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 text-white text-xs px-2 py-1">
                  {formatFileSize(img.size)}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Botões de Ação */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Upload className="w-4 h-4" />
            Selecionar Imagens
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileInputChange}
            className="hidden"
          />
          {images.length > 0 && (
            <button
              type="button"
              onClick={clearImages}
              className="text-sm text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
            >
              Limpar todas ({images.length})
            </button>
          )}
        </div>

        {/* Dicas */}
        <div className="mt-3 space-y-1">
          <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
            <ImageIcon className="w-4 h-4" />
            <span>
              <strong>Dica:</strong> Pressione <kbd className="px-2 py-0.5 text-xs bg-gray-200 dark:bg-gray-700 rounded">Print Screen</kbd> e cole aqui com <kbd className="px-2 py-0.5 text-xs bg-gray-200 dark:bg-gray-700 rounded">Ctrl+V</kbd>
            </span>
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500">
            A IA analisará as imagens junto com o texto para extrair informações adicionais
          </p>
        </div>
      </div>
      )}

      {/* Botão Submit */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 dark:bg-blue-500 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {isEdit ? 'Salvando...' : `Analisando${images.length > 0 ? ` (${images.length} ${images.length === 1 ? 'imagem' : 'imagens'})` : ''}...`}
            </>
          ) : (
            isEdit ? 'Salvar Alterações' : `Criar e Analisar com IA${images.length > 0 ? ` (${images.length} ${images.length === 1 ? 'imagem' : 'imagens'})` : ''}`
          )}
        </button>
      </div>
    </form>
  );
};
