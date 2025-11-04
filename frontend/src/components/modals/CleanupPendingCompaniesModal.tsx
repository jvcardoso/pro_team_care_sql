/**
 * Modal para limpeza de empresas com cadastro pendente
 * Permite visualizar e remover empresas que nunca concluíram o cadastro
 */

import React, { useState, useEffect } from "react";
import {
  X,
  AlertTriangle,
  Trash2,
  Calendar,
  Building,
  Shield,
  CheckCircle,
  XCircle,
  Clock,
  Filter
} from "lucide-react";

import { notify } from "../../utils/notifications";

interface PendingCompany {
  company_id: number;
  razao_social: string;
  cnpj: string;
  created_at: string;
}

interface CleanupResult {
  company_id: number;
  status: 'success' | 'error';
  message: string;
}

interface CleanupPendingCompaniesModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const CleanupPendingCompaniesModal: React.FC<CleanupPendingCompaniesModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [pendingCompanies, setPendingCompanies] = useState<PendingCompany[]>([]);
  const [selectedCompanies, setSelectedCompanies] = useState<number[]>([]);
  const [daysOld, setDaysOld] = useState(30);
  const [searchTerm, setSearchTerm] = useState("");
  const [cutoffDate, setCutoffDate] = useState<string>("");
  const [cleanupResults, setCleanupResults] = useState<CleanupResult[]>([]);

  // Carregar empresas pendentes
  const loadPendingCompanies = async () => {
    setLoading(true);
    try {
      const { companiesService } = await import("../../services/companiesService");
      const response = await CompaniesService.getPendingCompanies({
        days_old: daysOld,
        search: searchTerm || undefined
      });

      setPendingCompanies(response.companies || []);
      setCutoffDate(response.cutoff_date || "");
      setSelectedCompanies([]); // Reset selection
      setCleanupResults([]); // Reset results
    } catch (error: any) {
      console.error("Erro ao carregar empresas pendentes:", error);
      notify.error("Erro ao carregar empresas pendentes");
    } finally {
      setLoading(false);
    }
  };

  // Executar limpeza
  const executeCleanup = async () => {
    if (selectedCompanies.length === 0) {
      notify.warning("Selecione pelo menos uma empresa para remover");
      return;
    }

    // Usar notify.confirm com Promise
    const confirmed = await new Promise<boolean>((resolve) => {
      notify.confirm(
        "🧹 Confirmar Limpeza",
        `Tem certeza que deseja remover ${selectedCompanies.length} empresa(s) pendente(s)?\n\nEsta ação não pode ser desfeita e removerá todos os dados relacionados (pessoas, perfis, contatos, endereços).`,
        () => resolve(true), // onConfirm
        () => resolve(false), // onCancel
        { duration: Infinity }
      );
    });

    if (!confirmed) return;

    setDeleting(true);
    try {
      const { companiesService } = await import("../../services/companiesService");
      const response = await CompaniesService.cleanupPendingCompanies(selectedCompanies);

      setCleanupResults(response.results || []);

      const successCount = response.success_count || 0;
      const errorCount = response.error_count || 0;

      if (successCount > 0) {
        notify.success(`${successCount} empresa(s) removida(s) com sucesso!`);
        if (onSuccess) onSuccess();
        // Recarregar lista após sucesso
        await loadPendingCompanies();
      }

      if (errorCount > 0) {
        notify.warning(`${errorCount} empresa(s) não puderam ser removidas. Verifique os detalhes.`);
      }

    } catch (error: any) {
      console.error("Erro ao executar limpeza:", error);
      notify.error("Erro ao executar limpeza das empresas");
    } finally {
      setDeleting(false);
    }
  };

  // Efeitos
  useEffect(() => {
    if (isOpen) {
      loadPendingCompanies();
    }
  }, [isOpen, daysOld]);

  // Handlers
  const handleSelectAll = () => {
    if (selectedCompanies.length === pendingCompanies.length) {
      setSelectedCompanies([]);
    } else {
      setSelectedCompanies(pendingCompanies.map(c => c.company_id));
    }
  };

  const handleSelectCompany = (companyId: number) => {
    setSelectedCompanies(prev =>
      prev.includes(companyId)
        ? prev.filter(id => id !== companyId)
        : [...prev, companyId]
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCNPJ = (cnpj: string) => {
    // Máscara básica para CNPJ
    if (cnpj && cnpj.length === 14) {
      return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }
    return cnpj;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose}></div>

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div className="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-6 w-6 text-orange-500" />
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    🧹 Limpeza de Empresas Pendentes
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Empresas com cadastro iniciado mas nunca concluído
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Warning */}
            <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4 mb-6">
              <div className="flex items-start gap-3">
                <Shield className="h-5 w-5 text-orange-500 dark:text-orange-400 mt-0.5" />
                <div>
                  <h4 className="text-sm font-medium text-orange-800 dark:text-orange-200">
                    ⚠️ Operação Irreversível
                  </h4>
                  <p className="text-sm text-orange-700 dark:text-orange-300 mt-1">
                    Esta ação removerá permanentemente todas as empresas selecionadas e todos os dados relacionados
                    (pessoas, perfis, contatos, endereços). Certifique-se de que estas empresas realmente não serão utilizadas.
                  </p>
                </div>
              </div>
            </div>

            {/* Filters */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-6">
              <div className="flex flex-col gap-4">
                {/* Search */}
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Buscar:</span>
                  </div>
                  <div className="flex-1 max-w-md">
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          loadPendingCompanies();
                        }
                      }}
                      placeholder="Nome da empresa ou CNPJ..."
                      className="w-full text-sm border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      disabled={loading}
                    />
                  </div>
                  <button
                    type="button"
                    onClick={loadPendingCompanies}
                    disabled={loading}
                    className="flex items-center justify-center text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 font-medium rounded-lg text-sm px-4 py-2 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700 disabled:opacity-50 disabled:pointer-events-none"
                  >
                    {loading ? "Buscando..." : "Buscar"}
                  </button>
                </div>

                {/* Date filter and update button */}
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filtros:</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 dark:text-gray-400">Criadas há mais de:</label>
                    <select
                      value={daysOld}
                      onChange={(e) => setDaysOld(Number(e.target.value))}
                      className="text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      disabled={loading}
                    >
                      <option value={1}>1 dia</option>
                      <option value={3}>3 dias</option>
                      <option value={7}>7 dias</option>
                      <option value={14}>14 dias</option>
                      <option value={30}>30 dias</option>
                      <option value={60}>60 dias</option>
                    </select>
                  </div>
                  {cutoffDate && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <Calendar className="h-4 w-4" />
                      <span>Corte: {formatDate(cutoffDate)}</span>
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={loadPendingCompanies}
                    disabled={loading}
                    className="flex items-center justify-center text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 font-medium rounded-lg text-sm px-4 py-2 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700 disabled:opacity-50 disabled:pointer-events-none"
                  >
                    {loading ? "Carregando..." : "Atualizar"}
                  </button>
                </div>
              </div>
            </div>

            {/* Companies List */}
            {loading ? (
              <div className="text-center py-8">
                <Clock className="h-8 w-8 text-gray-400 dark:text-gray-500 mx-auto mb-2 animate-spin" />
                <p className="text-gray-600 dark:text-gray-400">Carregando empresas pendentes...</p>
              </div>
            ) : pendingCompanies.length === 0 ? (
              <div className="text-center py-8">
                <CheckCircle className="h-8 w-8 text-green-500 dark:text-green-400 mx-auto mb-2" />
                <p className="text-gray-600 dark:text-gray-400">Nenhuma empresa pendente encontrada com os filtros atuais.</p>
              </div>
            ) : (
              <div className="border border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden">
                {/* Header */}
                <div className="bg-gray-50 dark:bg-gray-700 px-4 py-3 border-b border-gray-200 dark:border-gray-600">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={selectedCompanies.length === pendingCompanies.length && pendingCompanies.length > 0}
                        onChange={handleSelectAll}
                        className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 dark:bg-gray-800"
                      />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {selectedCompanies.length} de {pendingCompanies.length} selecionadas
                      </span>
                    </div>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {pendingCompanies.length} empresa(s) encontrada(s)
                    </span>
                  </div>
                </div>

                {/* List */}
                <div className="max-h-96 overflow-y-auto">
                  {pendingCompanies.map((company) => (
                    <div
                      key={company.company_id}
                      className={`border-b border-gray-100 dark:border-gray-600 last:border-b-0 hover:bg-gray-50 dark:hover:bg-gray-700 ${
                        selectedCompanies.includes(company.company_id) ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                      }`}
                    >
                      <div className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <input
                            type="checkbox"
                            checked={selectedCompanies.includes(company.company_id)}
                            onChange={() => handleSelectCompany(company.company_id)}
                            className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 dark:bg-gray-800"
                          />
                          <Building className="h-5 w-5 text-gray-400 dark:text-gray-500" />
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-gray-900 dark:text-white">
                                  {company.razao_social || "Razão Social não informada"}
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  CNPJ: {formatCNPJ(company.cnpj)}
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                  Criada em: {formatDate(company.created_at)}
                                </p>
                                <p className="text-xs text-orange-600 dark:text-orange-400 font-medium">
                                  Status: Pendente
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Cleanup Results */}
            {cleanupResults.length > 0 && (
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">📋 Resultado da Limpeza:</h4>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {cleanupResults.map((result) => (
                    <div
                      key={result.company_id}
                      className={`flex items-center gap-2 text-sm p-2 rounded ${
                        result.status === 'success'
                          ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400'
                          : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400'
                      }`}
                    >
                      {result.status === 'success' ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <XCircle className="h-4 w-4" />
                      )}
                      <span>{result.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-3">
            <button
              type="button"
              onClick={executeCleanup}
              disabled={selectedCompanies.length === 0 || deleting}
              className="flex items-center justify-center text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-red-600 dark:hover:bg-red-700 focus:outline-none dark:focus:ring-red-900 disabled:opacity-50 disabled:pointer-events-none"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              {deleting ? "Removendo..." : `Remover ${selectedCompanies.length} Empresa(s)`}
            </button>

            <button
              type="button"
              onClick={onClose}
              disabled={deleting}
              className="flex items-center justify-center text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 font-medium rounded-lg text-sm px-4 py-2 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700 disabled:opacity-50 disabled:pointer-events-none"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CleanupPendingCompaniesModal;