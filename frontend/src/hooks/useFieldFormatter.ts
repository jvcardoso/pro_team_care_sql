/**
 * Hook centralizado para formatação de campos.
 *
 * Suporta formatação automática de:
 * - CPF, CNPJ, Telefone, CEP
 * - Mascaramento de dados sensíveis
 * - Validação integrada
 *
 * @example
 * const { format, validate, mask } = useFieldFormatter('cpf');
 * const formatted = format('12345678900'); // 123.456.789-00
 * const isValid = validate('123.456.789-00'); // true/false
 */

import { useMemo, useCallback } from 'react';

// ========================================
// TIPOS
// ========================================

export type FieldType =
  | 'cpf'
  | 'cnpj'
  | 'phone'
  | 'cep'
  | 'rg'
  | 'cns'
  | 'email'
  | 'credit_card'
  | 'bank_account'
  | 'pix_key'
  | 'date'
  | 'currency'
  | 'text';

export interface FormatterConfig {
  mask?: string;
  maxLength?: number;
  pattern?: RegExp;
  revealStart?: number;
  revealEnd?: number;
}

export interface FormatResult {
  value: string;
  isValid: boolean;
  error?: string;
}

// ========================================
// CONFIGURAÇÕES DE FORMATAÇÃO
// ========================================

const FORMATTER_CONFIGS: Record<FieldType, FormatterConfig> = {
  cpf: {
    mask: '###.###.###-##',
    maxLength: 14,
    pattern: /^\d{3}\.\d{3}\.\d{3}-\d{2}$/,
    revealStart: 3,
    revealEnd: 2,
  },
  cnpj: {
    mask: '##.###.###/####-##',
    maxLength: 18,
    pattern: /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/,
    revealStart: 2,
    revealEnd: 4,
  },
  phone: {
    maxLength: 15,
    pattern: /^\(\d{2}\)\s\d{4,5}-\d{4}$/,
    revealStart: 0,
    revealEnd: 4,
  },
  cep: {
    mask: '#####-###',
    maxLength: 9,
    pattern: /^\d{5}-\d{3}$/,
    revealStart: 5,
    revealEnd: 0,
  },
  rg: {
    maxLength: 20,
    revealStart: 0,
    revealEnd: 2,
  },
  cns: {
    maxLength: 15,
    pattern: /^\d{15}$/,
    revealStart: 0,
    revealEnd: 4,
  },
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    revealStart: 2,
    revealEnd: 0,
  },
  credit_card: {
    maxLength: 19,
    pattern: /^\d{4}\s\d{4}\s\d{4}\s\d{4}$/,
    revealStart: 0,
    revealEnd: 4,
  },
  bank_account: {
    maxLength: 20,
    revealStart: 0,
    revealEnd: 3,
  },
  pix_key: {
    maxLength: 100,
    revealStart: 3,
    revealEnd: 3,
  },
  date: {
    mask: '##/##/####',
    maxLength: 10,
    pattern: /^\d{2}\/\d{2}\/\d{4}$/,
  },
  currency: {
    maxLength: 20,
  },
  text: {
    maxLength: 255,
  },
};

// ========================================
// FUNÇÕES DE FORMATAÇÃO
// ========================================

/**
 * Remove caracteres não numéricos de uma string.
 */
const onlyNumbers = (str: string): string => {
  return str.replace(/\D/g, '');
};

/**
 * Formata CPF: 123.456.789-00
 */
const formatCPF = (value: string): string => {
  const numbers = onlyNumbers(value);
  if (numbers.length <= 3) return numbers;
  if (numbers.length <= 6) return `${numbers.slice(0, 3)}.${numbers.slice(3)}`;
  if (numbers.length <= 9)
    return `${numbers.slice(0, 3)}.${numbers.slice(3, 6)}.${numbers.slice(6)}`;
  return `${numbers.slice(0, 3)}.${numbers.slice(3, 6)}.${numbers.slice(
    6,
    9
  )}-${numbers.slice(9, 11)}`;
};

/**
 * Formata CNPJ: 12.345.678/0001-00
 */
const formatCNPJ = (value: string): string => {
  const numbers = onlyNumbers(value);
  if (numbers.length <= 2) return numbers;
  if (numbers.length <= 5) return `${numbers.slice(0, 2)}.${numbers.slice(2)}`;
  if (numbers.length <= 8)
    return `${numbers.slice(0, 2)}.${numbers.slice(2, 5)}.${numbers.slice(5)}`;
  if (numbers.length <= 12)
    return `${numbers.slice(0, 2)}.${numbers.slice(2, 5)}.${numbers.slice(
      5,
      8
    )}/${numbers.slice(8)}`;
  return `${numbers.slice(0, 2)}.${numbers.slice(2, 5)}.${numbers.slice(
    5,
    8
  )}/${numbers.slice(8, 12)}-${numbers.slice(12, 14)}`;
};

/**
 * Formata Telefone: (11) 98765-4321 ou (11) 3456-7890
 */
const formatPhone = (value: string): string => {
  const numbers = onlyNumbers(value);
  if (numbers.length <= 2) return numbers;
  if (numbers.length <= 6)
    return `(${numbers.slice(0, 2)}) ${numbers.slice(2)}`;
  if (numbers.length <= 10)
    return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 6)}-${numbers.slice(
      6
    )}`;
  return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 7)}-${numbers.slice(
    7,
    11
  )}`;
};

/**
 * Formata CEP: 12345-678
 */
const formatCEP = (value: string): string => {
  const numbers = onlyNumbers(value);
  if (numbers.length <= 5) return numbers;
  return `${numbers.slice(0, 5)}-${numbers.slice(5, 8)}`;
};

/**
 * Formata Data: DD/MM/YYYY
 */
const formatDate = (value: string): string => {
  const numbers = onlyNumbers(value);
  if (numbers.length <= 2) return numbers;
  if (numbers.length <= 4) return `${numbers.slice(0, 2)}/${numbers.slice(2)}`;
  return `${numbers.slice(0, 2)}/${numbers.slice(2, 4)}/${numbers.slice(4, 8)}`;
};

/**
 * Formata Moeda: R$ 1.234,56
 */
const formatCurrency = (value: string | number): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return 'R$ 0,00';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(numValue);
};

/**
 * Formata Cartão de Crédito: 1234 5678 9012 3456
 */
const formatCreditCard = (value: string): string => {
  const numbers = onlyNumbers(value);
  const parts = [];
  for (let i = 0; i < numbers.length; i += 4) {
    parts.push(numbers.slice(i, i + 4));
  }
  return parts.join(' ');
};

// ========================================
// FUNÇÕES DE VALIDAÇÃO
// ========================================

/**
 * Valida CPF (algoritmo completo)
 */
const validateCPF = (cpf: string): boolean => {
  const numbers = onlyNumbers(cpf);
  if (numbers.length !== 11) return false;
  if (/^(\d)\1{10}$/.test(numbers)) return false; // Rejeita sequências iguais

  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(numbers.charAt(i)) * (10 - i);
  }
  let remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(numbers.charAt(9))) return false;

  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(numbers.charAt(i)) * (11 - i);
  }
  remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(numbers.charAt(10))) return false;

  return true;
};

/**
 * Valida CNPJ (algoritmo completo)
 */
const validateCNPJ = (cnpj: string): boolean => {
  const numbers = onlyNumbers(cnpj);
  if (numbers.length !== 14) return false;
  if (/^(\d)\1{13}$/.test(numbers)) return false; // Rejeita sequências iguais

  let size = numbers.length - 2;
  let nums = numbers.substring(0, size);
  const digits = numbers.substring(size);
  let sum = 0;
  let pos = size - 7;

  for (let i = size; i >= 1; i--) {
    sum += parseInt(nums.charAt(size - i)) * pos--;
    if (pos < 2) pos = 9;
  }

  let result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  if (result !== parseInt(digits.charAt(0))) return false;

  size += 1;
  nums = numbers.substring(0, size);
  sum = 0;
  pos = size - 7;

  for (let i = size; i >= 1; i--) {
    sum += parseInt(nums.charAt(size - i)) * pos--;
    if (pos < 2) pos = 9;
  }

  result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  if (result !== parseInt(digits.charAt(1))) return false;

  return true;
};

