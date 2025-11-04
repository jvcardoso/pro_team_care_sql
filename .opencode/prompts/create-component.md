# Criar Componente React

## Contexto
Você está criando um novo componente React para o Pro Team Care.

## Requisitos
- **SEMPRE** use TypeScript com interfaces
- **SEMPRE** use Tailwind CSS (nunca CSS inline)
- **SEMPRE** torne reutilizável (aceite prop className)
- **SEMPRE** use hooks funcionais
- **SEMPRE** verifique se componente similar já existe
- **NUNCA** use `any` em TypeScript
- **NUNCA** crie componentes > 300 linhas

## Estrutura do Componente
```typescript
interface ComponentProps {
  prop1: string;
  prop2?: number;
  className?: string;
}

export const Component: React.FC<ComponentProps> = ({
  prop1,
  prop2,
  className
}) => {
  return (
    <div className={`base-classes ${className || ''}`}>
      {/* Conteúdo */}
    </div>
  );
};
```

## Padrões Visuais
- Use design system definido no AGENTS.md
- Cores: blue-600/700 (primary), green-600/700 (success), red-600/700 (error)
- Espaçamento: p-4, p-6, p-8 (consistente)
- Botões: bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg

## Testes Necessários
- Teste de renderização
- Teste de interações (click, input)
- Teste de props obrigatórias/opcionais