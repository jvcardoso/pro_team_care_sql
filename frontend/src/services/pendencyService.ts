/**
 * Serviço de Pendências - Módulo de Gestão de Atividades com IA
 * @module pendencyService
 */

import { api } from './api';

// ========================================
// INTERFACES
// ========================================

export interface Pendency {
  PendencyID: number;
  ActivityID: number;
  Description: string;
  Owner: string | null;
  Status: string;
  Impediment: string | null;
  CreatedAt: string;
  ResolvedAt: string | null;
}

export interface PendencyCreateData {
  ActivityID: number;
  Description: string;
  Owner?: string | null;
  Status?: string;
  Impediment?: string | null;
}

export interface PendencyUpdateData {
  Description?: string;
  Owner?: string | null;
  Status?: string;
  Impediment?: string | null;
  ResolvedAt?: string | null;
}

// ========================================
// FUNÇÕES DO SERVIÇO
// ========================================

/**
 * Cria nova pendência manualmente
 */
export const createPendency = async (
  data: PendencyCreateData
): Promise<Pendency> => {
  const response = await api.post('/api/v1/pendencies', data);
  return response.data;
};

/**
 * Lista pendências da empresa (com filtro opcional por status)
 */
export const listPendencies = async (
  status?: string,
  skip: number = 0,
  limit: number = 100
): Promise<Pendency[]> => {
  const params: any = { skip, limit };
  if (status) {
    params.status = status;
  }

  const response = await api.get('/api/v1/pendencies', { params });
  return response.data || [];
};

/**
 * Busca pendência por ID
 */
export const getPendency = async (
  pendencyId: number
): Promise<Pendency> => {
  const response = await api.get(`/api/v1/pendencies/${pendencyId}`);
  return response.data;
};

/**
 * Atualiza pendência completa
 */
export const updatePendency = async (
  pendencyId: number,
  data: PendencyUpdateData
): Promise<Pendency> => {
  const response = await api.put(`/api/v1/pendencies/${pendencyId}`, data);
  return response.data;
};

/**
 * Atualiza apenas o status da pendência
 */
export const updatePendencyStatus = async (
  pendencyId: number,
  status: string
): Promise<Pendency> => {
  const response = await api.patch(
    `/api/v1/pendencies/${pendencyId}/status`,
    null,
    { params: { status } }
  );
  return response.data;
};

/**
 * Hook helper para usar no componente (opcional)
 */
export const pendencyService = {
  create: createPendency,
  list: listPendencies,
  get: getPendency,
  update: updatePendency,
  updateStatus: updatePendencyStatus
};
