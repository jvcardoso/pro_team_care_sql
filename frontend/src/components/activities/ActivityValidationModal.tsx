/**
 * Modal para validação de dados sugeridos pela IA
 */

import React, { useState, useEffect } from 'react';
import { AISuggestions, ValidatedData, PendencySuggestion } from '../../services/activityService';

interface ActivityValidationModalProps {
  isOpen: boolean;
  onClose: () => void;
  aiSuggestions: AISuggestions | null;
  onSave: (validatedData: ValidatedData) => Promise<void>;
  loading?: boolean;
}

export const ActivityValidationModal: React.FC<ActivityValidationModalProps> = ({
  isOpen,
  onClose,
  aiSuggestions,
  onSave,
  loading = false
}) => {
  const [validatedData, setValidatedData] = useState<ValidatedData>({
    pessoas: [],
    sistemas: [],
    tags: [],
    pendencias: []
  });

  const [newPessoa, setNewPessoa] = useState('');
  const [newSistema, setNewSistema] = useState('');
  const [newTag, setNewTag] = useState('');
  const [newPendencia, setNewPendencia] = useState({
    descricao: '',
    responsavel: '',
    impedimento: ''
  });

  // Inicializar com sugestões da IA
  useEffect(() => {
    if (aiSuggestions) {
      setValidatedData({
        pessoas: aiSuggestions.pessoas || [],
        sistemas: aiSuggestions.sistemas || [],
        tags: aiSuggestions.tags || [],
        pendencias: aiSuggestions.pendencias || []
      });
    }
  }, [aiSuggestions]);

  const handleSave = async () => {
    await onSave(validatedData);
  };

  const handleRemovePessoa = (index: number) => {
    setValidatedData(prev => ({
      ...prev,
      pessoas: prev.pessoas.filter((_, i) => i !== index)
    }));
  };

  const handleRemoveSistema = (index: number) => {
    setValidatedData(prev => ({
      ...prev,
      sistemas: prev.sistemas.filter((_, i) => i !== index)
    }));
  };

  const handleRemoveTag = (index: number) => {
    setValidatedData(prev => ({
      ...prev,
      tags: prev.tags.filter((_, i) => i !== index)
    }));
  };

  const handleRemovePendencia = (index: number) => {
    setValidatedData(prev => ({
      ...prev,
      pendencias: prev.pendencias.filter((_, i) => i !== index)
    }));
  };

  const handleEditPendencia = (index: number, field: keyof PendencySuggestion, value: string | null) => {
    setValidatedData(prev => ({
      ...prev,
      pendencias: prev.pendencias.map((p, i) =>
        i === index ? { ...p, [field]: value } : p
      )
    }));
  };

  const handleAddPessoa = () => {
    if (newPessoa.trim()) {
      setValidatedData(prev => ({
        ...prev,
        pessoas: [...prev.pessoas, newPessoa.trim()]
      }));
      setNewPessoa('');
    }
  };

  const handleAddSistema = () => {
    if (newSistema.trim()) {
      setValidatedData(prev => ({
        ...prev,
        sistemas: [...prev.sistemas, newSistema.trim()]
      }));
      setNewSistema('');
    }
  };

  const handleAddTag = () => {
    if (newTag.trim()) {
      setValidatedData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const handleAddPendencia = () => {
    if (newPendencia.descricao.trim()) {
      setValidatedData(prev => ({
        ...prev,
        pendencias: [...prev.pendencias, {
          descricao: newPendencia.descricao.trim(),
          responsavel: newPendencia.responsavel.trim() || null,
          impedimento: newPendencia.impedimento.trim() || null
        }]
      }));
      setNewPendencia({ descricao: '', responsavel: '', impedimento: '' });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Overlay */}
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
          onKeyDown={(e) => e.key === 'Escape' && onClose()}
          role="button"
          tabIndex={0}
        />

        {/* Modal */}
        <div className="relative w-full max-w-4xl rounded-lg bg-white dark:bg-gray-800 shadow-xl">
          {/* Header */}
          <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Validar Dados Sugeridos pela IA
            </h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Revise e corrija os dados identificados antes de salvar
            </p>
          </div>

          {/* Content */}
          <div className="max-h-[60vh] overflow-y-auto px-6 py-4 space-y-6">
            {/* Pessoas */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Pessoas Identificadas</h3>
              <div className="flex flex-wrap gap-2 mb-2">
                {(validatedData.pessoas || []).map((pessoa, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 rounded-full bg-blue-100 dark:bg-blue-900/30 px-3 py-1 text-sm text-blue-800 dark:text-blue-400"
                  >
                    {pessoa}
                    <button
                      type="button"
                      onClick={() => handleRemovePessoa(index)}
                      className="ml-1 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                    >
                      ×
                    </button>
                  </span>
                ))}
                {(validatedData.pessoas || []).length === 0 && (
                  <span className="text-sm text-gray-400 dark:text-gray-500">Nenhuma pessoa identificada</span>
                )}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newPessoa}
                  onChange={(e) => setNewPessoa(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddPessoa()}
                  placeholder="Adicionar pessoa..."
                  className="flex-1 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                />
                <button
                  type="button"
                  onClick={handleAddPessoa}
                  disabled={!newPessoa.trim()}
                  className="rounded-md bg-blue-600 dark:bg-blue-500 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  +
                </button>
              </div>
            </div>

            {/* Sistemas */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sistemas Mencionados</h3>
              <div className="flex flex-wrap gap-2 mb-2">
                {(validatedData.sistemas || []).map((sistema, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 rounded-full bg-green-100 dark:bg-green-900/30 px-3 py-1 text-sm text-green-800 dark:text-green-400"
                  >
                    {sistema}
                    <button
                      type="button"
                      onClick={() => handleRemoveSistema(index)}
                      className="ml-1 text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-300"
                    >
                      ×
                    </button>
                  </span>
                ))}
                {(validatedData.sistemas || []).length === 0 && (
                  <span className="text-sm text-gray-400 dark:text-gray-500">Nenhum sistema identificado</span>
                )}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newSistema}
                  onChange={(e) => setNewSistema(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddSistema()}
                  placeholder="Adicionar sistema..."
                  className="flex-1 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                />
                <button
                  type="button"
                  onClick={handleAddSistema}
                  disabled={!newSistema.trim()}
                  className="rounded-md bg-green-600 dark:bg-green-500 px-3 py-2 text-sm font-medium text-white hover:bg-green-700 dark:hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  +
                </button>
              </div>
            </div>

            {/* Tags */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tags</h3>
              <div className="flex flex-wrap gap-2 mb-2">
                {(validatedData.tags || []).map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 rounded-full bg-purple-100 dark:bg-purple-900/30 px-3 py-1 text-sm text-purple-800 dark:text-purple-400"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(index)}
                      className="ml-1 text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-300"
                    >
                      ×
                    </button>
                  </span>
                ))}
                {(validatedData.tags || []).length === 0 && (
                  <span className="text-sm text-gray-400 dark:text-gray-500">Nenhuma tag sugerida</span>
                )}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
                  placeholder="Adicionar tag..."
                  className="flex-1 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                />
                <button
                  type="button"
                  onClick={handleAddTag}
                  disabled={!newTag.trim()}
                  className="rounded-md bg-purple-600 dark:bg-purple-500 px-3 py-2 text-sm font-medium text-white hover:bg-purple-700 dark:hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  +
                </button>
              </div>
            </div>

            {/* Pendências */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Pendências Identificadas {(validatedData.pendencias || []).length > 0 && `(${validatedData.pendencias.length})`}
              </h3>

              {/* Lista de pendências existentes (da IA) */}
              <div className="space-y-3 mb-4">
                {(validatedData.pendencias || []).map((pendencia, index) => (
                  <div key={index} className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-700/50 p-3 shadow-sm">
                    <div className="flex justify-between items-start mb-2">
                      <input
                        type="text"
                        value={pendencia.descricao}
                        onChange={(e) => handleEditPendencia(index, 'descricao', e.target.value)}
                        className="flex-1 text-sm font-medium text-gray-900 dark:text-white bg-transparent border-0 focus:ring-0 p-0"
                      />
                      <button
                        type="button"
                        onClick={() => handleRemovePendencia(index)}
                        className="ml-2 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                        title="Remover pendência"
                      >
                        ×
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                       <div>
                         <label htmlFor={`responsavel-${index}`} className="text-gray-500 dark:text-gray-400">Responsável:</label>
                         <input
                           id={`responsavel-${index}`}
                           type="text"
                           value={pendencia.responsavel || ''}
                           onChange={(e) => handleEditPendencia(index, 'responsavel', e.target.value || null)}
                           className="mt-1 block w-full rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                           placeholder="Nome do responsável"
                         />
                       </div>
                       <div>
                         <label htmlFor={`impedimento-${index}`} className="text-gray-500 dark:text-gray-400">Impedimento:</label>
                         <input
                           id={`impedimento-${index}`}
                           type="text"
                           value={pendencia.impedimento || ''}
                           onChange={(e) => handleEditPendencia(index, 'impedimento', e.target.value || null)}
                           className="mt-1 block w-full rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                           placeholder="Descrição do bloqueio"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                {(validatedData.pendencias || []).length === 0 && (
                  <div className="text-center py-4 text-sm text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-dashed border-gray-300 dark:border-gray-600">
                    💡 Nenhuma pendência identificada pela IA. Você pode adicionar manualmente abaixo.
                  </div>
                )}
              </div>

              {/* Adicionar nova pendência */}
              <div className="rounded-lg border border-dashed border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/30 p-4">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">➕ Adicionar Nova Pendência</h4>
                <div className="space-y-3">
                  <div>
                    <input
                      type="text"
                      value={newPendencia.descricao}
                      onChange={(e) => setNewPendencia(prev => ({ ...prev, descricao: e.target.value }))}
                      placeholder="Descrição da pendência..."
                      className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <input
                        type="text"
                        value={newPendencia.responsavel}
                        onChange={(e) => setNewPendencia(prev => ({ ...prev, responsavel: e.target.value }))}
                        placeholder="Responsável (opcional)"
                        className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                      />
                    </div>
                    <div>
                      <input
                        type="text"
                        value={newPendencia.impedimento}
                        onChange={(e) => setNewPendencia(prev => ({ ...prev, impedimento: e.target.value }))}
                        placeholder="Impedimento (opcional)"
                        className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="button"
                      onClick={handleAddPendencia}
                      disabled={!newPendencia.descricao.trim()}
                      className="rounded-md bg-orange-600 dark:bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-700 dark:hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Adicionar Pendência
                    </button>
                  </div>
                </div>
              </div>
            </div>


          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={loading}
              className="rounded-md bg-blue-600 dark:bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? 'Salvando...' : 'Salvar Dados Validados'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
