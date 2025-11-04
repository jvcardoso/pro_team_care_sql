/**
 * Companies Page
 * Página completa de gestão de empresas usando o DataTableTemplate
 */

import React, { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { DataTableTemplate } from "../components/shared/DataTable/DataTableTemplate";
import { useCompaniesDataTable } from "../hooks/useCompaniesDataTable";
import { createCompaniesConfig } from "../config/tables/companies.config";
import CompanyDetailsNew from "../components/views/CompanyDetailsNew";
import CompaniesService from "../services/companiesService";
import { notify } from "../utils/notifications";

export const CompaniesPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();

  // ✅ SEMPRE chamar hooks no topo, antes de qualquer condicional
  const tableData = useCompaniesDataTable({
    initialPageSize: 10,
  });

  // Buscar nome da empresa para breadcrumb quando houver ID
  useEffect(() => {
    if (id && !isNaN(parseInt(id))) {
      const loadCompanyName = async () => {
        try {
          const company = await CompaniesService.getById(parseInt(id));
          if (company?.people?.name) {
            localStorage.setItem(`company_name_${id}`, company.people.name);
          }
        } catch (error) {
          console.error("Erro ao buscar nome da empresa:", error);
        }
      };
      loadCompanyName();
    }
  }, [id]);

  // Handler para inativação de empresa da tabela
  const handleDelete = async (companyId: number) => {
    console.log("🔍 [CompaniesPage] handleDelete chamado com ID:", companyId);
    console.log("🔍 [CompaniesPage] notify existe?", !!notify);
    console.log("🔍 [CompaniesPage] notify.confirm existe?", !!notify?.confirm);

    try {
      console.log("🔍 [CompaniesPage] Buscando dados da empresa...");
      // Buscar dados da empresa para exibir nome no modal
      const company = await CompaniesService.getById(companyId);
      const companyName =
        company?.people?.name || company?.name || "esta empresa";
      console.log("🔍 [CompaniesPage] Empresa encontrada:", companyName);

      const executeDelete = async () => {
        console.log("🔍 [CompaniesPage] executeDelete chamado");
        try {
          await CompaniesService.deactivate(companyId);
          notify.success("Empresa inativada com sucesso!");

          // Recarregar dados da tabela
          window.location.reload();
        } catch (err: any) {
          console.log("🔍 [ERRO COMPLETO]", {
            err: err,
            response: err.response,
            responseData: err.response?.data,
            responseDataDetail: err.response?.data?.detail,
            detailType: typeof err.response?.data?.detail,
            isArray: Array.isArray(err.response?.data?.detail),
          });

          // Diferenciar erro de validação (400/422) de erro técnico (500)
          if (
            err.status === 400 ||
            err.status_code === 400 ||
            err.response?.status === 400 ||
            err.status === 422 ||
            err.status_code === 422 ||
            err.response?.status === 422
          ) {
            // Extrair mensagem de erro do FastAPI 422
            let errorMessage = "Não é possível inativar a empresa";

            if (err.response?.data?.detail) {
              // FastAPI 422 pode retornar array de erros ou string
              if (Array.isArray(err.response.data.detail)) {
                // Formato Pydantic: [{type, loc, msg, input}, ...]
                errorMessage = err.response.data.detail
                  .map((e: any) => {
                    // Garantir que msg é string
                    if (typeof e.msg === "string") {
                      return e.msg;
                    } else if (typeof e === "string") {
                      return e;
                    } else {
                      // Serializar objeto como JSON se necessário
                      return JSON.stringify(e.msg || e);
                    }
                  })
                  .join(", ");
              } else if (typeof err.response.data.detail === "object") {
                // Se detail for objeto, serializar
                errorMessage = JSON.stringify(err.response.data.detail);
              } else if (typeof err.response.data.detail === "string") {
                errorMessage = err.response.data.detail;
              }
            } else if (err.detail) {
              errorMessage = err.detail;
            } else if (err.message) {
              errorMessage = err.message;
            }

            notify.warning(errorMessage);
          } else {
            notify.error("Erro ao inativar empresa. Tente novamente.");
          }
          console.error(err);
        }
      };

      console.log("🔍 [CompaniesPage] Chamando notify.confirm...");
      notify.confirm(
        "Inativar Empresa",
        `Tem certeza que deseja inativar a empresa "${companyName}"?\n\nA empresa será removida das listagens ativas, mas todos os dados serão preservados e poderão ser reativados posteriormente.`,
        executeDelete
      );
      console.log("✅ [CompaniesPage] notify.confirm executado");
    } catch (error) {
      console.error(
        "❌ [CompaniesPage] Erro ao buscar dados da empresa:",
        error
      );
      notify.error("Erro ao carregar dados da empresa");
    }
  };

  // Criar configuração com navegação e action handlers
  const companiesConfig = createCompaniesConfig(navigate, {
    onDelete: handleDelete,
  });

  // Se tem ID na URL, mostrar detalhes da empresa
  if (id && !isNaN(parseInt(id))) {
    console.log("📋 Mostrando detalhes da empresa ID:", id);
    return <CompanyDetailsNew />;
  }

  return (
    <div className="p-6">
      <DataTableTemplate config={companiesConfig} tableData={tableData} />
    </div>
  );
};

export default CompaniesPage;
