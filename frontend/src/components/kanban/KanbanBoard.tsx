/**
 * Componente principal do Kanban Board
 */

import React, { useEffect, useState } from 'react';
import { DragDropContext, DropResult } from '@hello-pangea/dnd';
import { KanbanColumn } from './KanbanColumn';
import { useKanban } from '../../hooks/useKanban';
import { Card } from '../../services/kanbanService';

interface KanbanBoardProps {
  onCardClick: (card: Card) => void;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({ onCardClick }) => {
  const { board, loading, loadBoard, moveCard } = useKanban();

  useEffect(() => {
    loadBoard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Carregar apenas uma vez ao montar

  const handleDragEnd = async (result: DropResult) => {
    const { destination, source, draggableId } = result;

    // Dropped outside
    if (!destination) return;

    // Dropped in same position
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    // Extract card ID and column IDs
    const cardId = parseInt(draggableId.replace('card-', ''));
    const destColumnId = parseInt(destination.droppableId.replace('column-', ''));
    const newPosition = destination.index;

    // Move card to new column with position
    const success = await moveCard(cardId, destColumnId, newPosition);
    
    // Recarregar board para garantir sincronização
    if (success) {
      await loadBoard();
    }
  };

  if (loading && !board) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <svg
            className="animate-spin h-10 w-10 text-blue-600 mx-auto mb-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <p className="text-gray-600 dark:text-gray-400">Carregando board...</p>
        </div>
      </div>
    );
  }

  if (!board) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-gray-600 dark:text-gray-400">Nenhum board disponível</p>
      </div>
    );
  }

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {board.columns.map(column => (
          <KanbanColumn
            key={column.ColumnID}
            column={column}
            cards={board.cards_by_column[column.ColumnID] || []}
            onCardClick={onCardClick}
          />
        ))}
      </div>
    </DragDropContext>
  );
};
