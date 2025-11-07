/**
 * ITIL Analytics Table Configuration
 * Configuração da tabela de cards ITIL com paginação e filtros avançados
 */

import React from "react";
import {
  Eye,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  TrendingUp,
} from "lucide-react";
import { DataTableConfig } from "../../types/dataTable.types";

// Interface para card ITIL (estende BaseEntity)
export interface ITILCard {
  id: number; // Alias para cardId (requerido por BaseEntity)
  cardId: number;
  externalCardId: string;
  title: string;
  itilCategory: string;
  columnName: string;
  riskLevel: string;
  hasWindow: boolean;
  hasCAB: boolean;
  hasBackout: boolean;
  metSLA: boolean | null;
  daysLate: number | null;
  completedDate: string | null;
  status: string; // Requerido por BaseEntity
  created_at: string; // Requerido por BaseEntity
  updated_at: string; // Requerido por BaseEntity
}

// Cores por categoria ITIL
const CATEGORY_COLORS: Record<string, string> = {
  'Change': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  'Incident': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  'Service Request': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  'Operation Task': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200'
};

// Cores por nível de risco
const RISK_COLORS: Record<string, string> = {
  'High': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  'Medium': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  'Low': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
};

// Formatar data
const formatDate = (dateString: string | null): string => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR');
};

