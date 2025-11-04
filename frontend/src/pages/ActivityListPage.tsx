/**
 * Página de listagem de atividades
 */

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useActivities } from '../hooks/useActivities';

export const ActivityListPage: React.FC = () => {
  const navigate = useNavigate();
  const { activities, loading, listActivities, deleteActivity } = useActivities();
  const [deletingId, setDeletingId] = React.useState<number | null>(null);

  useEffect(() => {
    listActivities();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      'Pendente': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      'Em Andamento': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
      'Concluído': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      'Cancelado': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    };

    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  };

  const handleDelete = React.useCallback(async (activityId: number) => {
    if (window.confirm('Tem certeza que deseja excluir esta atividade?')) {
      setDeletingId(activityId);
      await deleteActivity(activityId);
      setDeletingId(null);
    }
  }, [deleteActivity]);



  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Minhas Atividades
            </h1>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Histórico de atividades registradas e analisadas pela IA
            </p>
          </div>
          <button
            onClick={() => navigate('/admin/activities/new')}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
          >
            + Nova Atividade
          </button>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">Carregando atividades...</p>
          </div>
        )}

        {/* Lista */}
        {!loading && (
          <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {(activities || []).map((activity) => (
                <li
                  key={activity.ActivityID}
                  className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {activity.Title}
                      </h3>
                      <div className="mt-2 flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                        <span>Criado em: {formatDate(activity.CreationDate)}</span>
                        {activity.DueDate && (
                          <span>Prazo: {formatDate(activity.DueDate)}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(activity.Status)}`}>
                        {activity.Status}
                      </span>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => navigate(`/admin/activities/${activity.ActivityID}/edit`)}
                          className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 p-1"
                          title="Editar atividade"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDelete(activity.ActivityID)}
                          disabled={deletingId === activity.ActivityID}
                          className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 p-1 disabled:opacity-50"
                          title="Excluir atividade"
                        >
                          {deletingId === activity.ActivityID ? (
                            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                          ) : (
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
              {(activities || []).length === 0 && (
                <li className="px-6 py-12 text-center">
                  <p className="text-gray-500 dark:text-gray-400">Nenhuma atividade registrada ainda.</p>
                  <button
            onClick={() => navigate('/admin/activities/new')}
                    className="mt-4 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
                  >
                    Criar primeira atividade
                  </button>
                </li>
              )}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
