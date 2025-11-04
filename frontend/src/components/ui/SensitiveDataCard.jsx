/**
 * SensitiveDataCard - Card com badge LGPD no cabeçalho
 * 
 * Wrapper do Card padrão que adiciona automaticamente:
 * - Badge de dados sensíveis no cabeçalho
 * - Informação sobre auditoria LGPD
 * - Mensagem de auto-ocultação quando dados revelados
 * 
 * Evita repetição de avisos LGPD em cada item individual.
 */

import React from "react";
import { Shield } from "lucide-react";
import Card from "./Card";

const SensitiveDataCard = ({
  title,
  children,
  actions,
  showAutoHideWarning = false,
  autoHideMinutes = 3,
  className,
}) => {

  return (
    <Card className={className} noPadding shadow>
      {/* Header customizado com badge LGPD */}
      <div className="px-6 py-4 border-b border-border">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-lg font-semibold text-foreground">{title}</h3>
              
              {/* Badge de dados sensíveis */}
              <div 
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 text-xs rounded-md"
                title="Dados Sensíveis - LGPD"
              >
                <Shield className="h-3 w-3" />
                <span className="font-medium">Dados Sensíveis</span>
              </div>
            </div>
            
            {/* Informação LGPD */}
            <p className="text-xs text-muted-foreground">
              🔒 Revelação auditada (LGPD Art. 18, VIII)
              {showAutoHideWarning && (
                <span className="ml-2 text-orange-600 dark:text-orange-400 font-medium">
                  • Dados serão ocultados em {autoHideMinutes} min
                </span>
              )}
            </p>
          </div>

          {/* Ações do header */}
          {actions && (
            <div className="flex items-center gap-2">
              {actions}
            </div>
          )}
        </div>
      </div>

      {/* Conteúdo do card */}
      <div className="px-6 py-4">
        {children}
      </div>
    </Card>
  );
};

export default SensitiveDataCard;