/**
 * Valida Email (regex básico)
 */
const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

/**
 * Valida Telefone (formato brasileiro)
 */
const validatePhone = (phone: string): boolean => {
  const numbers = onlyNumbers(phone);
  return numbers.length >= 10 && numbers.length <= 11;
};

/**
 * Valida CEP
 */
const validateCEP = (cep: string): boolean => {
  const numbers = onlyNumbers(cep);
  return numbers.length === 8;
};

// ========================================
// FUNÇÕES DE MASCARAMENTO
// ========================================

/**
 * Mascara um valor mostrando apenas início e fim.
 */
const maskValue = (
  value: string,
  revealStart: number = 0,
  revealEnd: number = 0,
  maskChar: string = '*'
): string => {
  if (!value) return '';

  const length = value.length;
  if (length <= revealStart + revealEnd) return value;

  const start = value.slice(0, revealStart);
  const end = value.slice(-revealEnd);
  const middle = maskChar.repeat(length - revealStart - revealEnd);

  return `${start}${middle}${end}`;
};

/**
 * Mascara email: jo**@example.com
 */
const maskEmail = (email: string): string => {
  if (!email || !email.includes('@')) return email;

  const [local, domain] = email.split('@');
  const maskedLocal = maskValue(local, 2, 0, '*');
  return `${maskedLocal}@${domain}`;
};

// ========================================
// HOOK PRINCIPAL
// ========================================

export interface UseFieldFormatterReturn {
  format: (value: string) => string;
  validate: (value: string) => boolean;
  mask: (value: string) => string;
  unmask: (value: string) => string;
  config: FormatterConfig;
}

export const useFieldFormatter = (fieldType: FieldType): UseFieldFormatterReturn => {
  const config = useMemo(() => FORMATTER_CONFIGS[fieldType], [fieldType]);

  const format = useCallback(
    (value: string): string => {
      if (!value) return '';

      switch (fieldType) {
        case 'cpf':
          return formatCPF(value);
        case 'cnpj':
          return formatCNPJ(value);
        case 'phone':
          return formatPhone(value);
        case 'cep':
          return formatCEP(value);
        case 'date':
          return formatDate(value);
        case 'currency':
          return formatCurrency(value);
        case 'credit_card':
          return formatCreditCard(value);
        default:
          return value;
      }
    },
    [fieldType]
  );

  const validate = useCallback(
    (value: string): boolean => {
      if (!value) return false;

      switch (fieldType) {
        case 'cpf':
          return validateCPF(value);
        case 'cnpj':
          return validateCNPJ(value);
        case 'email':
          return validateEmail(value);
        case 'phone':
          return validatePhone(value);
        case 'cep':
          return validateCEP(value);
        default:
          // Se tem pattern, valida com regex
          if (config.pattern) {
            return config.pattern.test(value);
          }
          return true;
      }
    },
    [fieldType, config.pattern]
  );

  const mask = useCallback(
    (value: string): string => {
      if (!value) return '';

      // Email tem mascaramento especial
      if (fieldType === 'email') {
        return maskEmail(value);
      }

      // Formatar primeiro, depois mascarar
      const formatted = format(value);

      return maskValue(
        formatted,
        config.revealStart || 0,
        config.revealEnd || 0,
        '*'
      );
    },
    [fieldType, format, config]
  );

  const unmask = useCallback(
    (value: string): string => {
      // Remove todos caracteres não alfanuméricos (exceto @ para email)
      if (fieldType === 'email') {
        return value;
      }
      return onlyNumbers(value);
    },
    [fieldType]
  );

  return {
    format,
    validate,
    mask,
    unmask,
    config,
  };
};

// ========================================
// HOOKS ESPECIALIZADOS
// ========================================

export const useCPFFormatter = () => useFieldFormatter('cpf');
export const useCNPJFormatter = () => useFieldFormatter('cnpj');
export const usePhoneFormatter = () => useFieldFormatter('phone');
export const useCEPFormatter = () => useFieldFormatter('cep');
export const useEmailFormatter = () => useFieldFormatter('email');
export const useDateFormatter = () => useFieldFormatter('date');
export const useCurrencyFormatter = () => useFieldFormatter('currency');
