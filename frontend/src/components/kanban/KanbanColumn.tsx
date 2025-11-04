/**
 * Componente de Coluna do Kanban Board
 */

import React from 'react';
import { Droppable } from '@hello-pangea/dnd';
import { KanbanCard } from './KanbanCard';
import { CardColumn, Card } from '../../services/kanbanService';

interface KanbanColumnProps {
  column: CardColumn;
  cards: Card[];
  onCardClick: (card: Card) => void;
}

export const KanbanColumn: React.FC<KanbanColumnProps> = ({ column, cards, onCardClick }) => {
  return (
    <div className="flex flex-col bg-gray-50 dark:bg-gray-900 rounded-lg p-4 h-full">
      {/* Column Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: column.Color }}
          />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            {column.ColumnName}
          </h2>
        </div>
        <span className="bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs font-medium px-2 py-1 rounded-full">
          {cards?.length || 0}
        </span>
      </div>

      {/* Droppable Area */}
      <Droppable droppableId={`column-${column.ColumnID}`}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`
              flex-1 
              min-h-[200px]
              rounded-lg
              transition-colors
              ${snapshot.isDraggingOver ? 'bg-blue-50 dark:bg-blue-900/20' : ''}
            `}
          >
            {/* Cards */}
            {(cards || []).map((card, index) => (
              <KanbanCard
                key={card.CardID}
                card={card}
                index={index}
                onClick={onCardClick}
              />
            ))}
            {provided.placeholder}

            {/* Empty State */}
            {(!cards || cards.length === 0) && !snapshot.isDraggingOver && (
              <div className="flex items-center justify-center h-32 text-gray-400 dark:text-gray-600 text-sm">
                Nenhum card
              </div>
            )}
          </div>
        )}
      </Droppable>
    </div>
  );
};
