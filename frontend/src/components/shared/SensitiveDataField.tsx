/**
 * SensitiveDataField Component - LGPD Compliant
 *
 * Exibe dados sensíveis mascarados com opção de revelação sob demanda.
 * - Sempre mostra valor mascarado inicialmente
 * - Revelação mediante ação explícita do usuário
 * - Auto-hide após 3 minutos
 * - Auditoria automática no backend
 *
 * FUNCIONA COM QUALQUER ENTIDADE: companies, clients, users, establishments
 *
 * @requires Backend endpoint: POST /api/v1/lgpd/{entityType}/{entityId}/reveal-field
 */

import React, { useState, useEffect, useRef } from "react";
import { Eye, EyeOff, Shield } from "lucide-react";
import { notify } from "../../utils/notifications";
import { revealSensitiveField, EntityType } from "../../services/lgpdService";

interface SensitiveDataFieldProps {
  /** Valor mascarado recebido do backend */
  value: string;
  /** Tipo da entidade ("companies", "clients", "users", "establishments") */
  entityType: EntityType;
  /** ID da entidade */
  entityId: number;
  /** Nome do campo a revelar (ex: "tax_id", "cpf", "email") */
  fieldName: string;
  /** Label do campo */
  label?: string;
  /** Ícone opcional para exibir ao lado do label */
  icon?: React.ReactNode;
  /** Classes CSS adicionais */
  className?: string;
}

