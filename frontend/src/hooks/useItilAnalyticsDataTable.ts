/**
 * useItilAnalyticsDataTable Hook
 * Hook personalizado para tabela ITIL com paginação server-side
 */

import { useState, useEffect, useCallback } from "react";
import { UseDataTableReturn, DataTableState, DataTableCallbacks, DataTableMetric } from "../types/dataTable.types";
import { ITILCard } from "../config/tables/itil-analytics.config";
import { api } from "../services/api";

interface ItilAnalyticsParams {
  startDate: string;
  endDate: string;
}

interface PaginatedResponse {
  items: ITILCard[];
  total: number;
  page: number;
  pages: number;
  skip: number;
  limit: number;
}

export const useItilAnalyticsDataTable = (
  params: ItilAnalyticsParams
): UseDataTableReturn<ITILCard> => {
  // State
  const [data, setData] = useState<ITILCard[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  // Filters
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({});

  // Sorting
  const [sortBy, setSortBy] = useState("completedDate");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // Selection
  const [selectedItems, setSelectedItems] = useState<number[]>([]);

  // UI State
  const [showDetailedMetrics, setShowDetailedMetrics] = useState(false);
  const [showExportDropdown, setShowExportDropdown] = useState(false);

  // Fetch data from API
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const skip = (currentPage - 1) * pageSize;
      
      // Construir parâmetros da query
      const queryParams: Record<string, any> = {
        skip,
        limit: pageSize,
        start_date: params.startDate,
        end_date: params.endDate,
        sort_by: sortBy,
        sort_order: sortOrder,
      };

      // Adicionar busca
      if (searchTerm.trim()) {
        queryParams.search = searchTerm.trim();
      }

      // Adicionar filtros ativos
      Object.entries(activeFilters).forEach(([key, value]) => {
        if (value && value !== "all") {
          // Converter filtros booleanos
          if (key === "has_window" || key === "has_cab" || key === "has_backout") {
            queryParams[key] = value === "true";
          } else {
            queryParams[key] = value;
          }
        }
      });

      // Fazer requisição
      const response = await api.get<PaginatedResponse>(
        "/api/v1/kanban/analytics/itil-cards-paginated",
        { params: queryParams }
      );

      // Mapear dados para incluir id (alias de cardId)
      const mappedData = response.data.items.map(item => ({
        ...item,
        id: item.cardId,
        status: "completed", // Todos os cards estão concluídos
        created_at: item.completedDate || new Date().toISOString(),
        updated_at: item.completedDate || new Date().toISOString(),
      }));

      setData(mappedData);
      setTotalRecords(response.data.total);
      setTotalPages(response.data.pages);
      
    } catch (err: any) {
      console.error("Error fetching ITIL cards:", err);
      setError(err.response?.data?.detail || "Erro ao carregar dados");
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [
    currentPage,
    pageSize,
    params.startDate,
    params.endDate,
    searchTerm,
    activeFilters,
    sortBy,
    sortOrder,
  ]);

  // Fetch data when dependencies change
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Reset to page 1 when filters change
  useEffect(() => {
    if (currentPage !== 1) {
      setCurrentPage(1);
    }
  }, [searchTerm, activeFilters, sortBy, sortOrder]);

  // Callbacks
  const callbacks: DataTableCallbacks<ITILCard> = {
    onPageChange: (page: number) => {
      setCurrentPage(page);
    },

    onPageSizeChange: (size: number) => {
      setPageSize(size);
      setCurrentPage(1); // Reset to first page
    },

    onSearch: (term: string) => {
      setSearchTerm(term);
    },

    onFilter: (key: string, value: any) => {
      setActiveFilters(prev => ({ ...prev, [key]: value }));
    },

    onClearFilters: () => {
      setActiveFilters({});
      setSearchTerm("");
    },

    onSelectAll: (selected: boolean) => {
      if (selected) {
        setSelectedItems(data.map(item => item.id));
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

    onExport: (format: string, data?: ITILCard[]) => {
      const exportData = (data || []).map(item => ({
        ID: item.externalCardId,
        Título: item.title,
        Categoria: item.itilCategory,
        Coluna: item.columnName,
        Risco: item.riskLevel,
        SLA: item.metSLA === null ? "-" : item.metSLA ? "Atendido" : `${item.daysLate}d atraso`,
        Conclusão: item.completedDate ? new Date(item.completedDate).toLocaleDateString("pt-BR") : "-",
      }));

      if (format === "csv") {
        // Converter para CSV
        const headers = Object.keys(exportData[0] || {});
        const csvContent = [
          headers.join(","),
          ...exportData.map(row =>
            headers.map(header => `"${row[header as keyof typeof row]}"`).join(",")
          ),
        ].join("\n");

        // Download
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `relatorio-itil-${new Date().toISOString().split("T")[0]}.csv`;
        link.click();
      } else {
        // JSON
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
          type: "application/json",
        });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `relatorio-itil-${new Date().toISOString().split("T")[0]}.json`;
        link.click();
      }
    },

    onAction: (actionId: string, item: ITILCard) => {
      // Handle individual actions
      console.log("Action:", actionId, "Item:", item);
    },

    onBulkAction: (actionId: string, items: ITILCard[]) => {
      // Handle bulk actions
      console.log("Bulk Action:", actionId, "Items:", items);
    },

    // UI State callbacks
    onToggleDetailedMetrics: () => {
      setShowDetailedMetrics(prev => !prev);
    },

    onToggleExportDropdown: () => {
      setShowExportDropdown(prev => !prev);
    },

    onOpenModal: (item: ITILCard) => {
      // Handle modal opening
      console.log("Open modal for:", item);
    },

    onCloseModal: () => {
      // Handle modal closing
      console.log("Close modal");
    },
  };

  // Metrics
  const metrics: DataTableMetric[] = [
    {
      id: "total_cards",
      title: "Total de Cards",
      value: totalRecords,
      subtitle: "concluídos no período",
      icon: "📊",
      color: "blue",
    },
    {
      id: "sla_compliance",
      title: "SLA Compliance",
      value: data.length > 0
        ? Math.round(
            (data.filter(item => item.metSLA === true).length /
             data.filter(item => item.metSLA !== null).length) * 100
          ) || 0
        : 0,
      subtitle: "percentual de atendimento",
      icon: "✓",
      color: "green",
    },
    {
      id: "high_risk",
      title: "Alto Risco",
      value: data.filter(item => item.riskLevel === "High").length,
      subtitle: "cards de alto risco",
      icon: "⚠",
      color: "red",
    },
  ];

  // State
  const state: DataTableState = {
    data,
    filteredData: data, // For now, same as data
    loading,
    error,
    currentPage,
    pageSize,
    totalPages,
    total: totalRecords,
    searchTerm,
    activeFilters,
    selectedItems,
    showDetailedMetrics,
    showExportDropdown,
    selectedItemForModal: null,
    isModalOpen: false,
  };

  return {
    state,
    callbacks,
    metrics,
  };
};
