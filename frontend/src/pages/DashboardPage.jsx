import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import ContextSwitcher from "../components/security/ContextSwitcher";
import MetricCard from "../components/dashboard/MetricCard";

const DashboardPage = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const { data } = await api.get("/api/v1/dashboard/stats");
        setDashboardData(data);
        setError(null);
      } catch (err) {
        console.error("Erro ao carregar dashboard:", err);
        setError("Não foi possível carregar os dados do dashboard. Verifique sua conexão e tente novamente.");
        setDashboardData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();

    // Atualizar dashboard a cada 5 minutos
    const interval = setInterval(fetchDashboard, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="animate-fade-in">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">
            Visão geral das atividades e métricas do sistema
          </p>
        </div>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Carregando dados...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="animate-fade-in">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">
            Visão geral das atividades e métricas do sistema
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700 font-medium">{error}</p>
          <button
            className="btn btn-primary mt-4"
            onClick={() => window.location.reload()}
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  // Validar estrutura da resposta da API
  if (!dashboardData.stats) {
    return (
      <div className="animate-fade-in">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">
            Visão geral das atividades e métricas do sistema
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700 font-medium">
            Erro: Estrutura de dados inválida recebida da API.
          </p>
          <p className="text-sm text-red-600 mt-2">
            Resposta recebida: {JSON.stringify(dashboardData)}
          </p>
          <button
            className="btn btn-primary mt-4"
            onClick={() => window.location.reload()}
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  // Extrair dados da resposta da API
  const stats = dashboardData.stats;

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Dashboard Administrativo
            </h1>
            <p className="text-gray-600">
              Visão geral do sistema Pro Team Care
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <ContextSwitcher />
          </div>
        </div>
      </div>

      {/* Metric Cards - Resumo Principal */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <MetricCard
          icon="🏢"
          title="Empresas"
          value={stats?.companies?.total ?? 0}
          subtitle={`${stats?.companies?.active ?? 0} ativas, ${stats?.companies?.inactive ?? 0} inativas`}
          color="blue"
        />
        <MetricCard
          icon="🏬"
          title="Estabelecimentos"
          value={stats?.establishments?.total ?? 0}
          subtitle={`${stats?.establishments?.active ?? 0} ativos, ${stats?.establishments?.inactive ?? 0} inativos`}
          color="green"
        />
        <MetricCard
          icon="👥"
          title="Usuários"
          value={stats?.users?.total ?? 0}
          subtitle={`${stats?.users?.active ?? 0} ativos, ${stats?.users?.inactive ?? 0} inativos`}
          color="purple"
        />
        <MetricCard
          icon="🔔"
          title="Notificações"
          value={stats?.notifications?.total ?? 0}
          subtitle={`${stats?.notifications?.unread ?? 0} não lidas`}
          color="orange"
        />
      </div>

      {/* Estatísticas Adicionais */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Perfis de Acesso</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Total:</span>
              <span className="font-semibold">{stats?.roles?.total ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Ativos:</span>
              <span className="font-semibold text-green-600">{stats?.roles?.active ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Inativos:</span>
              <span className="font-semibold text-gray-400">{stats?.roles?.inactive ?? 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Sessões Ativas</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Usuários Online:</span>
              <span className="font-semibold text-blue-600">{stats?.sessions?.active ?? 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Contexto</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Tipo:</span>
              <span className="font-semibold capitalize">{dashboardData?.user_context ?? 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Usuário ID:</span>
              <span className="font-semibold">{dashboardData?.user_id ?? 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer com timestamp */}
      <div className="mt-6 text-center text-xs text-gray-500">
        Última atualização:{" "}
        {new Date(dashboardData.generated_at).toLocaleString("pt-BR")}
      </div>
    </div>
  );
};

export default DashboardPage;
