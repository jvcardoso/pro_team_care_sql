/**
 * PessoaJuridicaFields - Campos específicos de Pessoa Jurídica
 *
 * Exibe campos apropriados para CNPJ (empresas, estabelecimentos)
 */

import React from "react";
import { Building, FileText, ExternalLink } from "lucide-react";
import SensitiveDataField from "../shared/SensitiveDataField";
import { getTaxRegimeLabel, formatBrazilianDate } from "../../utils/personFormatters";

interface People {
  name: string;
  trade_name?: string | null;
  tax_id: string;
  person_type: string;
  incorporation_date?: string | null;
  tax_regime?: string | null;
  legal_nature?: string | null;
  secondary_tax_id?: string | null;
  municipal_registration?: string | null;
  website?: string | null;
}

interface PessoaJuridicaFieldsProps {
  person: People;
  entityType: 'companies' | 'clients' | 'users' | 'establishments';
  entityId: number;
}

const PessoaJuridicaFields: React.FC<PessoaJuridicaFieldsProps> = ({
  person,
  entityType,
  entityId,
}) => {
  return (
    <>
      {/* Razão Social */}
      <div>
        <label className="block text-sm font-medium text-muted-foreground mb-1">
          Razão Social
        </label>
        <p className="text-foreground font-medium">{person.name}</p>
      </div>

      {/* Nome Fantasia */}
      {person.trade_name && (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Nome Fantasia
          </label>
          <p className="text-foreground">{person.trade_name}</p>
        </div>
      )}

       {/* CNPJ com revelação LGPD */}
       <SensitiveDataField
         label="CNPJ"
         value={person.tax_id}
         entityType={entityType}
         entityId={entityId}
         fieldName="tax_id"
         icon={<Building className="w-4 h-4" />}
       />

      {/* Tipo de Pessoa */}
      <div>
        <label className="block text-sm font-medium text-muted-foreground mb-1">
          Tipo de Pessoa
        </label>
        <p className="text-foreground">{person.person_type}</p>
      </div>

      {/* Data de Incorporação/Abertura */}
      {person.incorporation_date && (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Data de Abertura
          </label>
          <p className="text-foreground">
            {formatBrazilianDate(person.incorporation_date)}
          </p>
        </div>
      )}

      {/* Regime Tributário */}
      {person.tax_regime && (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Regime Tributário
          </label>
          <p className="text-foreground capitalize">
            {getTaxRegimeLabel(person.tax_regime)}
          </p>
        </div>
      )}

      {/* Natureza Jurídica */}
      {person.legal_nature && (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Natureza Jurídica
          </label>
          <p className="text-foreground uppercase">
            {person.legal_nature}
          </p>
        </div>
      )}

       {/* Inscrição Estadual com revelação LGPD */}
       {person.secondary_tax_id && (
         <SensitiveDataField
           label="Inscrição Estadual"
           value={person.secondary_tax_id}
           entityType={entityType}
           entityId={entityId}
           fieldName="secondary_tax_id"
           icon={<FileText className="w-4 h-4" />}
         />
       )}

       {/* Inscrição Municipal com revelação LGPD */}
       {person.municipal_registration && (
         <SensitiveDataField
           label="Inscrição Municipal"
           value={person.municipal_registration}
           entityType={entityType}
           entityId={entityId}
           fieldName="municipal_registration"
           icon={<FileText className="w-4 h-4" />}
         />
       )}

      {/* Website */}
      {person.website && (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Website
          </label>
          <a
            href={
              person.website.startsWith("http")
                ? person.website
                : `https://${person.website}`
            }
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline flex items-center gap-1"
          >
            {person.website}
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      )}
    </>
  );
};

export default PessoaJuridicaFields;
