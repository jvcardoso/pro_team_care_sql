import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, useParams } from "react-router-dom";
import CompaniesService from "../services/companiesService";
import { PageErrorBoundary } from "../components/error";
import AccessDeniedError from "../components/error/AccessDeniedError";
import useErrorHandler from "../hooks/useErrorHandler";
import DataTableTemplate from "../components/shared/DataTable/DataTableTemplate";
import { useDataTable } from "../hooks/useDataTable";
import { useCompaniesDataTable } from "../hooks/useCompaniesDataTable";
import { createCompaniesConfig } from "../config/tables/companies.config";
import CompanyForm from "../components/forms/CompanyForm";
import CompanyDetailsNew from "../components/views/CompanyDetailsNew";
import { Plus } from "lucide-react";
import { notify } from "../utils/notifications";
import CleanupPendingCompaniesModal from "../components/modals/CleanupPendingCompaniesModal";

const EmpresasPage = () => {
  return (
    <PageErrorBoundary pageName="Empresas">
      <EmpresasPageContent />
    </PageErrorBoundary>
  );
};

const EmpresasPageContent = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { id } = useParams();
  const {
    handleError,
    isAccessDenied,
    hasError,
    userMessage,
    statusCode,
    canRetry,
  } = useErrorHandler();

  const [currentView, setCurrentView] = useState("list"); // 'list', 'create', 'edit', 'details'
  const [selectedCompanyId, setSelectedCompanyId] = useState(null);
  const [showCleanupModal, setShowCleanupModal] = useState(false);

  const handleAddCompany = () => {
    setCurrentView("create");
  };

  // Handler para inativação de empresa da tabela
  const handleDelete = async (companyId) => {
    console.log("🔍 [EmpresasPage] handleDelete chamado com ID:", companyId);
    console.log("🔍 [EmpresasPage] notify existe?", !!notify);
    console.log("🔍 [EmpresasPage] notify.confirm existe?", !!notify?.confirm);

    try {
      console.log("🔍 [EmpresasPage] Buscando dados da empresa...");
      // Buscar dados da empresa para exibir nome no modal
      const company = await CompaniesService.getById(companyId);
      const companyName =
        company?.people?.name || company?.name || "esta empresa";
      console.log("🔍 [EmpresasPage] Empresa encontrada:", companyName);

      const executeDelete = async () => {
        console.log("🔍 [EmpresasPage] executeDelete chamado");
        try {
          await CompaniesService.deactivate(companyId);
          notify.success("Empresa inativada com sucesso!");

          // Recarregar dados da tabela
          window.location.reload();
        } catch (err) {
          // Diferenciar erro de validação (400/422) de erro técnico (500)
          if (
            err.status === 400 ||
            err.status_code === 400 ||
            err.response?.status === 400 ||
            err.status === 422 ||
            err.status_code === 422 ||
            err.response?.status === 422
          ) {
            const errorMessage =
              err.detail ||
              err.response?.data?.detail ||
              err.response?.data?.error?.message ||
              err.message ||
              "Não é possível inativar a empresa";
            notify.warning(errorMessage);
          } else {
            notify.error("Erro ao inativar empresa. Tente novamente.");
          }
          console.error(err);
        }
      };

      console.log("🔍 [EmpresasPage] Chamando notify.confirm...");
      notify.confirm(
        "Inativar Empresa",
        `Tem certeza que deseja inativar a empresa "${companyName}"?\n\nA empresa e todos os seus estabelecimentos ativos serão removidos das listagens ativas, mas todos os dados serão preservados e poderão ser reativados posteriormente.`,
        executeDelete
      );
      console.log("✅ [EmpresasPage] notify.confirm executado");
    } catch (error) {
      console.error(
        "❌ [EmpresasPage] Erro ao buscar dados da empresa:",
        error
      );
      notify.error("Erro ao carregar dados da empresa");
    }
  };

  // Handler para reativação de empresa da tabela
  const handleReactivate = async (companyId) => {
    console.log("🔍 [EmpresasPage] handleReactivate chamado com ID:", companyId);

    try {
      const company = await CompaniesService.getById(companyId);
      const companyName =
        company?.people?.name || company?.name || "esta empresa";

      const executeReactivate = async () => {
        try {
          await CompaniesService.activate(companyId);
          notify.success("Empresa reativada com sucesso!");
          window.location.reload();
        } catch (err) {
          if (
            err.status === 400 ||
            err.status_code === 400 ||
            err.response?.status === 400 ||
            err.status === 404 ||
            err.response?.status === 404
          ) {
            const errorMessage =
              err.detail ||
              err.response?.data?.detail ||
              err.message ||
              "Não é possível reativar a empresa";
            notify.warning(errorMessage);
          } else {
            notify.error("Erro ao reativar empresa. Tente novamente.");
          }
          console.error(err);
        }
      };

      notify.confirm(
        "Reativar Empresa",
        `Tem certeza que deseja reativar a empresa "${companyName}"?\n\nA empresa voltará a aparecer nas listagens ativas e poderá ser utilizada normalmente.`,
        executeReactivate
      );
    } catch (error) {
      console.error("❌ [EmpresasPage] Erro ao buscar dados da empresa:", error);
      notify.error("Erro ao carregar dados da empresa");
    }
  };

  // Initialize companies data table hook
  const companiesTableData = useCompaniesDataTable({
    initialPageSize: 10,
  });

  // Verificar parâmetros da URL ao carregar a página
  useEffect(() => {
    const companyIdParam = searchParams.get("companyId");
    const action = searchParams.get("action");
    const view = searchParams.get("view");

    // Se há um ID na URL, mostrar detalhes da empresa
    if (id) {
      setSelectedCompanyId(parseInt(id));
      setCurrentView("details");
    } else if (view === "create") {
      setCurrentView("create");
      setSelectedCompanyId(null);
    } else if (companyIdParam) {
      setSelectedCompanyId(parseInt(companyIdParam));
      if (action === "edit") {
        setCurrentView("edit");
      } else {
        setCurrentView("details");
      }
    } else {
      // Sem ID ou params → voltar para lista
      setCurrentView("list");
      setSelectedCompanyId(null);
    }
  }, [searchParams, id]);



  const handleBackToList = () => {
    setCurrentView("list");
    setSelectedCompanyId(null);
    navigate("/admin/companies");
  };

  const handleSave = (redirectToDetails = false, companyId = null) => {
    if (redirectToDetails && companyId) {
      setSelectedCompanyId(companyId);
      setCurrentView("details");
      navigate(`/admin/companies/${companyId}?tab=faturamento`);
    } else {
      setCurrentView("list");
      setSelectedCompanyId(null);
    navigate("/admin/companies");
    }
  };

  const handleCancel = () => {
    setCurrentView("list");
    setSelectedCompanyId(null);
    navigate("/admin/companies");
  };

  // Render different views based on current state
  if (currentView === "create" || currentView === "edit") {
    const companyIdToPass = currentView === "create" ? null : selectedCompanyId;

    return (
      <CompanyForm
        companyId={companyIdToPass}
        onSave={() => handleSave(false)}
        onCancel={handleCancel}
        onRedirectToDetails={(companyId) => handleSave(true, companyId)}
      />
    );
  }

  if (currentView === "details") {
    return (
      <CompanyDetailsNew
        companyId={selectedCompanyId}
        onBack={handleBackToList}
        onEdit={() => setCurrentView("edit")}
        onDelete={handleBackToList}
      />
    );
  }

  // Default: list view using DataTableTemplate
  console.log("🎨 [EmpresasPage] Renderizando página, companies:", companiesTableData.data?.length || 0, "loading:", companiesTableData.loading);

  return (
    <div className="space-y-6">
      <DataTableTemplate
        config={createCompaniesConfig(navigate, {
          onDelete: handleDelete,
          onReactivate: handleReactivate,
        }, {
          onCleanup: () => setShowCleanupModal(true),
        })}
        tableData={companiesTableData}
      />

      {/* Modal de limpeza */}
      <CleanupPendingCompaniesModal
        isOpen={showCleanupModal}
        onClose={() => setShowCleanupModal(false)}
        onSuccess={() => {
          // Recarregar lista após limpeza
          window.location.reload();
        }}
      />
    </div>
  );
};

export default EmpresasPage;
