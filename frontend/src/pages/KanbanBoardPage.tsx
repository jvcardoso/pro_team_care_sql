/**
 * Página principal do Kanban Board
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KanbanBoard } from '../components/kanban/KanbanBoard';
import { CardDetailModal } from '../components/kanban/CardDetailModal';
import { ImportBMModal } from '../components/kanban/ImportBMModal';
import { Card } from '../services/kanbanService';

export const KanbanBoardPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [showImportModal, setShowImportModal] = useState(false);

  const handleCardClick = (card: Card) => {
    setSelectedCard(card);
  };

  const handleNewCard = () => {
    navigate('/admin/kanban/new');
  };

  const handleImport = () => {
    setShowImportModal(true);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                📋 Kanban Board
              </h1>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Gerencie suas atividades com drag & drop
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleImport}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg
                  className="w-5 h-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                Importar BM
              </button>

              <button
                onClick={handleNewCard}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg
                  className="w-5 h-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Novo Card
              </button>
            </div>
          </div>
        </div>

        {/* Board */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <KanbanBoard onCardClick={handleCardClick} />
        </div>



        {/* Modal de Detalhes */}
        {selectedCard && (
          <CardDetailModal
            card={selectedCard}
            onClose={() => setSelectedCard(null)}
          />
        )}

        {/* Modal de Importação */}
        {showImportModal && (
          <ImportBMModal
            onClose={() => setShowImportModal(false)}
            onSuccess={() => window.location.reload()}
          />
        )}
      </div>
    </div>
  );
};
