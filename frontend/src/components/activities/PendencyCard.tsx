/**
 * Card de pendência para board Kanban
 */

import React from 'react';
import { Pendency } from '../../services/pendencyService';

interface PendencyCardProps {
  pendency: Pendency;
  onStatusChange: (pendencyId: number, newStatus: string) => Promise<void>;
  onEdit?: (pendency: Pendency) => void;
}

export const PendencyCard: React.FC<PendencyCardProps> = ({
  pendency,
  onStatusChange,
  onEdit
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Pendente':
        return 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-300 border-yellow-200 dark:border-yellow-700';
      case 'Cobrado':
        return 'bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-700';
      case 'Resolvido':
        return 'bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 border-green-200 dark:border-green-700';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-600';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <div className={`rounded-lg border-2 p-4 shadow-sm hover:shadow-md transition-shadow ${getStatusColor(pendency.Status)}`}>
      {/* Descrição */}
      <p className="text-sm font-medium mb-3">
        {pendency.Description}
      </p>

      {/* Responsável */}
      {pendency.Owner && (
        <div className="mb-2">
          <span className="text-xs font-semibold">Responsável:</span>
          <span className="ml-1 text-xs">{pendency.Owner}</span>
        </div>
      )}

      {/* Impedimento */}
      {pendency.Impediment && (
        <div className="mb-2 p-2 bg-red-50 dark:bg-red-900/30 rounded border border-red-200 dark:border-red-700">
          <span className="text-xs font-semibold text-red-800 dark:text-red-400">⚠️ Impedimento:</span>
          <p className="text-xs text-red-700 dark:text-red-300 mt-1">{pendency.Impediment}</p>
        </div>
      )}

      {/* Data de criação */}
      <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
        Criado em: {formatDate(pendency.CreatedAt)}
      </div>

      {/* Ações */}
      <div className="flex gap-2">
        {pendency.Status === 'Pendente' && (
          <button
            onClick={() => onStatusChange(pendency.PendencyID, 'Cobrado')}
            className="flex-1 text-xs py-1 px-2 rounded bg-blue-600 dark:bg-blue-500 text-white hover:bg-blue-700 dark:hover:bg-blue-600"
          >
            Cobrar
          </button>
        )}
        {pendency.Status === 'Cobrado' && (
          <button
            onClick={() => onStatusChange(pendency.PendencyID, 'Resolvido')}
            className="flex-1 text-xs py-1 px-2 rounded bg-green-600 dark:bg-green-500 text-white hover:bg-green-700 dark:hover:bg-green-600"
          >
            Resolver
          </button>
        )}
        {pendency.Status === 'Resolvido' && pendency.ResolvedAt && (
          <div className="text-xs text-green-700 dark:text-green-400">
            ✓ Resolvido em {formatDate(pendency.ResolvedAt)}
          </div>
        )}
        {onEdit && (
          <button
            onClick={() => onEdit(pendency)}
            className="text-xs py-1 px-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600"
          >
            Editar
          </button>
        )}
      </div>
    </div>
  );
};
