/**
 * PessoaFisicaFields - Campos específicos de Pessoa Física
 *
 * Exibe campos apropriados para CPF (clientes, usuários, profissionais)
 */

import React from "react";
import { User, Briefcase, Calendar, Users } from "lucide-react";
import SensitiveDataField from "../shared/SensitiveDataField";
import { getGenderLabel, getMaritalStatusLabel, formatBrazilianDate } from "../../utils/personFormatters";

interface People {
  name: string;
  tax_id: string;
  person_type: string;
  birth_date?: string | null;
  gender?: string | null;
  marital_status?: string | null;
  occupation?: string | null;
  nationality?: string | null;
}

interface PessoaFisicaFieldsProps {
  person: People;
  entityType: 'companies' | 'clients' | 'users' | 'establishments';
  entityId: number;
}

const PessoaFisicaFields: React.FC<PessoaFisicaFieldsProps> = ({
  person,
  entityType,
  entityId,
}) => {
  return (
    <>
      {/* Nome Completo */}
      <div>
        <label className="block text-sm font-medium text-muted-foreground mb-1">
          Nome Completo
        </label>
        <p className="text-foreground font-medium">{person.name}</p>
      </div>

      {/* CPF com revelação LGPD */}
      <SensitiveDataField
        label="CPF"
        value={person.tax_id}
        entityType={entityType}
        entityId={entityId}
        fieldName="tax_id"
        icon={<User className="w-4 h-4" />}
      />

      {/* Tipo de Pessoa */}
      <div>
        <label className="block text-sm font-medium text-muted-foreground mb-1">
          Tipo de Pessoa
        </label>
        <p className="text-foreground">{person.person_type}</p>
      </div>

      {/* Data de Nascimento */}
      {person.birth_date && (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Data de Nascimento
          </label>
          <p className="text-foreground flex items-center gap-2">
            <Calendar className="w-4 h-4 text-muted-foreground" />
            {formatBrazilianDate(person.birth_date)}
          </p>
        </div>
      )}

      {/* Gênero */}
      {person.gender && (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Gênero
          </label>
          <p className="text-foreground">
            {getGenderLabel(person.gender)}
          </p>
        </div>
      )}

      {/* Estado Civil */}
      {person.marital_status && (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Estado Civil
          </label>
          <p className="text-foreground flex items-center gap-2">
            <Users className="w-4 h-4 text-muted-foreground" />
            {getMaritalStatusLabel(person.marital_status)}
          </p>
        </div>
      )}

      {/* Ocupação */}
      {person.occupation && (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Ocupação
          </label>
          <p className="text-foreground flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-muted-foreground" />
            {person.occupation}
          </p>
        </div>
      )}

      {/* Nacionalidade (opcional) */}
      {person.nationality && (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Nacionalidade
          </label>
          <p className="text-foreground capitalize">
            {person.nationality}
          </p>
        </div>
      )}
    </>
  );
};

export default PessoaFisicaFields;
