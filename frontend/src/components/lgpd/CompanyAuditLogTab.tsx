import React, { useState, useEffect, useCallback } from "react";
import { companiesService } from "../../services/companiesService";
import DataTableTemplate from "../shared/DataTable/DataTableTemplate";
import { useDataTable } from "../../hooks/useDataTable";
import {
  createLGPDAuditConfig,
  LGPDAuditLog,
} from "../../config/tables/lgpd-audit.config";
import LGPDAuditLogDetailsModal from "./LGPDAuditLogDetailsModal";

interface CompanyAuditLogTabProps {
  companyId: number;
}

const CompanyAuditLogTab: React.FC<CompanyAuditLogTabProps> = ({
  companyId,
}) => {
  const [logs, setLogs] = useState<LGPDAuditLog[]>([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedLog, setSelectedLog] = useState<LGPDAuditLog | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);

  // Handler para abrir modal com detalhes do log
  const handleViewDetails = (log: LGPDAuditLog) => {
    setSelectedLog(log);
    setIsModalOpen(true);
  };

  // Handler para fechar modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedLog(null);
  };

  // Load audit logs
  const loadAuditLogs = useCallback(async (page: number = currentPage, size: number = pageSize, isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const response = await companiesService.getLGPDLogs(companyId, page, size);
      setLogs(response.items || []);
      setTotalLogs(response.total || 0);
      setCurrentPage(page);
      setPageSize(size);
    } catch (err: any) {
      console.error("Erro ao carregar log de auditoria:", err);
      setError(
        err.response?.data?.detail ||
          "Erro ao carregar histórico de auditoria"
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [companyId, currentPage, pageSize]);

  // Handler para botão de atualizar
  const handleRefreshClick = () => {
    loadAuditLogs(1, pageSize, true); // Passa true para indicar que é um refresh
  };

  // Initialize data table hook com handler para ver detalhes
  const config = createLGPDAuditConfig(handleViewDetails);
  config.showAddButton = true;
  config.addButtonLabel = refreshing ? "Atualizando..." : "Atualizar dados";
  config.onAdd = handleRefreshClick;

  const dataTableProps = useDataTable<LGPDAuditLog>({
    config,
    initialData: logs,
    total: totalLogs,
  });

  // Override pagination callbacks to use backend pagination
  const handlePageChange = useCallback((page: number) => {
    loadAuditLogs(page, pageSize, false);
  }, [loadAuditLogs, pageSize]);

  const handlePageSizeChange = useCallback((newPageSize: number) => {
    loadAuditLogs(1, newPageSize, false);
  }, [loadAuditLogs]);

  // Override the callbacks in dataTableProps
  dataTableProps.callbacks.onPageChange = handlePageChange;
  dataTableProps.callbacks.onPageSizeChange = handlePageSizeChange;

  // Load audit logs on mount
  useEffect(() => {
    loadAuditLogs(1, 50, false);
  }, []); // Remove dependency to avoid infinite loops

  // Update dataTable when logs change
  useEffect(() => {
    if (logs.length > 0) {
      // Update the dataTable with current page data
      dataTableProps.state.data = logs;
      dataTableProps.state.currentPage = currentPage;
      dataTableProps.state.pageSize = pageSize;
    }
  }, [logs, currentPage, pageSize]);

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
            Ainda não há acessos a dados sensíveis registrados para esta empresa.
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
              Este histórico registra todos os acessos a dados sensíveis desta empresa,
              incluindo revelações de campos mascarados e ações realizadas (ligações,
               emails, navegação). Total de registros: <strong>{totalLogs}</strong>
            </p>
          </div>
        </div>
      </div>

      {/* Data table */}
      <DataTableTemplate<LGPDAuditLog>
        config={config}
        tableData={dataTableProps}
      />

      {/* Modal de detalhes */}
      <LGPDAuditLogDetailsModal
        log={selectedLog}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
};

export default CompanyAuditLogTab;
