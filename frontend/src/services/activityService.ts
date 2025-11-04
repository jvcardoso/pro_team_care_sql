/**
 * Serviço de Atividades - Módulo de Gestão de Atividades com IA
 * @module activityService
 */

import { api } from './api';

// ========================================
// INTERFACES
// ========================================

export interface Activity {
  ActivityID: number;
  UserID: number;
  CompanyID: number;
  Title: string;
  Status: string;
  CreationDate: string;
  DueDate: string | null;
  IsDeleted: boolean;
  DeletedAt: string | null;
}

export interface ActivityWithAI extends Activity {
  ai_suggestions?: AISuggestions;
}

export interface AISuggestions {
  pessoas: string[];
  sistemas: string[];
  datas: string[];
  tags: string[];
  pendencias: PendencySuggestion[];
}

export interface PendencySuggestion {
  descricao: string;
  responsavel: string | null;
  impedimento: string | null;
}

export interface ActivityCreateData {
  Title: string;
  Status: string;
  DueDate?: string | null;
  RawText?: string;
  RawImagePath?: string;
}

export interface ActivityUpdateData {
  Title?: string;
  Status?: string;
  DueDate?: string | null;
}

export interface ValidatedData {
  pessoas: string[];
  sistemas: string[];
  tags: string[];
  pendencias: PendencySuggestion[];
}

// ========================================
// FUNÇÕES DO SERVIÇO
// ========================================

/**
 * Cria nova atividade e retorna com sugestões da IA
 * Se houver imagens, faz upload primeiro e adiciona os paths
 */
export const createActivity = async (
  data: ActivityCreateData,
  images: File[] = []
): Promise<ActivityWithAI> => {
  let imagePaths: string[] = [];

  // 1. Upload de imagens (se houver)
  if (images.length > 0) {
    const formData = new FormData();
    images.forEach(img => formData.append('files', img));

    const uploadResponse = await api.post('/api/v1/uploads/images', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    imagePaths = uploadResponse.data.paths || [];
  }

  // 2. Criar atividade com paths das imagens
  const activityData = {
    ...data,
    image_paths: imagePaths.length > 0 ? imagePaths : undefined
  };

  const response = await api.post('/api/v1/activities', activityData);
  return response.data;
};

/**
 * Salva dados validados pelo usuário
 */
export const saveValidatedData = async (
  activityId: number,
  validatedData: ValidatedData
): Promise<{ message: string }> => {
  const response = await api.post(
    `/api/v1/activities/${activityId}/validate`,
    validatedData
  );
  return response.data;
};

/**
 * Lista atividades da empresa
 */
export const listActivities = async (
  skip: number = 0,
  limit: number = 100
): Promise<Activity[]> => {
  const response = await api.get('/api/v1/activities', {
    params: { skip, limit }
  });
  return response.data || [];
};

/**
 * Busca atividade por ID
 */
export const getActivity = async (
  activityId: number
): Promise<Activity> => {
  const response = await api.get(`/api/v1/activities/${activityId}`);
  return response.data;
};

/**
 * Atualiza atividade
 */
export const updateActivity = async (
  activityId: number,
  data: ActivityUpdateData
): Promise<Activity> => {
  const response = await api.put(`/api/v1/activities/${activityId}`, data);
  return response.data;
};

/**
 * Deleta atividade (soft delete)
 */
export const deleteActivity = async (
  activityId: number
): Promise<void> => {
  await api.delete(`/api/v1/activities/${activityId}`);
};

/**
  * Hook helper para usar no componente (opcional)
  */
export const activityService = {
  create: createActivity,
  saveValidated: saveValidatedData,
  list: listActivities,
  get: getActivity,
  update: updateActivity,
  delete: deleteActivity
};
