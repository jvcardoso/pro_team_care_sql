# 🎣 Hooks Centralizados - Sistema de Campos Sensíveis

Hooks React para formatação, validação, mascaramento e auditoria LGPD.

---

## 📚 Hooks Disponíveis

### 1. `useFieldFormatter` - Formatação e Validação

**Uso:** Formatação pura sem estado (stateless).

```tsx
import { useFieldFormatter, useCPFFormatter } from '@/hooks/useFieldFormatter';

const MyComponent = () => {
  const cpfFormatter = useCPFFormatter();

  const formatted = cpfFormatter.format('12345678900');   // "123.456.789-00"
  const isValid = cpfFormatter.validate('123.456.789-00'); // true
  const masked = cpfFormatter.mask('123.456.789-00');      // "123.***.***-00"
};
```

**Tipos suportados:**
- `cpf`, `cnpj`, `phone`, `cep`, `rg`, `cns`
- `email`, `credit_card`, `bank_account`, `pix_key`
- `date`, `currency`, `text`

---

### 2. `useSensitiveField` - Gerenciamento Completo

**Uso:** Gerenciamento completo de campo sensível (stateful).

```tsx
import { useSensitiveField, useCPFField } from '@/hooks/useSensitiveField';

const ClientForm = ({ clientId }) => {
  const cpfField = useCPFField({
    initialValue: '12345678900',
    entityType: 'client',
    entityId: clientId,
    autoFormat: true,   // Formata ao digitar
    autoMask: true,     // Mascara por padrão
    autoAudit: true,    // Audita ao revelar
  });

  return (
    <div>
      <input
        value={cpfField.displayValue}    // "123.***.***-00"
        onChange={cpfField.handleChange}
        onBlur={cpfField.handleBlur}
      />
      <button onClick={cpfField.reveal}>Revelar</button>
      {cpfField.error && <span>{cpfField.error}</span>}
    </div>
  );
};
```

**API completa:**
```tsx
{
  value: string;              // Valor não formatado
  displayValue: string;       // Valor formatado e/ou mascarado
  formattedValue: string;     // Valor formatado sem máscara
  isRevealed: boolean;        // Se está revelado
  isValid: boolean;           // Se é válido
  error: string | null;       // Erro de validação
  setValue: (value) => void;  // Alterar valor
  handleChange: (e) => void;  // Handler para input
  handleBlur: () => void;     // Handler para blur
  reveal: () => Promise<void>; // Revelar (com auditoria)
  hide: () => void;           // Ocultar
  toggle: () => Promise<void>; // Toggle reveal/hide
  validate: () => boolean;    // Validar manualmente
  clear: () => void;          // Limpar campo
  reset: () => void;          // Reset para valor inicial
}
```

---

## 🧩 Componentes Relacionados

### `FormattedInput` - Input com Formatação
```tsx
import { CPFInput, CNPJInput, PhoneInput } from '@/components/shared/FormattedInput';

<CPFInput
  value={cpf}
  onChange={(value, isValid) => setCpf(value)}
  required
  showValidation
/>
```

### `SensitiveField` - Campo com Reveal/Hide
```tsx
import { CPFField, EmailField } from '@/components/shared/SensitiveField';

<CPFField
  value="12345678900"
  entityType="client"
  entityId={123}
  mode="display"  // ou "input"
/>
```

---

## 📖 Exemplos Rápidos

### Formulário Simples
```tsx
import { useCPFField, useEmailField } from '@/hooks/useSensitiveField';

const [cpf, setCpf] = useState('');
const [email, setEmail] = useState('');

const cpfField = useCPFField({
  initialValue: cpf,
  onChange: (value, isValid) => {
    setCpf(value);
    console.log('CPF válido?', isValid);
  }
});
```

### Apenas Formatação (sem estado)
```tsx
import { useCPFFormatter } from '@/hooks/useFieldFormatter';

const formatter = useCPPFormatter();
const formatted = formatter.format(rawCpf);
```

### Com React Hook Form
```tsx
import { useForm } from 'react-hook-form';
import { useCPFField } from '@/hooks/useSensitiveField';

const { register, handleSubmit } = useForm();
const cpfField = useCPFField({ initialValue: '' });

<input
  {...register('cpf')}
  value={cpfField.displayValue}
  onChange={(e) => {
    cpfField.handleChange(e);
    register('cpf').onChange(e);
  }}
/>
```

---

## 🔐 LGPD Compliance

Todos os hooks com `autoAudit: true` registram automaticamente:
- Acesso a dados sensíveis
- Revelação de campos mascarados
- IP do usuário
- Timestamp
- Contexto (entityType, entityId)

**Tabela de auditoria:** `master.user_data_access_log`

---

## 📚 Documentação Completa

- **Guia Completo:** `docs/SISTEMA_CENTRALIZADO_CAMPOS_SENSIVEIS.md`
- **Migração:** `docs/EXEMPLO_MIGRACAO_CAMPOS_SENSIVEIS.md`
- **LGPD:** `docs/LGPD_USAGE.md`
