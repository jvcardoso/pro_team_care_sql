# Implementação Frontend - Módulo de Atividades com IA

**Responsável:** Dev Frontend  
**Tempo Estimado:** 3-4 dias  
**Dependências:** Backend funcionando

---

## 📁 Estrutura de Arquivos

```
frontend/src/
├── pages/
│   ├── ActivitiesPage.jsx (novo)
│   └── PendenciesBoard.jsx (novo)
├── components/
│   ├── activities/
│   │   ├── ActivityForm.jsx (novo)
│   │   ├── ActivityValidationModal.jsx (novo)
│   │   └── ActivityList.jsx (novo)
│   └── pendencies/
│       ├── PendencyCard.jsx (novo)
│       └── PendencyColumn.jsx (novo)
├── services/
│   ├── activityService.js (novo)
│   └── pendencyService.js (novo)
├── hooks/
│   └── useActivities.js (novo)
└── routes/
    └── index.jsx (adicionar rotas)
```

---

## 🎨 Fase 1: Services (API Client)

### `services/activityService.js`
```javascript
import api from './api';

export const activityService = {
  /**
   * Cria nova atividade e recebe sugestões da IA
   */
  async create(data) {
    const response = await api.post('/activities', data);
    return response.data;
  },

  /**
   * Lista atividades da empresa
   */
  async getAll(params = {}) {
    const response = await api.get('/activities', { params });
    return response.data;
  },

  /**
   * Busca atividade por ID
   */
  async getById(id) {
    const response = await api.get(`/activities/${id}`);
    return response.data;
  },

  /**
   * Atualiza atividade
   */
  async update(id, data) {
    const response = await api.put(`/activities/${id}`, data);
    return response.data;
  },

  /**
   * Salva dados validados pelo usuário
   */
  async saveValidatedData(activityId, validatedData) {
    // Salvar entidades
    if (validatedData.pessoas?.length) {
      await Promise.all(
        validatedData.pessoas.map(pessoa =>
          api.post('/activity-entities', {
            ActivityID: activityId,
            EntityType: 'Pessoa',
            EntityName: pessoa
          })
        )
      );
    }

    // Salvar pendências
    if (validatedData.pendencias?.length) {
      await Promise.all(
        validatedData.pendencias.map(pend =>
          api.post('/pendencies', {
            ActivityID: activityId,
            Description: pend.descricao,
            Owner: pend.responsavel,
            Impediment: pend.impedimento
          })
        )
      );
    }

    return { success: true };
  }
};
```

### `services/pendencyService.js`
```javascript
import api from './api';

export const pendencyService = {
  async getAll(params = {}) {
    const response = await api.get('/pendencies', { params });
    return response.data;
  },

  async update(id, data) {
    const response = await api.put(`/pendencies/${id}`, data);
    return response.data;
  },

  async updateStatus(id, status) {
    return this.update(id, { Status: status });
  }
};
```

---

## 🪝 Fase 2: Custom Hook

### `hooks/useActivities.js`
```javascript
import { useState } from 'react';
import { activityService } from '../services/activityService';
import { toast } from 'react-toastify';

export const useActivities = () => {
  const [loading, setLoading] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState(null);
  const [currentActivity, setCurrentActivity] = useState(null);

  /**
   * Cria atividade e abre modal de validação
   */
  const createActivity = async (formData) => {
    setLoading(true);
    try {
      const response = await activityService.create(formData);
      
      // Resposta contém: ActivityID + ai_suggestions
      setCurrentActivity(response);
      setAiSuggestions(response.ai_suggestions);
      
      return response;
    } catch (error) {
      toast.error('Erro ao criar atividade: ' + error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Salva dados validados pelo usuário
   */
  const saveValidatedData = async (validatedData) => {
    setLoading(true);
    try {
      await activityService.saveValidatedData(
        currentActivity.ActivityID,
        validatedData
      );
      
      toast.success('Atividade salva com sucesso!');
      
      // Limpar estado
      setCurrentActivity(null);
      setAiSuggestions(null);
      
      return true;
    } catch (error) {
      toast.error('Erro ao salvar: ' + error.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    aiSuggestions,
    currentActivity,
    createActivity,
    saveValidatedData
  };
};
```

