/**
 * PersonBasicInfo - Componente Genérico de Informações de Pessoa
 *
 * Detecta automaticamente o tipo de pessoa (PF ou PJ) e renderiza os campos apropriados:
 * - Pessoa Física (PF): CPF, Nome Completo, Data Nascimento, etc.
 * - Pessoa Jurídica (PJ): CNPJ, Razão Social, Nome Fantasia, etc.
 *
 * Uso:
 * - Empresas (companies): sempre PJ
 * - Clientes (clients): pode ser PF ou PJ
 * - Usuários (users): sempre PF
 * - Estabelecimentos (establishments): sempre PJ
 * - Profissionais (professionals): sempre PF
 */

import React from "react";
import Card from "../ui/Card";
import { Building2, User } from "lucide-react";
import PessoaFisicaFields from "./PessoaFisicaFields";
import PessoaJuridicaFields from "./PessoaJuridicaFields";

interface People {
  name: string;
  trade_name?: string | null;
  tax_id: string;
  person_type: string;
  // PF fields
  birth_date?: string | null;
  gender?: string | null;
  marital_status?: string | null;
  occupation?: string | null;
  nationality?: string | null;
  // PJ fields
  incorporation_date?: string | null;
  tax_regime?: string | null;
  legal_nature?: string | null;
  secondary_tax_id?: string | null;
  municipal_registration?: string | null;
  website?: string | null;
}

interface PersonBasicInfoProps {
  person?: People | null;
  entityType: 'companies' | 'clients' | 'users' | 'establishments';
  entityId: number;
  title?: string; // Título opcional do card (padrão: "Informações Básicas")
}

const PersonBasicInfo: React.FC<PersonBasicInfoProps> = ({
  person,
  entityType,
  entityId,
  title = "Informações Básicas",
}) => {
  // Verificar se person existe
  if (!person) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {title}
        </h3>
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">
            Nenhuma pessoa associada a esta entidade.
          </p>
        </div>
      </div>
    );
  }

  const isPessoaFisica = person.person_type === 'PF';
  const isPessoaJuridica = person.person_type === 'PJ';

  // Se person_type não for reconhecido, inferir pelo tamanho do tax_id
  const inferredType = !isPessoaFisica && !isPessoaJuridica
    ? (person.tax_id?.replace(/\D/g, '').length === 11 ? 'PF' : 'PJ')
    : null;

  const displayType = inferredType || person.person_type;

  const cardTitle = displayType === 'PF'
    ? `${title} - Pessoa Física`
    : `${title} - Pessoa Jurídica`;

  return (
    <Card title={
      <div className="flex items-center gap-2">
        {displayType === 'PF' ? (
          <>
            <User className="h-5 w-5" />
            {cardTitle}
          </>
        ) : (
          <>
            <Building2 className="h-5 w-5" />
            {cardTitle}
          </>
        )}
      </div>
    }>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {displayType === 'PF' ? (
          <PessoaFisicaFields
            person={person}
            entityType={entityType}
            entityId={entityId}
          />
        ) : (
          <PessoaJuridicaFields
            person={person}
            entityType={entityType}
            entityId={entityId}
          />
        )}
      </div>
    </Card>
  );
};

export default PersonBasicInfo;
