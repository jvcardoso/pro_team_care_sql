/**
 * LGPD Audit Logs Table Configuration
 * Configuração da tabela de logs de auditoria LGPD
 */

import React from "react";
import { Clock, User, Search, Filter, Download, RefreshCw } from "lucide-react";
import { DataTableConfig } from "../../types/dataTable.types";
import { AuditLogItem } from "../../types/auditLog.types";

interface LgpdAuditLogsConfigProps {
  onRefresh?: () => void;
  onExport?: () => void;
}

export const createLgpdAuditLogsConfig = ({
  onRefresh,
  onExport,
}: LgpdAuditLogsConfigProps = {}): DataTableConfig<AuditLogItem> => ({
  // Informações básicas
  entity: "log_lgpd",
  title: "🔒 Logs de Auditoria LGPD",
  description: "Registro de todas as ações relacionadas a dados sensíveis",

  // Estrutura de dados
  columns: [
    {
      key: "created_at",
      label: "Data/Hora",
      type: "date",
      sortable: true,
      render: (value) => (
        <div className="flex items-center">
          <Clock className="w-4 h-4 mr-2 text-gray-400" />
          <span>{new Date(value).toLocaleString("pt-BR")}</span>
        </div>
      ),
    },
    {
      key: "action_type",
      label: "Ação",
      type: "badge",
      render: (value) => {
        const actionStyles = {
          REVEAL: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
          VIEW: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
          EDIT: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
          UPDATE: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
          CREATE: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
          DELETE: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
          default: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300",
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
      type: "text",
      sortable: true,
      render: (value, item) => (
        <div className="flex items-center">
          <User className="w-4 h-4 mr-2 text-gray-400" />
          <span>{value || `Usuário #${item.user_id}`}</span>
        </div>
      ),
    },
    {
      key: "ip_address",
      label: "Endereço IP",
      type: "text",
      render: (value) => value || "-",
    },
    {
      key: "sensitive_fields",
      label: "Campos Acessados",
      type: "text",
      render: (value) => (
        <div className="max-w-xs truncate" title={value?.join(", ") || "-"}>
          {value?.join(", ") || "-"}
        </div>
      ),
    },
  ],

  // Campos para busca
  searchFields: ["user_email", "action_type", "ip_address", "sensitive_fields"],
  sortField: "created_at",
  sortDirection: "desc",

  // Ações da tabela
  actions: [
    {
      id: "refresh",
      label: "Atualizar",
      icon: <RefreshCw className="w-4 h-4 mr-1" />,
      onClick: onRefresh,
      variant: "outline",
    },
    {
      id: "export",
      label: "Exportar",
      icon: <Download className="w-4 h-4 mr-1" />,
      onClick: onExport,
      variant: "outline",
    },
  ],

  // Filtros
  filters: [
    {
      id: "action_type",
      label: "Tipo de Ação",
      type: "select",
      options: [
        { value: "all", label: "Todas as Ações" },
        { value: "REVEAL", label: "Revelação de Dados" },
        { value: "VIEW", label: "Visualização" },
        { value: "EDIT", label: "Edição" },
        { value: "CREATE", label: "Criação" },
        { value: "DELETE", label: "Exclusão" },
      ],
      placeholder: "Filtrar por tipo de ação",
    },
  ],

  // Configuração de paginação
  pagination: {
    showSizeChanger: true,
    pageSizeOptions: [10, 20, 50, 100],
    showTotal: (total: number, range: [number, number]) =>
      `${range[0]}-${range[1]} de ${total} itens`,
  },

  // Mensagens personalizadas
  messages: {
    noData: "Nenhum registro de auditoria encontrado",
    loading: "Carregando registros de auditoria...",
    error: "Erro ao carregar registros de auditoria",
  },
});

export default createLgpdAuditLogsConfig;
