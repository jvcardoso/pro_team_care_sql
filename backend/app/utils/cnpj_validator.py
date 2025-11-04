"""
Validador de CNPJ com suporte a formato alfanumérico (a partir de 2026)
Baseado na Instrução Normativa RFB nº XXXX/2025
"""

def calculate_cnpj_digit(cnpj_base: str, weights: list) -> int:
    """
    Calcula dígito verificador do CNPJ (numérico ou alfanumérico)

    Args:
        cnpj_base: Primeiros 12 ou 13 caracteres do CNPJ
        weights: Lista de pesos para cálculo

    Returns:
        Dígito verificador (0-9)
    """
    total = 0

    for i, char in enumerate(cnpj_base):
        if char.isdigit():
            # Numérico: usar valor direto
            value = int(char)
        else:
            # Alfanumérico: usar valor ASCII - 55
            # A=65-55=10, B=66-55=11, ..., Z=90-55=35
            value = ord(char.upper()) - 55

        total += value * weights[i]

    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ (numérico ou alfanumérico)

    Args:
        cnpj: CNPJ com ou sem formatação

    Returns:
        True se válido, False caso contrário
    """
    # Remover formatação
    clean = cnpj.replace('.', '').replace('/', '').replace('-', '').upper()

    # Validar tamanho
    if len(clean) != 14:
        return False

    # Validar formato: primeiros 12 alfanuméricos, últimos 2 numéricos
    if not clean[:12].isalnum():
        return False

    if not clean[12:].isdigit():
        return False

    # Validar se todos os caracteres são iguais (ex: 00000000000000)
    if len(set(clean)) == 1:
        return False

    # Calcular primeiro dígito verificador
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digit1 = calculate_cnpj_digit(clean[:12], weights1)

    if int(clean[12]) != digit1:
        return False

    # Calcular segundo dígito verificador
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digit2 = calculate_cnpj_digit(clean[:13], weights2)

    if int(clean[13]) != digit2:
        return False

    return True


def format_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX

    Args:
        cnpj: CNPJ sem formatação (14 caracteres)

    Returns:
        CNPJ formatado
    """
    clean = cnpj.replace('.', '').replace('/', '').replace('-', '').upper()

    if len(clean) != 14:
        return cnpj

    return f"{clean[:2]}.{clean[2:5]}.{clean[5:8]}/{clean[8:12]}-{clean[12:]}"


def mask_cnpj(cnpj: str) -> str:
    """
    Mascara CNPJ conforme LGPD, mostrando apenas os 4 primeiros e 2 últimos dígitos

    Args:
        cnpj: CNPJ formatado ou não

    Returns:
        CNPJ mascarado (ex: 12.345.***/0001-XX)
    """
    if not cnpj:
        return cnpj

    # Primeiro formata se necessário
    formatted = format_cnpj(cnpj)

    # Se não conseguiu formatar, retorna como está
    if formatted == cnpj and len(cnpj.replace('.', '').replace('/', '').replace('-', '')) != 14:
        return cnpj

    # Mascara: mostra 2 primeiros dígitos, depois *** para os próximos 6, depois /, 4 dígitos, -, 2 últimos
    clean = formatted.replace('.', '').replace('/', '').replace('-', '')

    if len(clean) == 14:
        return f"{clean[:2]}.***.***/{clean[8:12]}-{clean[12:]}"

    return formatted