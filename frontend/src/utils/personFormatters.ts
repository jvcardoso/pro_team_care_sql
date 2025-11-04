/**
 * Person Formatters - Formatadores para Pessoa Física e Jurídica
 *
 * Funções auxiliares para formatação e labels de PF/PJ
 */

/**
 * Formata CPF (11 dígitos) ou CNPJ (14 dígitos)
 */
export function formatTaxId(taxId: string | null | undefined): string {
  if (!taxId) return '';

  const cleaned = taxId.replace(/\D/g, '');

  if (cleaned.length === 11) {
    // CPF: 000.000.000-00
    return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  }

  if (cleaned.length === 14) {
    // CNPJ: 00.000.000/0000-00
    return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
  }

  return taxId;
}

/**
 * Mascara CPF/CNPJ mantendo alguns dígitos visíveis
 */
export function maskTaxId(taxId: string | null | undefined): string {
  if (!taxId) return '';

  const cleaned = taxId.replace(/\D/g, '');

  if (cleaned.length === 11) {
    // CPF: 123.***.**-01
    return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.***.**-$4');
  }

  if (cleaned.length === 14) {
    // CNPJ: 12.345.***/**-01
    return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.***/**-$5');
  }

  return taxId;
}

/**
 * Labels para gênero
 */
export function getGenderLabel(gender: string | null | undefined): string {
  const labels: Record<string, string> = {
    male: 'Masculino',
    female: 'Feminino',
    non_binary: 'Não-binário',
    not_informed: 'Não informado',
  };

  return labels[gender || ''] || gender || 'Não informado';
}

/**
 * Labels para estado civil
 */
export function getMaritalStatusLabel(status: string | null | undefined): string {
  const labels: Record<string, string> = {
    single: 'Solteiro(a)',
    married: 'Casado(a)',
    divorced: 'Divorciado(a)',
    widowed: 'Viúvo(a)',
    stable_union: 'União Estável',
    not_informed: 'Não informado',
  };

  return labels[status || ''] || status || 'Não informado';
}

/**
 * Labels para regime tributário
 */
export function getTaxRegimeLabel(regime: string | null | undefined): string {
  const labels: Record<string, string> = {
    simples_nacional: 'Simples Nacional',
    lucro_presumido: 'Lucro Presumido',
    lucro_real: 'Lucro Real',
    mei: 'MEI - Microempreendedor Individual',
  };

  return labels[regime || ''] || regime || 'Não informado';
}

/**
 * Detecta tipo de pessoa pelo tamanho do tax_id
 */
export function inferPersonType(taxId: string | null | undefined): 'PF' | 'PJ' | null {
  if (!taxId) return null;

  const cleaned = taxId.replace(/\D/g, '');

  if (cleaned.length === 11) return 'PF';
  if (cleaned.length === 14) return 'PJ';

  return null;
}

/**
 * Formata data brasileira
 */
export function formatBrazilianDate(date: string | null | undefined): string {
  if (!date) return '';

  try {
    return new Date(date).toLocaleDateString('pt-BR');
  } catch {
    return date;
  }
}
