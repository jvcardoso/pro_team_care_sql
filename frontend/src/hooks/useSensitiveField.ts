/**
 * Hook universal para gerenciar campos sensíveis.
 *
 * Combina formatação, mascaramento, validação e auditoria em um único hook.
 *
 * @example
 * const cpfField = useSensitiveField({
 *   fieldName: 'cpf',
 *   fieldType: 'cpf',
 *   initialValue: '12345678900',
 *   entityType: 'client',
 *   entityId: 123,
 * });
 *
 * // Use no componente:
 * <input value={cpfField.displayValue} onChange={cpfField.handleChange} />
 * <button onClick={cpfField.reveal}>Revelar</button>
 */

import { useState, useCallback, useEffect, useMemo } from 'react';
import { useFieldFormatter, FieldType } from './useFieldFormatter';
// import { auditService } from '../services/auditService'; // DEPRECATED: Usar lgpdService

// ========================================
// TIPOS
// ========================================

export interface UseSensitiveFieldOptions {
  /** Nome do campo (ex: 'cpf', 'email') */
  fieldName: string;

  /** Tipo do campo para formatação */
  fieldType: FieldType;

  /** Valor inicial (não formatado) */
  initialValue?: string;

  /** Tipo de entidade (ex: 'client', 'company') */
  entityType?: string;

  /** ID da entidade */
  entityId?: number;

  /** Formatar automaticamente ao digitar */
  autoFormat?: boolean;

  /** Mascarar por padrão */
  autoMask?: boolean;

  /** Auditar quando revelar */
  autoAudit?: boolean;

  /** Validar ao perder foco */
  validateOnBlur?: boolean;

  /** Callback ao alterar valor */
  onChange?: (value: string, isValid: boolean) => void;

  /** Callback ao revelar */
  onReveal?: () => void;

  /** Permite edição */
  readOnly?: boolean;
}

export interface UseSensitiveFieldReturn {
  /** Valor atual (não formatado) */
  value: string;

  /** Valor para exibição (formatado e/ou mascarado) */
  displayValue: string;

  /** Valor formatado (sem mascaramento) */
  formattedValue: string;

  /** Se o campo está revelado */
  isRevealed: boolean;

  /** Se o valor é válido */
  isValid: boolean;

  /** Mensagem de erro de validação */
  error: string | null;

  /** Função para alterar o valor */
  setValue: (value: string) => void;

  /** Handler para input onChange */
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;

  /** Handler para input onBlur */
  handleBlur: () => void;

  /** Revelar o campo (remove mascaramento) */
  reveal: () => Promise<void>;

  /** Ocultar o campo (aplica mascaramento) */
  hide: () => void;

  /** Toggle reveal/hide */
  toggle: () => Promise<void>;

  /** Validar manualmente */
  validate: () => boolean;

  /** Limpar campo */
  clear: () => void;

  /** Reset para valor inicial */
  reset: () => void;
}

// ========================================
// HOOK PRINCIPAL
// ========================================

