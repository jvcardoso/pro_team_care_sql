/**
 * Company Details Component
 * Mostra os detalhes completos de uma empresa específica
 */

import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import {
  Building,
  Phone,
  Mail,
  MapPin,
  Calendar,
  ArrowLeft,
  Edit,
  Trash2,
  RefreshCw,
  User,
  Globe,
  Plus,
  Download,
  FileText,
  AlertTriangle,
  Shield,
  Eye,
} from "lucide-react";
import { Company } from "../../types/company.types";
import Card from "../ui/Card";
import Button from "../ui/Button";
import EntityDetailsLayout from "./EntityDetailsLayout";
import { establishmentsService } from "../../services/api";
import CompaniesService from "../../services/companiesService";
import { notify } from "../../utils/notifications.jsx";
import {
  getEntityAuditLog,
  AuditLogItem,
  AuditLogResponse,
} from "../../services/lgpdService";
import SensitiveDataField from "../shared/SensitiveDataField";
import AuditLogTab from "../shared/AuditLogTab";

import axios from "axios";
import { API_BASE_URL } from "../../config/http";
import PersonBasicInfo from "../entities/PersonBasicInfo";
import ReceitaFederalInfo from "../metadata/ReceitaFederalInfo";
import {
  PhoneDisplayCard,
  EmailDisplayCard,
  AddressDisplayCard,
} from "../contacts";
import {
  formatPhone,
  formatZipCode,
  getPhoneTypeLabel,
  getEmailTypeLabel,
  getAddressTypeLabel,
} from "../../utils/statusUtils";