---

## 📝 Fase 3: Componentes

### `components/activities/ActivityForm.jsx`
```jsx
import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Textarea } from '../ui/Textarea';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';

export const ActivityForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    Title: '',
    Status: 'Pendente',
    RawText: '',
    DueDate: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Card>
      <CardHeader>
        <h2 className="text-xl font-bold">Nova Atividade</h2>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Título (obrigatório) */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Título *
            </label>
            <Input
              value={formData.Title}
              onChange={(e) => setFormData({ ...formData, Title: e.target.value })}
              placeholder="Ex: Abertura RDM CHG0076721"
              required
            />
          </div>

          {/* Status (obrigatório) */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Status *
            </label>
            <Select
              value={formData.Status}
              onChange={(e) => setFormData({ ...formData, Status: e.target.value })}
              required
            >
              <option value="Pendente">Pendente</option>
              <option value="Em Andamento">Em Andamento</option>
              <option value="Concluído">Concluído</option>
              <option value="Cancelado">Cancelado</option>
            </Select>
          </div>

          {/* Prazo (opcional) */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Prazo
            </label>
            <Input
              type="datetime-local"
              value={formData.DueDate}
              onChange={(e) => setFormData({ ...formData, DueDate: e.target.value })}
            />
          </div>

          {/* Conteúdo (texto ou imagem) */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Conteúdo (Cole texto ou imagem)
            </label>
            <Textarea
              value={formData.RawText}
              onChange={(e) => setFormData({ ...formData, RawText: e.target.value })}
              placeholder="Cole aqui o texto de um chat, email, ou descrição da atividade..."
              rows={6}
            />
            <p className="text-xs text-gray-500 mt-1">
              💡 A IA analisará este conteúdo e sugerirá pessoas, datas e pendências
            </p>
          </div>

          {/* Botão */}
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? '🤖 Analisando com IA...' : 'Criar e Analisar'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};
```

