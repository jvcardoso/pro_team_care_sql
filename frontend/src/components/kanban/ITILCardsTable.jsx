import React, { useState } from "react";
import { Eye, Loader2, AlertTriangle, CheckCircle, XCircle } from "lucide-react";

/**
 * Componente reutilizável para exibir tabela de cards ITIL
 * Permite filtrar por categoria e visualizar detalhes
 */
export const ITILCardsTable = ({ cards, loading, onViewDetails }) => {
  const [categoryFilter, setCategoryFilter] = useState("all");

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!cards || cards.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <AlertTriangle className="mx-auto h-12 w-12 mb-4" />
        <p>Nenhum card encontrado para o período selecionado</p>
      </div>
    );
  }

  // Filtrar cards por categoria
  const filteredCards = categoryFilter === "all" 
    ? cards 
    : cards.filter(card => card.itilCategory === categoryFilter);

  // Obter categorias únicas
  const categories = ["all", ...new Set(cards.map(card => card.itilCategory))];

  // Cores por categoria
  const CATEGORY_COLORS = {
    'Change': 'bg-blue-100 text-blue-800',
    'Incident': 'bg-red-100 text-red-800',
    'Service Request': 'bg-green-100 text-green-800',
    'Operation Task': 'bg-amber-100 text-amber-800'
  };

  // Cores por nível de risco
  const RISK_COLORS = {
    'High': 'bg-red-100 text-red-800',
    'Medium': 'bg-yellow-100 text-yellow-800',
    'Low': 'bg-green-100 text-green-800'
  };

  // Formatar data
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  return (
    <div className="space-y-4">
      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">
            Filtrar por Categoria:
          </label>
          <div className="flex gap-2">
            {categories.map(category => (
              <button
                key={category}
                onClick={() => setCategoryFilter(category)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  categoryFilter === category
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category === "all" ? "Todas" : category}
                {category !== "all" && (
                  <span className="ml-2 text-xs">
                    ({cards.filter(c => c.itilCategory === category).length})
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tabela */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold">
            Cards ITIL ({filteredCards.length})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Título
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Categoria ITIL
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Coluna
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risco
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metadados
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  SLA
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conclusão
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredCards.map((card) => (
                <tr key={card.cardId} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {card.externalCardId}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {card.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      CATEGORY_COLORS[card.itilCategory] || 'bg-gray-100 text-gray-800'
                    }`}>
                      {card.itilCategory}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {card.columnName}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      RISK_COLORS[card.riskLevel] || 'bg-gray-100 text-gray-800'
                    }`}>
                      {card.riskLevel}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex gap-1">
                      {card.hasWindow && (
                        <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
                          Janela
                        </span>
                      )}
                      {card.hasCAB && (
                        <span className="px-2 py-1 text-xs bg-indigo-100 text-indigo-800 rounded">
                          CAB
                        </span>
                      )}
                      {card.hasBackout && (
                        <span className="px-2 py-1 text-xs bg-pink-100 text-pink-800 rounded">
                          Backout
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {card.metSLA !== null ? (
                      <div className="flex items-center gap-2">
                        {card.metSLA ? (
                          <>
                            <CheckCircle className="h-5 w-5 text-green-500" />
                            <span className="text-sm text-green-600 font-medium">Atendido</span>
                          </>
                        ) : (
                          <>
                            <XCircle className="h-5 w-5 text-red-500" />
                            <span className="text-sm text-red-600 font-medium">
                              {card.daysLate}d atraso
                            </span>
                          </>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(card.completedDate)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => onViewDetails && onViewDetails(card.cardId)}
                      className="inline-flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm hover:shadow-md"
                    >
                      <Eye className="h-4 w-4" />
                      Ver Detalhes
                    </button>
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
