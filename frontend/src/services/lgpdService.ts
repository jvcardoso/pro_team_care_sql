/**
 * LGPD Service - Service genérico para operações LGPD.
 *
 * Funciona com QUALQUER entidade do sistema através dos endpoints genéricos v2.0.
 *
 * @example
 * // Revelar campo de cliente
 * const result = await revealSensitiveField('clients', 123, 'cpf');
 *
 * // Obter logs de auditoria de empresa
 * const logs = await getEntityAuditLog('companies', 456);
 */

import axios from "axios";
import { API_BASE_URL } from "../config/http";

// ========================================
// TIPOS
// ========================================

export type EntityType =
  | "companies"
  | "clients"
  | "users"
  | "establishments";
  // | "professionals"  // TODO: Adicionar quando criar repositório backend

export interface RevealFieldResponse {
  field_name: string;
  field_value: string;
  revealed_at: string;
  revealed_by: number;
}

export interface AuditLogItem {
  id: number;
  created_at: string;  // ✅ Backend retorna created_at
  action_type: string;  // ✅ Backend retorna action_type
  entity_type: string;
  entity_id: number | null;
  user_id: number;
  user_email: string;  // ✅ Backend retorna user_email
  ip_address?: string;
  sensitive_fields?: string[];
  changed_fields?: any;
  endpoint?: string;
  company_id?: number;
}

export interface AuditLogResponse {
  items: AuditLogItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface SupportedEntitiesResponse {
  supported_entities: string[];
  total: number;
}

export interface RevealMultipleFieldsResponse {
  revealed_data: Record<string, string>;
  revealed_count: number;
  failed_fields?: string[] | null;
  revealed_at: string;
  revealed_by: number;
}

// ========================================
// FUNÇÕES PRINCIPAIS
// ========================================

/**
 * Revela campo sensível de qualquer entidade.
 *
 * Chama endpoint genérico que funciona para todas as entidades.
 * Auditoria LGPD automática no backend.
 *
 * @param entityType - Tipo da entidade ("companies", "clients", etc.)
 * @param entityId - ID da entidade
 * @param fieldName - Nome do campo a revelar (ex: "cpf", "tax_id", "email")
 * @returns Dados do campo revelado + timestamp + auditoria
 *
 * @throws Error se autenticação inválida, entidade não encontrada, ou campo inválido
 *
 * @example
 * const result = await revealSensitiveField('clients', 123, 'cpf');
 * console.log(result.field_value); // "12345678900" (não mascarado)
 */
export async function revealSensitiveField(
  entityType: EntityType,
  entityId: number,
  fieldName: string
): Promise<RevealFieldResponse> {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("Authentication required");
  }

  try {
    const response = await axios.post<RevealFieldResponse>(
      `${API_BASE_URL}/api/v1/lgpd/${entityType}/${entityId}/reveal-field`,
      null,
      {
        params: { field_name: fieldName },
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error("Session expired. Please login again.");
    } else if (error.response?.status === 403) {
      throw new Error("You don't have permission to reveal this field.");
    } else if (error.response?.status === 404) {
      throw new Error(`${entityType} not found.`);
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || "Invalid field name.");
    }

    throw new Error(error.response?.data?.detail || "Error revealing field.");
  }
}

/**
 * Revela múltiplos campos sensíveis de uma vez.
 * Ideal para endereços completos (todos os campos de uma vez).
 *
 * @param entityType - Tipo da entidade ("companies", "clients", etc.)
 * @param entityId - ID da entidade
 * @param fieldNames - Array de nomes dos campos a revelar
 * @returns Dados dos campos revelados + timestamp + auditoria consolidada
 *
 * @throws Error se autenticação inválida, entidade não encontrada, ou campos inválidos
 *
 * @example
 * const result = await revealMultipleSensitiveFields('companies', 65, [
 *   'address_84_street',
 *   'address_84_number',
 *   'address_84_neighborhood',
 *   'address_84_zip_code'
 * ]);
 * console.log(result.revealed_data); // { address_84_street: "Rua das Flores", ... }
 */
export async function revealMultipleSensitiveFields(
  entityType: EntityType,
  entityId: number,
  fieldNames: string[]
): Promise<RevealMultipleFieldsResponse> {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("Authentication required");
  }

  if (!fieldNames || fieldNames.length === 0) {
    throw new Error("At least one field name is required");
  }

  try {
    // ✅ CORREÇÃO: Enviar field_names no body (JSON), não em query params
    const response = await axios.post<RevealMultipleFieldsResponse>(
      `${API_BASE_URL}/api/v1/lgpd/${entityType}/${entityId}/reveal-fields`,
      { field_names: fieldNames },  // Enviar como JSON no body
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error("Session expired. Please login again.");
    } else if (error.response?.status === 403) {
      throw new Error("You don't have permission to reveal these fields.");
    } else if (error.response?.status === 404) {
      throw new Error(`${entityType} not found.`);
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || "Invalid field names.");
    }

    throw new Error(error.response?.data?.detail || "Error revealing fields.");
  }
}

/**
 * Obtém histórico de auditoria LGPD de qualquer entidade.
 *
 * @param entityType - Tipo da entidade
 * @param entityId - ID da entidade
 * @param page - Número da página (padrão: 1)
 * @param size - Registros por página (padrão: 50, max: 500)
 * @returns Logs de auditoria paginados
 *
 * @example
 * const logs = await getEntityAuditLog('companies', 456, 1, 50);
 * logs.items.forEach(log => {
 *   console.log(`${log.access_type} by user ${log.accessed_by_user_id}`);
 * });
 */