### `components/activities/ActivityValidationModal.jsx`
```jsx
import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { X, Check, Plus } from 'lucide-react';

export const ActivityValidationModal = ({ 
  isOpen, 
  onClose, 
  aiSuggestions, 
  onSave 
}) => {
  const [validatedData, setValidatedData] = useState({
    pessoas: [],
    sistemas: [],
    tags: [],
    pendencias: []
  });

  useEffect(() => {
    if (aiSuggestions) {
      setValidatedData({
        pessoas: aiSuggestions.pessoas || [],
        sistemas: aiSuggestions.sistemas || [],
        tags: aiSuggestions.tags || [],
        pendencias: aiSuggestions.pendencias || []
      });
    }
  }, [aiSuggestions]);

  const removePessoa = (index) => {
    setValidatedData({
      ...validatedData,
      pessoas: validatedData.pessoas.filter((_, i) => i !== index)
    });
  };

  const addPessoa = () => {
    const nome = prompt('Nome da pessoa:');
    if (nome) {
      setValidatedData({
        ...validatedData,
        pessoas: [...validatedData.pessoas, nome]
      });
    }
  };

  const removePendencia = (index) => {
    setValidatedData({
      ...validatedData,
      pendencias: validatedData.pendencias.filter((_, i) => i !== index)
    });
  };

  const handleSave = () => {
    onSave(validatedData);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Validar Sugestões da IA">
      <div className="space-y-6">
        {/* Pessoas */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">Pessoas Envolvidas</h3>
            <Button size="sm" variant="ghost" onClick={addPessoa}>
              <Plus className="w-4 h-4 mr-1" /> Adicionar
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {validatedData.pessoas.map((pessoa, index) => (
              <Badge key={index} variant="secondary" className="flex items-center gap-1">
                {pessoa}
                <X 
                  className="w-3 h-3 cursor-pointer hover:text-red-500" 
                  onClick={() => removePessoa(index)}
                />
              </Badge>
            ))}
            {validatedData.pessoas.length === 0 && (
              <p className="text-sm text-gray-500">Nenhuma pessoa identificada</p>
            )}
          </div>
        </div>

        {/* Sistemas */}
        <div>
          <h3 className="font-semibold mb-2">Sistemas Mencionados</h3>
          <div className="flex flex-wrap gap-2">
            {validatedData.sistemas.map((sistema, index) => (
              <Badge key={index} variant="outline">
                {sistema}
              </Badge>
            ))}
            {validatedData.sistemas.length === 0 && (
              <p className="text-sm text-gray-500">Nenhum sistema identificado</p>
            )}
          </div>
        </div>

        {/* Tags */}
        <div>
          <h3 className="font-semibold mb-2">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {validatedData.tags.map((tag, index) => (
              <Badge key={index} variant="default">
                {tag}
              </Badge>
            ))}
          </div>
        </div>

        {/* Pendências */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">Pendências Identificadas</h3>
            <Badge variant="destructive">{validatedData.pendencias.length}</Badge>
          </div>
          <div className="space-y-3">
            {validatedData.pendencias.map((pend, index) => (
              <div key={index} className="border rounded p-3 relative">
                <X 
                  className="absolute top-2 right-2 w-4 h-4 cursor-pointer hover:text-red-500" 
                  onClick={() => removePendencia(index)}
                />
                <p className="font-medium">{pend.descricao}</p>
                {pend.responsavel && (
                  <p className="text-sm text-gray-600">
                    👤 Responsável: {pend.responsavel}
                  </p>
                )}
                {pend.impedimento && (
                  <p className="text-sm text-red-600">
                    ⚠️ Impedimento: {pend.impedimento}
                  </p>
                )}
              </div>
            ))}
            {validatedData.pendencias.length === 0 && (
              <p className="text-sm text-gray-500">Nenhuma pendência identificada</p>
            )}
          </div>
        </div>

        {/* Botões */}
        <div className="flex gap-2 pt-4 border-t">
          <Button variant="outline" onClick={onClose} className="flex-1">
            Cancelar
          </Button>
          <Button onClick={handleSave} className="flex-1">
            <Check className="w-4 h-4 mr-2" />
            Salvar Atividade
          </Button>
        </div>
      </div>
    </Modal>
  );
};
```

### `components/pendencies/PendencyCard.jsx`
```jsx
import React from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { User, AlertCircle } from 'lucide-react';

export const PendencyCard = ({ pendency, onClick }) => {
  return (
    <Card 
      className="cursor-pointer hover:shadow-md transition-shadow mb-3"
      onClick={onClick}
    >
      <div className="p-3">
        <p className="font-medium text-sm mb-2">{pendency.Description}</p>
        
        {pendency.Owner && (
          <div className="flex items-center gap-1 text-xs text-gray-600 mb-1">
            <User className="w-3 h-3" />
            {pendency.Owner}
          </div>
        )}
        
        {pendency.Impediment && (
          <div className="flex items-center gap-1 text-xs text-red-600">
            <AlertCircle className="w-3 h-3" />
            {pendency.Impediment}
          </div>
        )}
        
        <Badge variant="secondary" className="mt-2 text-xs">
          {pendency.Status}
        </Badge>
      </div>
    </Card>
  );
};
```

### `components/pendencies/PendencyColumn.jsx`
```jsx
import React from 'react';
import { PendencyCard } from './PendencyCard';

export const PendencyColumn = ({ title, pendencies, onCardClick }) => {
  return (
    <div className="bg-gray-50 rounded-lg p-4 min-w-[300px]">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold">{title}</h3>
        <span className="bg-gray-200 text-gray-700 text-xs font-medium px-2 py-1 rounded">
          {pendencies.length}
        </span>
      </div>
      
      <div className="space-y-2">
        {pendencies.map(pend => (
          <PendencyCard 
            key={pend.PendencyID} 
            pendency={pend}
            onClick={() => onCardClick(pend)}
          />
        ))}
        
        {pendencies.length === 0 && (
          <p className="text-sm text-gray-400 text-center py-4">
            Nenhuma pendência
          </p>
        )}
      </div>
    </div>
  );
};
```

---

## 📄 Fase 4: Pages

