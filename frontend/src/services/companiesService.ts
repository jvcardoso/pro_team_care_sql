/**
 * Serviço de Empresas - Pro Team Care
 * Alinhado com backend 100% funcional
 * Baseado nos testes validados do backend
 * @module companiesService
 */

import { useState } from 'react';
import { api } from './api';

// ========================================
// INTERFACES ATUALIZADAS
// ========================================

export interface Company {
  id: number;
  // Campos originais da API
  razao_social: string;
  nome_fantasia: string;
  cnpj: string; // Pode estar mascarado
  is_active: boolean;
  access_status: 'active' | 'inactive' | 'pending';
  created_at: string;
  updated_at: string;

  // Campos mapeados para compatibilidade com tabela
  name: string;
  tax_id: string;
  trade_name: string;
  status: 'active' | 'inactive' | 'suspended';
  establishments_count?: number;
  clients_count?: number;
  professionals_count?: number;
  users_count?: number;

  // Relacionamentos
  enderecos?: Address[];
  telefones?: Phone[];
  emails?: Email[];
}

export interface Address {
  id: number;
  company_id: number;
  cep: string;
  logradouro: string;
  numero: string;
  complemento?: string;
  bairro: string;
  cidade: string;
  uf: string;
  tipo: 'comercial' | 'residencial' | 'correspondencia';
  is_principal: boolean;
  is_active: boolean;
  // Dados de geocodificação
  latitude?: number;
  longitude?: number;
}

export interface Phone {
  id: number;
  company_id: number;
  number: string; // Pode estar mascarado
  type: 'comercial' | 'residencial' | 'celular' | 'fax';
  is_whatsapp: boolean;
  is_active: boolean;
}

export interface Email {
  id: number;
  company_id: number;
  email: string; // Pode estar mascarado
  type: 'comercial' | 'pessoal' | 'financeiro';
  is_principal: boolean;
  is_active: boolean;
}

export interface CompanyCreateRequest {
  cnpj: string;
  razao_social: string;
  nome_fantasia: string;
  telefones: Omit<Phone, 'id' | 'company_id'>[];
  emails: Omit<Email, 'id' | 'company_id'>[];
  enderecos: Omit<Address, 'id' | 'company_id' | 'latitude' | 'longitude'>[];
}

export interface CompanyCreateResponse {
  new_company_id: number;
  new_person_id: number;
  new_pj_profile_id: number;
  message: string;
}

export interface CNPJConsultResponse {
  cnpj: string;
  razao_social: string;
  nome_fantasia: string;
  situacao_cadastral: string;
  data_abertura: string;
  cnae_principal: string;
  natureza_juridica: string;
  capital_social: string;
  endereco: {
    logradouro: string;
    numero: string;
    complemento?: string;
    bairro: string;
    municipio: string;
    uf: string;
    cep: string;
  };
  telefone?: string;
  email?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// ========================================
// SERVIÇO ATUALIZADO
// ========================================

// Debug: Módulo carregado
console.log('✅ CompaniesService module loaded');

export class CompaniesService {
  
  /**
    * Lista empresas com paginação e filtros
    * Endpoint validado: GET /api/v1/companies/complete-list
    */
  static async list(params?: {
    skip?: number;
    limit?: number;
    status?: 'active' | 'inactive';
    search?: string;
  }): Promise<PaginatedResponse<Company>> {
    const queryParams = new URLSearchParams();

    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.search) queryParams.append('search', params.search);

    const response = await api.get(`/api/v1/companies/complete-list?${queryParams.toString()}`);

    // Mapear a resposta da API para a estrutura esperada
    // API retorna: { total, companies[] } com dados completos
    // PaginatedResponse espera: { items[], total, page, size, pages }
    const mappedItems = (response.data.companies || []).map((company: any) => {
      return {
        ...company,
        // Mapeamento de campos para compatibilidade com tabela
        id: company.company_id,
        name: company.razao_social || 'Nome não disponível',
        tax_id: company.cnpj || 'CNPJ não disponível',
        trade_name: company.nome_fantasia || 'Nome fantasia não disponível',
        status: company.access_status || 'inactive',
        establishments_count: company.establishments_count || 0,
        clients_count: company.clients_count || 0,
        professionals_count: company.professionals_count || 0,
        users_count: company.users_count || 0,
      };
    });

