import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { 
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer 
} from "recharts";
import { 
  TrendingUp, Clock, CheckCircle, AlertCircle, 
  Activity, Calendar, Eye, Loader2, FileText, BarChart3 
} from "lucide-react";
import { CardDetailModal } from "../components/kanban/CardDetailModal";
import { ITILSummaryChart } from "../components/kanban/ITILSummaryChart";
import { DataTableTemplate } from "../components/shared/DataTable/DataTableTemplate";
import { createItilAnalyticsConfig } from "../config/tables/itil-analytics.config";
import { useItilAnalyticsDataTable } from "../hooks/useItilAnalyticsDataTable";

/**
 * Dashboard de Analytics dedicado ao Kanban
 * Rota: /admin/kanban/analytics
 */
const KanbanAnalyticsPage = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dateRange, setDateRange] = useState({
    start: getDefaultStartDate(),
    end: getDefaultEndDate()
  });
  const [columns, setColumns] = useState([]);
  const [selectedColumns, setSelectedColumns] = useState([]);
  
  // Estados para ITIL
  const [activeTab, setActiveTab] = useState('analytics'); // 'analytics' ou 'itil'
  const [itilSummary, setItilSummary] = useState([]);
  const [itilLoading, setItilLoading] = useState(false);
  const [selectedCard, setSelectedCard] = useState(null);
  
  // Hook para tabela ITIL paginada
  const itilTableData = useItilAnalyticsDataTable({
    startDate: dateRange.start,
    endDate: dateRange.end,
  });
  
  // Configuração da tabela ITIL
  const itilConfig = createItilAnalyticsConfig(undefined, {
    onViewDetails: (cardId) => {
      // Buscar card e abrir modal
      const card = itilTableData.state.data.find(c => c.cardId === cardId);
      if (card) {
        setSelectedCard(card);
      }
    },
  });

  // Datas padrão: ano atual (01/01 até hoje)
  function getDefaultStartDate() {
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(today.getDate() - 30);
    return thirtyDaysAgo.toISOString().split('T')[0];
  }

  function getDefaultEndDate() {
    return new Date().toISOString().split('T')[0];
  }

  useEffect(() => {
    fetchColumns();
  }, []);

  useEffect(() => {
    if (activeTab === 'analytics') {
      fetchAnalytics();
    } else if (activeTab === 'itil') {
      fetchITILData();
    }
  }, [dateRange, activeTab]);

  const fetchColumns = async () => {
    try {
      const response = await api.get("/api/v1/kanban/columns");
      setColumns(response.data || []);
      // Selecionar todas as colunas por padrão
      setSelectedColumns(response.data.map(col => col.ColumnID));
    } catch (err) {
      console.error("Erro ao carregar colunas:", err);
    }
  };

  const toggleColumn = (columnId) => {
    setSelectedColumns(prev => 
      prev.includes(columnId)
        ? prev.filter(id => id !== columnId)
        : [...prev, columnId]
    );
  };

  const toggleAllColumns = () => {
    if (selectedColumns.length === columns.length) {
      setSelectedColumns([]);
    } else {
      setSelectedColumns(columns.map(col => col.ColumnID));
    }
  };

  const setPeriod = (period) => {
    const today = new Date();
    let start, end;

    switch (period) {
      case 'today':
        start = end = today.toISOString().split('T')[0];
        break;
      
      case 'week':
        // Segunda-feira desta semana
        const monday = new Date(today);
        monday.setDate(today.getDate() - today.getDay() + 1);
        start = monday.toISOString().split('T')[0];
        end = today.toISOString().split('T')[0];
        break;
      
      case 'month':
        // Primeiro dia do mês até hoje
        start = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
        end = today.toISOString().split('T')[0];
        break;
      
      case 'quarter':
        // Início do trimestre até hoje
        const quarter = Math.floor(today.getMonth() / 3);
        start = new Date(today.getFullYear(), quarter * 3, 1).toISOString().split('T')[0];
        end = today.toISOString().split('T')[0];
        break;
      
      case 'year':
        // 01/01 até hoje
        start = new Date(today.getFullYear(), 0, 1).toISOString().split('T')[0];
        end = today.toISOString().split('T')[0];
        break;
      
      default:
        return;
    }

    setDateRange({ start, end });
  };

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await api.get(
        `/api/v1/kanban/analytics?start_date=${dateRange.start}&end_date=${dateRange.end}`
      );
      setAnalytics(response.data);
      setError(null);
    } catch (err) {
      console.error("Erro ao carregar analytics do Kanban:", err);
      setError("Não foi possível carregar os dados. Tente novamente.");
      setAnalytics(null);
    } finally {
      setLoading(false);
    }
  };

  // Buscar dados ITIL
  const fetchITILData = async () => {
    try {
      setItilLoading(true);
      
      // Buscar resumo ITIL
      const summaryResponse = await api.get(
        `/api/v1/kanban/analytics/itil-summary?start_date=${dateRange.start}&end_date=${dateRange.end}`
      );
      setItilSummary(summaryResponse.data);
      
      // Buscar cards ITIL
      const cardsResponse = await api.get(
        `/api/v1/kanban/analytics/itil-cards?start_date=${dateRange.start}&end_date=${dateRange.end}`
      );
      setItilCards(cardsResponse.data);
      
    } catch (err) {
      console.error("Erro ao carregar dados ITIL:", err);
      setError("Não foi possível carregar os dados ITIL. Tente novamente.");
    } finally {
      setItilLoading(false);
    }
  };

  const formatSeconds = (seconds) => {
    if (!seconds) return "N/A";
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h`;
    return `${Math.floor(seconds / 60)}min`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Carregando analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-600 dark:text-red-400 mx-auto mb-4" />
          <p className="text-red-800 dark:text-red-200 text-center">{error}</p>
          <button
            onClick={fetchAnalytics}
            className="mt-4 w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  const { summary, timePerStage, throughputHistory } = analytics || {};

  return (
    <div className="p-3 sm:p-4 lg:p-6 space-y-4 sm:space-y-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 sm:gap-0">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Analytics do Kanban</h1>
          <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">Métricas e insights sobre o fluxo de trabalho</p>
        </div>

        {/* Filtro de Data */}
        <div className="flex flex-col gap-3">
          {/* Botões de Período Rápido */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setPeriod('today')}
              className="px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            >
              Hoje
            </button>
            <button
              onClick={() => setPeriod('week')}
              className="px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            >
              Semana
            </button>
            <button
              onClick={() => setPeriod('month')}
              className="px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            >
              Mês
            </button>
            <button
              onClick={() => setPeriod('quarter')}
              className="px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            >
              Trimestre
            </button>
            <button
              onClick={() => setPeriod('year')}
              className="px-3 py-1 text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-200 dark:hover:bg-green-800 transition-colors font-medium"
            >
              Ano (Padrão)
            </button>
          </div>
          
          {/* Seletores de Data */}
          <div className="flex gap-3 items-center">
            <div className="flex flex-col">
              <label className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                Data Inicial
              </label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>
            <div className="flex flex-col">
              <label className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                Data Final
              </label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Sistema de Abas */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === 'analytics'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <BarChart3 className="w-5 h-5" />
              Analytics Geral
            </button>
            <button
              onClick={() => setActiveTab('itil')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === 'itil'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FileText className="w-5 h-5" />
              Relatório ITIL
            </button>
          </nav>
        </div>
      </div>

      {/* Conteúdo da Aba Analytics */}
      {activeTab === 'analytics' && (
        <>
          {/* Métricas Principais */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Throughput */}
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <CheckCircle className="w-8 h-8 opacity-80" />
            <span className="text-3xl font-bold">{summary?.throughput || 0}</span>
          </div>
          <h3 className="text-sm font-medium opacity-90">Cards Concluídos</h3>
          <p className="text-xs opacity-75 mt-1">Throughput no período</p>
        </div>

        {/* WIP */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <Activity className="w-8 h-8 opacity-80" />
            <span className="text-3xl font-bold">{summary?.wip || 0}</span>
          </div>
          <h3 className="text-sm font-medium opacity-90">Em Andamento</h3>
          <p className="text-xs opacity-75 mt-1">Work-in-Progress (WIP)</p>
        </div>

        {/* Lead Time */}
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-8 h-8 opacity-80" />
            <span className="text-3xl font-bold">
              {formatSeconds(summary?.leadTimeAvgSeconds)}
            </span>
          </div>
          <h3 className="text-sm font-medium opacity-90">Lead Time Médio</h3>
          <p className="text-xs opacity-75 mt-1">Criação → Conclusão</p>
        </div>

        {/* SLA Compliance */}
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-8 h-8 opacity-80" />
            <span className="text-3xl font-bold">
              {summary?.slaCompliance?.toFixed(1) || 0}%
            </span>
          </div>
          <h3 className="text-sm font-medium opacity-90">SLA Compliance</h3>
          <p className="text-xs opacity-75 mt-1">Cards no prazo</p>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tempo por Estágio */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Tempo Médio por Estágio
          </h2>
          {timePerStage && timePerStage.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={timePerStage}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="columnName" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  tickFormatter={(value) => formatSeconds(value)}
                />
                <Tooltip 
                  formatter={(value) => formatSeconds(value)}
                  labelStyle={{ color: '#000' }}
                />
                <Bar dataKey="avgSeconds" fill="#8b5cf6" name="Tempo Médio" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              <p>Sem dados para exibir</p>
            </div>
          )}
        </div>

        {/* Histórico de Throughput */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Histórico de Conclusões
          </h2>
          {throughputHistory && throughputHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={throughputHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date"
                  tickFormatter={(date) => {
                    const d = new Date(date);
                    return `${d.getDate()}/${d.getMonth() + 1}`;
                  }}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(date) => new Date(date).toLocaleDateString('pt-BR')}
                  labelStyle={{ color: '#000' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  name="Cards Concluídos"
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              <p>Sem dados para exibir</p>
            </div>
          )}
        </div>
      </div>

      {/* Métricas Secundárias */}
      {summary?.cycleTimeAvgSeconds && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            📈 Métricas Adicionais
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Cycle Time Médio</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {formatSeconds(summary.cycleTimeAvgSeconds)}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                Início do trabalho → Conclusão
              </p>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Taxa de Entrega</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {((summary.throughput / 30) || 0).toFixed(1)} cards/dia
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                Média diária de conclusões
              </p>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Eficiência</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {summary.cycleTimeAvgSeconds && summary.leadTimeAvgSeconds
                  ? ((summary.cycleTimeAvgSeconds / summary.leadTimeAvgSeconds) * 100).toFixed(1)
                  : 0}%
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                Cycle Time / Lead Time
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tabela de Cards Concluídos */}
      <CardsTable 
        startDate={dateRange.start} 
        endDate={dateRange.end}
        columns={columns}
        selectedColumns={selectedColumns}
        onToggleColumn={toggleColumn}
        onToggleAllColumns={toggleAllColumns}
      />
        </>
      )}

      {/* Conteúdo da Aba ITIL */}
      {activeTab === 'itil' && (
        <>
          <ITILSummaryChart data={itilSummary} loading={itilLoading} />
          <DataTableTemplate
            config={itilConfig}
            tableData={itilTableData}
            loading={itilTableData.state.loading}
          />
        </>
      )}

      {/* Modal de Detalhes do Card */}
      {selectedCard && (
        <CardDetailModal
          card={selectedCard}
          onClose={() => setSelectedCard(null)}
        />
      )}
    </div>
  );
};

// Componente de Tabela de Cards
const CardsTable = ({ startDate, endDate, columns, selectedColumns, onToggleColumn, onToggleAllColumns }) => {
  const [cards, setCards] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [selectedCard, setSelectedCard] = React.useState(null);
  const [loadingCard, setLoadingCard] = React.useState(false);

  React.useEffect(() => {
    if (selectedColumns.length > 0) {
      fetchCards();
    } else {
      setCards([]);
      setLoading(false);
    }
  }, [startDate, endDate, selectedColumns]);

  const fetchCards = async () => {
    try {
      setLoading(true);
      // Buscar cards concluídos no período com filtro de colunas
      const columnIds = selectedColumns.join(',');
      const url = `/api/v1/kanban/analytics/cards-in-period?start_date=${startDate}&end_date=${endDate}&column_ids=${columnIds}`;
      
      // 🔍 DEBUG
      console.log('🔍 TABELA fetchCards:', { startDate, endDate, columnIds, url });
      
      const response = await api.get(url);
      
      console.log('✅ TABELA resposta:', response.data?.length, 'cards');
      
      setCards(response.data || []);
    } catch (err) {
      console.error("Erro ao carregar cards:", err);
      setCards([]);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'High': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      'Average': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'Low': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
  };

  const handleViewDetails = async (cardId) => {
    try {
      setLoadingCard(true);
      // Buscar card completo com todos os detalhes
      const response = await api.get(`/api/v1/kanban/cards/${cardId}`);
      setSelectedCard(response.data);
    } catch (err) {
      console.error("Erro ao carregar detalhes do card:", err);
    } finally {
      setLoadingCard(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          📋 Cards Concluídos no Período
        </h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Carregando cards...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            📋 Cards Concluídos no Período
          </h2>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {cards.length} {cards.length === 1 ? 'card' : 'cards'}
          </span>
        </div>

        {/* Filtro de Colunas */}
        <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              🔍 Filtrar por Coluna
            </h3>
            <button
              onClick={onToggleAllColumns}
              className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
            >
              {selectedColumns.length === columns.length ? 'Desmarcar Todas' : 'Selecionar Todas'}
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {columns.map((column) => (
              <label
                key={column.ColumnID}
                className="inline-flex items-center px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selectedColumns.includes(column.ColumnID)}
                  onChange={() => onToggleColumn(column.ColumnID)}
                  className="mr-2 h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {column.ColumnName}
                </span>
              </label>
            ))}
          </div>
        </div>

        {cards.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-lg font-medium">Nenhum card encontrado</p>
            <p className="text-sm mt-1">Ajuste os filtros de data ou colunas para ver os resultados</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Card
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Coluna
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Prioridade
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Concluído em
                  </th>
                  <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {cards.map((card) => (
                  <tr 
                    key={card.CardID}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <td className="px-6 py-4 max-w-md">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {card.Title}
                        </span>
                        {card.Description && (
                          <span className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-1">
                            {card.Description}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        {card.ColumnName || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(card.Priority)}`}>
                        {card.Priority || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      {formatDate(card.CompletedDate)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <button
                        onClick={() => handleViewDetails(card.CardID)}
                        disabled={loadingCard}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
                        title="Ver detalhes do card"
                      >
                        {loadingCard ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Carregando...</span>
                          </>
                        ) : (
                          <>
                            <Eye className="w-4 h-4" />
                            <span>Ver Detalhes</span>
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
};

export default KanbanAnalyticsPage;