### `pages/ActivitiesPage.jsx`
```jsx
import React, { useState } from 'react';
import { ActivityForm } from '../components/activities/ActivityForm';
import { ActivityValidationModal } from '../components/activities/ActivityValidationModal';
import { useActivities } from '../hooks/useActivities';

export const ActivitiesPage = () => {
  const [showValidationModal, setShowValidationModal] = useState(false);
  const { 
    loading, 
    aiSuggestions, 
    createActivity, 
    saveValidatedData 
  } = useActivities();

  const handleCreateActivity = async (formData) => {
    const response = await createActivity(formData);
    if (response) {
      setShowValidationModal(true);
    }
  };

  const handleSaveValidated = async (validatedData) => {
    const success = await saveValidatedData(validatedData);
    if (success) {
      setShowValidationModal(false);
    }
  };

  return (
    <div className="container mx-auto py-6">
      <h1 className="text-2xl font-bold mb-6">Gestão de Atividades</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityForm onSubmit={handleCreateActivity} loading={loading} />
        
        <div>
          {/* Aqui pode adicionar lista de atividades recentes */}
        </div>
      </div>

      <ActivityValidationModal
        isOpen={showValidationModal}
        onClose={() => setShowValidationModal(false)}
        aiSuggestions={aiSuggestions}
        onSave={handleSaveValidated}
      />
    </div>
  );
};
```

### `pages/PendenciesBoard.jsx`
```jsx
import React, { useEffect, useState } from 'react';
import { PendencyColumn } from '../components/pendencies/PendencyColumn';
import { pendencyService } from '../services/pendencyService';
import { toast } from 'react-toastify';

export const PendenciesBoard = () => {
  const [pendencies, setPendencies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPendencies();
  }, []);

  const loadPendencies = async () => {
    try {
      const data = await pendencyService.getAll();
      setPendencies(data);
    } catch (error) {
      toast.error('Erro ao carregar pendências');
    } finally {
      setLoading(false);
    }
  };

  const groupByStatus = (status) => {
    return pendencies.filter(p => p.Status === status);
  };

  const handleCardClick = (pendency) => {
    // Abrir modal com detalhes ou navegar para atividade
    console.log('Clicou em:', pendency);
  };

  if (loading) {
    return <div className="text-center py-12">Carregando...</div>;
  }

  return (
    <div className="container mx-auto py-6">
      <h1 className="text-2xl font-bold mb-6">Board de Pendências</h1>
      
      <div className="flex gap-4 overflow-x-auto pb-4">
        <PendencyColumn
          title="Pendente"
          pendencies={groupByStatus('Pendente')}
          onCardClick={handleCardClick}
        />
        
        <PendencyColumn
          title="Cobrado"
          pendencies={groupByStatus('Cobrado')}
          onCardClick={handleCardClick}
        />
        
        <PendencyColumn
          title="Resolvido"
          pendencies={groupByStatus('Resolvido')}
          onCardClick={handleCardClick}
        />
      </div>
    </div>
  );
};
```

---

## 🛣️ Fase 5: Rotas

### `routes/index.jsx` (adicionar)
```jsx
import { ActivitiesPage } from '../pages/ActivitiesPage';
import { PendenciesBoard } from '../pages/PendenciesBoard';

// Adicionar nas rotas protegidas
{
  path: '/atividades',
  element: <ActivitiesPage />,
},
{
  path: '/pendencias',
  element: <PendenciesBoard />,
}
```

---

## ✅ Checklist

- [ ] Criar services (activityService, pendencyService)
- [ ] Criar hook useActivities
- [ ] Criar ActivityForm
- [ ] Criar ActivityValidationModal
- [ ] Criar PendencyCard
- [ ] Criar PendencyColumn
- [ ] Criar ActivitiesPage
- [ ] Criar PendenciesBoard
- [ ] Adicionar rotas
- [ ] Testar fluxo completo
- [ ] Adicionar menu lateral com links

---

## 🎨 Melhorias Futuras

- Drag & drop no board Kanban
- Upload de imagens
- Busca e filtros avançados
- Notificações de prazos
- Relatórios e dashboards
