/**
 * Página de board Kanban de pendências
 */

import React, { useEffect, useState } from 'react';
import { Pendency, pendencyService } from '../services/pendencyService';
import { PendencyColumn } from '../components/activities/PendencyColumn';
import { useToast } from '@/components/ui/use-toast';

export const PendencyBoardPage: React.FC = () => {
  const { toast } = useToast();
  const [pendencies, setPendencies] = useState<Pendency[]>([]);
  const [loading, setLoading] = useState(false);

  const loadPendencies = async () => {
    setLoading(true);
    try {
      const data = await pendencyService.list();
      setPendencies(data || []);
    } catch {
      toast({
        title: 'Erro',
        description: 'Erro ao carregar pendências',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPendencies();
  }, []);

  const handleStatusChange = async (pendencyId: number, newStatus: string) => {
    try {
      await pendencyService.updateStatus(pendencyId, newStatus);

      toast({
        title: 'Sucesso',
        description: 'Status atualizado com sucesso',
        variant: 'default'
      });

      // Recarregar lista
      await loadPendencies();
    } catch {
      toast({
        title: 'Erro',
        description: 'Erro ao atualizar status',
        variant: 'destructive'
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Board de Pendências
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Gerencie suas pendências em um board Kanban
          </p>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">Carregando pendências...</p>
          </div>
        )}

        {/* Board Kanban */}
        {!loading && (
          <div className="flex gap-4 overflow-x-auto pb-4">
            <PendencyColumn
              title="Pendente"
              status="Pendente"
              pendencies={pendencies}
              onStatusChange={handleStatusChange}
            />
            <PendencyColumn
              title="Cobrado"
              status="Cobrado"
              pendencies={pendencies}
              onStatusChange={handleStatusChange}
            />
            <PendencyColumn
              title="Resolvido"
              status="Resolvido"
              pendencies={pendencies}
              onStatusChange={handleStatusChange}
            />
          </div>
        )}
      </div>
    </div>
  );
};
