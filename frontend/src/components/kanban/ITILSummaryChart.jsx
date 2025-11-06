import React from "react";
import { 
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from "recharts";
import { TrendingUp, AlertTriangle, CheckCircle, Clock } from "lucide-react";

/**
 * Componente reutilizável para exibir resumo ITIL
 * Mostra métricas agregadas por categoria ITIL
 */
export const ITILSummaryChart = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <AlertTriangle className="mx-auto h-12 w-12 mb-4" />
        <p>Nenhum dado disponível para o período selecionado</p>
      </div>
    );
  }

  // Cores por categoria ITIL
  const COLORS = {
    'Change': '#3b82f6',        // blue-500
    'Incident': '#ef4444',      // red-500
    'Service Request': '#10b981', // green-500
    'Operation Task': '#f59e0b'  // amber-500
  };

  // Preparar dados para gráfico de pizza
  const pieData = data.map(item => ({
    name: item.itilCategory,
    value: item.totalCards,
    color: COLORS[item.itilCategory] || '#6b7280'
  }));

  // Preparar dados para gráfico de barras (SLA)
  const barData = data.map(item => ({
    name: item.itilCategory,
    sla: parseFloat(item.slaCompliance.toFixed(1)),
    avgCycle: (item.avgCycleTime / 3600).toFixed(1), // Converter para horas
  }));

  // Calcular totais
  const totalCards = data.reduce((sum, item) => sum + item.totalCards, 0);
  const avgSLA = data.reduce((sum, item) => sum + item.slaCompliance, 0) / data.length;
  const highRiskTotal = data.reduce((sum, item) => sum + item.highRiskCount, 0);

  return (
    <div className="space-y-6">
      {/* Cards de Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total de Cards</p>
              <p className="text-3xl font-bold text-gray-900">{totalCards}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">SLA Médio</p>
              <p className="text-3xl font-bold text-green-600">{avgSLA.toFixed(1)}%</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Alto Risco</p>
              <p className="text-3xl font-bold text-red-600">{highRiskTotal}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Categorias</p>
              <p className="text-3xl font-bold text-gray-900">{data.length}</p>
            </div>
            <Clock className="h-8 w-8 text-amber-500" />
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Pizza - Distribuição por Categoria */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Distribuição por Categoria</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Gráfico de Barras - SLA Compliance */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">SLA Compliance por Categoria</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="sla" fill="#10b981" name="SLA (%)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tabela Detalhada */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold">Métricas Detalhadas por Categoria</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Categoria
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tempo Médio
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  SLA %
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Alto Risco
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Janela
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CAB
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Backout
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.map((item) => (
                <tr key={item.itilCategory} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span 
                      className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full"
                      style={{ 
                        backgroundColor: `${COLORS[item.itilCategory]}20`,
                        color: COLORS[item.itilCategory]
                      }}
                    >
                      {item.itilCategory}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.totalCards}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(item.avgCycleTime / 3600).toFixed(1)}h
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${
                      item.slaCompliance >= 90 ? 'text-green-600' :
                      item.slaCompliance >= 70 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {item.slaCompliance.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.highRiskCount}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.withWindow}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.withCAB}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.withBackout}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
