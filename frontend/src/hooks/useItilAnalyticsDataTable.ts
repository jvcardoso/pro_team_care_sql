/**
 * useItilAnalyticsDataTable Hook
 * Hook personalizado para tabela ITIL com paginação server-side
 */

import { useState, useEffect, useCallback } from "react";
import { UseDataTableReturn } from "../types/dataTable.types";
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
        "/kanban/analytics/itil-cards-paginated",
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
  const callbacks: UseDataTableReturn<ITILCard>["callbacks"] = {
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
    
    onFilterChange: (filters: Record<string, any>) => {
      setActiveFilters(filters);
    },
    
    onSort: (field: string) => {
      if (sortBy === field) {
        // Toggle order
        setSortOrder(sortOrder === "asc" ? "desc" : "asc");
      } else {
        // New field, default to desc
        setSortBy(field);
        setSortOrder("desc");
      }
    },
    
    onSelectItem: (id: number) => {
      setSelectedItems(prev =>
        prev.includes(id)
          ? prev.filter(itemId => itemId !== id)
          : [...prev, id]
      );
    },
    
    onSelectAll: () => {
      if (selectedItems.length === data.length) {
        setSelectedItems([]);
      } else {
        setSelectedItems(data.map(item => item.id));
      }
    },
    
    onClearSelection: () => {
      setSelectedItems([]);
    },
    
    onRefresh: () => {
      fetchData();
    },
    
    onExport: (format: "csv" | "json") => {
      // Exportar dados atuais
      const exportData = data.map(item => ({
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
    
    toggleDetailedMetrics: () => {
      setShowDetailedMetrics(prev => !prev);
    },
    
    toggleExportDropdown: () => {
      setShowExportDropdown(prev => !prev);
    },
  };

  // Metrics
  const metrics = {
    primary: [
      {
        label: "Total de Cards",
        value: totalRecords,
        color: "blue" as const,
      },
      {
        label: "SLA Compliance",
        value: data.length > 0
          ? Math.round(
              (data.filter(item => item.metSLA === true).length / 
               data.filter(item => item.metSLA !== null).length) * 100
            ) || 0
          : 0,
        format: "percentage" as const,
        color: "green" as const,
      },
      {
        label: "Alto Risco",
        value: data.filter(item => item.riskLevel === "High").length,
        color: "red" as const,
      },
    ],
  };

  // State
  const state: UseDataTableReturn<ITILCard>["state"] = {
    data,
    loading,
    error,
    currentPage,
    pageSize,
    totalRecords,
    totalPages,
    searchTerm,
    activeFilters,
    sortBy,
    sortOrder,
    selectedItems,
    showDetailedMetrics,
    showExportDropdown,
  };

  return {
    state,
    callbacks,
    metrics,
  };
};
