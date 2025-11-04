/**
 * AddressRevealCard Component - LGPD Compliant
 *
 * Exibe endereço com opção de revelar TODOS os campos de uma vez.
 * - Sempre mostra dados mascarados inicialmente
 * - Revelação completa mediante ação explícita do usuário
 * - Auto-hide após 3 minutos
 * - Auditoria consolidada no backend (1 log para todos os campos)
 *
 * @requires Backend endpoint: POST /api/v1/lgpd/{entityType}/{entityId}/reveal-fields
 */

import React, { useState, useEffect, useRef } from "react";
import { MapPin, Eye, EyeOff, Shield, Navigation, ExternalLink } from "lucide-react";
import { notify } from "../../utils/notifications";
import { revealCompleteAddress, EntityType } from "../../services/lgpdService";
import {
  formatFullAddress,
  buildFullAddressLine,
  buildGoogleMapsUrl,
  buildWazeUrl,
  FormattedAddress,
} from "../../utils/addressFormatters";


interface AddressData {
  id?: string | number;
  street: string;
  number?: string;
  complement?: string;
  details?: string;
  neighborhood: string;
  city: string;
  state: string;
  postal_code?: string;
  zip_code?: string;
  country?: string;
  type: string;
  is_principal?: boolean;
  description?: string;
}

interface AddressRevealCardProps {
  /** Dados do endereço */
  address: AddressData;
  /** Tipo da entidade ("companies", "clients", "users", "establishments") */
  entityType: EntityType;
  /** ID da entidade */
  entityId: number;
  /** Função para obter label do tipo de endereço */
  getAddressTypeLabel?: (type: string) => string;
  /** Callback quando endereço for revelado */
  onReveal?: (revealedData: FormattedAddress) => void;
  /** Callback quando endereço for ocultado */
  onHide?: () => void;
}

