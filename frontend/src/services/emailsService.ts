/**
 * Emails Service - API client para gerenciamento de e-mails
 *
 * Provê operações CRUD para e-mails com validações e auditoria LGPD.
 */

import { api } from './api';

export interface Email {
  id: number;
  email_address: string;
  type: 'work' | 'personal' | 'billing' | 'contact';
  is_principal: boolean;
  is_active: boolean;
  verified_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface EmailCreate {
  email_address: string;
  type?: 'work' | 'personal' | 'billing' | 'contact';
  is_principal?: boolean;
  is_active?: boolean;
}

export interface EmailUpdate {
  email_address?: string;
  type?: 'work' | 'personal' | 'billing' | 'contact';
  is_principal?: boolean;
  is_active?: boolean;
}

/**
 * Cria novo e-mail para uma entidade
 */
export async function createEmail(
  entityType: string,
  entityId: number,
  data: EmailCreate
): Promise<Email> {
  const response = await api.post(`/${entityType}/${entityId}/emails`, data);
  return response.data;
}

/**
 * Busca e-mail por ID
 */
export async function getEmail(emailId: number): Promise<Email> {
  const response = await api.get(`/emails/${emailId}`);
  return response.data;
}

/**
 * Lista todos os e-mails de uma entidade
 */
export async function listEmails(
  entityType: string,
  entityId: number
): Promise<Email[]> {
  const response = await api.get(`/${entityType}/${entityId}/emails`);
  return response.data;
}

/**
 * Atualiza e-mail existente
 */
export async function updateEmail(
  emailId: number,
  data: EmailUpdate
): Promise<Email> {
  const response = await api.put(`/emails/${emailId}`, data);
  return response.data;
}

/**
 * Deleta e-mail (soft delete)
 */
export async function deleteEmail(emailId: number): Promise<void> {
  await api.delete(`/emails/${emailId}`);
}

/**
 * Marca e-mail como principal
 */
export async function setPrincipalEmail(emailId: number): Promise<void> {
  await api.post(`/emails/${emailId}/set-principal`);
}

/**
 * Envia e-mail de verificação
 */
export async function sendVerificationEmail(emailId: number): Promise<{ message: string }> {
  const response = await api.post(`/emails/${emailId}/send-verification`);
  return response.data;
}

export const emailsService = {
  createEmail,
  getEmail,
  listEmails,
  updateEmail,
  deleteEmail,
  setPrincipalEmail,
  sendVerificationEmail,
};

export default emailsService;