export async function getEntityAuditLog(
  entityType: EntityType,
  entityId: number,
  page: number = 1,
  size: number = 50
): Promise<AuditLogResponse> {
  console.log('🌐 [lgpdService] getEntityAuditLog CHAMADO:', { entityType, entityId, page, size });
  
  const token = localStorage.getItem("access_token");

  if (!token) {
    console.error('❌ [lgpdService] Token não encontrado');
    throw new Error("Authentication required");
  }

  const url = `${API_BASE_URL}/api/v1/lgpd/${entityType}/${entityId}/audit-log`;
  console.log('🌐 [lgpdService] URL da requisição:', url);
  console.log('🌐 [lgpdService] Params:', { page, size });

  try {
    console.log('🌐 [lgpdService] Fazendo requisição GET...');
    const response = await axios.get<AuditLogResponse>(
      url,
      {
        params: { page, size },
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    console.log('✅ [lgpdService] Resposta recebida:', response.status);
    console.log('✅ [lgpdService] Dados:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ [lgpdService] Erro na requisição:', error);
    console.error('❌ [lgpdService] Status:', error.response?.status);
    console.error('❌ [lgpdService] Data:', error.response?.data);
    
    if (error.response?.status === 401) {
      throw new Error("Session expired. Please login again.");
    }

    throw new Error(
      error.response?.data?.detail || "Error fetching audit logs."
    );
  }
}

/**
 * Lista entidades suportadas pelos endpoints genéricos.
 *
 * @returns Lista de entity_types suportados
 *
 * @example
 * const entities = await getSupportedEntities();
 * // ["companies", "clients", "professionals", "users", "establishments"]
 */
export async function getSupportedEntities(): Promise<SupportedEntitiesResponse> {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("Authentication required");
  }

  try {
    const response = await axios.get<SupportedEntitiesResponse>(
      `${API_BASE_URL}/api/v1/lgpd/supported-entities`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error: any) {
    throw new Error(
      error.response?.data?.detail || "Error fetching supported entities."
    );
  }
}

// ========================================
// FUNÇÕES DE CONVENIÊNCIA
// ========================================

/**
 * Log de campo revelado (para uso em componentes).
 *
 * @param fieldName - Nome do campo revelado
 * @param entityType - Tipo da entidade
 * @param entityId - ID da entidade
 */
export function logFieldReveal(
  fieldName: string,
  entityType: EntityType,
  entityId: number
): void {
  console.log(`[LGPD] Field "${fieldName}" revealed for ${entityType} ${entityId}`);
}

/**
 * Wrapper para revelar CPF.
 */
export async function revealCPF(
  entityType: Extract<EntityType, "clients" | "users">,
  entityId: number
): Promise<string> {
  const result = await revealSensitiveField(entityType, entityId, "cpf");
  return result.field_value;
}

/**
 * Wrapper para revelar CNPJ.
 */
export async function revealCNPJ(
  entityType: Extract<EntityType, "companies" | "establishments">,
  entityId: number
): Promise<string> {
  const result = await revealSensitiveField(entityType, entityId, "tax_id");
  return result.field_value;
}

/**
 * Wrapper para revelar Email.
 */
export async function revealEmail(
  entityType: EntityType,
  entityId: number
): Promise<string> {
  const result = await revealSensitiveField(entityType, entityId, "email");
  return result.field_value;
}

/**
 * Wrapper para revelar Telefone.
 */
export async function revealPhone(
  entityType: EntityType,
  entityId: number
): Promise<string> {
  const result = await revealSensitiveField(entityType, entityId, "phone");
  return result.field_value;
}

/**
 * Wrapper para revelar endereço completo (todos os campos de uma vez).
 *
 * @param entityType - Tipo da entidade
 * @param entityId - ID da entidade
 * @param addressId - ID do endereço
 * @returns Dados completos do endereço revelado
 *
 * @example
 * const result = await revealCompleteAddress('companies', 65, 84);
 * console.log(result.revealed_data);
 * // {
 * //   address_84_street: "Rua das Flores",
 * //   address_84_number: "123",
 * //   address_84_complement: "Apto 45",
 * //   address_84_neighborhood: "Jardim Paulista",
 * //   address_84_zip_code: "01452000"
 * // }
 */
export async function revealCompleteAddress(
  entityType: EntityType,
  entityId: number,
  addressId: number | string
): Promise<RevealMultipleFieldsResponse> {
  // ⚠️ VALIDAÇÃO: addressId não pode ser null/undefined
  if (!addressId || addressId === 'null' || addressId === 'undefined') {
    throw new Error(
      "ID do endereço não disponível. Execute o script SQL 037_Add_Address_ID_To_Company_View.sql no banco de dados."
    );
  }

  // Backend espera: address_ID_field (ex: address_123_street)
  const fieldNames = [
    `address_${addressId}_street`,
    `address_${addressId}_number`,
    `address_${addressId}_complement`,
    `address_${addressId}_neighborhood`,
    `address_${addressId}_zip_code`,
  ];

  return await revealMultipleSensitiveFields(entityType, entityId, fieldNames);
}

// ========================================
// EXPORT DEFAULT
// ========================================

export default {
  revealSensitiveField,
  revealMultipleSensitiveFields,
  getEntityAuditLog,
  getSupportedEntities,
  logFieldReveal,
  revealCPF,
  revealCNPJ,
  revealEmail,
  revealPhone,
  revealCompleteAddress,
};
