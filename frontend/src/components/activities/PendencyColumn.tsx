/**
 * Coluna do board Kanban de pendências
 */

import React from 'react';
import { Pendency } from '../../services/pendencyService';
import { PendencyCard } from './PendencyCard';

interface PendencyColumnProps {
  title: string;
  status: string;
  pendencies: Pendency[];
  onStatusChange: (pendencyId: number, newStatus: string) => Promise<void>;
  onEdit?: (pendency: Pendency) => void;
}

export const PendencyColumn: React.FC<PendencyColumnProps> = ({
  title,
  status,
  pendencies,
  onStatusChange,
  onEdit
}) => {
  const getColumnColor = (status: string) => {
    switch (status) {
      case 'Pendente':
        return 'border-yellow-300 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-900/20';
      case 'Cobrado':
        return 'border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20';
      case 'Resolvido':
        return 'border-green-300 dark:border-green-700 bg-green-50 dark:bg-green-900/20';
      default:
        return 'border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800';
    }
  };

  const filteredPendencies = (pendencies || []).filter(p => p.Status === status);

  return (
    <div className={`flex-1 min-w-[300px] rounded-lg border-2 p-4 ${getColumnColor(status)}`}>
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {filteredPendencies.length} {filteredPendencies.length === 1 ? 'item' : 'itens'}
        </span>
      </div>

      {/* Cards */}
      <div className="space-y-3 max-h-[calc(100vh-300px)] overflow-y-auto">
        {filteredPendencies.map(pendency => (
          <PendencyCard
            key={pendency.PendencyID}
            pendency={pendency}
            onStatusChange={onStatusChange}
            onEdit={onEdit}
          />
        ))}
        {filteredPendencies.length === 0 && (
          <div className="text-center py-8 text-gray-400 dark:text-gray-500 text-sm">
            Nenhuma pendência neste status
          </div>
        )}
      </div>
    </div>
  );
};
