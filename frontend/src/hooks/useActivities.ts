/**
 * Hook customizado para gerenciar atividades com IA
 * @module useActivities
 */

import { useState, useCallback } from 'react';
import {
  Activity,
  ActivityWithAI,
  ActivityCreateData,
  ValidatedData,
  activityService
} from '../services/activityService';
import { useToast } from '@/components/ui/use-toast';

interface UseActivitiesState {
  activities: Activity[];
  loading: boolean;
  error: string | null;
  currentActivity: ActivityWithAI | null;
  aiSuggestions: any | null;
}

export const useActivities = () => {
  const { toast } = useToast();

  const [state, setState] = useState<UseActivitiesState>({
    activities: [],
    loading: false,
    error: null,
    currentActivity: null,
    aiSuggestions: null
  });

  /**
   * Cria nova atividade e recebe sugestões da IA
   */
  const createActivity = useCallback(async (data: ActivityCreateData, images: File[] = []) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const result = await activityService.create(data, images);

      setState(prev => ({
        ...prev,
        currentActivity: result,
        aiSuggestions: result.ai_suggestions || null,
        loading: false
      }));

      toast({
        title: 'Atividade criada!',
        description: `Análise da IA concluída${images.length > 0 ? ` (${images.length} imagem${images.length > 1 ? 's' : ''} analisada${images.length > 1 ? 's' : ''})` : ''}. Valide os dados sugeridos.`,
        variant: 'default'
      });

      return result;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao criar atividade';

      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMsg
      }));

      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      throw error;
    }
  }, [toast]);

  /**
   * Salva dados validados pelo usuário
   */
  const saveValidatedData = useCallback(async (
    activityId: number,
    validatedData: ValidatedData
  ) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      await activityService.saveValidated(activityId, validatedData);

      setState(prev => ({
        ...prev,
        loading: false,
        aiSuggestions: null,
        currentActivity: null
      }));

      toast({
        title: 'Sucesso!',
        description: 'Dados validados salvos com sucesso.',
        variant: 'default'
      });

      return true;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao salvar dados';

      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMsg
      }));

      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return false;
    }
  }, [toast]);

  /**
   * Lista atividades
   */
  const listActivities = useCallback(async (
    skip: number = 0,
    limit: number = 100
  ) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const activities = await activityService.list(skip, limit);

      setState(prev => ({
        ...prev,
        activities: activities || [],
        loading: false
      }));

      return activities;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao listar atividades';

      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMsg,
        activities: []
      }));

      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return [];
    }
  }, [toast]);

  /**
   * Busca atividade por ID
   */
  const getActivity = useCallback(async (activityId: number) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const activity = await activityService.get(activityId);

      setState(prev => ({
        ...prev,
        currentActivity: activity as ActivityWithAI,
        loading: false
      }));

      return activity;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao buscar atividade';

      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMsg
      }));

      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return null;
    }
  }, [toast]);

  /**
   * Deleta atividade
   */
  const deleteActivity = useCallback(async (activityId: number) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      await activityService.delete(activityId);

      // Remove da lista local
      setState(prev => ({
        ...prev,
        activities: prev.activities.filter(a => a.ActivityID !== activityId),
        loading: false
      }));

      toast({
        title: 'Sucesso!',
        description: 'Atividade excluída com sucesso.',
        variant: 'default'
      });

      return true;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao excluir atividade';

      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMsg
      }));

      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return false;
    }
  }, [toast]);

  /**
   * Atualiza atividade
   */
  const updateActivity = useCallback(async (activityId: number, data: any) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      await activityService.update(activityId, data);

      // Atualiza na lista local
      setState(prev => ({
        ...prev,
        activities: prev.activities.map(a => 
          a.ActivityID === activityId ? { ...a, ...data } : a
        ),
        loading: false
      }));

      toast({
        title: 'Sucesso!',
        description: 'Atividade atualizada com sucesso.',
        variant: 'default'
      });

      return true;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao atualizar atividade';

      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMsg
      }));

      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return false;
    }
  }, [toast]);

  /**
    * Limpa sugestões da IA
    */
  const clearAISuggestions = useCallback(() => {
    setState(prev => ({
      ...prev,
      aiSuggestions: null,
      currentActivity: null
    }));
  }, []);

  return {
    // Estado
    ...state,

    // Ações
    createActivity,
    saveValidatedData,
    listActivities,
    getActivity,
    updateActivity,
    deleteActivity,
    clearAISuggestions
  };
};
