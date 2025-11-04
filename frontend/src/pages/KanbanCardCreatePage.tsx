/**
 * Página de criação de card com IA
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useKanban } from '../hooks/useKanban';
import { CardCreateData } from '../services/kanbanService';

export const KanbanCardCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const { createCard, saveValidatedData, loading, aiSuggestions } = useKanban();

  const [formData, setFormData] = useState<CardCreateData>({
    Title: '',
    OriginalText: '',
    ColumnID: 1, // Backlog
    Priority: 'Média',
    DueDate: null
  });

  const [currentCardId, setCurrentCardId] = useState<number | null>(null);
  const [showValidationModal, setShowValidationModal] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value || null }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const result = await createCard(formData);
    
    if (result) {
      setCurrentCardId(result.CardID);
      setShowValidationModal(true);
    }
  };

  const handleSaveValidated = async () => {
    if (!currentCardId || !aiSuggestions) return;

    const success = await saveValidatedData(currentCardId, aiSuggestions);
    
    if (success) {
      navigate('/admin/kanban');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            ➕ Novo Card
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Crie um novo card e deixe a IA analisar o conteúdo
          </p>
        </div>

        {/* Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title */}
            <div>
              <label htmlFor="Title" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Título *
              </label>
              <input
                type="text"
                id="Title"
                name="Title"
                value={formData.Title}
                onChange={handleChange}
                required
                className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="Ex: Aprovações Sprint 10"
              />
            </div>

            {/* Priority */}
            <div>
              <label htmlFor="Priority" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Prioridade
              </label>
              <select
                id="Priority"
                name="Priority"
                value={formData.Priority}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="Baixa">Baixa</option>
                <option value="Média">Média</option>
                <option value="Alta">Alta</option>
                <option value="Urgente">Urgente</option>
              </select>
            </div>

            {/* Due Date */}
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

            {/* Original Text */}
            <div>
              <label htmlFor="OriginalText" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Conteúdo *
              </label>
              <textarea
                id="OriginalText"
                name="OriginalText"
                value={formData.OriginalText}
                onChange={handleChange}
                required
                rows={8}
                className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="Cole aqui o conteúdo para a IA analisar..."
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                A IA analisará este conteúdo para sugerir pessoas, sistemas, tags e sub-tarefas.
              </p>
            </div>

            {/* Submit */}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => navigate('/admin/kanban')}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analisando com IA...
                  </>
                ) : (
                  'Criar e Analisar'
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Validation Modal (Simple) */}
        {showValidationModal && aiSuggestions && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                ✅ Análise da IA Concluída
              </h2>

              <div className="space-y-4">
                {/* Description */}
                {aiSuggestions.description && (
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Descrição:</h3>
                    <p className="text-gray-700 dark:text-gray-300">{aiSuggestions.description}</p>
                  </div>
                )}

                {/* Priority */}
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Prioridade:</h3>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                    {aiSuggestions.priority}
                  </span>
                </div>

                {/* Assignees */}
                {aiSuggestions.assignees?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Pessoas:</h3>
                    <div className="flex flex-wrap gap-2">
                      {aiSuggestions.assignees.map((person: string, idx: number) => (
                        <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          {person}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Tags */}
                {aiSuggestions.tags?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Tags:</h3>
                    <div className="flex flex-wrap gap-2">
                      {aiSuggestions.tags.map((tag: string, idx: number) => (
                        <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Movements */}
                {aiSuggestions.movements?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Sub-tarefas ({aiSuggestions.movements.length}):</h3>
                    <ul className="space-y-2">
                      {aiSuggestions.movements.map((mov: any, idx: number) => (
                        <li key={idx} className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                          <p className="font-medium text-gray-900 dark:text-white">{mov.subject}</p>
                          {mov.description && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{mov.description}</p>
                          )}
                          {mov.estimated_time && (
                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                              ⏱️ {mov.estimated_time} minutos
                            </p>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={() => setShowValidationModal(false)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSaveValidated}
                  disabled={loading}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Salvando...' : 'Salvar Dados'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
