/**
 * Página de criação de atividades com análise de IA
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ActivityForm } from '../components/activities/ActivityForm';
import { ActivityValidationModal } from '../components/activities/ActivityValidationModal';
import { useActivities } from '../hooks/useActivities';

export const ActivityCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const {
    loading,
    aiSuggestions,
    createActivity,
    saveValidatedData,
    clearAISuggestions
  } = useActivities();

  const [showValidationModal, setShowValidationModal] = useState(false);
  const [currentActivityId, setCurrentActivityId] = useState<number | null>(null);

  const handleCreateActivity = async (data: any, images: File[]) => {
    const result = await createActivity(data, images);

    if (result) {
      setCurrentActivityId(result.ActivityID);
      setShowValidationModal(true);
    }
  };

  const handleSaveValidated = async (validatedData: any) => {
    if (!currentActivityId) return;

    const success = await saveValidatedData(currentActivityId, validatedData);

    if (success) {
      setShowValidationModal(false);
      clearAISuggestions();
      navigate('/admin/activities');
    }
  };

  const handleCloseModal = () => {
    setShowValidationModal(false);
    clearAISuggestions();
    navigate('/admin/activities');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Nova Atividade
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Registre uma nova atividade e deixe a IA analisar o conteúdo para sugerir pessoas, sistemas e pendências.
          </p>
        </div>

        {/* Formulário */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <ActivityForm
            onSubmit={handleCreateActivity}
            loading={loading}
          />
        </div>

        {/* Modal de Validação */}
        <ActivityValidationModal
          isOpen={showValidationModal}
          onClose={handleCloseModal}
          aiSuggestions={aiSuggestions}
          onSave={handleSaveValidated}
          loading={loading}
        />
      </div>
    </div>
  );
};
