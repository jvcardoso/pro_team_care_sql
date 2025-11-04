/**
 * Serviço para consulta de dados de empresa via CNPJ
 * Utiliza APENAS endpoint público - sem autenticação
 * Evita problemas de loop de login
 */

import axios from "axios";
import { createAxiosConfig } from "../config/http";
import { removeCNPJFormatting } from "../utils/validators";

/**
 * Consulta dados de empresa pelo CNPJ
 * @param {string} cnpj - CNPJ (pode ser alfanumérico)
 * @returns {Promise<Object>} Dados da empresa
 */
export const consultarCNPJ = async (cnpj) => {
  const clean = removeCNPJFormatting(cnpj);

  if (clean.length !== 14) {
    throw new Error("CNPJ deve ter 14 caracteres");
  }

  // Verificar se é alfanumérico
  const isAlphanumeric = /[A-Z]/.test(clean);

  if (isAlphanumeric) {
    // ⚠️ APIs externas podem não suportar CNPJs alfanuméricos ainda
    console.warn('CNPJ alfanumérico: APIs externas podem não suportar');

    // Retornar dados básicos sem consulta externa
    return {
      people: {
        person_type: 'PJ',
        name: '',
        trade_name: '',
        tax_id: clean,
        incorporation_date: '',
        tax_regime: 'simples_nacional',
        legal_nature: '',
        status: 'active',
        description: '',
      },
      company: {
        settings: {},
        metadata: {},
        display_order: 0,
      },
      phones: [
        {
          country_code: "55",
          number: "",
          type: "commercial",
          is_principal: true,
          is_whatsapp: false,
        },
      ],
      emails: [
        {
          email_address: "",
          type: "work",
          is_principal: true,
        },
      ],
      addresses: [
        {
          street: "",
          number: "",
          details: "",
          neighborhood: "",
          city: "",
          state: "",
          zip_code: "",
          country: "BR",
          type: "commercial",
          is_principal: true,
        },
      ],
    };
  }

  // CNPJ numérico: consultar normalmente
  // Remover caracteres não numéricos para consulta externa
  const cnpjLimpo = clean.replace(/\D/g, "");

  // 🔄 Usar configuração HTTP padronizada para CNPJ service
  const cnpjApi = axios.create(createAxiosConfig("cnpj"));

  try {
    console.log("Consultando CNPJ (apenas endpoint público):", cnpjLimpo);

    // Usar apenas endpoint público - sem autenticação
    const response = await cnpjApi.get(
      `/api/v1/cnpj/publico/consultar/${cnpjLimpo}`
    );
    const data = response.data;

    if (!data.success) {
      throw new Error(data.message || "CNPJ não encontrado ou inválido");
    }

    return data.data;
  } catch (error) {
    console.error("Erro ao consultar CNPJ:", error);

    // Tratamento específico para erros da API
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }

    // Tratamento para erros de rede
    if (
      error.message.includes("Network Error") ||
      error.code === "ECONNABORTED"
    ) {
      throw new Error(
        "Erro de conexão. Verifique sua internet e tente novamente."
      );
    }

    // Tratamento para timeout
    if (error.code === "ECONNABORTED") {
      throw new Error(
        "Consulta demorou muito para responder. Tente novamente."
      );
    }

    throw new Error(error.message || "Erro inesperado ao consultar CNPJ");
  }
};

// Dados já vêm mapeados do backend, não precisa mais mapear

// Funções de mapeamento removidas - backend já faz isso

/**
 * Valida formato do CNPJ
 * @param {string} cnpj - CNPJ para validar (pode ser alfanumérico)
 * @returns {boolean} True se válido
 */
export const validarFormatoCNPJ = (cnpj) => {
  const clean = removeCNPJFormatting(cnpj);
  return clean.length === 14 && /^[A-Z0-9]{12}\d{2}$/.test(clean);
};

/**
 * Formata CNPJ para exibição
 * @param {string} cnpj - CNPJ (pode ser alfanumérico)
 * @returns {string} CNPJ formatado
 */
export const formatarCNPJ = (cnpj) => {
  const clean = removeCNPJFormatting(cnpj);

  if (clean.length === 14) {
    return clean.replace(
      /^([A-Z0-9]{2})([A-Z0-9]{3})([A-Z0-9]{3})([A-Z0-9]{4})(\d{2})$/,
      "$1.$2.$3/$4-$5"
    );
  }

  return cnpj;
};
