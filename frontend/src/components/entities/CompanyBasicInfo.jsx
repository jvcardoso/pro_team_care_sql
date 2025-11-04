import React from "react";
import Card from "../ui/Card";
import { ExternalLink, Building, FileText, Calendar } from "lucide-react";
import SensitiveDataField from "../shared/SensitiveDataField";

const CompanyBasicInfo = ({
  company,
  title = "Informações da Empresa",
  showDescription = true,
  className = "",
}) => {
  if (!company || !company.people) {
    return null;
  }

  return (
    <Card title={title} className={className}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Razão Social
          </label>
          <p className="text-foreground font-medium">{company.people.name}</p>
        </div>

        {company.people.trade_name && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1">
              Nome Fantasia
            </label>
            <p className="text-foreground">{company.people.trade_name}</p>
          </div>
        )}

        <SensitiveDataField
          label="CNPJ"
          value={company.people.tax_id}
          entityType="companies"
          entityId={company.id}
          fieldName="tax_id"
          icon={<Building className="w-4 h-4" />}
        />

        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">
            Tipo de Pessoa
          </label>
          <p className="text-foreground">{company.people.person_type}</p>
        </div>

        {company.people.incorporation_date && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1">
              Data de Incorporação
            </label>
            <p className="text-foreground">
              {new Date(company.people.incorporation_date).toLocaleDateString(
                "pt-BR"
              )}
            </p>
          </div>
        )}

        {company.people.tax_regime && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1">
              Regime Tributário
            </label>
            <p className="text-foreground capitalize">
              {company.people.tax_regime.replace("_", " ")}
            </p>
          </div>
        )}

        {company.people.legal_nature && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1">
              Natureza Jurídica
            </label>
            <p className="text-foreground uppercase">
              {company.people.legal_nature}
            </p>
          </div>
        )}

        {company.people.secondary_tax_id && (
          <SensitiveDataField
            label="Inscrição Estadual"
            value={company.people.secondary_tax_id}
            entityType="companies"
            entityId={company.id}
            fieldName="secondary_tax_id"
            icon={<FileText className="w-4 h-4" />}
          />
        )}

        {company.people.municipal_registration && (
          <SensitiveDataField
            label="Inscrição Municipal"
            value={company.people.municipal_registration}
            entityType="companies"
            entityId={company.id}
            fieldName="municipal_registration"
            icon={<FileText className="w-4 h-4" />}
          />
        )}

        {company.people.website && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1">
              Website
            </label>
            <a
              href={
                company.people.website.startsWith("http")
                  ? company.people.website
                  : `https://${company.people.website}`
              }
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline flex items-center gap-1"
            >
              {company.people.website}
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        )}
      </div>

      {showDescription && company.people.description && (
        <div className="mt-6">
          <label className="block text-sm font-medium text-muted-foreground mb-2">
            Descrição da Empresa
          </label>
          <p className="text-foreground bg-muted/30 p-3 rounded-lg">
            {company.people.description}
          </p>
        </div>
      )}
    </Card>
  );
};

export default CompanyBasicInfo;