export const createItilAnalyticsConfig = (
  navigate?: (path: string) => void,
  actionHandlers?: {
    onViewDetails?: (cardId: number) => void;
  }
): DataTableConfig<ITILCard> => ({
  // Informações Básicas
  entity: "itil-card",
  title: "📋 Relatório ITIL - Cards Concluídos",
  description: "Análise detalhada de cards por categoria ITIL com métricas de SLA e risco",

  // Estrutura de Dados - Colunas
  columns: [
    {
      key: "externalCardId",
      label: "ID",
      type: "text",
      sortable: true,
      render: (value) => (
        <span className="font-mono text-sm font-medium text-gray-900 dark:text-gray-100">
          {value}
        </span>
      ),
    },
    {
      key: "title",
      label: "Título",
      type: "text",
      sortable: true,
      render: (value) => (
        <div className="max-w-xs truncate text-sm text-gray-900 dark:text-gray-100" title={value}>
          {value}
        </div>
      ),
    },
    {
      key: "itilCategory",
      label: "Categoria ITIL",
      type: "custom",
      sortable: true,
      render: (value) => (
        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
          CATEGORY_COLORS[value] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
        }`}>
          {value}
        </span>
      ),
    },
    {
      key: "columnName",
      label: "Coluna",
      type: "text",
      sortable: true,
      render: (value) => (
        <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
          {value}
        </span>
      ),
    },
    {
      key: "riskLevel",
      label: "Risco",
      type: "custom",
      sortable: true,
      render: (value) => (
        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
          RISK_COLORS[value] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
        }`}>
          {value}
        </span>
      ),
    },
    {
      key: "hasWindow",
      label: "Metadados",
      type: "custom",
      render: (_, item) => (
        <div className="flex gap-1">
          {item.hasWindow && (
            <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200 rounded" title="Janela de Mudança">
              Janela
            </span>
          )}
          {item.hasCAB && (
            <span className="px-2 py-1 text-xs bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200 rounded" title="Change Advisory Board">
              CAB
            </span>
          )}
          {item.hasBackout && (
            <span className="px-2 py-1 text-xs bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200 rounded" title="Plano de Backout">
              Backout
            </span>
          )}
        </div>
      ),
    },
    {
      key: "metSLA",
      label: "SLA",
      type: "custom",
      sortable: true,
      render: (value, item) => {
        if (value === null) {
          return <span className="text-sm text-gray-400 dark:text-gray-500">-</span>;
        }
        
        return value ? (
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-sm text-green-600 dark:text-green-400 font-medium">Atendido</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <XCircle className="h-5 w-5 text-red-500" />
            <span className="text-sm text-red-600 dark:text-red-400 font-medium">
              {item.daysLate}d atraso
            </span>
          </div>
        );
      },
    },
    {
      key: "completedDate",
      label: "Conclusão",
      type: "date",
      sortable: true,
      render: (value) => (
        <span className="text-sm text-gray-900 dark:text-gray-100">
          {formatDate(value)}
        </span>
      ),
    },
  ],

  // Filtros Avançados
  filters: [
    {
      key: "category_filter",
      label: "Categoria ITIL",
      type: "select",
      options: [
        { value: "all", label: "Todas" },
        { value: "Change", label: "Change" },
        { value: "Incident", label: "Incident" },
        { value: "Service Request", label: "Service Request" },
        { value: "Operation Task", label: "Operation Task" },
      ],
    },
    {
      key: "risk_filter",
      label: "Nível de Risco",
      type: "select",
      options: [
        { value: "all", label: "Todos" },
        { value: "High", label: "Alto" },
        { value: "Medium", label: "Médio" },
        { value: "Low", label: "Baixo" },
      ],
    },
    {
      key: "sla_filter",
      label: "Status SLA",
      type: "select",
      options: [
        { value: "all", label: "Todos" },
        { value: "met", label: "Atendido" },
        { value: "missed", label: "Não Atendido" },
      ],
    },
    {
      key: "has_window",
      label: "Com Janela",
      type: "select",
      options: [
        { value: "all", label: "Todos" },
        { value: "true", label: "Sim" },
        { value: "false", label: "Não" },
      ],
    },
    {
      key: "has_cab",
      label: "Com CAB",
      type: "select",
      options: [
        { value: "all", label: "Todos" },
        { value: "true", label: "Sim" },
        { value: "false", label: "Não" },
      ],
    },
    {
      key: "has_backout",
      label: "Com Backout",
      type: "select",
      options: [
        { value: "all", label: "Todos" },
        { value: "true", label: "Sim" },
        { value: "false", label: "Não" },
      ],
    },
  ],

  // Métricas
  metrics: {
    primary: [
    {
      key: "total",
      label: "Total de Cards",
      icon: <TrendingUp className="h-5 w-5" />,
      color: "blue",
      getValue: (data) => data?.length || 0,
    },
    {
      key: "slaCompliance",
      label: "SLA Compliance",
      icon: <CheckCircle className="h-5 w-5" />,
      color: "green",
      format: "percentage",
      getValue: (data) => {
        if (!data || data.length === 0) return 0;
        const withSLA = data.filter((item: ITILCard) => item.metSLA !== null);
        if (withSLA.length === 0) return 0;
        const met = withSLA.filter((item: ITILCard) => item.metSLA === true).length;
        return (met / withSLA.length) * 100;
      },
    },
    {
      key: "highRisk",
      label: "Alto Risco",
      icon: <AlertTriangle className="h-5 w-5" />,
      color: "red",
      getValue: (data) => {
        if (!data) return 0;
        return data.filter((item: ITILCard) => item.riskLevel === 'High').length;
      },
    },
    ],
  },

  // Ações
  actions: [
    {
      label: "Ver Detalhes",
      icon: <Eye className="h-4 w-4" />,
      onClick: (item) => {
        if (actionHandlers?.onViewDetails) {
          actionHandlers.onViewDetails(item.cardId);
        }
      },
    },
  ],

  // Configuração de Exportação
  exportConfig: {
    filename: "relatorio-itil",
    formats: ["csv", "json"],
    columns: [
      "externalCardId",
      "title",
      "itilCategory",
      "columnName",
      "riskLevel",
      "metSLA",
      "daysLate",
      "completedDate",
    ],
  },

  // Configuração de Paginação
  pagination: {
    defaultPageSize: 50,
    pageSizeOptions: [25, 50, 100],
  },

  // Configuração de Busca
  searchConfig: {
    placeholder: "Buscar por ID, título ou descrição...",
    debounceMs: 300,
  },

  // Tema
  theme: "default",

  // Não mostrar botão de adicionar
  hideAddButton: true,

  // Não mostrar seleção múltipla
  disableSelection: true,
});
