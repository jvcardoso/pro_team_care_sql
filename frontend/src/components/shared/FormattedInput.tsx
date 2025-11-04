/**
 * Componente de input com formatação automática.
 *
 * Suporta todos os tipos de campos do sistema com formatação,
 * validação e feedback visual integrados.
 *
 * @example
 * <FormattedInput
 *   type="cpf"
 *   label="CPF"
 *   value={cpf}
 *   onChange={(value, isValid) => setCpf(value)}
 *   required
 * />
 */

import React from 'react';
import { useFieldFormatter, FieldType } from '../../hooks/useFieldFormatter';

// ========================================
// TIPOS
// ========================================

export interface FormattedInputProps {
  /** Tipo do campo */
  type: FieldType;

  /** Label do campo */
  label?: string;

  /** Valor atual (não formatado) */
  value?: string;

  /** Placeholder */
  placeholder?: string;

  /** Campo obrigatório */
  required?: boolean;

  /** Campo desabilitado */
  disabled?: boolean;

  /** Campo somente leitura */
  readOnly?: boolean;

  /** Mostrar indicador de validação */
  showValidation?: boolean;

  /** Mensagem de erro customizada */
  error?: string;

  /** Dica de ajuda */
  helperText?: string;

  /** Callback ao alterar valor */
  onChange?: (value: string, isValid: boolean) => void;

  /** Callback ao perder foco */
  onBlur?: () => void;

  /** Classes CSS adicionais */
  className?: string;

  /** ID do input */
  id?: string;

  /** Nome do input (para forms) */
  name?: string;

  /** Autocompletar */
  autoComplete?: string;

  /** Autofocus */
  autoFocus?: boolean;
}

// ========================================
// COMPONENTE
// ========================================

export const FormattedInput: React.FC<FormattedInputProps> = ({
  type,
  label,
  value = '',
  placeholder,
  required = false,
  disabled = false,
  readOnly = false,
  showValidation = true,
  error,
  helperText,
  onChange,
  onBlur,
  className = '',
  id,
  name,
  autoComplete,
  autoFocus = false,
}) => {
  const formatter = useFieldFormatter(type);
  const [internalValue, setInternalValue] = React.useState(value);
  const [touched, setTouched] = React.useState(false);

  // Sincronizar valor externo
  React.useEffect(() => {
    setInternalValue(value);
  }, [value]);

  // Valor formatado para exibição
  const displayValue = formatter.format(internalValue);

  // Validação
  const isValid = !internalValue || formatter.validate(internalValue);
  const showError = touched && showValidation && !isValid && !error;
  const hasError = !!error || showError;

  // Handler de mudança
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = e.target.value;

    // Remover formatação antes de salvar
    newValue = formatter.unmask(newValue);

    // Limitar tamanho
    if (
      formatter.config.maxLength &&
      newValue.length > formatter.config.maxLength
    ) {
      return;
    }

    setInternalValue(newValue);

    // Validar
    const valid = formatter.validate(newValue);

    // Callback externo
    if (onChange) {
      onChange(newValue, valid);
    }
  };

  // Handler de blur
  const handleBlur = () => {
    setTouched(true);
    if (onBlur) {
      onBlur();
    }
  };

  // Classes de estilo
  const inputClasses = `
    w-full px-3 py-2 border rounded-md
    focus:outline-none focus:ring-2
    transition-colors duration-200
    ${
      hasError
        ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
        : isValid && internalValue
        ? 'border-green-500 focus:ring-green-500 focus:border-green-500'
        : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
    }
    ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
    ${readOnly ? 'bg-gray-50' : ''}
    ${className}
  `.trim();

  const labelClasses = `
    block text-sm font-medium mb-1
    ${hasError ? 'text-red-700' : 'text-gray-700'}
  `.trim();

  return (
    <div className="w-full">
      {/* Label */}
      {label && (
        <label htmlFor={id} className={labelClasses}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {/* Input Container */}
      <div className="relative">
        <input
          id={id}
          name={name}
          type="text"
          value={displayValue}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          readOnly={readOnly}
          autoComplete={autoComplete}
          autoFocus={autoFocus}
          onChange={handleChange}
          onBlur={handleBlur}
          className={inputClasses}
          aria-invalid={hasError}
          aria-describedby={
            hasError ? `${id}-error` : helperText ? `${id}-helper` : undefined
          }
        />

        {/* Ícone de validação */}
        {showValidation && touched && internalValue && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            {isValid && !error ? (
              <svg
                className="h-5 w-5 text-green-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              hasError && (
                <svg
                  className="h-5 w-5 text-red-500"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              )
            )}
          </div>
        )}
      </div>

      {/* Mensagem de erro */}
      {hasError && (
        <p id={`${id}-error`} className="mt-1 text-sm text-red-600">
          {error || `${label || 'Campo'} inválido`}
        </p>
      )}

      {/* Helper text */}
      {!hasError && helperText && (
        <p id={`${id}-helper`} className="mt-1 text-sm text-gray-500">
          {helperText}
        </p>
      )}
    </div>
  );
};

