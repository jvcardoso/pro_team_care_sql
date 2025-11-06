/**
 * Modal de Importação de Cards do BusinessMap (CSV ou XLSX)
 */

import React, { useState } from 'react';
import { api } from '../../services/api';

interface ImportBMModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export const ImportBMModal: React.FC<ImportBMModalProps> = ({ onClose, onSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState<{
    total: number;
    processed: number;
    created: number;
    updated: number;
    errors: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validar se é CSV ou XLSX
      const fileName = selectedFile.name.toLowerCase();
      if (!fileName.endsWith('.csv') && !fileName.endsWith('.xlsx')) {
        setError('Por favor, selecione um arquivo CSV ou XLSX');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleImport = async () => {
    if (!file) {
      setError('Selecione um arquivo CSV ou XLSX');
      return;
    }

    console.log('🚀 Iniciando importação...');
    console.log('📁 Arquivo selecionado:', file.name, file.size, 'bytes');

    try {
      setLoading(true);
      setError(null);
      setProgress(null);

      const formData = new FormData();
      formData.append('file', file);

      console.log('📤 Enviando FormData...');
      console.log('📋 Conteúdo do FormData:', Array.from(formData.entries()));

      // Verificar se o arquivo está no FormData
      const fileInFormData = formData.get('file');
      console.log('📁 Arquivo no FormData:', fileInFormData);

      // Detectar endpoint baseado na extensão do arquivo
      const endpoint = file.name.toLowerCase().endsWith('.xlsx')
        ? '/api/v1/kanban/import-bm-xlsx'
        : '/api/v1/kanban/import-bm';
      
      console.log('🎯 Endpoint:', endpoint);

      // IMPORTANTE: Não definir headers - o interceptor cuida disso
      // O browser define automaticamente o Content-Type com boundary para FormData
      const response = await api.post(endpoint, formData);

      console.log('✅ Resposta recebida:', response.data);

      setProgress(response.data);

      // Aguardar 2 segundos para mostrar resultado
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 2000);

    } catch (err: any) {
      console.error('❌ Erro na importação:', err);
      console.error('📋 Detalhes do erro:', err.response?.data);
      setError(err.response?.data?.detail || 'Erro ao importar arquivo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            📥 Importar Cards do BusinessMap
          </h2>
          <button
            onClick={onClose}
            disabled={loading}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 disabled:opacity-50"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="p-6">
          {/* Instruções */}
          <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-2">
              ℹ️ Instruções
            </h3>
            <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1 list-disc list-inside">
              <li>Exporte do BusinessMap em CSV ou XLSX</li>
              <li>✅ XLSX recomendado (melhor suporte a multilinha)</li>
              <li>CSV deve usar separador ";"</li>
              <li>Cards existentes serão atualizados</li>
              <li>Novos cards serão criados automaticamente</li>
            </ul>
          </div>

          {/* Upload de Arquivo */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Arquivo CSV ou XLSX
            </label>
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <svg className="w-10 h-10 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-semibold">Clique para selecionar</span> ou arraste o arquivo
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {file ? file.name : 'CSV ou XLSX do BusinessMap'}
                  </p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept=".csv,.xlsx"
                  onChange={handleFileChange}
                  disabled={loading}
                />
              </label>
            </div>
          </div>

          {/* Erro */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-300">
                ❌ {error}
              </p>
            </div>
          )}

          {/* Progresso */}
          {progress && (
            <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <h3 className="text-sm font-semibold text-green-900 dark:text-green-200 mb-2">
                ✅ Importação Concluída!
              </h3>
              <div className="grid grid-cols-2 gap-3 text-sm text-green-800 dark:text-green-300">
                <div>
                  <span className="font-medium">Total:</span> {progress.total} cards
                </div>
                <div>
                  <span className="font-medium">Processados:</span> {progress.processed}
                </div>
                <div>
                  <span className="font-medium">Criados:</span> {progress.created}
                </div>
                <div>
                  <span className="font-medium">Atualizados:</span> {progress.updated}
                </div>
                {progress.errors > 0 && (
                  <div className="col-span-2 text-red-600 dark:text-red-400">
                    <span className="font-medium">Erros:</span> {progress.errors}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="mb-4 flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
              <span className="text-gray-600 dark:text-gray-400">
                Importando cards...
              </span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-end gap-3">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleImport}
            disabled={!file || loading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Importando...' : 'Importar'}
          </button>
        </div>
      </div>
    </div>
  );
};