    return {
      items: mappedItems,
      total: response.data.total || 0,
      page: 1, // API não retorna paginação detalhada
      size: params?.limit || 10,
      pages: Math.ceil((response.data.total || 0) / (params?.limit || 10))
    };
  }

  /**
   * Consulta empresa por ID
   * Endpoint validado: GET /api/v1/companies/{id}
   */
  static async getById(id: number): Promise<Company> {
    const response = await api.get(`/api/v1/companies/${id}`);
    return response.data;
  }

  /**
   * Consulta CNPJ em APIs externas
   * Endpoint validado: GET /api/v1/cnpj/{cnpj}
   */
  static async consultCNPJ(cnpj: string): Promise<CNPJConsultResponse> {
    // Remove formatação do CNPJ
    const cleanCNPJ = cnpj.replace(/\D/g, '');
    const response = await api.get(`/api/v1/cnpj/${cleanCNPJ}`);
    return response.data;
  }

  /**
   * Cria empresa completa (Person + Company + PJ Profile + relacionamentos)
   * Endpoint validado: POST /api/v1/companies/complete
   */
  static async createComplete(data: CompanyCreateRequest): Promise<CompanyCreateResponse> {
    const response = await api.post('/api/v1/companies/complete', data);
    return response.data;
  }

  /**
   * Atualiza empresa existente
   * Endpoint validado: PUT /api/v1/companies/{id}
   */
  static async update(id: number, data: Partial<CompanyCreateRequest>): Promise<Company> {
    const response = await api.put(`/api/v1/companies/${id}`, data);
    return response.data;
  }

  /**
   * Inativa empresa
   * Endpoint validado: PATCH /api/v1/companies/{id}/deactivate
   */
  static async deactivate(id: number): Promise<Company> {
    const response = await api.patch(`/api/v1/companies/${id}/deactivate`);
    return response.data;
  }

  /**
   * Ativa empresa
   * Endpoint validado: PATCH /api/v1/companies/{id}/activate
   */
  static async activate(id: number): Promise<Company> {
    const response = await api.patch(`/api/v1/companies/${id}/activate`);
    return response.data;
  }

  /**
   * Revela dados sensíveis (LGPD)
   * Endpoint: POST /api/v1/companies/{id}/reveal
   */
  static async revealSensitiveData(id: number, fields?: string[]): Promise<Company> {
    const response = await api.post(`/api/v1/companies/${id}/reveal`, { fields });
    return response.data;
  }

  /**
    * Consulta logs de auditoria LGPD
    * Endpoint: GET /api/v1/lgpd/audit-logs/
    */
  static async getLGPDLogs(id: number, page: number = 1, size: number = 100): Promise<{ items: any[], total: number }> {
    const response = await api.get(`/api/v1/lgpd/audit-logs/?entity_type=companies&entity_id=${id}&page=${page}&size=${size}`);
    return {
      items: response.data.items || [],
      total: response.data.total || 0
    };
  }
}

// ========================================
// HOOKS UTILITÁRIOS
// ========================================

/**
 * Hook para gerenciar estado de loading/error
 */
export const useAsyncState = <T>() => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = async (asyncFn: () => Promise<T>) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await asyncFn();
      setData(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, execute, setData };
};

/**
 * Utilitários para formatação
 */
export const formatters = {
  cnpj: (cnpj: string) => {
    if (!cnpj) return '';
    const clean = cnpj.replace(/\D/g, '');
    return clean.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5');
  },
  
  phone: (phone: string) => {
    if (!phone) return '';
    const clean = phone.replace(/\D/g, '');
    if (clean.length === 11) {
      return clean.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
    }
    return clean.replace(/^(\d{2})(\d{4})(\d{4})$/, '($1) $2-$3');
  },
  
  cep: (cep: string) => {
    if (!cep) return '';
    const clean = cep.replace(/\D/g, '');
    return clean.replace(/^(\d{5})(\d{3})$/, '$1-$2');
  }
};

// Export default da classe
export default CompaniesService;
