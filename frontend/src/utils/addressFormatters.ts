/**
 * Address Formatters - Utilitários para formatação de endereços
 *
 * Funções para formatar e processar dados de endereços revelados via LGPD.
 */

/**
 * Formata CEP brasileiro: 01452000 → 01452-000
 */
export function formatZipCode(zipCode: string): string {
  if (!zipCode) return "";
  
  const clean = zipCode.replace(/\D/g, "");
  if (clean.length === 8) {
    return clean.replace(/^(\d{5})(\d{3})$/, "$1-$2");
  }
  return zipCode;
}

/**
 * Formata número do endereço (trata casos especiais)
 */
export function formatAddressNumber(number: string | null | undefined): string {
  if (!number || number.trim() === "") {
    return "S/N";
  }
  return number;
}

/**
 * Interface para dados de endereço formatados
 */
export interface FormattedAddress {
  street: string;
  number: string;
  complement: string;
  neighborhood: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

/**
 * Extrai e formata todos os campos de endereço do revealed_data
 *
 * @param revealedData - Dados revelados do backend
 * @param addressId - ID do endereço
 * @param originalAddress - Dados originais do endereço (para city, state, country)
 * @returns Objeto com todos os campos formatados
 *
 * @example
 * const formatted = formatFullAddress(result.revealed_data, 84, address);
 * console.log(formatted.street); // "Rua das Flores"
 * console.log(formatted.zipCode); // "01452-000"
 */
export function formatFullAddress(
  revealedData: Record<string, string>,
  addressId: number | string,
  originalAddress?: {
    city?: string;
    state?: string;
    country?: string;
  }
): FormattedAddress {
  return {
    street: revealedData[`address_${addressId}_street`] || "",
    number: formatAddressNumber(revealedData[`address_${addressId}_number`]),
    complement: revealedData[`address_${addressId}_complement`] || "",
    neighborhood: revealedData[`address_${addressId}_neighborhood`] || "",
    city: originalAddress?.city || "",
    state: originalAddress?.state || "",
    zipCode: formatZipCode(revealedData[`address_${addressId}_zip_code`] || ""),
    country: originalAddress?.country || "Brasil",
  };
}

/**
 * Monta endereço completo em uma linha
 *
 * @param formatted - Objeto FormattedAddress
 * @returns String com endereço completo formatado
 *
 * @example
 * const line = buildFullAddressLine(formatted);
 * // "Rua das Flores, 123 - Apto 45, Jardim Paulista - CEP: 01452-000"
 */
export function buildFullAddressLine(formatted: FormattedAddress): string {
  const parts: string[] = [];

  // Logradouro + número
  if (formatted.street) {
    parts.push(`${formatted.street}, ${formatted.number}`);
  }

  // Complemento
  if (formatted.complement) {
    parts.push(formatted.complement);
  }

  // Bairro
  if (formatted.neighborhood) {
    parts.push(formatted.neighborhood);
  }

  const addressLine = parts.join(" - ");

  // CEP
  if (formatted.zipCode) {
    return `${addressLine} - CEP: ${formatted.zipCode}`;
  }

  return addressLine;
}

/**
 * Monta endereço completo com cidade/estado
 *
 * @param formatted - Objeto FormattedAddress
 * @returns String com endereço completo incluindo cidade/estado
 *
 * @example
 * const full = buildFullAddressWithCity(formatted);
 * // "Rua das Flores, 123 - Apto 45, Jardim Paulista, São Paulo/SP - CEP: 01452-000"
 */
export function buildFullAddressWithCity(formatted: FormattedAddress): string {
  const baseLine = buildFullAddressLine(formatted);

  if (formatted.city && formatted.state) {
    // Remover CEP do final se existir
    const withoutZip = baseLine.replace(/ - CEP: \d{5}-\d{3}$/, "");
    return `${withoutZip}, ${formatted.city}/${formatted.state} - CEP: ${formatted.zipCode}`;
  }

  return baseLine;
}

/**
 * Valida se todos os campos obrigatórios do endereço foram revelados
 *
 * @param revealedData - Dados revelados do backend
 * @param addressId - ID do endereço
 * @returns true se todos os campos obrigatórios estão presentes
 */
export function validateRevealedAddress(
  revealedData: Record<string, string>,
  addressId: number | string
): boolean {
  const requiredFields = [
    `address_${addressId}_street`,
    `address_${addressId}_neighborhood`,
    `address_${addressId}_zip_code`,
  ];

  return requiredFields.every(field => {
    const value = revealedData[field];
    return value !== undefined && value !== null && value.trim() !== "";
  });
}

/**
 * Extrai apenas os campos de endereço do revealed_data
 *
 * @param revealedData - Dados revelados completos
 * @param addressId - ID do endereço
 * @returns Objeto apenas com campos do endereço específico
 */
export function extractAddressFields(
  revealedData: Record<string, string>,
  addressId: number | string
): Record<string, string> {
  const prefix = `address_${addressId}_`;
  const addressFields: Record<string, string> = {};

  Object.keys(revealedData).forEach(key => {
    if (key.startsWith(prefix)) {
      const fieldName = key.replace(prefix, "");
      addressFields[fieldName] = revealedData[key];
    }
  });

  return addressFields;
}

/**
 * Monta URL do Google Maps com endereço completo
 *
 * @param formatted - Objeto FormattedAddress
 * @returns URL do Google Maps
 */
export function buildGoogleMapsUrl(formatted: FormattedAddress): string {
  const parts = [
    formatted.street,
    formatted.number !== "S/N" ? formatted.number : "",
    formatted.neighborhood,
    formatted.city,
    formatted.state,
    formatted.zipCode,
    formatted.country,
  ].filter(Boolean);

  const query = encodeURIComponent(parts.join(", "));
  return `https://www.google.com/maps/search/?api=1&query=${query}`;
}

/**
 * Monta URL do Waze com endereço completo
 *
 * @param formatted - Objeto FormattedAddress
 * @returns URL do Waze
 */
export function buildWazeUrl(formatted: FormattedAddress): string {
  const parts = [
    formatted.street,
    formatted.number !== "S/N" ? formatted.number : "",
    formatted.city,
    formatted.state,
  ].filter(Boolean);

  const query = encodeURIComponent(parts.join(", "));
  return `https://waze.com/ul?q=${query}`;
}

/**
 * Capitaliza primeira letra de cada palavra
 */
export function capitalizeWords(text: string): string {
  if (!text) return "";
  
  return text
    .toLowerCase()
    .split(" ")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * Formata logradouro (capitaliza e remove espaços extras)
 */
export function formatStreet(street: string): string {
  if (!street) return "";
  
  return capitalizeWords(street.trim().replace(/\s+/g, " "));
}

/**
 * Formata bairro (capitaliza e remove espaços extras)
 */
export function formatNeighborhood(neighborhood: string): string {
  if (!neighborhood) return "";
  
  return capitalizeWords(neighborhood.trim().replace(/\s+/g, " "));
}
