/**
 * SensitiveField Component - LGPD Compliant (Versão Centralizada)
 *
 * Componente universal para exibir dados sensíveis com:
 * - Formatação automática (CPF, CNPJ, telefone, etc.)
 * - Mascaramento por padrão
 * - Revelação sob demanda com auditoria
 * - Auto-hide configurável
 * - Validação integrada
 *
 * USO SIMPLIFICADO:
 * ```tsx
 * <SensitiveField
 *   type="cpf"
 *   value="12345678900"
 *   entityType="client"
 *   entityId={123}
 * />
 * ```
 *
 * @requires useSensitiveField hook
 */

import React, { useRef, useEffect } from 'react';
import { Eye, EyeOff, Shield, CheckCircle, AlertCircle } from 'lucide-react';
import { useSensitiveField } from '../../hooks/useSensitiveField';
import { FieldType } from '../../hooks/useFieldFormatter';

// ========================================
// TIPOS
// ========================================

export interface SensitiveFieldProps {
  /** Tipo do campo (cpf, cnpj, email, phone, etc.) */
  type: FieldType;

  /** Valor inicial (não formatado) */
  value: string;

  /** Label do campo */
  label?: string;

  /** Tipo de entidade (client, company, user, etc.) */
  entityType?: string;

  /** ID da entidade */
  entityId?: number;

  /** Ícone personalizado para o label */
  icon?: React.ReactNode;

  /** Classes CSS adicionais */
  className?: string;

  /** Tempo para auto-hide em milissegundos (padrão: 180000 = 3 min) */
  autoHideDelay?: number;

  /** Desabilitar auto-hide */
  disableAutoHide?: boolean;

  /** Mostrar indicador de validação */
  showValidation?: boolean;

  /** Mostrar aviso LGPD */
  showLGPDNotice?: boolean;

  /** Callback ao revelar */
  onReveal?: () => void;

  /** Callback ao ocultar */
  onHide?: () => void;

  /** Modo de exibição: 'display' (somente leitura) ou 'input' (editável) */
  mode?: 'display' | 'input';

  /** Permite edição (apenas no modo input) */
  editable?: boolean;

  /** Callback ao alterar valor (modo input) */
  onChange?: (value: string, isValid: boolean) => void;
}

// ========================================
// COMPONENTE
// ========================================

