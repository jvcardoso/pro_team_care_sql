// frontend/src/hooks/useCompaniesDataTable.fixed.ts
/**
 * Hook atualizado para DataTable de empresas
 * Alinhado com APIs backend validadas
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { CompaniesService, Company, PaginatedResponse } from '../services/companiesService';
import { useToast } from '@/components/ui/use-toast';

interface UseCompaniesDataTableProps {
  initialPageSize?: number;
  autoLoad?: boolean;
}

interface DataTableState {
  data: Company[];
  loading: boolean;
  error: string | null;
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  // Propriedades adicionais para funcionalidades avançadas
  filteredData?: Company[];
  currentPage?: number;
  searchTerm?: string;
  activeFilters?: any;
  selectedItems?: any[];
  showDetailedMetrics?: boolean;
  showExportDropdown?: boolean;
  selectedItemForModal?: any;
  isModalOpen?: boolean;
}

interface DataTableFilters {
  status?: 'active' | 'inactive';
  search?: string;
}

export const useCompaniesDataTable = ({
  initialPageSize = 10,
  autoLoad = true
}: UseCompaniesDataTableProps = {}) => {
  
  const { toast } = useToast();
  
  // Estado principal
  const [state, setState] = useState<DataTableState>({
    data: [],
    filteredData: [],
    loading: false,
    error: null,
    total: 0,
    currentPage: 1,
    pageSize: initialPageSize,
    totalPages: 0,
    searchTerm: '',
    activeFilters: {},
    selectedItems: [],
    showDetailedMetrics: false,
    showExportDropdown: false,
    selectedItemForModal: null,
    isModalOpen: false
  });
  
  // Filtros
  const [filters, setFilters] = useState<DataTableFilters>({
    status: 'active' // Por padrão, mostrar apenas ativas
  });
  
  // Função para carregar dados
  const loadData = useCallback(async (
    page: number = 1,
    pageSize: number = initialPageSize,
    currentFilters: DataTableFilters = filters
  ) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const skip = (page - 1) * pageSize;
      
      const response: PaginatedResponse<Company> = await CompaniesService.list({
        skip,
        limit: pageSize,
        status: currentFilters.status,
        search: currentFilters.search
      });
      
      setState(prev => ({
        ...prev,
        data: response.items || [],
        filteredData: response.items || [],
        total: response.total || 0,
        currentPage: response.page || 1,
        pageSize: response.size || initialPageSize,
        totalPages: response.pages || 0,
        loading: false
      }));
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao carregar empresas';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive"
      });
    }
  }, [filters, toast]);
  
  // Função para alterar página
  const goToPage = useCallback((page: number) => {
    if (page >= 1 && page <= state.totalPages) {
      setState(prev => ({ ...prev, currentPage: page }));
      loadData(page, state.pageSize, filters);
    }
  }, [state.pageSize, state.totalPages, filters, loadData]);
  
  // Função para alterar tamanho da página
  const changePageSize = useCallback((pageSize: number) => {
    setState(prev => ({ ...prev, pageSize, currentPage: 1 }));
    loadData(1, pageSize, filters);
  }, [filters, loadData]);
  
  // Função para aplicar filtros
  const applyFilters = useCallback((newFilters: DataTableFilters) => {
    setFilters(newFilters);
    setState(prev => ({ ...prev, currentPage: 1 }));
    loadData(1, state.pageSize, newFilters);
  }, [state.pageSize, loadData]);
  
  // Função para limpar filtros
  const clearFilters = useCallback(() => {
    const defaultFilters = { status: 'active' as const };
    setFilters(defaultFilters);
    setState(prev => ({ ...prev, currentPage: 1 }));
    loadData(1, state.pageSize, defaultFilters);
  }, [state.pageSize, loadData]);
  
  // Função para recarregar dados
  const refresh = useCallback(() => {
    loadData(state.currentPage, state.pageSize, filters);
  }, [state.currentPage, state.pageSize, filters, loadData]);
  
  // Função para busca rápida
  const search = useCallback((searchTerm: string) => {
    const newFilters = { ...filters, search: searchTerm || undefined };
    applyFilters(newFilters);
  }, [filters, applyFilters]);
  
  // Função para alternar status
  const toggleStatus = useCallback((status: 'active' | 'inactive') => {
    const newFilters = { ...filters, status };
    applyFilters(newFilters);
  }, [filters, applyFilters]);
  
  // ========================================
  // AÇÕES CRUD
  // ========================================
  
  // Função para inativar empresa
  const deactivateCompany = useCallback(async (id: number) => {
    try {
      await CompaniesService.deactivate(id);
      
      toast({
        title: "Sucesso",
        description: "Empresa inativada com sucesso"
      });
      
      // Recarregar dados
      refresh();
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao inativar empresa';
      
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive"
      });
    }
  }, [refresh, toast]);
  
  // Função para ativar empresa
  const activateCompany = useCallback(async (id: number) => {
    try {
      await CompaniesService.activate(id);
      
      toast({
        title: "Sucesso",
        description: "Empresa ativada com sucesso"
      });
      
      // Recarregar dados
      refresh();
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao ativar empresa';
      
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive"
      });
    }
  }, [refresh, toast]);
  
  // Função para revelar dados sensíveis
  const revealSensitiveData = useCallback(async (id: number, fields?: string[]) => {
    try {
      const company = await CompaniesService.revealSensitiveData(id, fields);
      
      // Atualizar empresa na lista local
      setState(prev => ({
        ...prev,
        data: prev.data.map(item => 
          item.id === id ? company : item
        )
      }));
      
      toast({
        title: "Dados Revelados",
        description: "Dados sensíveis revelados com sucesso. Ação registrada nos logs LGPD."
      });
      
      return company;
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao revelar dados';
      
      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive"
      });
      
      throw error;
    }
  }, [toast]);
  
  // ========================================
  // EFEITOS
  // ========================================
  
  // Carregar dados iniciais
  useEffect(() => {
    if (autoLoad) {
      loadData();
    }
  }, []); // Executar apenas uma vez
  
  // ========================================
  // DADOS COMPUTADOS
  // ========================================
  
  const hasData = state.data && state.data.length > 0;
  const isEmpty = !state.loading && !hasData && !state.error;
  const hasError = !!state.error;
  const hasNextPage = state.currentPage < state.totalPages;
  const hasPreviousPage = state.currentPage > 1;
  
  // Informações de paginação
  const paginationInfo = {
    from: state.total === 0 ? 0 : (state.currentPage - 1) * state.pageSize + 1,
    to: Math.min(state.currentPage * state.pageSize, state.total),
    total: state.total,
    page: state.currentPage,
    totalPages: state.totalPages
  };
  
  return useMemo(() => ({
    // Spread state properties for backward compatibility
    ...state,

    state: {
      ...state,
      // Propriedades obrigatórias do DataTableState
      filteredData: state.data || [], // Dados já filtrados pela API
      currentPage: state.currentPage,
      searchTerm: filters.search || '',
      activeFilters: filters as Record<string, any>,
      selectedItems: [],
      showDetailedMetrics: false,
      showExportDropdown: false,
      selectedItemForModal: null,
      isModalOpen: false,
    },
    callbacks: {
      onPageChange: goToPage,
      onPageSizeChange: changePageSize,
      onSearch: search,
      onFilter: (key: string, value: any) => {
        if (key === 'status') {
          toggleStatus(value as 'active' | 'inactive');
        } else {
          applyFilters({ ...filters, [key]: value });
        }
      },
      onClearFilters: clearFilters,
      onSelectAll: () => {},
      onSelectItem: () => {},
      onExport: () => {},
      onAction: () => {},
      onBulkAction: () => {},
      onToggleDetailedMetrics: () => {},
      onToggleExportDropdown: () => {},
      onOpenModal: () => {},
      onCloseModal: () => {},
    },
    metrics: [], // Empty metrics for now
    detailedMetrics: undefined,

    // Keep the original properties for backward compatibility
    filters,
    hasData,
    isEmpty,
    hasError,
    hasNextPage,
    hasPreviousPage,
    paginationInfo,
    goToPage,
    changePageSize,
    refresh,
    applyFilters,
    clearFilters,
    search,
    toggleStatus,
    deactivateCompany,
    activateCompany,
    revealSensitiveData,
    loadData
  }), [
    state,
    filters,
    hasData,
    isEmpty,
    hasError,
    hasNextPage,
    hasPreviousPage,
    paginationInfo,
    goToPage,
    changePageSize,
    refresh,
    applyFilters,
    clearFilters,
    search,
    toggleStatus,
    deactivateCompany,
    activateCompany,
    revealSensitiveData,
    loadData
  ]);
};

export default useCompaniesDataTable;