// ========================================
// COMPONENTES ESPECIALIZADOS
// ========================================

export const CPFInput: React.FC<Omit<FormattedInputProps, 'type'>> = (
  props
) => {
  return (
    <FormattedInput
      {...props}
      type="cpf"
      label={props.label || 'CPF'}
      placeholder={props.placeholder || '000.000.000-00'}
      autoComplete={props.autoComplete || 'off'}
    />
  );
};

export const CNPJInput: React.FC<Omit<FormattedInputProps, 'type'>> = (
  props
) => {
  return (
    <FormattedInput
      {...props}
      type="cnpj"
      label={props.label || 'CNPJ'}
      placeholder={props.placeholder || '00.000.000/0000-00'}
      autoComplete={props.autoComplete || 'off'}
    />
  );
};

export const PhoneInput: React.FC<Omit<FormattedInputProps, 'type'>> = (
  props
) => {
  return (
    <FormattedInput
      {...props}
      type="phone"
      label={props.label || 'Telefone'}
      placeholder={props.placeholder || '(00) 00000-0000'}
      autoComplete={props.autoComplete || 'tel'}
    />
  );
};

export const CEPInput: React.FC<Omit<FormattedInputProps, 'type'>> = (
  props
) => {
  return (
    <FormattedInput
      {...props}
      type="cep"
      label={props.label || 'CEP'}
      placeholder={props.placeholder || '00000-000'}
      autoComplete={props.autoComplete || 'postal-code'}
    />
  );
};

export const EmailInput: React.FC<Omit<FormattedInputProps, 'type'>> = (
  props
) => {
  return (
    <FormattedInput
      {...props}
      type="email"
      label={props.label || 'E-mail'}
      placeholder={props.placeholder || 'exemplo@email.com'}
      autoComplete={props.autoComplete || 'email'}
    />
  );
};

export const DateInput: React.FC<Omit<FormattedInputProps, 'type'>> = (
  props
) => {
  return (
    <FormattedInput
      {...props}
      type="date"
      label={props.label || 'Data'}
      placeholder={props.placeholder || 'DD/MM/AAAA'}
      autoComplete={props.autoComplete || 'off'}
    />
  );
};

// ========================================
// EXEMPLO DE USO
// ========================================

/*
// Em um formulário:

const MyForm = () => {
  const [cpf, setCpf] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');

  return (
    <form>
      <CPFInput
        value={cpf}
        onChange={(value, isValid) => {
          setCpf(value);
          console.log('CPF válido?', isValid);
        }}
        required
      />

      <EmailInput
        value={email}
        onChange={(value) => setEmail(value)}
        helperText="Digite um e-mail válido"
      />

      <PhoneInput
        value={phone}
        onChange={(value) => setPhone(value)}
      />
    </form>
  );
};
*/
