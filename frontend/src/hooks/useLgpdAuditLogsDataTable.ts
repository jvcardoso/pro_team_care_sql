/**
 * Hook para gerenciar dados da tabela de logs LGPD
 * Implementa toda a lógica de filtros, paginação e busca
 */

import { useState, useEffect, useMemo } from "react";
import { AuditLogItem } from "../types/auditLog.types";
import {
  UseDataTableReturn,
  DataTableState,
  DataTableCallbacks,
} from "../types/dataTable.types";
import { lgpdService } from "../services/lgpdService";

export interface UseLgpdAuditLogsDataTableProps {
  initialPageSize?: number;
  entityType: string;
  entityId: number;
}

export function useLgpdAuditLogsDataTable({
  initialPageSize = 10,
  entityType,
  entityId,
}: UseLgpdAuditLogsDataTableProps): UseDataTableReturn<AuditLogItem> {
  console.log("🚀 [useLgpdAuditLogsDataTable] Hook inicializado");
  
  // State
  const [data, setData] = useState<AuditLogItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Table state
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({});
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);

  // Fetch data
  const fetchData = async () => {
    setLoading(true);
    setError(null);

    console.log("🔍 [useLgpdAuditLogsDataTable] Iniciando fetch de logs LGPD");
    
    try {
      const response = await lgpdService.getAuditLogs(
        entityType as any,
        entityId,
        currentPage,
        pageSize
      );

      console.log("✅ [useLgpdAuditLogsDataTable] Resposta recebida:", {
        items: response?.items?.length || 0,
        total: response?.total,
        hasData: !!response?.items,
      });

      setData(response.items || []);
      setTotal(response.total || 0);
    } catch (err: any) {
      console.error("❌ [useLgpdAuditLogsDataTable] Erro no fetch:", {
        message: err.message,
        status: err.status,
        statusCode: err.status_code,
        responseStatus: err.response?.status,
        responseData: err.response?.data,
      });
      setError(err.message || "Erro ao carregar logs de auditoria");
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
      console.log("🏁 [useLgpdAuditLogsDataTable] Fetch finalizado");
    }
  };

  // Filtrar dados localmente
  const filteredData = useMemo(() => {
    let filtered = [...data];

    // Aplicar busca
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (log) =>
          log.user_email?.toLowerCase().includes(searchLower) ||
          log.action_type?.toLowerCase().includes(searchLower) ||
          log.entity_type?.toLowerCase().includes(searchLower) ||
          log.ip_address?.toLowerCase().includes(searchLower) ||
          log.sensitive_fields?.some(field => 
            field.toLowerCase().includes(searchLower)
          )
      );
    }

    // Aplicar filtros
    Object.entries(activeFilters).forEach(([key, value]) => {
      if (!value || value === "all") return;

      if (key === "action_type") {
        filtered = filtered.filter((log) => log.action_type === value);
      } else if (key === "user_id") {
        filtered = filtered.filter((log) => log.user_id === value);
      }
    });

    return filtered;
  }, [data, searchTerm, activeFilters]);

  // Atualizar dados quando a página ou tamanho da página mudar
  useEffect(() => {
    fetchData();
  }, [currentPage, pageSize, entityType, entityId]);

  // Atualizar dados quando filtros ou busca mudarem (com debounce)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentPage === 1) {
        fetchData();
      } else {
        setCurrentPage(1); // Volta para a primeira página ao aplicar filtros
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm, activeFilters]);

  // Callbacks
  const callbacks: DataTableCallbacks<AuditLogItem> = {
    onPageChange: (page) => setCurrentPage(page),
    onPageSizeChange: (size) => {
      setPageSize(size);
      setCurrentPage(1); // Reset para a primeira página ao mudar o tamanho
    },
    onSearch: (term) => setSearchTerm(term),
    onFilter: (key: string, value: any) => {
      setActiveFilters(prev => ({ ...prev, [key]: value }));
    },
    onClearFilters: () => setActiveFilters({}),
    onSelectAll: (selected: boolean) => {
      if (selected) {
        setSelectedItems(filteredData.map(item => item.id));
      } else {
        setSelectedItems([]);
      }
    },
    onSelectItem: (id: number, selected: boolean) => {
      if (selected) {
        setSelectedItems(prev => [...prev, id]);
      } else {
        setSelectedItems(prev => prev.filter(itemId => itemId !== id));
      }
    },
    onExport: () => {},
    onAction: () => {},
    onBulkAction: () => {},
    onToggleDetailedMetrics: () => {},
    onToggleExportDropdown: () => {},
    onOpenModal: () => {},
    onCloseModal: () => {},
  };

  // Calcular total de páginas
  const totalPages = Math.ceil(total / pageSize);

  // Estado da tabela
  const state: DataTableState = {
    data: filteredData,
    filteredData,
    loading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    activeFilters,
    selectedItems,
    showDetailedMetrics: false,
    showExportDropdown: false,
    selectedItemForModal: null,
    isModalOpen: false,
  };

  return {
    state,
    callbacks,
    metrics: [],
    detailedMetrics: undefined,
  };
}

export default useLgpdAuditLogsDataTable;
