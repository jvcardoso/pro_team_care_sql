import React from 'react';
import Card from '../components/ui/Card';
import { User, Wrench, Clock } from 'lucide-react';

const ProfessionalPage = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard Profissional
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Área de trabalho para profissionais da saúde
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <User className="h-8 w-8 text-blue-600" />
          <span className="text-lg font-medium text-gray-900 dark:text-white">
            Profissional
          </span>
        </div>
      </div>

      {/* Cards de Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card
          title="Consultas Hoje"
          className="p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold">0</div>
              <p className="text-xs text-muted-foreground">
                Em construção
              </p>
            </div>
            <Clock className="h-8 w-8 text-gray-400" />
          </div>
        </Card>

        <Card
          title="Pacientes Ativos"
          className="p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold">0</div>
              <p className="text-xs text-muted-foreground">
                Em construção
              </p>
            </div>
            <User className="h-8 w-8 text-gray-400" />
          </div>
        </Card>

        <Card
          title="Funcionalidades"
          className="p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold">🚧</div>
              <p className="text-xs text-muted-foreground">
                Em desenvolvimento
              </p>
            </div>
            <Wrench className="h-8 w-8 text-gray-400" />
          </div>
        </Card>
      </div>

      {/* Área Principal */}
      <Card
        title="Área de Trabalho"
        className="p-6"
      >
        <div className="flex flex-col items-center justify-center py-12">
          <Wrench className="h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Dashboard em Construção
          </h3>
          <p className="text-gray-600 dark:text-gray-400 text-center max-w-md">
            Esta é a área de trabalho do profissional da saúde.
            Funcionalidades como agendamento de consultas, gerenciamento de pacientes
            e relatórios serão implementadas em breve.
          </p>
          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              🔧 <strong>Status:</strong> Página criada e integrada ao sistema de roteamento.
              Próximas implementações incluirão dados reais e funcionalidades completas.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ProfessionalPage;