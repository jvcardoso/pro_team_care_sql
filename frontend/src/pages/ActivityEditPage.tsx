/**
 * Página de edição de atividades
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ActivityForm } from '../components/activities/ActivityForm';
import { useActivities } from '../hooks/useActivities';
import { Activity } from '../services/activityService';

export const ActivityEditPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { loading, getActivity, updateActivity } = useActivities();

  const [activity, setActivity] = useState<Activity | null>(null);
  const [loadingActivity, setLoadingActivity] = useState(true);

  useEffect(() => {
    const loadActivity = async () => {
      if (!id) return;

      try {
        const activityData = await getActivity(parseInt(id));
        if (activityData) {
          setActivity(activityData);
        }
      } catch (error) {
        console.error('Erro ao carregar atividade:', error);
      } finally {
        setLoadingActivity(false);
      }
    };

    loadActivity();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]); // Remover getActivity das dependências para evitar loop

  const handleUpdateActivity = async (data: any, images: File[]) => {
    if (!id) return;

    // Se tem RawText, atualiza com processamento de IA
    // Senão, apenas atualiza campos básicos
    const updateData = data.RawText ? {
      Title: data.Title,
      Status: data.Status,
      DueDate: data.DueDate,
      RawText: data.RawText
    } : {
      Title: data.Title,
      Status: data.Status,
      DueDate: data.DueDate
    };

    const success = await updateActivity(parseInt(id), updateData);

    if (success) {
      navigate('/admin/activities');
    }
  };

  if (loadingActivity) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">Carregando atividade...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!activity) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <p className="text-red-500">Atividade não encontrada</p>
            <button
              onClick={() => navigate('/admin/activities')}
              className="mt-4 text-blue-600 hover:text-blue-700 dark:text-blue-400"
            >
              Voltar para lista
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Editar Atividade
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Atualize as informações da atividade.
          </p>
        </div>

        {/* Formulário */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <ActivityForm
            onSubmit={handleUpdateActivity}
            loading={loading}
            initialData={{
              Title: activity.Title,
              Status: activity.Status,
              DueDate: activity.DueDate,
              RawText: null // Permitir que usuário adicione novo conteúdo para reprocessar
            }}
            isEdit={true}
          />
        </div>
      </div>
    </div>
  );
};