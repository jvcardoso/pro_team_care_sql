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
      width: "w-24", // Largura reduzida para IDs
      render: (value) => (
        <span className="font-mono text-sm font-medium text-gray-900 dark:text-gray-100 whitespace-nowrap">
          {value}
        </span>
      ),
    },
    {
      key: "title",
      label: "Título",
      type: "text",
      sortable: true,
      width: "w-40", // Largura reduzida para títulos
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
      width: "w-28", // Largura reduzida para categoria ITIL
      render: (value) => (
        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full whitespace-nowrap ${
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
      width: "w-28", // Largura para nome da coluna
      render: (value) => (
        <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full whitespace-nowrap bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
          {value}
        </span>
      ),
    },
    {
      key: "riskLevel",
      label: "Risco",
      type: "custom",
      sortable: true,
      width: "w-20", // Largura para nível de risco
      render: (value) => (
        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full whitespace-nowrap ${
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
      width: "w-32", // Largura reduzida para metadados
      render: (_, item) => (
        <div className="flex gap-1 whitespace-nowrap">
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
      width: "w-24", // Largura reduzida para status SLA
      render: (value, item) => {
        if (value === null) {
          return <span className="text-sm text-gray-400 dark:text-gray-500">-</span>;
        }

        return value ? (
          <div className="flex items-center gap-2 whitespace-nowrap">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-sm text-green-600 dark:text-green-400 font-medium">Atendido</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 whitespace-nowrap">
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
      width: "w-24", // Largura para data de conclusão
      render: (value) => (
        <span className="text-sm text-gray-900 dark:text-gray-100 whitespace-nowrap">
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
        id: "total_cards",
        title: "Total de Cards",
        value: 0,
        subtitle: "concluídos no período",
        icon: "📊",
        color: "blue",
      },
      {
        id: "sla_compliance",
        title: "SLA Compliance",
        value: 0,
        subtitle: "percentual de atendimento",
        icon: "✓",
        color: "green",
      },
      {
        id: "high_risk",
        title: "Alto Risco",
        value: 0,
        subtitle: "cards de alto risco",
        icon: "⚠",
        color: "red",
      },
    ],
  },

  // Campos de busca
  searchFields: ["externalCardId", "title"] as (keyof ITILCard)[],

  // Ações (coluna sempre visível à direita)
  actions: [
    {
      id: "view_details",
      label: "Ver Detalhes",
      icon: <Eye className="h-4 w-4" />,
      color: "blue",
      onClick: (item) => {
        if (actionHandlers?.onViewDetails) {
          actionHandlers.onViewDetails(item.cardId);
        }
      },
    },
  ],

  // Configuração de Exportação
  export: {
    filename: "relatorio-itil",
    formats: ["csv", "json"],
    includeFiltered: true,
  },

  // Paginação
  defaultPageSize: 50,
  pageSizeOptions: [25, 50, 100],

  // Busca
  searchPlaceholder: "Buscar por ID, título ou descrição...",

  // Tema
  theme: "default",

  // Não mostrar botão de adicionar
  showAddButton: false,
});
