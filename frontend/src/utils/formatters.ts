/**
 * Formatting utilities
 */

export function formatTaxId(taxId: string): string {
  if (!taxId) return "";

  const cleanTaxId = taxId.replace(/\D/g, "");

  if (cleanTaxId.length === 14) {
    // CNPJ: 00.000.000/0000-00
    return cleanTaxId.replace(
      /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
      "$1.$2.$3/$4-$5"
    );
  } else if (cleanTaxId.length === 11) {
    // CPF: 000.000.000-00
    return cleanTaxId.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
  }

  return taxId;
}

export function formatCPF(cpf: string): string {
  if (!cpf) return "";
  const clean = cpf.replace(/\D/g, "");
  if (clean.length !== 11) return cpf;
  return clean.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
}

export function formatCNPJ(cnpj: string): string {
  if (!cnpj) return "";
  const clean = cnpj.replace(/\D/g, "");
  if (clean.length !== 14) return cnpj;
  return clean.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
}

export function formatPhone(phone: string): string {
  if (!phone) return "";
  const clean = phone.replace(/\D/g, "");

  if (clean.length === 11) {
    // Celular: (00) 00000-0000
    return clean.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
  } else if (clean.length === 10) {
    // Fixo: (00) 0000-0000
    return clean.replace(/(\d{2})(\d{4})(\d{4})/, "($1) $2-$3");
  }

  return phone;
}

export function formatCEP(cep: string): string {
  if (!cep) return "";
  const clean = cep.replace(/\D/g, "");
  if (clean.length !== 8) return cep;
  return clean.replace(/(\d{5})(\d{3})/, "$1-$2");
}

export function formatCurrency(value: number | string): string {
  const numValue = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(numValue);
}

export function formatDate(date: string | Date): string {
  if (!date) return "";
  return new Date(date).toLocaleDateString("pt-BR");
}

export function parseDate(dateString: string): Date | null {
  if (!dateString) return null;
  const parts = dateString.split(/[/-]/);
  if (parts.length !== 3) return null;
  const day = parseInt(parts[0]);
  const month = parseInt(parts[1]) - 1;
  const year = parseInt(parts[2]);
  return new Date(year, month, day);
}
