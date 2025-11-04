/**
 * Utilitários de Mascaramento para LGPD
 *
 * NOTA: O mascaramento OFICIAL vem do backend.
 * Estas funções são apenas para componentes legados.
 */

/**
 * Mascara telefone para exibição visual
 */
export const maskPhone = (phone: string): string => {
  if (!phone) return "";

  // Remove todos os não-dígitos (incluindo +55, parênteses, hífens, etc)
  const clean = phone.replace(/\D/g, "");

  // Telefone com código do país (+55) - 13 dígitos
  if (clean.length === 13) {
    // +55 11 91919-1919 → +55 (11) 9****-**19
    return `+${clean.slice(0, 2)} (${clean.slice(2, 4)}) ${clean[4]}****-**${clean.slice(-2)}`;
  }
  // Telefone celular - 11 dígitos (com 9 na frente)
  else if (clean.length === 11) {
    return `(${clean.slice(0, 2)}) ${clean[2]}****-**${clean.slice(-2)}`;
  }
  // Telefone fixo - 10 dígitos
  else if (clean.length === 10) {
    return `(${clean.slice(0, 2)}) ****-**${clean.slice(-2)}`;
  }

  return phone;
};

/**
 * Mascara email para exibição visual
 */
export const maskEmail = (email: string): string => {
  if (!email || !email.includes("@")) return email;

  const [local, domain] = email.split("@");
  const maskedLocal = local.length > 1
    ? `${local[0]}***`
    : local;

  return `${maskedLocal}@${domain}`;
};

/**
 * Mascara logradouro (rua + número + complemento)
 */
export const maskStreet = (street: string): string => {
  if (!street) return "";

  // Mostra primeiras e últimas 3 letras
  if (street.length <= 6) return "***";

  return `${street.slice(0, 3)}***${street.slice(-3)}`;
};

/**
 * Mascara bairro
 */
export const maskNeighborhood = (neighborhood: string): string => {
  if (!neighborhood) return "";

  // Mostra primeiras 2 letras
  if (neighborhood.length <= 2) return "**";

  return `${neighborhood.slice(0, 2)}***`;
};

/**
 * Mascara CEP
 */
export const maskZipCode = (zipCode: string): string => {
  if (!zipCode) return "";

  const clean = zipCode.replace(/\D/g, "");

  if (clean.length === 8) {
    // 12345-678 → 12***-**8
    return `${clean.slice(0, 2)}***-**${clean.slice(-1)}`;
  }

  return zipCode;
};
