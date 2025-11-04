import { TableConfig } from "../../components/shared/DataTable/types";
import { Eye } from "lucide-react";

export interface LGPDAuditLog {
  id: number;
  accessed_at: string | null;
  accessed_by_user_id: number;
  accessed_by_user_name: string | null;
  accessed_by_user_email: string | null;
  view_name: string | null;
  access_type: string;
  ip_address: string | null;
  user_agent: string | null;
  sensitive_fields: string[] | null;
}

export const createLGPDAuditConfig = (
  onViewDetails?: (log: LGPDAuditLog) => void
): TableConfig<LGPDAuditLog> => ({
  entity: "auditoria-lgpd",
  title: "Histórico de Auditoria LGPD",
  description: "Registro de acessos a dados sensíveis conforme Art. 37 da LGPD",

  metrics: {
    primary: [],
    detailed: undefined,
  },

  filters: [],
  actions: [
    {
      id: "view",
      label: "Ver Detalhes",
      icon: <Eye className="w-4 h-4" />,
      color: "blue",
      onClick: (log) => {
        if (onViewDetails) {
          onViewDetails(log);
        }
      },
    },
  ],

  export: {
    enabled: true,
    filename: "lgpd_audit_log",
    formats: ["csv", "json", "print"],
  },

  defaultPageSize: 50,  // Define o tamanho padrão da página
  pagination: {
    pageSize: 50,  // Aumentado de 10 para 50 registros por página
    pageSizeOptions: [10, 25, 50, 100, 200, 500],  // Adicionadas mais opções
  },

  searchFields: ["view_name", "access_type", "ip_address"],

  columns: [
    {
      key: "accessed_at",
      label: "Data/Hora",
      type: "custom",
      sortable: true,
      render: (value, item) => {
        if (!value) {
          return <span className="text-xs text-gray-400">-</span>;
        }

        try {
          const date = new Date(value);
          if (isNaN(date.getTime())) {
            return <span className="text-xs text-red-400">Data inválida</span>;
          }

          return (
            <div className="flex flex-col">
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {date.toLocaleDateString("pt-BR")}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {date.toLocaleTimeString("pt-BR")}
              </span>
            </div>
          );
        } catch (error) {
          return <span className="text-xs text-gray-400">-</span>;
        }
      },
    },
    {
      key: "access_type",
      label: "Tipo",
      type: "custom",
      sortable: true,
      render: (value, item) => {
        const typeColors: Record<string, string> = {
          VIEW_SENSITIVE: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
          ACTION_SENSITIVE: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
          VIEW: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300",
        };

        const typeLabels: Record<string, string> = {
          VIEW_SENSITIVE: "Revelação",
          ACTION_SENSITIVE: "Ação",
          VIEW: "Visualização",
        };

        const accessType = value || "VIEW";
        const colorClass = typeColors[accessType] || "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300";
        const label = typeLabels[accessType] || (accessType.charAt(0).toUpperCase() + accessType.slice(1).toLowerCase());

        return (
          <span className={`px-2 py-1 text-xs font-medium rounded ${colorClass}`}>
            {label}
          </span>
        );
      },
    },
    {
      key: "view_name",
      label: "Operação",
      type: "custom",
      sortable: true,
      render: (value, item) => {
        // Função para formatar operação (mesmo do modal)
        const formatOperation = (viewName: string | null): string => {
          if (!viewName) return "Operação Desconhecida";

          // Mapeamento de operações conhecidas
          const operationMap: Record<string, string> = {
            "company.reveal_field.tax_id": "Revelar CNPJ",
            "company.reveal_field.secondary_tax_id": "Revelar Insc. Estadual",
            "company.reveal_field.municipal_registration": "Revelar Insc. Municipal",
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
                parts.push(`${addressFields} endereço${addressFields > 1 ? "s" : ""}`);
              }

              return `Múltiplos Campos (${parts.join(" + ")})`;
            }
          }

          // Fallback: retornar versão legível
          return viewName
            .replace(/company\./g, "")
            .replace(/\./g, " ")
            .replace(/_/g, " ")
            .replace(/\b\w/g, (l) => l.toUpperCase());
        };

        const operationLabel = formatOperation(value);

        return (
          <span className="text-sm text-gray-900 dark:text-white" title={value || undefined}>
            {operationLabel}
          </span>
        );
      },
    },
    {
      key: "sensitive_fields",
      label: "Campos Acessados",
      type: "custom",
      render: (value, item) => {
        let fields: string[] = [];

        if (Array.isArray(value)) {
          fields = value;
        } else if (typeof value === 'string') {
          fields = [value];
        } else if (value && typeof value === 'object') {
          // Se for um objeto, tentar extrair valores
          fields = Object.values(value).filter(v => typeof v === 'string') as string[];
        }

        if (fields.length === 0) {
          return <span className="text-xs text-gray-400">-</span>;
        }

        return (
          <div className="flex flex-wrap gap-1">
            {fields.map((field, index) => (
              <span
                key={index}
                className="px-2 py-0.5 text-xs bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded"
              >
                {field}
              </span>
            ))}
          </div>
        );
      },
    },
    {
      key: "ip_address",
      label: "IP",
      type: "custom",
      render: (value, item) => (
        <span className="text-xs font-mono text-gray-600 dark:text-gray-400">
          {value || "-"}
        </span>
      ),
    },
    {
      key: "accessed_by_user_id",
      label: "Usuário",
      type: "custom",
      sortable: true,
      render: (value, item) => {
        const userName = item.accessed_by_user_name || "Usuário Desconhecido";
        const userEmail = item.accessed_by_user_email;

        return (
          <div className="flex flex-col">
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              #{value} - {userName}
            </span>
            {userEmail && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {userEmail}
              </span>
            )}
          </div>
        );
      },
    },
  ],
});
