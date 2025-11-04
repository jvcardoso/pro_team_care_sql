/**
 * LGPD Audit Log Details Modal
 * Modal para exibir detalhes completos de um log de auditoria LGPD
 */

import React from "react";
import { Info, X, User, Globe, Shield, Calendar } from "lucide-react";
import { LGPDAuditLog } from "../../config/tables/lgpd-audit.config";

interface LGPDAuditLogDetailsModalProps {
  log: LGPDAuditLog | null;
  isOpen: boolean;
  onClose: () => void;
}

export const LGPDAuditLogDetailsModal: React.FC<LGPDAuditLogDetailsModalProps> = ({
  log,
  isOpen,
  onClose,
}) => {
  if (!isOpen || !log) return null;

  // Formatar data legível
  const formattedDate = log.accessed_at
    ? new Date(log.accessed_at).toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "N/A";

  // Formatar campos sensíveis
  const fieldsText =
    log.sensitive_fields && log.sensitive_fields.length > 0
      ? log.sensitive_fields.join(", ")
      : "Nenhum campo acessado";

  // Informações do usuário
  const userName = log.accessed_by_user_name || "Usuário Desconhecido";
  const userEmail = log.accessed_by_user_email || "Email não disponível";

  // Tipo de acesso formatado
  const accessTypeLabels: Record<string, string> = {
    VIEW_SENSITIVE: "Revelação de Campo Sensível",
    ACTION_SENSITIVE: "Ação sobre Dado Sensível",
    VIEW: "Visualização de Dados",
  };
  const accessTypeLabel = accessTypeLabels[log.access_type] || log.access_type;

  // Função para formatar operação de forma inteligente
  const formatOperation = (viewName: string | null): string => {
    if (!viewName) return "Operação Desconhecida";

    // Mapeamento de operações conhecidas
    const operationMap: Record<string, string> = {
      "company.reveal_field.tax_id": "Revelar CNPJ",
      "company.reveal_field.secondary_tax_id": "Revelar Inscrição Estadual",
      "company.reveal_field.municipal_registration": "Revelar Inscrição Municipal",
      "company.reveal_field.email": "Revelar Email",
      "company.reveal_field.phone": "Revelar Telefone",
      "company.action.call": "Ligação Telefônica",
      "company.action.email": "Enviar Email",
      "company.action.maps": "Abrir Google Maps",
      "company.action.waze": "Abrir Waze",
      "companies.detail": "Visualizar Empresa",
    };

    // Se existe no mapa, retornar
    if (operationMap[viewName]) {
      return operationMap[viewName];
    }

    // Tratar campos de endereço específicos
    if (viewName.includes("address_")) {
      const field = viewName.split(".").pop() || "";
      const fieldLabels: Record<string, string> = {
        street: "Rua",
        number: "Número",
        details: "Complemento",
        neighborhood: "Bairro",
        zip_code: "CEP",
      };
      return `Revelar ${fieldLabels[field] || field}`;
    }

    // Tratar requisições POST/GET com múltiplos campos (formato completo com URL)
    if (viewName.includes("reveal-fields") || viewName.startsWith("Revelar POST") || viewName.startsWith("Revelar GET")) {
      // Extrair campos da query string - regex mais robusta
      const fieldsMatch = viewName.match(/[?&]fields=([^&\s]+)/);
      if (fieldsMatch) {
        const fields = fieldsMatch[1].split(",");
        const fieldCount = fields.length;

        // Contar quantos campos de cada tipo
        const addressFields = fields.filter(f => f.includes("address_")).length;
        const otherFields = fieldCount - addressFields;

        let parts: string[] = [];
        if (otherFields > 0) {
          parts.push(`${otherFields} campo${otherFields > 1 ? "s" : ""}`);
        }
        if (addressFields > 0) {
          parts.push(`${addressFields} campo${addressFields > 1 ? "s" : ""} de endereço`);
        }

        return `Revelar Múltiplos Campos (${parts.join(" + ")})`;
      }
    }

    // Fallback: retornar versão legível
    return viewName
      .replace(/company\./g, "")
      .replace(/\./g, " ")
      .replace(/_/g, " ")
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const operationLabel = formatOperation(log.view_name);

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 rounded-t-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0 bg-white/20 p-2 rounded-lg">
                  <Info className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">
                    Detalhes do Log de Auditoria LGPD
                  </h3>
                  <p className="text-sm text-blue-100">
                    ID do Log: #{log.id}
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="rounded-md text-white/80 hover:text-white focus:outline-none focus:ring-2 focus:ring-white"
                aria-label="Fechar modal"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
          </div>

          {/* Body */}
          <div className="px-6 py-6 space-y-6 max-h-[calc(100vh-300px)] overflow-y-auto">
            {/* Data e Hora */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Calendar className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                    Informações Básicas
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">
                        Data/Hora:
                      </span>
                      <p className="text-gray-600 dark:text-gray-400 mt-1">
                        {formattedDate}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">
                        Tipo de Acesso:
                      </span>
                      <p className="text-gray-600 dark:text-gray-400 mt-1">
                        {accessTypeLabel}
                      </p>
                    </div>
                    <div className="sm:col-span-2">
                      <span className="font-medium text-gray-700 dark:text-gray-300">
                        Operação Realizada:
                      </span>
                      <p className="text-gray-600 dark:text-gray-400 mt-1">
                        {operationLabel}
                      </p>
                      {log.view_name && log.view_name !== operationLabel && (
                        <details className="mt-2">
                          <summary className="text-xs text-gray-500 dark:text-gray-400 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
                            Ver detalhes técnicos
                          </summary>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 font-mono break-all bg-gray-100 dark:bg-gray-800 p-2 rounded">
                            {log.view_name}
                          </p>
                        </details>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Usuário que Acessou */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <User className="h-5 w-5 text-purple-600 dark:text-purple-400 mt-0.5" />
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                    Usuário que Acessou
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">
                        Nome:
                      </span>
                      <p className="text-gray-600 dark:text-gray-400 mt-1">
                        {userName}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">
                        ID:
                      </span>
                      <p className="text-gray-600 dark:text-gray-400 mt-1">
                        {log.accessed_by_user_id}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">
                        Email:
                      </span>
                      <p className="text-gray-600 dark:text-gray-400 mt-1 break-words">
                        {userEmail}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Informações de Rede */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Globe className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" />
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                    Informações de Rede
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">
                        Endereço IP:
                      </span>
                      <p className="text-gray-600 dark:text-gray-400 mt-1 font-mono">
                        {log.ip_address || "N/A"}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">
                        User Agent:
                      </span>
                      <p className="text-gray-600 dark:text-gray-400 mt-1 break-words text-xs">
                        {log.user_agent || "N/A"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Dados Sensíveis Acessados */}
            <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-800">
              <div className="flex items-start space-x-3">
                <Shield className="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5" />
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-amber-900 dark:text-amber-100 mb-2">
                    Dados Sensíveis Acessados
                  </h4>
                  <div className="text-sm">
                    <span className="font-medium text-amber-700 dark:text-amber-300">
                      Campos:
                    </span>
                    <p className="text-amber-600 dark:text-amber-400 mt-1 break-words">
                      {fieldsText}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer LGPD */}
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
              <div className="flex items-center space-x-2">
                <svg
                  className="h-5 w-5 text-blue-600 dark:text-blue-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
                <div className="flex-1">
                  <p className="text-xs text-blue-700 dark:text-blue-300 font-medium">
                    Conformidade LGPD - Art. 37
                  </p>
                  <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                    Este registro documenta o acesso a dados sensíveis conforme
                    exigido pela Lei Geral de Proteção de Dados (Lei nº
                    13.709/2018).
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 dark:bg-gray-700 px-6 py-4 rounded-b-lg flex justify-end">
            <button
              onClick={onClose}
              className="inline-flex justify-center rounded-md border border-transparent shadow-sm px-6 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:text-sm transition-colors"
            >
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LGPDAuditLogDetailsModal;
