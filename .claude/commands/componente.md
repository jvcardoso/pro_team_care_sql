---
description: Criar componente React reutilizável com TypeScript e Tailwind
---

# Criar Componente React

Criar componente React TypeScript seguindo padrões de reutilização.

## Comandos Disponíveis
**Uso:** `/componente [nome] [categoria]`
**Exemplo:** `/componente DataTable common`

## Workflow

### 1. Verificação (SEMPRE)
ANTES de criar:
- [ ] Verificar se componente similar já existe
- [ ] Buscar em `src/components/` funcionalidade parecida
- [ ] Se encontrar, perguntar se deve reutilizar
- [ ] Aguardar confirmação do usuário

### 2. Planejar Estrutura
Apresentar plano:
```
Vou criar [Nome] com:
- Props: [listar]
- Localização: src/components/[categoria]/[Nome].tsx
- Reutilizável em: [onde]
```
Aguardar aprovação.

### 3. Criar Componente TypeScript

```typescript
// src/components/[categoria]/[Nome].tsx

/**
 * [Descrição do componente]
 * @example
 * <[Nome] prop1="valor" />
 */
interface [Nome]Props {
  prop1: string;
  prop2?: number;
  className?: string; // Para permitir personalização
  children?: React.ReactNode;
}

export const [Nome]: React.FC<[Nome]Props> = ({
  prop1,
  prop2,
  className,
  children
}) => {
  return (
    <div className={`[tailwind-base-classes] ${className || ''}`}>
      {/* Conteúdo */}
    </div>
  );
};

export default [Nome];
```

### 4. Regras Obrigatórias
- ✅ TypeScript com interface para props
- ✅ NUNCA usar `any`
- ✅ Tailwind CSS (NUNCA inline styles)
- ✅ JSDoc com descrição e exemplo
- ✅ Props className para personalização
- ✅ Componente funcional (não class)
- ✅ Máximo 200 linhas (quebrar se maior)

### 5. Criar Types (se necessário)
```typescript
// src/types/[nome].types.ts
export interface [Nome]Data {
  id: number;
  name: string;
}

export type [Nome]Status = 'active' | 'inactive';
```

### 6. Exemplo de Uso
```typescript
import { [Nome] } from '@/components/[categoria]/[Nome]';

function App() {
  return (
    <[Nome]
      prop1="exemplo"
      className="mt-4"
    >
      Conteúdo
    </[Nome>
  );
}
```

### 7. Oferecer Próximos Passos
```
Quer que eu crie:
1. [ ] Teste unitário (Jest/Testing Library)
2. [ ] Storybook story
3. [ ] Exemplo em uma página
```

## Checklist de Qualidade
- [ ] TypeScript sem erros
- [ ] Props tipadas (sem `any`)
- [ ] JSDoc completo
- [ ] Tailwind CSS (sem inline)
- [ ] Reutilizável (<200 linhas)
- [ ] Props className disponível
- [ ] Exemplo de uso fornecido

## Padrões do Projeto
- Usar hooks customizados para lógica complexa
- Criar service se precisar de API
- React Hook Form + Zod para formulários
- Axios com retry logic
- Tailwind para todos os estilos
