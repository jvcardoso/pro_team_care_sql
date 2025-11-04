import React, { useState, useCallback, useEffect, useMemo } from "react";
import { DataTableTemplate } from "./DataTable/DataTableTemplate";
import { getEntityAuditLog, EntityType, AuditLogItem } from "../../services/lgpdService";
import { useDataTable } from "../../hooks/useDataTable";
import { BaseEntity, DataTableConfig } from "../../types/dataTable.types";

// Estender AuditLogItem com BaseEntity
interface ExtendedAuditLogItem extends AuditLogItem, BaseEntity {
  status: string; // Adicionar campo status obrigatório do BaseEntity
  updated_at: string; // Adicionar campo updated_at obrigatório do BaseEntity
  [key: string]: any; // Adicionar índice de assinatura para permitir acesso dinâmico
}

// Configuração da tabela de audit logs
const createAuditLogConfig = (entityType: EntityType): DataTableConfig<ExtendedAuditLogItem> => ({
  entity: "audit-logs",
  showAddButton: false, // Remove o botão "Novo audit-logs"

  metrics: {
    primary: [],
    detailed: undefined,
  },

  filters: [],

  export: {
    enabled: true,
    filename: `audit_log_${entityType}`,
    formats: ["csv", "json", "print"],
  },

  defaultPageSize: 10,
  pagination: {
    pageSize: 10,
    pageSizeOptions: [10, 25, 50, 100, 200, 500],
  },

  searchFields: ["user_email", "action_type", "ip_address", "sensitive_fields"],
  searchPlaceholder: "Buscar por usuário, ação, IP ou campos acessados...",

  columns: [
    {
      key: "created_at",
      label: "Data/Hora",
      type: "custom",
      width: "w-32",
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
      key: "action_type",
      label: "Ação",
      type: "custom",
      width: "w-20",
      sortable: true,
      render: (value, item) => {
        const actionStyles = {
          REVEAL: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
          VIEW: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
          EDIT: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
          UPDATE: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
          CREATE: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
          DELETE: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
          default: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
        };

        const style = actionStyles[value as keyof typeof actionStyles] || actionStyles.default;

        return (
          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${style}`}>
            {value}
          </span>
        );
      },
    },
    {
      key: "user_email",
      label: "Usuário",
      type: "custom",
      width: "w-40",
      sortable: true,
      render: (value, item) => (
        <span className="text-sm text-gray-900 dark:text-white">
          {value || `Usuário #${item.user_id}`}
        </span>
      ),
    },
    {
      key: "ip_address",
      label: "IP",
      type: "custom",
      width: "w-24",
      render: (value, item) => (
        <span className="text-xs font-mono text-gray-600 dark:text-gray-400">
          {value || "-"}
        </span>
      ),
    },
    {
      key: "sensitive_fields",
      label: "Campos Acessados",
      type: "custom",
      width: "w-48",
      render: (value, item) => {
        let fields: string[] = [];

        if (Array.isArray(value)) {
          fields = value;
        } else if (typeof value === 'string') {
          fields = [value];
        } else if (value && typeof value === 'object') {
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
  ],
});

interface AuditLogTabProps {
  entityType: EntityType;
  entityId: number;
}

const AuditLogTab: React.FC<AuditLogTabProps> = ({ entityType, entityId }) => {
  const [logs, setLogs] = useState<ExtendedAuditLogItem[]>([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Load audit logs with backend pagination
  const loadAuditLogs = useCallback(async (page: number = currentPage, size: number = pageSize) => {
    try {
      setLoading(true);
      setError(null);

      const response = await getEntityAuditLog(entityType, entityId, page, size);

      // Convert AuditLogItem to ExtendedAuditLogItem
      const extendedLogs: ExtendedAuditLogItem[] = (response.items || []).map(log => ({
        ...log,
        status: 'active', // Default status for audit logs
        updated_at: log.created_at, // Use created_at as updated_at
      }));

      setLogs(extendedLogs);
      setTotalLogs(response.total || 0);
      setTotalPages(response.pages || 0);
      setCurrentPage(page);
      setPageSize(size);
    } catch (err: any) {
      console.error('❌ [AuditLogTab] Erro ao carregar logs:', {
        message: err.message,
        status: err.response?.status,
        data: err.response?.data
      });
      setError(err.message || "Erro ao carregar logs de auditoria");
    } finally {
      setLoading(false);
    }
  }, [entityType, entityId, currentPage, pageSize]);

  // Create config
  const config = useMemo(() => createAuditLogConfig(entityType), [entityType]);

  // Use real data from API with backend pagination
  const dataTableProps = useDataTable<ExtendedAuditLogItem>({
    config,
    data: logs,
    total: totalLogs,
    externalPageSize: pageSize,
    externalCurrentPage: currentPage,
  });

  // Custom pagination callbacks for backend pagination
  const handlePageChange = useCallback((page: number) => {
    console.log('📄 [AuditLogTab] Mudando página para:', page);
    loadAuditLogs(page, pageSize);
  }, [loadAuditLogs, pageSize]);

  const handlePageSizeChange = useCallback((newPageSize: number) => {
    console.log('📏 [AuditLogTab] Mudando pageSize para:', newPageSize);
    loadAuditLogs(1, newPageSize);
  }, [loadAuditLogs]);

  // Update state with backend pagination data (read-only sync)
  useEffect(() => {
    // Only update what's needed for display, don't override hook state
    dataTableProps.state.total = totalLogs;
    dataTableProps.state.totalPages = totalPages;
  }, [totalLogs, totalPages]);

  // Override the callbacks
  dataTableProps.callbacks.onPageChange = handlePageChange;
  dataTableProps.callbacks.onPageSizeChange = handlePageSizeChange;

  // Load audit logs on mount
  useEffect(() => {
    loadAuditLogs(1, 10);
  }, []);

  // Loading state
  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 relative shadow-md sm:rounded-lg overflow-hidden">
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-300">
            Carregando histórico de auditoria...
          </span>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 relative shadow-md sm:rounded-lg overflow-hidden p-6">
        <div className="flex items-center gap-3 text-red-600 dark:text-red-400">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <p className="font-medium">Erro ao carregar dados</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (logs.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 relative shadow-md sm:rounded-lg overflow-hidden p-8">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <svg
            className="mx-auto h-12 w-12 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="text-lg font-medium mb-2">
            Nenhum registro de auditoria encontrado
          </h3>
          <p className="text-sm">
            Ainda não há acessos a dados sensíveis registrados para esta entidade.
          </p>
        </div>
      </div>
    );
  }

  // Render data table
  return (
    <div className="space-y-4">
      {/* Info banner */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg
            className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-1">
              Conformidade LGPD - Art. 37
            </h3>
            <p className="text-sm text-blue-700 dark:text-blue-400">
              Este histórico registra todos os acessos a dados sensíveis conforme Art. 37 da LGPD.
              Total de registros: <strong>{totalLogs}</strong>
            </p>
          </div>
        </div>
      </div>

      {/* Data table */}
      <DataTableTemplate<ExtendedAuditLogItem>
        config={config}
        tableData={dataTableProps}
      />
    </div>
  );
};

export default AuditLogTab;