const SensitiveDataField: React.FC<SensitiveDataFieldProps> = ({
  value,
  entityType,
  entityId,
  fieldName,
  label,
  icon,
  className = "",
}) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const [revealedValue, setRevealedValue] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const autoHideTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Função para formatar CNPJ (adicionar pontos e barras)
  const formatCNPJ = (cnpj: string): string => {
    const clean = cnpj.replace(/\D/g, "");
    if (clean.length === 14) {
      return clean.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5");
    }
    return cnpj;
  };

  // Função para formatar CEP (adicionar hífen)
  const formatCEP = (cep: string): string => {
    const clean = cep.replace(/\D/g, "");
    if (clean.length === 8) {
      return clean.replace(/^(\d{5})(\d{3})$/, "$1-$2");
    }
    return cep;
  };

  // Função para formatar telefone (com DDD e hífen)
  const formatPhone = (phone: string): string => {
    const clean = phone.replace(/\D/g, "");

    // Celular com código do país (13 dígitos: 5511987654321)
    if (clean.length === 13) {
      return `+${clean.slice(0, 2)} (${clean.slice(2, 4)}) ${clean.slice(4, 9)}-${clean.slice(9, 13)}`;
    }
    // Celular (11 dígitos: 11987654321)
    if (clean.length === 11) {
      return `(${clean.slice(0, 2)}) ${clean.slice(2, 7)}-${clean.slice(7, 11)}`;
    }
    // Fixo (10 dígitos: 1140001234)
    if (clean.length === 10) {
      return `(${clean.slice(0, 2)}) ${clean.slice(2, 6)}-${clean.slice(6, 10)}`;
    }
    return phone;
  };

  // Função para obter placeholder mascarado baseado no tipo de campo
  const getMaskedPlaceholder = (fieldName: string): string => {
    switch (fieldName) {
      case "tax_id":
        return "••.•••.•••/••••-••"; // CNPJ mascarado
      case "secondary_tax_id":
        return "•••.•••••.••"; // IE mascarada
      case "municipal_registration":
        return "•••••••••"; // IM mascarada
      default:
        if (fieldName.includes("phone") && fieldName.includes("number")) {
          return "(••) •••••-••••"; // Telefone mascarado
        }
        if (fieldName.includes("zip_code") || fieldName.includes("cep") || fieldName.includes("postal_code")) {
          return "•••••-•••"; // CEP mascarado
        }
        return "••••••••••••••••••"; // Placeholder genérico
    }
  };

  // Limpar timer ao desmontar componente
  useEffect(() => {
    return () => {
      if (autoHideTimerRef.current) {
        clearTimeout(autoHideTimerRef.current);
      }
    };
  }, []);

  // Reset estado quando entityId mudar (navegação entre entidades)
  useEffect(() => {
    setIsRevealed(false);
    setRevealedValue(null);
    setLoading(false);
    if (autoHideTimerRef.current) {
      clearTimeout(autoHideTimerRef.current);
    }
  }, [entityId]);

  const handleReveal = async () => {
    setLoading(true);

    try {
      // ✅ Usa serviço genérico que funciona com qualquer entidade
      const result = await revealSensitiveField(entityType, entityId, fieldName);

      // Aplicar formatação específica baseada no tipo de campo
      let formattedValue = result.field_value;

      if (fieldName === "tax_id") {
        formattedValue = formatCNPJ(result.field_value);
      } else if (fieldName.includes("zip_code") || fieldName.includes("cep") || fieldName.includes("postal_code")) {
        formattedValue = formatCEP(result.field_value);
      } else if (fieldName.startsWith("phone_") && fieldName.includes("_number")) {
        formattedValue = formatPhone(result.field_value);
      }

      setRevealedValue(formattedValue);
      setIsRevealed(true);

      // Notificar sucesso
      notify.success("Dados sensíveis revelados com sucesso!");

      // Configurar auto-hide após 3 minutos
      autoHideTimerRef.current = setTimeout(() => {
        handleHide();
        notify.info("Dados sensíveis ocultados automaticamente por segurança");
      }, 180000); // 3 minutos

    } catch (error: any) {
      console.error("Erro ao revelar campo:", error);

      if (error.message.includes("Session expired")) {
        notify.error("Sessão expirada. Faça login novamente.");
      } else if (error.message.includes("permission")) {
        notify.error("Você não tem permissão para revelar este dado.");
      } else if (error.message.includes("not found")) {
        notify.error(`${entityType} não encontrado.`);
      } else {
        notify.error(error.message || "Erro ao revelar dado sensível");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleHide = () => {
    setIsRevealed(false);
    setRevealedValue(null);

    // Limpar timer
    if (autoHideTimerRef.current) {
      clearTimeout(autoHideTimerRef.current);
      autoHideTimerRef.current = null;
    }
  };

  return (
    <div className={className}>
      {/* Label com ícones */}
      {label && (
        <label className="block text-sm font-medium text-muted-foreground mb-1 flex items-center gap-1">
          {icon && <span className="text-muted-foreground">{icon}</span>}
          {label}
          {!isRevealed && (
            <Shield
              className="h-3 w-3 text-orange-500"
              title="Dado Sensível - LGPD"
            />
          )}
        </label>
      )}

       {/* Campo de valor + botão de revelação */}
       <div className="flex items-center gap-2">
         <span className="font-mono text-sm text-foreground flex-1">
           {isRevealed && revealedValue ? revealedValue : (value || getMaskedPlaceholder(fieldName))}
         </span>

        {isRevealed ? (
          // Botão Ocultar
          <button
            onClick={handleHide}
            className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded hover:bg-gray-100 dark:hover:bg-gray-800"
            title="Ocultar dado sensível"
          >
            <EyeOff className="h-3 w-3" />
            <span>Ocultar</span>
          </button>
        ) : (
          // Botão Revelar
          <button
            onClick={handleReveal}
            disabled={loading}
            className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed rounded hover:bg-blue-50 dark:hover:bg-blue-950"
            title="Revelar dado completo (ação auditada)"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>Revelando...</span>
              </>
            ) : (
              <>
                <Eye className="h-3 w-3" />
                <span>Revelar</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Aviso LGPD */}
      {!isRevealed && (
        <p className="text-xs text-muted-foreground mt-1">
          🔒 Revelação auditada (LGPD Art. 18, VIII)
        </p>
      )}

      {/* Timer de auto-hide */}
      {isRevealed && (
        <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
          ⏱️ Será ocultado automaticamente em 3 minutos
        </p>
      )}
    </div>
  );
};

export default SensitiveDataField;
