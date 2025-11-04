import React, { useState } from "react";
import { Mail, Send, Edit2, Trash2, Star, Plus } from "lucide-react";
import Card from "../ui/Card";
import { maskEmail } from "../../utils/maskingUtils";
import SensitiveDataField from "../shared/SensitiveDataField";
import { notify } from "../../utils/notifications";
import { deleteEmail, setPrincipalEmail } from "../../services/emailsService";

interface EmailData {
  id?: string | number;
  email_address: string;
  type: string;
  is_principal?: boolean;
  is_verified?: boolean;
  description?: string;
}

interface EmailDisplayCardProps {
  emails: EmailData[];
  title?: string;
  getEmailTypeLabel?: (type: string) => string;
  onOpenEmail?: (email: EmailData) => void;
  entityType: string;  // ✅ Agora obrigatório para LGPD revelation
  entityId: number | string;  // ✅ Agora obrigatório para LGPD revelation
  onAdd?: () => void;  // Callback para adicionar novo e-mail
  onEdit?: (email: EmailData) => void;  // Callback para editar e-mail
  onRefresh?: () => void;  // Callback para atualizar lista após mudanças
  readOnly?: boolean;  // Se true, oculta botões de ação
}

const EmailDisplayCard: React.FC<EmailDisplayCardProps> = ({
  emails,
  title = "E-mails",
  getEmailTypeLabel = (type) => type,
  onOpenEmail = (email) => {
    const url = `mailto:${email.email_address}`;
    window.open(url, "_blank");
  },
  entityType,
  entityId,
  onAdd,
  onEdit,
  onRefresh,
  readOnly = false,
}) => {
  const [loadingStates, setLoadingStates] = useState<Record<number, boolean>>({});

  const handleSetPrincipal = async (email: EmailData) => {
    if (!email.id) return;

    setLoadingStates(prev => ({ ...prev, [email.id as number]: true }));

    try {
      await setPrincipalEmail(Number(email.id));
      notify.success("E-mail marcado como principal!");
      
      if (onRefresh) {
        onRefresh();
      }
    } catch (error: any) {
      console.error("Erro ao marcar e-mail como principal:", error);
      notify.error(error.response?.data?.detail || "Erro ao marcar e-mail como principal");
    } finally {
      setLoadingStates(prev => ({ ...prev, [email.id as number]: false }));
    }
  };

  const handleDelete = async (email: EmailData) => {
    if (!email.id) return;

    const confirmed = window.confirm(
      `Tem certeza que deseja excluir o e-mail ${email.email_address}?`
    );

    if (!confirmed) return;

    setLoadingStates(prev => ({ ...prev, [email.id as number]: true }));

    try {
      await deleteEmail(Number(email.id));
      notify.success("E-mail excluído com sucesso!");
      
      if (onRefresh) {
        onRefresh();
      }
    } catch (error: any) {
      console.error("Erro ao excluir e-mail:", error);
      notify.error(error.response?.data?.detail || "Erro ao excluir e-mail");
    } finally {
      setLoadingStates(prev => ({ ...prev, [email.id as number]: false }));
    }
  };

  return (
    <Card 
      title={title}
      actions={
        !readOnly && onAdd && (
          <button
            onClick={onAdd}
            className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-white bg-primary hover:bg-primary/90 transition-colors rounded-lg"
            title="Adicionar novo e-mail"
          >
            <Plus className="h-4 w-4" />
            <span>Adicionar</span>
          </button>
        )
      }
    >
      {!emails || emails.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          Nenhum e-mail cadastrado
        </p>
      ) : (
        <div className="space-y-4">
          {emails.map((email, index) => (
            <div key={email.id || index} className="p-3 bg-muted/30 rounded-lg">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                  <Mail className="h-4 w-4 text-green-600 dark:text-green-300" />
                </div>
                <div className="flex-1">
                  {/* Email com revelação LGPD */}
                  <SensitiveDataField
                    value={email.email}
                    entityType={entityType as any}
                    entityId={Number(entityId)}
                    fieldName={`email_${email.id}_address`}
                    icon={<Mail className="w-4 h-4" />}
                  />

                  <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                    <span>{getEmailTypeLabel(email.type)}</span>
                    {email.is_principal && (
                      <span className="px-2 py-0.5 bg-primary/10 text-primary text-xs rounded">
                        Principal
                      </span>
                    )}
                    {email.is_verified && (
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                        Verificado
                      </span>
                    )}
                  </div>
                  {email.description && (
                    <p className="text-sm text-muted-foreground mt-1">
                      {email.description}
                    </p>
                  )}

                  {/* Botões de ação */}
                  {!readOnly && (
                    <div className="flex items-center gap-1 mt-2">
                      {/* Botão Enviar E-mail */}
                      <button
                        onClick={() => onOpenEmail(email)}
                        className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 transition-colors rounded hover:bg-blue-50 dark:hover:bg-blue-950"
                        title="Enviar e-mail"
                      >
                        <Send className="h-3 w-3" />
                        <span>Enviar</span>
                      </button>

                      {/* Botão Marcar como Principal */}
                      {!email.is_principal && (
                        <button
                          onClick={() => handleSetPrincipal(email)}
                          disabled={loadingStates[email.id as number]}
                          className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-yellow-600 hover:text-yellow-800 dark:text-yellow-400 dark:hover:text-yellow-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed rounded hover:bg-yellow-50 dark:hover:bg-yellow-950"
                          title="Marcar como principal"
                        >
                          <Star className="h-3 w-3" />
                          <span>Principal</span>
                        </button>
                      )}

                      {/* Botão Editar */}
                      {onEdit && (
                        <button
                          onClick={() => onEdit(email)}
                          disabled={loadingStates[email.id as number]}
                          className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed rounded hover:bg-gray-100 dark:hover:bg-gray-800"
                          title="Editar e-mail"
                        >
                          <Edit2 className="h-3 w-3" />
                          <span>Editar</span>
                        </button>
                      )}

                      {/* Botão Excluir */}
                      <button
                        onClick={() => handleDelete(email)}
                        disabled={loadingStates[email.id as number]}
                        className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed rounded hover:bg-red-50 dark:hover:bg-red-950"
                        title="Excluir e-mail"
                      >
                        <Trash2 className="h-3 w-3" />
                        <span>Excluir</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};

export default EmailDisplayCard;
