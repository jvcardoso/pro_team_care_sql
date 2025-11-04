/**
 * Componente de Card do Kanban Board
 */

import React from 'react';
import { Draggable } from '@hello-pangea/dnd';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { Card } from '../../services/kanbanService';

interface KanbanCardProps {
  card: Card;
  index: number;
  onClick: (card: Card) => void;
}

export const KanbanCard: React.FC<KanbanCardProps> = ({ card, index, onClick }) => {
  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'Urgente': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      'Alta': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      'Média': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'Baixa': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    };
    return colors[priority] || colors['Média'];
  };

  const getSubStatusIcon = (subStatus: string | null) => {
    if (!subStatus) return null;

    if (subStatus.includes('Bloqueado')) {
      return (
        <span className="text-red-500" title={subStatus}>
          🚫
        </span>
      );
    }

    if (subStatus.includes('Aguardando')) {
      return (
        <span className="text-yellow-500" title={subStatus}>
          ⏳
        </span>
      );
    }

    return null;
  };

  return (
    <Draggable draggableId={`card-${card.CardID}`} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          onClick={() => onClick(card)}
          className={`
            bg-white dark:bg-gray-800 
            rounded-lg shadow-sm 
            p-4 mb-3 
            cursor-pointer
            border border-gray-200 dark:border-gray-700
            hover:shadow-md
            transition-shadow
            ${snapshot.isDragging ? 'shadow-lg rotate-2' : ''}
          `}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white flex-1 pr-2">
              {card.Title}
            </h3>
            {getSubStatusIcon(card.SubStatus)}
          </div>

          {/* Description */}
          {card.Description && (
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
              {card.Description}
            </p>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between">
            {/* Priority Badge */}
            <span className={`
              inline-flex items-center px-2 py-1 
              rounded-full text-xs font-medium
              ${getPriorityColor(card.Priority)}
            `}>
              {card.Priority}
            </span>

            {/* Due Date */}
            {card.DueDate && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                📅 {format(new Date(card.DueDate), 'dd/MM', { locale: ptBR })}
              </span>
            )}
          </div>

          {/* Sub Status Badge */}
          {card.SubStatus && (
            <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
              <span className="text-xs text-gray-600 dark:text-gray-400">
                {card.SubStatus}
              </span>
            </div>
          )}
        </div>
      )}
    </Draggable>
  );
};