const CompanyDetailsNew: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [company, setCompany] = useState<Company | null>(null);
  const [establishments, setEstablishments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("informacoes");

  const [showDeletionModal, setShowDeletionModal] = useState(false);

  // Verificar aba da URL (apenas abas implementadas)
  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (
      tabParam &&
      ["informacoes", "estabelecimentos", "lgpd"].includes(tabParam)
    ) {
      console.log('🔄 [CompanyDetailsNew] URL tab parameter:', tabParam);
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  // Função para mudar aba
  const handleTabChange = (newTab: string) => {
    console.log('🔄 [CompanyDetailsNew] Tab changed to:', newTab);
    setActiveTab(newTab);
    // Atualizar URL
    const newUrl = `/admin/companies/${id}?tab=${newTab}`;
    console.log('🔄 [CompanyDetailsNew] Navigating to:', newUrl);
    navigate(newUrl, { replace: true });
  };

  const loadCompanyData = async () => {
    if (!id) return;

    setLoading(true);
    setError(null);

    try {
      const companyData = await CompaniesService.getById(parseInt(id));
      setCompany(companyData);
    } catch (err: any) {
      setError(err.message || "Erro ao carregar empresa");
    } finally {
      setLoading(false);
    }
  };



  useEffect(() => {
    loadCompanyData();
  }, [id]);

  useEffect(() => {
    if (activeTab === "estabelecimentos" && id) {
      loadEstablishments();
    }
  }, [activeTab, id]);



  const loadEstablishments = async () => {
    try {
      const response = await establishmentsService.getEstablishmentsByCompany(
        parseInt(id)
      );
      const establishmentsData = response?.establishments || response || [];
      setEstablishments(
        Array.isArray(establishmentsData) ? establishmentsData : []
      );
    } catch (err) {
      console.error("Erro ao carregar estabelecimentos:", err);
      setEstablishments([]);
    }
  };

  const handleBack = () => {
    navigate("/admin/companies");
  };

  const handleEdit = () => {
    navigate(`/admin/companies?companyId=${id}&action=edit`);
  };

  const handleDeactivate = async () => {
    if (!company) return;

    const executeDeactivate = async () => {
      try {
        await CompaniesService.deactivate(parseInt(id));
        notify.success("Empresa inativada com sucesso!");
        navigate("/admin/companies");
      } catch (err: any) {
        // Diferenciar erro de validação (400) de erro técnico (500)
        if (
          err.status === 400 ||
          err.status_code === 400 ||
          err.response?.status === 400
        ) {
          // Backend enviou mensagem de validação específica (ex: estabelecimentos ativos)
          const errorMessage =
            err.detail ||
            err.response?.data?.detail ||
            err.message ||
            "Não é possível inativar a empresa";
          notify.warning(errorMessage);
        } else {
          // Erro técnico/servidor
          notify.error("Erro ao inativar empresa. Tente novamente.");
        }
        console.error(err);
      }
    };

    notify.confirm(
      "Inativar Empresa",
      `Tem certeza que deseja inativar a empresa "${company.name}"?\n\nA empresa será removida das listagens ativas, mas todos os dados serão preservados e poderão ser reativados posteriormente.`,
      executeDeactivate
    );
  };

  const handleReactivate = async () => {
    if (!company) return;

    const executeReactivate = async () => {
      try {
        await CompaniesService.activate(parseInt(id));
        notify.success("Empresa reativada com sucesso!");
        // Recarregar dados da empresa
        await loadCompanyData();
      } catch (err: any) {
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
      `Tem certeza que deseja reativar a empresa "${company.name}"?\n\nA empresa voltará a aparecer nas listagens ativas e poderá ser utilizada normalmente.`,
      executeReactivate
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded dark:bg-gray-700 w-96 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded dark:bg-gray-700 w-64 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-24 bg-gray-200 rounded dark:bg-gray-700"
              ></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded dark:bg-red-900/20 dark:border-red-900 dark:text-red-400">
          <h3 className="font-semibold">Erro ao carregar empresa</h3>
          <p>{error}</p>
        </div>
        <button
          onClick={handleBack}
          className="mt-4 inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-100 rounded-lg hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-300 dark:hover:bg-blue-800"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Voltar para lista
        </button>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="p-6">
        <div className="text-center py-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full mb-4">
            <Building className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Empresa não encontrada
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            A empresa com ID {id} não foi encontrada.
          </p>
          <button
            onClick={handleBack}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-100 rounded-lg hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-300 dark:hover:bg-blue-800"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar para lista
          </button>
        </div>
      </div>
    );
  }

  const statusBadge = (
    <span
      className={`px-2 py-1 text-xs rounded whitespace-nowrap ${
        company.status === "active"
          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
          : company.status === "inactive"
          ? "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300"
          : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300"
      }`}
    >
      {company.status === "active"
        ? "Ativo"
        : company.status === "inactive"
        ? "Inativo"
        : "Suspenso"}
    </span>
  );

  // Métricas reais (sem dados mockados)
  const metrics = [
    {
      icon: <Building className="h-5 w-5 text-blue-600" />,
      label: "Estabelecimentos",
      value: establishments.length.toString(),
    },
  ];

  // Tabs implementadas (sem placeholders vazios)
  const tabs = [
    { key: "informacoes", label: "Informações", shortLabel: "Info" },
    {
      key: "estabelecimentos",
      label: "Estabelecimentos",
      shortLabel: "Estab.",
    },
    { key: "lgpd", label: "LGPD" },
  ];

  const handleExportData = async () => {
    if (!id || !company) return;
    try {
      notify.info("Exportando dados...");
      
      // ✅ USA ENDPOINT ESPECÍFICO (delega para genérico no backend)
      const token = localStorage.getItem("access_token");
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/companies/${id}/lgpd/export-data`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      // Download do arquivo JSON
      const json = JSON.stringify(response.data, null, 2);
      const blob = new Blob([json], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${company.people?.name || "empresa"}_dados_lgpd_${new Date().toISOString().split("T")[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      notify.success("Dados exportados com sucesso!");
      // Recarregar logs para mostrar a exportação
      loadAuditLogs();
    } catch (error: any) {
      notify.error(
        error.response?.data?.detail || error.message || "Erro ao exportar dados"
      );
    }
  };

  const handleRequestDeletion = async () => {
    if (!id) return;
    try {
      // ✅ USA ENDPOINT ESPECÍFICO (delega para genérico no backend)
      const token = localStorage.getItem("access_token");
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/companies/${id}/lgpd/request-deletion`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      notify.success(response.data.message || "Solicitação de exclusão registrada com sucesso!");
      setShowDeletionModal(false);
      // Recarregar logs para mostrar a solicitação
      loadAuditLogs();
    } catch (error: any) {
      notify.error(
        error.response?.data?.detail || error.message || "Erro ao solicitar exclusão"
      );
    }
  };

  const actionButtons = [
    {
      label: "Editar",
      onClick: handleEdit,
      icon: <Edit className="h-4 w-4" />,
    },
    // Mostrar botão de Reativar se empresa estiver inativa
    ...(company.status === "inactive"
      ? [
          {
            label: "Reativar",
            onClick: handleReactivate,
            variant: "success" as const,
            outline: true,
            icon: <RefreshCw className="h-4 w-4" />,
          },
        ]
      : [
          // Mostrar botão de Inativar se empresa estiver ativa
          {
            label: "Inativar",
            onClick: handleDeactivate,
            variant: "danger" as const,
            outline: true,
            icon: <Trash2 className="h-4 w-4" />,
          },
        ]),
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case "informacoes":
        return (
          <div className="space-y-6">
            {/* Informações Básicas da Empresa (PF ou PJ) */}
            <PersonBasicInfo
              person={company.people}
              entityType="companies"
              entityId={company.id}
            />

            {/* Cards de Contatos com dados sensíveis e revelação LGPD */}
            <PhoneDisplayCard
              phones={company.phones || []}
              formatPhone={formatPhone}
              getPhoneTypeLabel={getPhoneTypeLabel}
              entityType="companies"
              entityId={company.id}
            />

            <EmailDisplayCard
              emails={company.emails || []}
              getEmailTypeLabel={getEmailTypeLabel}
              entityType="companies"
              entityId={company.id}
            />

            <AddressDisplayCard
              addresses={company.addresses || []}
              getAddressTypeLabel={getAddressTypeLabel}
              formatZipCode={formatZipCode}
              entityType="companies"
              entityId={company.id}
            />

            {/* Informações da Receita Federal (CNAE, etc) */}
            <ReceitaFederalInfo
              metadata={
                company.company?.metadata ||
                company.people?.metadata ||
                company.metadata ||
                {}
              }
            />

            {/* Informações do Sistema */}
            <Card title="Informações do Sistema">
              <div className="space-y-4 text-sm">
                <div>
                  <label className="block text-muted-foreground mb-1">
                    ID da Empresa
                  </label>
                  <p className="text-foreground font-mono">#{company.id}</p>
                </div>
                <div>
                  <label className="block text-muted-foreground mb-1">
                    Criado em
                  </label>
                  <p className="text-foreground">
                    {new Date(company.created_at).toLocaleString("pt-BR")}
                  </p>
                </div>
                <div>
                  <label className="block text-muted-foreground mb-1">
                    Atualizado em
                  </label>
                  <p className="text-foreground">
                    {new Date(
                      company.updated_at || company.created_at
                    ).toLocaleString("pt-BR")}
                  </p>
                </div>
              </div>
            </Card>
          </div>
        );

      case "estabelecimentos":
        return (
          <div className="space-y-6">
            {/* Header com botão Novo Estabelecimento */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-medium text-foreground">
                  Estabelecimentos da Empresa
                </h3>
                <p className="text-muted-foreground">
                  Gerencie os estabelecimentos vinculados a esta empresa
                </p>
              </div>
              <Button
                onClick={() => {
                  navigate(
                    `/admin/establishments?companyId=${id}&action=create`
                  );
                }}
                icon={<Plus className="h-4 w-4" />}
                className="w-full sm:w-auto whitespace-nowrap"
              >
                <span className="hidden sm:inline">Novo Estabelecimento</span>
                <span className="sm:hidden">+ Estabelecimento</span>
              </Button>
            </div>

            {/* Lista de Estabelecimentos */}
            {establishments.length === 0 ? (
              <div className="text-center py-12">
                <Building className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">
                  Nenhum estabelecimento encontrado
                </h3>
                <p className="text-muted-foreground mb-6">
                  Esta empresa ainda não possui estabelecimentos cadastrados
                </p>
                <Button
                  onClick={() => {
                    navigate(
                      `/admin/establishments?companyId=${id}&action=create`
                    );
                  }}
                  icon={<Plus className="h-4 w-4" />}
                >
                  Criar Primeiro Estabelecimento
                </Button>
              </div>
            ) : (
              <div className="grid gap-4">
                {establishments.map((establishment) => (
                  <Card key={establishment.id} className="p-4">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3">
                          <Building className="h-5 w-5 text-primary flex-shrink-0" />
                          <div className="min-w-0 flex-1">
                            <h4 className="font-medium text-foreground break-words">
                              {establishment.person?.name || establishment.code}
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              Código: {establishment.code}
                            </p>
                            {establishment.person?.tax_id && (
                              <p className="text-sm text-muted-foreground break-all font-mono">
                                CNPJ: {establishment.person.tax_id}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-2">
                        <div className="flex flex-wrap gap-2">
                          <span
                            className={`px-2 py-1 text-xs rounded whitespace-nowrap ${
                              establishment.is_active
                                ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
                                : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
                            }`}
                          >
                            {establishment.is_active ? "Ativo" : "Inativo"}
                          </span>
                          {establishment.is_principal && (
                            <span className="px-2 py-1 text-xs bg-primary/10 text-primary rounded whitespace-nowrap">
                              Principal
                            </span>
                          )}
                        </div>
                        <Button
                          size="sm"
                          variant="secondary"
                          outline
                          onClick={() => {
                            navigate(
                              `/admin/establishments/${establishment.id}?tab=information`
                            );
                          }}
                          className="w-full sm:w-auto whitespace-nowrap"
                        >
                          Ver Detalhes
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        );

      case "lgpd":
        return (
          <div className="space-y-6">
            {/* Actions Card */}
            <Card title="Ações LGPD">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button
                  onClick={handleExportData}
                  variant="primary"
                  outline
                  icon={<Download className="h-4 w-4" />}
                >
                  Exportar Dados (Art. 18, II)
                </Button>
                <Button
                  onClick={() => setShowDeletionModal(true)}
                  variant="danger"
                  outline
                  icon={<AlertTriangle className="h-4 w-4" />}
                  disabled={company.status !== "inactive"}
                >
                  Solicitar Exclusão (Art. 18, VI)
                </Button>
              </div>
              {company.status !== "inactive" && (
                <p className="text-sm text-muted-foreground mt-4">
                  <Shield className="inline h-4 w-4 mr-1" />
                  A empresa deve estar inativa antes de solicitar exclusão
                  permanente
                </p>
              )}
            </Card>

            {/* ✅ Componente genérico substitui 175+ linhas de código inline */}
            <AuditLogTab
              entityType="companies"
              entityId={parseInt(id)}
            />

            {/* Deletion Modal */}
            {showDeletionModal && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-background border border-border rounded-lg p-6 max-w-md w-full mx-4">
                  <div className="flex items-center gap-3 mb-4">
                    <AlertTriangle className="h-6 w-6 text-red-600" />
                    <h3 className="text-lg font-semibold text-foreground">
                      Solicitar Exclusão Permanente
                    </h3>
                  </div>
                  <p className="text-muted-foreground mb-4">
                    Esta ação criará uma solicitação de exclusão permanente dos
                    dados da empresa. A solicitação será revisada manualmente
                    para conformidade com LGPD antes da exclusão.
                  </p>
                  <p className="text-sm text-muted-foreground mb-6">
                    <strong>Empresa:</strong> {company.name}
                    <br />
                    <strong>Status:</strong> {company.status}
                    <br />
                    <strong>LGPD:</strong> Art. 18, VI - Direito à eliminação
                  </p>
                  <div className="flex gap-3 justify-end">
                    <Button
                      onClick={() => setShowDeletionModal(false)}
                      variant="secondary"
                      outline
                    >
                      Cancelar
                    </Button>
                    <Button
                      onClick={handleRequestDeletion}
                      variant="danger"
                      icon={<AlertTriangle className="h-4 w-4" />}
                    >
                      Confirmar Solicitação
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <EntityDetailsLayout
      title={company.name}
      subtitle={
        company.trade_name && company.trade_name !== company.name
          ? company.trade_name
          : undefined
      }
      icon={<Building className="h-6 w-6" />}
      statusBadge={statusBadge}
      backButton={{ onClick: handleBack }}
      actionButtons={actionButtons}
      metrics={metrics}
      tabs={tabs}
      activeTab={activeTab}
      onTabChange={handleTabChange}
      loading={loading}
      error={error}
    >
      {renderTabContent()}
    </EntityDetailsLayout>
  );
};

export default CompanyDetailsNew;