export const useSensitiveField = (
  options: UseSensitiveFieldOptions
): UseSensitiveFieldReturn => {
  const {
    fieldName,
    fieldType,
    initialValue = '',
    entityType,
    entityId,
    autoFormat = true,
    autoMask = true,
    autoAudit = true,
    validateOnBlur = true,
    onChange,
    onReveal,
    readOnly = false,
  } = options;

  // Hook de formatação
  const formatter = useFieldFormatter(fieldType);

  // Estado
  const [value, setValue] = useState<string>(initialValue);
  const [isRevealed, setIsRevealed] = useState<boolean>(!autoMask);
  const [error, setError] = useState<string | null>(null);
  const [isAuditing, setIsAuditing] = useState<boolean>(false);

  // Valor formatado (sempre formatado, mesmo que mascarado)
  const formattedValue = useMemo(() => {
    if (!autoFormat || !value) return value;
    return formatter.format(value);
  }, [value, autoFormat, formatter]);

  // Valor para exibição (formatado + mascarado se necessário)
  const displayValue = useMemo(() => {
    if (isRevealed) {
      return formattedValue;
    }
    return autoMask ? formatter.mask(formattedValue) : formattedValue;
  }, [formattedValue, isRevealed, autoMask, formatter]);

  // Validação
  const isValid = useMemo(() => {
    if (!value) return true; // Campo vazio é considerado válido (use required no form)
    return formatter.validate(value);
  }, [value, formatter]);

  // Handler de mudança de valor
  const handleValueChange = useCallback(
    (newValue: string) => {
      setValue(newValue);

      // Validar
      const valid = formatter.validate(newValue);
      setError(valid || !newValue ? null : 'Valor inválido');

      // Callback externo
      if (onChange) {
        onChange(newValue, valid);
      }
    },
    [formatter, onChange]
  );

  // Handler para input onChange
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (readOnly) return;

      let newValue = e.target.value;

      // Remover formatação antes de salvar
      if (autoFormat) {
        newValue = formatter.unmask(newValue);
      }

      // Limitar tamanho
      if (formatter.config.maxLength && newValue.length > formatter.config.maxLength) {
        return;
      }

      handleValueChange(newValue);
    },
    [readOnly, autoFormat, formatter, handleValueChange]
  );

  // Handler para input onBlur
  const handleBlur = useCallback(() => {
    if (!validateOnBlur) return;

    if (value && !isValid) {
      setError(`${fieldName} inválido`);
    }
  }, [validateOnBlur, value, isValid, fieldName]);

  // Revelar campo
  const reveal = useCallback(async () => {
    if (isRevealed) return;

    setIsRevealed(true);

    // Auditar revelação
    // NOTA: A auditoria agora é feita automaticamente no backend quando
    // o componente SensitiveDataField chama revealSensitiveField()
    // Este hook é usado principalmente para formatação e validação
    if (autoAudit && entityType && entityId && !isAuditing) {
      setIsAuditing(true);
      try {
        // TODO: Implementar auditoria via lgpdService se necessário
        // Por enquanto, a auditoria é feita pelo componente SensitiveDataField
        console.log('[LGPD] Field revealed:', { fieldName, entityType, entityId });

        if (onReveal) {
          onReveal();
        }
      } catch (error) {
        console.error('Erro ao auditar revelação:', error);
      } finally {
        setIsAuditing(false);
      }
    }
  }, [
    isRevealed,
    autoAudit,
    entityType,
    entityId,
    fieldName,
    isAuditing,
    onReveal,
  ]);

  // Ocultar campo
  const hide = useCallback(() => {
    setIsRevealed(false);
  }, []);

  // Toggle reveal/hide
  const toggle = useCallback(async () => {
    if (isRevealed) {
      hide();
    } else {
      await reveal();
    }
  }, [isRevealed, hide, reveal]);

  // Validar manualmente
  const validate = useCallback(() => {
    const valid = formatter.validate(value);
    setError(valid ? null : `${fieldName} inválido`);
    return valid;
  }, [formatter, value, fieldName]);

  // Limpar campo
  const clear = useCallback(() => {
    handleValueChange('');
    setError(null);
  }, [handleValueChange]);

  // Reset para valor inicial
  const reset = useCallback(() => {
    handleValueChange(initialValue);
    setError(null);
    setIsRevealed(!autoMask);
  }, [handleValueChange, initialValue, autoMask]);

  // Atualizar quando initialValue mudar
  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  return {
    value,
    displayValue,
    formattedValue,
    isRevealed,
    isValid,
    error,
    setValue: handleValueChange,
    handleChange,
    handleBlur,
    reveal,
    hide,
    toggle,
    validate,
    clear,
    reset,
  };
};

// ========================================
// HOOKS ESPECIALIZADOS
// ========================================

/**
 * Hook para campo CPF
 */
export const useCPFField = (
  options: Omit<UseSensitiveFieldOptions, 'fieldType'>
) => {
  return useSensitiveField({
    ...options,
    fieldType: 'cpf',
    fieldName: options.fieldName || 'cpf',
  });
};

/**
 * Hook para campo CNPJ
 */
export const useCNPJField = (
  options: Omit<UseSensitiveFieldOptions, 'fieldType'>
) => {
  return useSensitiveField({
    ...options,
    fieldType: 'cnpj',
    fieldName: options.fieldName || 'cnpj',
  });
};

/**
 * Hook para campo Email
 */
export const useEmailField = (
  options: Omit<UseSensitiveFieldOptions, 'fieldType'>
) => {
  return useSensitiveField({
    ...options,
    fieldType: 'email',
    fieldName: options.fieldName || 'email',
  });
};

/**
 * Hook para campo Telefone
 */
export const usePhoneField = (
  options: Omit<UseSensitiveFieldOptions, 'fieldType'>
) => {
  return useSensitiveField({
    ...options,
    fieldType: 'phone',
    fieldName: options.fieldName || 'phone',
  });
};

/**
 * Hook para campo CEP
 */
export const useCEPField = (
  options: Omit<UseSensitiveFieldOptions, 'fieldType'>
) => {
  return useSensitiveField({
    ...options,
    fieldType: 'cep',
    fieldName: options.fieldName || 'cep',
    autoMask: false, // CEP geralmente não precisa mascarar
  });
};

// ========================================
// EXEMPLO DE USO
// ========================================

/*
// Em um componente:

const ClientForm = ({ clientId }) => {
  const cpfField = useCPFField({
    fieldName: 'cpf',
    initialValue: client?.cpf,
    entityType: 'client',
    entityId: clientId,
    onChange: (value, isValid) => {
      console.log('CPF alterado:', value, 'válido:', isValid);
    },
  });

  const emailField = useEmailField({
    fieldName: 'email',
    initialValue: client?.email,
    entityType: 'client',
    entityId: clientId,
  });

  return (
    <form>
      <div>
        <label>CPF</label>
        <input
          value={cpfField.displayValue}
          onChange={cpfField.handleChange}
          onBlur={cpfField.handleBlur}
        />
        {cpfField.error && <span>{cpfField.error}</span>}
        <button type="button" onClick={cpfField.toggle}>
          {cpfField.isRevealed ? 'Ocultar' : 'Revelar'}
        </button>
      </div>

      <div>
        <label>Email</label>
        <input
          value={emailField.displayValue}
          onChange={emailField.handleChange}
          onBlur={emailField.handleBlur}
        />
        {emailField.error && <span>{emailField.error}</span>}
      </div>
    </form>
  );
};
*/