const AddressRevealCard: React.FC<AddressRevealCardProps> = ({
  address,
  entityType,
  entityId,
  getAddressTypeLabel = (type) => type,
  onReveal,
  onHide,
}) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const [revealedData, setRevealedData] = useState<FormattedAddress | null>(null);
  const [loading, setLoading] = useState(false);
  const autoHideTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Limpar timer ao desmontar componente
  useEffect(() => {
    return () => {
      if (autoHideTimerRef.current) {
        clearTimeout(autoHideTimerRef.current);
      }
    };
  }, []);

  // Reset estado quando entityId mudar (navegação entre entidades)
  useEffect(() => {
    setIsRevealed(false);
    setRevealedData(null);
    setLoading(false);
    if (autoHideTimerRef.current) {
      clearTimeout(autoHideTimerRef.current);
    }
  }, [entityId, address.id]);

  const handleRevealComplete = async () => {
    // ✅ CORREÇÃO: Usar entityId como fallback quando address.id não existe
    // Isso acontece quando o endereço vem da View sem ID explícito
    const addressIdentifier = address.id || entityId;
    
    if (!addressIdentifier) {
      notify.error("Não foi possível identificar o endereço");
      return;
    }

    setLoading(true);

    try {
      // ✅ Chama endpoint que revela TODOS os campos de uma vez
      const result = await revealCompleteAddress(
        entityType,
        entityId,
        addressIdentifier
      );

      // Formatar dados revelados
      const formatted = formatFullAddress(
        result.revealed_data,
        address.id,
        {
          city: address.city,
          state: address.state,
          country: address.country,
        }
      );

      setRevealedData(formatted);
      setIsRevealed(true);

      // Notificar sucesso
      notify.success("Endereço completo revelado com sucesso!");

      // Callback
      if (onReveal) {
        onReveal(formatted);
      }

      // Configurar auto-hide após 3 minutos
      autoHideTimerRef.current = setTimeout(() => {
        handleHideComplete();
        notify.info("Endereço ocultado automaticamente por segurança");
      }, 180000); // 3 minutos

    } catch (error: any) {
      console.error("Erro ao revelar endereço:", error);

      if (error.message.includes("Session expired")) {
        notify.error("Sessão expirada. Faça login novamente.");
      } else if (error.message.includes("permission")) {
        notify.error("Você não tem permissão para revelar este endereço.");
      } else if (error.message.includes("not found")) {
        notify.error(`${entityType} não encontrado.`);
      } else if (error.message.includes("ID do endereço não disponível")) {
        notify.error(
          "Revelação de endereço indisponível. Entre em contato com o administrador do sistema.",
          { duration: 6000 }
        );
      } else {
        notify.error(error.message || "Erro ao revelar endereço completo");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleHideComplete = () => {
    setIsRevealed(false);
    setRevealedData(null);

    // Limpar timer
    if (autoHideTimerRef.current) {
      clearTimeout(autoHideTimerRef.current);
      autoHideTimerRef.current = null;
    }

    // Callback
    if (onHide) {
      onHide();
    }
  };

  const handleOpenGoogleMaps = () => {
    if (!revealedData) return;
    const url = buildGoogleMapsUrl(revealedData);
    window.open(url, "_blank");
  };

  const handleOpenWaze = () => {
    if (!revealedData) return;
    const url = buildWazeUrl(revealedData);
    window.open(url, "_blank");
  };

  return (
    <div className="p-4 bg-muted/30 rounded-lg">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
          <MapPin className="h-4 w-4 text-purple-600 dark:text-purple-300" />
        </div>

        <div className="flex-1">
          {/* Header com tipo e badge principal */}
          <div className="flex items-center gap-2 mb-3">
            <span className="font-medium text-foreground">
              {getAddressTypeLabel(address.type)}
            </span>
            {address.is_principal && (
              <span className="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded">
                Principal
              </span>
            )}
          </div>

          {/* Conteúdo: Mascarado ou Revelado */}
          {!isRevealed ? (
            // ========================================
            // ESTADO MASCARADO
            // ========================================
            <div className="space-y-2">
              {/* Logradouro com botão discreto */}
              <div className="text-sm flex items-center justify-between gap-2">
                <div className="flex-1">
                  <span className="font-medium text-muted-foreground">Logradouro:</span>{" "}
                  <span className="font-mono text-foreground">
                    {`${address.street}${address.number ? `, ${address.number}` : ""}`}
                  </span>
                </div>
                
                {/* Botão Revelar Discreto */}
                <button
                  onClick={handleRevealComplete}
                  disabled={loading}
                  className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed rounded hover:bg-blue-50 dark:hover:bg-blue-950"
                  title="Revelar endereço completo (ação auditada)"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                          fill="none"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                      <span>Revelando...</span>
                    </>
                  ) : (
                    <>
                      <Eye className="h-3 w-3" />
                      <span>Revelar</span>
                    </>
                  )}
                </button>
              </div>

              {(address.complement || address.details) && (
                <div className="text-sm">
                  <span className="font-medium text-muted-foreground">Complemento:</span>{" "}
                  <span className="font-mono text-foreground">
                    {address.complement || address.details}
                  </span>
                </div>
              )}

              <div className="text-sm">
                <span className="font-medium text-muted-foreground">Bairro:</span>{" "}
                <span className="font-mono text-foreground">
                  {address.neighborhood}
                </span>
              </div>

              <div className="text-sm">
                <span className="font-medium text-muted-foreground">Cidade/Estado:</span>{" "}
                <span className="text-foreground">
                  {address.city}/{address.state}
                </span>
              </div>

              <div className="text-sm">
                <span className="font-medium text-muted-foreground">CEP:</span>{" "}
                <span className="font-mono text-foreground">
                  {address.postal_code || address.zip_code || ""}
                </span>
              </div>

              {address.country && address.country !== "Brasil" && address.country !== "BR" && (
                <div className="text-sm">
                  <span className="font-medium text-muted-foreground">País:</span>{" "}
                  <span className="text-foreground">{address.country}</span>
                </div>
              )}

              {address.description && (
                <p className="text-sm text-muted-foreground mt-2">
                  {address.description}
                </p>
              )}
            </div>
          ) : (
            // ========================================
            // ESTADO REVELADO
            // ========================================
            <div className="space-y-2">
              {/* Logradouro com botão Ocultar discreto */}
              <div className="text-sm flex items-center justify-between gap-2">
                <div className="flex-1">
                  <span className="font-medium text-muted-foreground">Logradouro:</span>{" "}
                  <span className="font-mono text-foreground">
                    {revealedData?.street}, {revealedData?.number}
                  </span>
                </div>
                
                {/* Botão Ocultar Discreto */}
                <button
                  onClick={handleHideComplete}
                  className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded hover:bg-gray-100 dark:hover:bg-gray-800"
                  title="Ocultar endereço completo"
                >
                  <EyeOff className="h-3 w-3" />
                  <span>Ocultar</span>
                </button>
              </div>

              {revealedData?.complement && (
                <div className="text-sm">
                  <span className="font-medium text-muted-foreground">Complemento:</span>{" "}
                  <span className="font-mono text-foreground">
                    {revealedData.complement}
                  </span>
                </div>
              )}

              <div className="text-sm">
                <span className="font-medium text-muted-foreground">Bairro:</span>{" "}
                <span className="font-mono text-foreground">
                  {revealedData?.neighborhood}
                </span>
              </div>

              <div className="text-sm">
                <span className="font-medium text-muted-foreground">Cidade/Estado:</span>{" "}
                <span className="text-foreground">
                  {revealedData?.city}/{revealedData?.state}
                </span>
              </div>

              <div className="text-sm">
                <span className="font-medium text-muted-foreground">CEP:</span>{" "}
                <span className="font-mono text-foreground">
                  {revealedData?.zipCode}
                </span>
              </div>

              {revealedData?.country && revealedData.country !== "Brasil" && (
                <div className="text-sm">
                  <span className="font-medium text-muted-foreground">País:</span>{" "}
                  <span className="text-foreground">{revealedData.country}</span>
                </div>
              )}

              {/* Botões de ação */}
              <div className="flex items-center justify-end gap-1 mt-2 pt-2 border-t border-border">
                {/* Botão Google Maps */}
                <button
                  onClick={handleOpenGoogleMaps}
                  className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 transition-colors rounded hover:bg-blue-50 dark:hover:bg-blue-950"
                  title="Abrir no Google Maps"
                >
                  <MapPin className="h-3 w-3" />
                  <span>Maps</span>
                </button>

                {/* Botão Waze */}
                <button
                  onClick={handleOpenWaze}
                  className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-cyan-600 hover:text-cyan-800 dark:text-cyan-400 dark:hover:text-cyan-200 transition-colors rounded hover:bg-cyan-50 dark:hover:bg-cyan-950"
                  title="Abrir no Waze"
                >
                  <Navigation className="h-3 w-3" />
                  <span>Waze</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AddressRevealCard;