export const SensitiveField: React.FC<SensitiveFieldProps> = ({
  type,
  value,
  label,
  entityType,
  entityId,
  icon,
  className = '',
  autoHideDelay = 180000, // 3 minutos
  disableAutoHide = false,
  showValidation = true,
  showLGPDNotice = true,
  onReveal,
  onHide,
  mode = 'display',
  editable = false,
  onChange,
}) => {
  const autoHideTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Hook centralizado de campo sensível
  const field = useSensitiveField({
    fieldName: type,
    fieldType: type,
    initialValue: value,
    entityType,
    entityId,
    autoFormat: true,
    autoMask: true,
    autoAudit: true,
    onChange,
    onReveal,
    readOnly: !editable || mode === 'display',
  });

  // Auto-hide timer
  useEffect(() => {
    if (field.isRevealed && !disableAutoHide) {
      autoHideTimerRef.current = setTimeout(() => {
        field.hide();
        if (onHide) onHide();
      }, autoHideDelay);
    }

    return () => {
      if (autoHideTimerRef.current) {
        clearTimeout(autoHideTimerRef.current);
      }
    };
  }, [field.isRevealed, disableAutoHide, autoHideDelay]);

  // Limpar timer ao desmontar
  useEffect(() => {
    return () => {
      if (autoHideTimerRef.current) {
        clearTimeout(autoHideTimerRef.current);
      }
    };
  }, []);

  // Reset ao mudar entidade
  useEffect(() => {
    field.reset();
  }, [entityId]);

  // ========================================
  // RENDERIZAÇÃO
  // ========================================

  return (
    <div className={`w-full ${className}`}>
      {/* Label com ícones */}
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1.5">
          {icon && <span className="text-gray-500">{icon}</span>}
          {label}
          {!field.isRevealed && (
            <Shield
              className="h-3.5 w-3.5 text-orange-500"
              title="Dado Sensível - LGPD"
            />
          )}
          {showValidation && field.value && (
            field.isValid ? (
              <CheckCircle className="h-3.5 w-3.5 text-green-500" title="Válido" />
            ) : (
              <AlertCircle className="h-3.5 w-3.5 text-red-500" title="Inválido" />
            )
          )}
        </label>
      )}

      {/* Conteúdo principal */}
      <div className="flex items-center gap-2">
        {/* Campo de exibição ou input */}
        {mode === 'display' ? (
          <span className="font-mono text-sm text-gray-900 dark:text-gray-100 flex-1">
            {field.displayValue || '-'}
          </span>
        ) : (
          <input
            type="text"
            value={field.displayValue}
            onChange={field.handleChange}
            onBlur={field.handleBlur}
            disabled={!editable}
            className={`
              flex-1 px-3 py-2 border rounded-md font-mono text-sm
              focus:outline-none focus:ring-2 transition-colors
              ${
                field.error
                  ? 'border-red-500 focus:ring-red-500'
                  : field.isValid && field.value
                  ? 'border-green-500 focus:ring-green-500'
                  : 'border-gray-300 focus:ring-blue-500'
              }
              ${!editable ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
              dark:bg-gray-800 dark:text-gray-100
            `}
            readOnly={!editable}
          />
        )}

        {/* Botão Revelar/Ocultar */}
        {field.isRevealed ? (
          <button
            onClick={field.hide}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 border border-gray-300 dark:border-gray-600"
            title="Ocultar dado sensível"
          >
            <EyeOff className="h-4 w-4" />
            <span>Ocultar</span>
          </button>
        ) : (
          <button
            onClick={field.reveal}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 transition-colors rounded-md hover:bg-blue-50 dark:hover:bg-blue-950 border border-blue-300 dark:border-blue-600"
            title="Revelar dado completo (ação auditada)"
          >
            <Eye className="h-4 w-4" />
            <span>Revelar</span>
          </button>
        )}
      </div>

      {/* Mensagem de erro */}
      {field.error && (
        <p className="mt-1 text-xs text-red-600 dark:text-red-400">
          {field.error}
        </p>
      )}

      {/* Aviso LGPD */}
      {!field.isRevealed && showLGPDNotice && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          🔒 Revelação auditada (LGPD Art. 18, VIII)
        </p>
      )}

      {/* Timer de auto-hide */}
      {field.isRevealed && !disableAutoHide && (
        <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
          ⏱️ Será ocultado automaticamente em{' '}
          {Math.round(autoHideDelay / 60000)} min
        </p>
      )}
    </div>
  );
};

// ========================================
// COMPONENTES ESPECIALIZADOS
// ========================================

export const CPFField: React.FC<Omit<SensitiveFieldProps, 'type'>> = (
  props
) => {
  return (
    <SensitiveField
      {...props}
      type="cpf"
      label={props.label || 'CPF'}
    />
  );
};

export const CNPJField: React.FC<Omit<SensitiveFieldProps, 'type'>> = (
  props
) => {
  return (
    <SensitiveField
      {...props}
      type="cnpj"
      label={props.label || 'CNPJ'}
    />
  );
};

export const EmailField: React.FC<Omit<SensitiveFieldProps, 'type'>> = (
  props
) => {
  return (
    <SensitiveField
      {...props}
      type="email"
      label={props.label || 'E-mail'}
    />
  );
};

export const PhoneField: React.FC<Omit<SensitiveFieldProps, 'type'>> = (
  props
) => {
  return (
    <SensitiveField
      {...props}
      type="phone"
      label={props.label || 'Telefone'}
    />
  );
};

// ========================================
// EXPORT DEFAULT
// ========================================

export default SensitiveField;

// ========================================
// EXEMPLO DE USO
// ========================================

/*
// Modo Display (somente leitura):
<CPFField
  value="12345678900"
  entityType="client"
  entityId={123}
/>

// Modo Input (editável):
<SensitiveField
  type="email"
  value={email}
  label="E-mail"
  mode="input"
  editable
  entityType="client"
  entityId={123}
  onChange={(value, isValid) => {
    setEmail(value);
    console.log('Válido:', isValid);
  }}
/>

// Com customizações:
<CNPJField
  value="12345678000100"
  entityType="company"
  entityId={456}
  autoHideDelay={60000} // 1 minuto
  showValidation
  onReveal={() => console.log('Revelado!')}
  onHide={() => console.log('Ocultado!')}
/>
*/
