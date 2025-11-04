/**
 * Status utilities for companies
 */

export function getStatusBadge(status: string): string {
  const statusConfig: Record<string, string> = {
    active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
    inactive: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300",
    suspended:
      "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
  };

  return `inline-flex px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap ${
    statusConfig[status] || statusConfig["inactive"]
  }`;
}

export function getStatusLabel(status: string): string {
  const statusLabels: Record<string, string> = {
    active: "Ativo",
    inactive: "Inativo",
    suspended: "Suspenso",
  };

  return statusLabels[status] || status;
}

// Re-export formatters used in CompanyDetails.jsx for backwards compatibility
export { formatPhone, formatCEP as formatZipCode } from "./formatters";

// Label functions for contact types
export function getPhoneTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    mobile: "Celular",
    home: "Residencial",
    work: "Comercial",
    whatsapp: "WhatsApp",
    other: "Outro",
  };
  return labels[type] || type;
}

export function getEmailTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    personal: "Pessoal",
    work: "Comercial",
    other: "Outro",
  };
  return labels[type] || type;
}

export function getAddressTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    main: "Principal",
    billing: "Cobrança",
    shipping: "Entrega",
    other: "Outro",
  };
  return labels[type] || type;
}
