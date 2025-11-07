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
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
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
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
            Filtrar por Categoria:
          </label>
          <div className="flex flex-wrap gap-2">
            {categories.map(category => (
              <button
                key={category}
                onClick={() => setCategoryFilter(category)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  categoryFilter === category
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
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

      {/* Visualização em Cards (Mobile) */}
      <div className="lg:hidden space-y-3">
        {filteredCards.map((card) => (
          <div key={card.cardId} className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 space-y-3">
            {/* Header do Card */}
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{card.externalCardId}</p>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 line-clamp-2">
                  {card.title}
                </h4>
              </div>
              <button
                onClick={() => onViewDetails && onViewDetails(card.cardId)}
                className="flex-shrink-0 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Eye className="h-4 w-4" />
              </button>
            </div>

            {/* Badges */}
            <div className="flex flex-wrap gap-2">
              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                CATEGORY_COLORS[card.itilCategory] || 'bg-gray-100 text-gray-800'
              }`}>
                {card.itilCategory}
              </span>
              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                {card.columnName}
              </span>
              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                RISK_COLORS[card.riskLevel] || 'bg-gray-100 text-gray-800'
              }`}>
                {card.riskLevel}
              </span>
            </div>

            {/* Metadados */}
            {(card.hasWindow || card.hasCAB || card.hasBackout) && (
              <div className="flex flex-wrap gap-1">
                {card.hasWindow && (
                  <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">🪟 Janela</span>
                )}
                {card.hasCAB && (
                  <span className="px-2 py-1 text-xs bg-indigo-100 text-indigo-800 rounded">👥 CAB</span>
                )}
                {card.hasBackout && (
                  <span className="px-2 py-1 text-xs bg-cyan-100 text-cyan-800 rounded">🔄 Backout</span>
                )}
              </div>
            )}

            {/* SLA e Data */}
            <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
              <div>
                {card.metSLA !== null && (
                  <div className="flex items-center gap-1">
                    {card.metSLA ? (
                      <CheckCircle className="h-3 w-3 text-green-600" />
                    ) : (
                      <XCircle className="h-3 w-3 text-red-600" />
                    )}
                    <span>{card.metSLA ? 'SLA OK' : `${card.daysLate}d atraso`}</span>
                  </div>
                )}
              </div>
              <div>
                {card.completedDate && (
                  <span>Concluído: {formatDate(card.completedDate)}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Tabela (Desktop) */}
      <div className="hidden lg:block bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-gray-100">
            Cards ITIL ({filteredCards.length})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-3 sm:px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                  ID
                </th>
                <th className="px-3 sm:px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                  Título
                </th>
                <th className="px-3 sm:px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                  Categoria ITIL
                </th>
                <th className="px-3 sm:px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                  Coluna
                </th>
                <th className="px-3 sm:px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                  Risco
                </th>
                <th className="px-3 sm:px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                  Metadados
                </th>
                <th className="px-3 sm:px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                  SLA
                </th>
                <th className="px-3 sm:px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                  Conclusão
                </th>
                <th className="px-3 sm:px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredCards.map((card) => (
                <tr key={card.cardId} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-3 sm:px-4 lg:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-gray-900 dark:text-gray-100">
                    {card.externalCardId}
                  </td>
                  <td className="px-3 sm:px-4 lg:px-6 py-3 sm:py-4 text-xs sm:text-sm text-gray-900 dark:text-gray-100 max-w-[200px] sm:max-w-xs truncate">
                    {card.title}
                  </td>
                  <td className="px-3 sm:px-4 lg:px-6 py-3 sm:py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      CATEGORY_COLORS[card.itilCategory] || 'bg-gray-100 text-gray-800'
                    }`}>
                      {card.itilCategory}
                    </span>
                  </td>
                  <td className="px-3 sm:px-4 lg:px-6 py-3 sm:py-4 whitespace-nowrap">
                    <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {card.columnName}
                    </span>
                  </td>
                  <td className="px-3 sm:px-4 lg:px-6 py-3 sm:py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      RISK_COLORS[card.riskLevel] || 'bg-gray-100 text-gray-800'
                    }`}>
                      {card.riskLevel}
                    </span>
                  </td>
                  <td className="px-3 sm:px-4 lg:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-900">
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
                   <td className="px-3 sm:px-4 lg:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-900 dark:text-gray-100">
                     {formatDate(card.completedDate)}
                   </td>
                   <td className="px-3 sm:px-4 lg:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm">
                     <button
                       onClick={() => onViewDetails && onViewDetails(card.cardId)}
                       className="inline-flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1.5 sm:py-2 bg-blue-600 text-white text-xs sm:text-sm rounded-lg hover:bg-blue-700 transition-colors shadow-sm hover:shadow-md"
                     >
                       <Eye className="h-3 w-3 sm:h-4 sm:w-4" />
                       <span className="hidden sm:inline">Ver Detalhes</span>
                       <span className="sm:hidden">Ver</span>
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
