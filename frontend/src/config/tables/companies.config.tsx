/**
 * Companies Table Configuration
 * Defines all settings for the companies data table
 */

import React from "react";
import {
  Building,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Eye,
  Edit,
  Trash2,
  RefreshCw,
  Users,
  UserCheck,
  User,
  Shield,
  AlertTriangle,
} from "lucide-react";
import { DataTableConfig } from "../../types/dataTable.types";
import { Company } from "../../types/company.types";
import { getStatusBadge, getStatusLabel } from "../../utils/statusUtils";

export const createCompaniesConfig = (
  navigate?: (path: string) => void,
  actionHandlers?: {
    onDelete?: (companyId: number) => void;
    onReactivate?: (companyId: number) => void;
  },
  cleanupHandlers?: {
    onCleanup?: () => void;
  }
): DataTableConfig<Company> => ({
  // Basic Info
  entity: "empresa",
  title: "🏢 Dashboard de Empresas",
  description: "Gestão completa de empresas cadastradas no sistema",

  // Data Structure
  columns: [
    {
      key: "name",
      label: "Empresa",
      type: "text",
      sortable: true,
      render: (value, item) => (
        <div>
          <div className="text-base font-semibold">{value || 'Nome não disponível'}</div>
          {item.trade_name && item.trade_name !== value && (
            <div className="font-normal text-gray-500 text-sm">
              {item.trade_name || 'Nome fantasia não disponível'}
            </div>
          )}
        </div>
      ),
    },
    {
      key: "tax_id",
      label: "CNPJ",
      type: "text",
      render: (value) => (
        <div className="flex items-center gap-1">
          <span className="font-mono text-sm text-foreground">{value || 'CNPJ não disponível'}</span>
          <Shield className="h-3 w-3 text-orange-500 flex-shrink-0" title="Dado Protegido - LGPD" />
        </div>
      ),
    },
    {
      key: "establishments_count",
      label: "Entidades",
      type: "custom",
      render: (value, item) => (
        <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-xs">
          <div className="flex items-center text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors whitespace-nowrap">
            <Building className="w-3 h-3 mr-1.5 flex-shrink-0" />
            <span className="font-semibold">
              {item.establishments_count || 0}
            </span>
            <span className="ml-1 text-gray-500 dark:text-gray-400">est.</span>
          </div>
          <div className="flex items-center text-green-600 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300 transition-colors whitespace-nowrap">
            <Users className="w-3 h-3 mr-1.5 flex-shrink-0" />
            <span className="font-semibold">{item.clients_count || 0}</span>
            <span className="ml-1 text-gray-500 dark:text-gray-400">cli.</span>
          </div>
          <div className="flex items-center text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 transition-colors whitespace-nowrap">
            <UserCheck className="w-3 h-3 mr-1.5 flex-shrink-0" />
            <span className="font-semibold">
              {item.professionals_count || 0}
            </span>
            <span className="ml-1 text-gray-500 dark:text-gray-400">pro.</span>
          </div>
          <div className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors whitespace-nowrap">
            <User className="w-3 h-3 mr-1.5 flex-shrink-0" />
            <span className="font-semibold">{item.users_count || 0}</span>
            <span className="ml-1 text-gray-500 dark:text-gray-400">usr.</span>
          </div>
        </div>
      ),
    },
    {
      key: "status",
      label: "Status",
      type: "badge",
      render: (value) => (
        <span className={getStatusBadge(value)}>{getStatusLabel(value)}</span>
      ),
    },
    {
      key: "created_at",
      label: "Criado em",
      type: "date",
      render: (value) => (
        <div className="flex items-center">
          <Calendar className="w-4 h-4 mr-2 text-gray-400" />
          <span>{value ? new Date(value).toLocaleDateString("pt-BR") : 'Data não disponível'}</span>
        </div>
      ),
    },
  ],

  searchFields: ["name", "trade_name", "tax_id"],
  sortField: "created_at",
  sortDirection: "desc",

  // Metrics
  metrics: {
    primary: [
      {
        id: "total_companies",
        title: "Total Empresas",
        value: 0, // Will be calculated dynamically
        subtitle: "cadastradas",
        icon: (
          <svg
            className="h-6 w-6 text-blue-600 dark:text-blue-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
            />
          </svg>
        ),
        color: "blue",
      },
      {
        id: "active_companies",
        title: "Empresas Ativas",
        value: 0, // Will be calculated dynamically
        subtitle: "({percentage}%)",
        icon: (
          <svg
            className="h-6 w-6 text-green-600 dark:text-green-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        ),
        color: "green",
      },
      {
        id: "inactive_companies",
        title: "Empresas Inativas",
        value: 0, // Will be calculated dynamically
        subtitle: "({percentage}%)",
        icon: (
          <svg
            className="h-6 w-6 text-gray-600 dark:text-gray-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        ),
        color: "gray",
      },
      {
        id: "suspended_companies",
        title: "Empresas Suspensas",
        value: 0, // Will be calculated dynamically
        subtitle: "({percentage}%)",
        icon: (
          <svg
            className="h-6 w-6 text-yellow-600 dark:text-yellow-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
        ),
        color: "yellow",
      },
    ],
    detailed: {
      title: "📊 Estatísticas de Empresas",
      sections: [
        {
          title: "📈 Status das Empresas",
          items: [
            {
              id: "active_companies",
              title: "✅ Ativas",
              value: 0,
              subtitle: "({percentage}%)",
              icon: <span>✅</span>,
              color: "green",
            },
            {
              id: "inactive_companies",
              title: "⏸️ Inativas",
              value: 0,
              subtitle: "({percentage}%)",
              icon: <span>⏸️</span>,
              color: "gray",
            },
            {
              id: "suspended_companies",
              title: "⏳ Suspensas",
              value: 0,
              subtitle: "({percentage}%)",
              icon: <span>⏳</span>,
              color: "yellow",
            },
          ],
        },
        {
          title: "📅 Cadastros Recentes",
          items: [
            {
              id: "recent_week",
              title: "📅 Esta semana",
              value: 0,
              subtitle: "novas empresas",
              icon: <span>📅</span>,
              color: "blue",
            },
            {
              id: "recent_month",
              title: "📆 Este mês",
              value: 0,
              subtitle: "novas empresas",
              icon: <span>📆</span>,
              color: "purple",
            },
          ],
        },
      ],
      quickActions: [
        {
          label: "📊 Exportar Ativas",
          action: () => {
            // This will be implemented in the component
          },
          color: "green",
        },
        {
          label: "📋 Relatório Geral",
          action: () => {
            // This will be implemented in the component
          },
          color: "purple",
        },
      ],
    },
  },

  // Actions
  actions: {
    toolbar: [
      {
        key: "cleanup",
        label: "Limpar Pendentes",
        icon: <AlertTriangle className="h-4 w-4" />,
        variant: "danger" as const,
        action: () => {
          if (cleanupHandlers?.onCleanup) {
            cleanupHandlers.onCleanup();
          } else {
            console.error("❌ [companies.config] cleanupHandlers.onCleanup não existe!");
          }
        },
      },
    ],
  },

  // Filters
  filters: [
    {
      key: "status",
      label: "Status",
      type: "select",
      options: [
        { value: "all", label: "📋 Todos os status" },
        { value: "active", label: "✅ Ativo" },
        { value: "inactive", label: "⏸️ Inativo" },
        { value: "suspended", label: "⏳ Suspenso" },
      ],
    },
  ],

  // Actions - função que retorna ações baseadas no status da empresa
  getActions: (company) => {
    const baseActions = [
      {
        id: "view",
        label: "Ver Detalhes",
        icon: <Eye className="w-4 h-4" />,
        color: "blue",
        onClick: () => {
          if (navigate) {
            navigate(`/admin/companies/${company.id}?tab=information`);
          } else {
            window.location.href = `/admin/companies/${company.id}?tab=information`;
          }
        },
      },
      {
        id: "edit",
        label: "Editar",
        icon: <Edit className="w-4 h-4" />,
        color: "yellow",
        onClick: () => {
          if (navigate) {
            navigate(`/admin/companies?companyId=${company.id}&action=edit`);
          } else {
            window.location.href = `/admin/companies?companyId=${company.id}&action=edit`;
          }
        },
      },
    ];

    // Adicionar ação de Inativar OU Reativar baseado no status
    if (company.status === "inactive") {
      // Empresa inativa - mostrar opção de Reativar
      baseActions.push({
        id: "reactivate",
        label: "Reativar",
        icon: <RefreshCw className="w-4 h-4" />,
        color: "green",
        onClick: () => {
          if (actionHandlers?.onReactivate) {
            actionHandlers.onReactivate(company.id);
          } else {
            console.error(
              "❌ [companies.config] actionHandlers.onReactivate não existe!"
            );
          }
        },
      });
    } else {
      // Empresa ativa - mostrar opção de Inativar
      baseActions.push({
        id: "delete",
        label: "Inativar",
        icon: <Trash2 className="w-4 h-4" />,
        color: "red",
        onClick: () => {
          if (actionHandlers?.onDelete) {
            actionHandlers.onDelete(company.id);
          } else {
            console.error(
              "❌ [companies.config] actionHandlers.onDelete não existe!"
            );
          }
        },
      });
    }

    return baseActions;
  },

  // Show add button
  showAddButton: true,
  onAdd: () => {
    if (navigate) {
      navigate("/admin/companies?view=create");
    }
  },

  // Export
  export: {
    filename: "empresas",
    formats: ["csv", "json", "print"],
    includeFiltered: true,
  },

  // Pagination
  defaultPageSize: 10,
  pageSizeOptions: [10, 25, 50, 100],

  // Customization
  className: "",
  theme: "default",
});

// Versão padrão para compatibilidade
export const companiesConfig = createCompaniesConfig();

export default companiesConfig;
