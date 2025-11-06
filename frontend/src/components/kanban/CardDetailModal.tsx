/**
 * Modal de detalhes do card com histórico de movimentos
 */

import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useKanban } from '../../hooks/useKanban';
import { Card, CardWithDetails, MovementCreateData } from '../../services/kanbanService';
import { CardEditForm } from './CardEditForm';
import { kanbanService } from '../../services/kanbanService';
import { API_BASE_URL } from '../../config/http';

type TabType = 'details' | 'images' | 'movements';
import { ImageUpload } from './ImageUpload';
import { ImageGallery } from './ImageGallery';
import { ImageUploadWithAI } from './ImageUploadWithAI';
import { RichTextEditor } from '../common/RichTextEditor';
import MDEditor from '@uiw/react-md-editor';

interface CardDetailModalProps {
  card: Card;
  onClose: () => void;
}

export const CardDetailModal: React.FC<CardDetailModalProps> = ({ card, onClose }) => {
  const { getCard, addMovement, updateCard, loading } = useKanban();
  const [cardDetails, setCardDetails] = useState<CardWithDetails | null>(null);
  const [showAddMovement, setShowAddMovement] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('details');
  const [editingMovementId, setEditingMovementId] = useState<number | null>(null);
  const [movementToDelete, setMovementToDelete] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({
    Title: card.Title,
    Description: card.Description || '',
    DueDate: card.DueDate ? card.DueDate.substring(0, 16) : '',
    Priority: card.Priority
  });
  const [newTag, setNewTag] = useState('');
  const [movementForm, setMovementForm] = useState<MovementCreateData>({
    Subject: '',
    Description: '',
    TimeSpent: undefined
  });

  useEffect(() => {
    loadCardDetails();
  }, [card.CardID]);

  // Fechar modal de imagem com ESC
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && selectedImage) {
        setSelectedImage(null);
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [selectedImage]);

  const loadCardDetails = async () => {
    const details = await getCard(card.CardID);
    if (details) {
      setCardDetails(details);
    }
  };

  const handleAddMovement = async (e: React.FormEvent) => {
    e.preventDefault();

    const success = await addMovement(card.CardID, movementForm);

    if (success) {
      setMovementForm({ Subject: '', Description: '', TimeSpent: undefined });
      setShowAddMovement(false);
      await loadCardDetails();
    }
  };

  const handleSaveEdit = async () => {
    const success = await updateCard(card.CardID, {
      Title: editForm.Title,
      Description: editForm.Description,
      Priority: editForm.Priority,
      DueDate: editForm.DueDate ? new Date(editForm.DueDate).toISOString() : null
    } as any);

    if (success) {
      setIsEditing(false);
      await loadCardDetails();
    }
  };

  const handleAddTag = async () => {
    if (!newTag.trim()) return;

    try {
      await kanbanService.addTag(card.CardID, newTag.trim());
      setNewTag('');
      await loadCardDetails();
    } catch (error) {
      console.error('Erro ao adicionar tag:', error);
    }
  };

  const handleRemoveTag = async (tagId: number) => {
    try {
      await kanbanService.removeTag(tagId);
      await loadCardDetails();
    } catch (error) {
      console.error('Erro ao remover tag:', error);
    }
  };

  const handleDelete = async () => {
    try {
      await kanbanService.deleteCard(card.CardID);
      onClose();
      window.location.reload();
    } catch (error) {
      console.error('Erro ao deletar card:', error);
      alert('Erro ao deletar card. Tente novamente.');
    }
  };

  const handleEditMovement = (movementId: number, movement: any) => {
    setEditingMovementId(movementId);
    setMovementForm({
      Subject: movement.Subject,
      Description: movement.Description || '',
      TimeSpent: movement.TimeSpent || undefined
    });
    setShowAddMovement(false);
  };

  const handleUpdateMovement = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingMovementId) return;

    // Validação: Subject não pode ser vazio
    if (!movementForm.Subject.trim()) {
      alert('O assunto do movimento é obrigatório.');
      return;
    }

    try {
      await kanbanService.updateMovement(editingMovementId, movementForm);
      setEditingMovementId(null);
      setMovementForm({ Subject: '', Description: '', TimeSpent: undefined });
      await loadCardDetails();
    } catch (error) {
      console.error('Erro ao atualizar movimento:', error);
      alert('Erro ao atualizar movimento. Tente novamente.');
    }
  };

  const handleDeleteMovement = async () => {
    if (!movementToDelete) return;

    try {
      await kanbanService.deleteMovement(movementToDelete);
      setMovementToDelete(null);
      await loadCardDetails();
    } catch (error) {
      console.error('Erro ao deletar movimento:', error);
      alert('Erro ao deletar movimento. Tente novamente.');
    }
  };

  const formatTime = (minutes: number | null) => {
    if (!minutes) return '-';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}min` : `${mins}min`;
  };

  if (!cardDetails) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
          <p className="text-gray-600 dark:text-gray-400">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {cardDetails.Title}
            </h2>
            <div className="flex items-center gap-3">
              <span className={`
                inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
                ${cardDetails.Priority === 'Urgente' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                  cardDetails.Priority === 'Alta' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                  cardDetails.Priority === 'Média' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                  'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'}
              `}>
                {cardDetails.Priority}
              </span>
              {cardDetails.SubStatus && (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {cardDetails.SubStatus}
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
              title="Editar card"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
              title="Deletar card"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('details')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'details'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📋 Detalhes
            </button>
            <button
              onClick={() => setActiveTab('images')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'images'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              🖼️ Imagens
            </button>
            <button
              onClick={() => setActiveTab('movements')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'movements'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📝 Movimentos ({cardDetails.movements?.length || 0})
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Edit Form */}
          {isEditing && (
            <CardEditForm
              editForm={editForm}
              onChange={(field, value) => setEditForm(prev => ({ ...prev, [field]: value }))}
              onSave={handleSaveEdit}
              onCancel={() => setIsEditing(false)}
              loading={loading}
            />
          )}

          {activeTab === 'details' && !isEditing && (
            <div className="space-y-6">
               {/* Description */}
               {cardDetails.Description && (
                 <div>
                   <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                     📝 Descrição
                   </h3>
                   <div className="rich-text-editor" data-color-mode="auto">
                     <MDEditor
                       value={cardDetails.Description}
                       preview="preview"
                       hideToolbar={true}
                       height={200}
                       commands={[]}
                     />
                   </div>
                 </div>
               )}

              {/* Info Grid */}
              <div className="grid grid-cols-2 gap-4">
                {/* Dates */}
                <div>
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    📅 Criado em
                  </h4>
                  <p className="text-gray-900 dark:text-white">
                    {format(new Date(cardDetails.CreatedAt), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                  </p>
                </div>
                {cardDetails.DueDate && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                      ⏰ Prazo
                    </h4>
                    <p className="text-gray-900 dark:text-white">
                      {format(new Date(cardDetails.DueDate), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                    </p>
                  </div>
                )}
                {/* Total Time */}
                <div>
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    ⏱️ Tempo Total
                  </h4>
                  <p className="text-gray-900 dark:text-white">
                    {formatTime(cardDetails.total_time_spent)}
                  </p>
                </div>
              </div>

              {/* Assignees */}
              {cardDetails.assignees && cardDetails.assignees.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    👥 Envolvidos
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {cardDetails.assignees.map((assignee) => (
                      <span
                        key={assignee.AssigneeID}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                      >
                        {assignee.PersonName}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Tags */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  🏷️ Tags
                </h3>
                <div className="flex flex-wrap gap-2 mb-3">
                  {cardDetails.tags && cardDetails.tags.length > 0 ? (
                    cardDetails.tags.map((tag) => (
                      <span
                        key={tag.CardTagID}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 group"
                      >
                        {tag.TagName}
                        <button
                          onClick={() => handleRemoveTag(tag.CardTagID)}
                          className="ml-2 text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-200"
                          title="Remover tag"
                        >
                          ×
                        </button>
                      </span>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma tag adicionada</p>
                  )}
                </div>
                {/* Add Tag */}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                    placeholder="Nova tag..."
                    className="flex-1 rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                  <button
                    onClick={handleAddTag}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                  >
                    Adicionar
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'images' && (
            <div className="space-y-6">
              <ImageUploadWithAI
                cardId={card.CardID}
                onImageProcessed={loadCardDetails}
                context="card do quadro kanban"
              />

              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  🖼️ Imagens do Card
                </h3>
                <ImageGallery
                  images={cardDetails.images || []}
                  onDelete={loadCardDetails}
                  type="card"
                />
              </div>
            </div>
          )}

          {activeTab === 'movements' && (
            <div className="space-y-6">
              {/* Add Movement Button */}
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  📋 Movimentos Internos ({cardDetails.movements?.length || 0})
                </h3>
                {!editingMovementId && (
                  <button
                    onClick={() => setShowAddMovement(!showAddMovement)}
                    className="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Adicionar Lançamento
                  </button>
                )}
              </div>

              {/* Add/Edit Movement Form */}
              {(showAddMovement || editingMovementId) && (
                <form onSubmit={editingMovementId ? handleUpdateMovement : handleAddMovement} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Assunto *
                    </label>
                    <input
                      type="text"
                      value={movementForm.Subject}
                      onChange={(e) => setMovementForm(prev => ({ ...prev, Subject: e.target.value }))}
                      required
                      className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      placeholder="Ex: Reunião com cliente"
                    />
                  </div>
                   <div>
                     <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                       Descrição
                     </label>
                     <RichTextEditor
                       value={movementForm.Description || ''}
                       onChange={(value) => setMovementForm(prev => ({ ...prev, Description: value }))}
                       placeholder="Descreva o movimento com texto formatado..."
                       minHeight="120px"
                     />
                   </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Tempo gasto (minutos)
                    </label>
                    <input
                      type="number"
                      value={movementForm.TimeSpent || ''}
                      onChange={(e) => setMovementForm(prev => ({ ...prev, TimeSpent: e.target.value ? parseInt(e.target.value) : undefined }))}
                      min="0"
                      className="w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      placeholder="Ex: 30"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setShowAddMovement(false);
                        setEditingMovementId(null);
                        setMovementForm({ Subject: '', Description: '', TimeSpent: undefined });
                      }}
                      className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                    >
                      Cancelar
                    </button>
                    <button
                      type="submit"
                      disabled={loading}
                      className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                    >
                      {loading ? 'Salvando...' : editingMovementId ? 'Atualizar' : 'Salvar'}
                    </button>
                  </div>
                </form>
              )}

              {/* Movements List */}
              <div className="space-y-3">
                {cardDetails.movements && cardDetails.movements.length > 0 ? (
                  cardDetails.movements.map((movement) => (
                    <div
                      key={movement.MovementID}
                      className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4"
                    >
                      {/* Movement with Images - Layout Lateral */}
                      {movement.images && movement.images.length > 0 ? (
                        <div className="flex gap-4">
                          {/* Miniatura à esquerda */}
                          <div className="flex-shrink-0">
                            {movement.images.map((image) => {
                              const imageUrl = `${API_BASE_URL}/uploads/kanban/${image.ImagePath.split('/').pop() || image.ImagePath.split('\\').pop()}`;
                              return (
                                <img
                                  key={image.MovementImageID}
                                  src={imageUrl}
                                  alt={image.Description || 'Imagem'}
                                  className="w-24 h-24 object-cover rounded-lg cursor-pointer hover:opacity-90 transition-all border-2 border-gray-300 hover:border-blue-500"
                                  onClick={() => setSelectedImage(imageUrl)}
                                  title="Clique para ampliar"
                                />
                              );
                            })}
                          </div>

                          {/* Conteúdo à direita */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                                <span className="text-blue-500" title="Movimento com imagem">📸</span>
                                {movement.Subject}
                              </h4>
                              <div className="flex items-center gap-2">
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                  {format(new Date(movement.LogDate), "dd/MM/yyyy HH:mm", { locale: ptBR })}
                                </span>
                                {movement.MovementType !== 'Created' && movement.MovementType !== 'ColumnChange' && movement.MovementType !== 'Completed' && (
                                  <>
                                    <button
                                      onClick={() => handleEditMovement(movement.MovementID, movement)}
                                      className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 p-1"
                                      title="Editar movimento"
                                    >
                                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                      </svg>
                                    </button>
                                    <button
                                      onClick={() => setMovementToDelete(movement.MovementID)}
                                      className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 p-1"
                                      title="Deletar movimento"
                                    >
                                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                      </svg>
                                    </button>
                                  </>
                                )}
                              </div>
                            </div>

                            {/* Descrição do usuário */}
                            {movement.images[0]?.Description && (
                              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                {movement.images[0].Description}
                              </p>
                            )}

                            {/* Análise da IA */}
                            {movement.images[0]?.AIAnalysis && (
                              <p className="text-sm text-gray-600 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 p-2 rounded">
                                🤖 {movement.images[0].AIAnalysis}
                              </p>
                            )}

                            {/* Descrição do movimento */}
                            {movement.Description && (
                              <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                                {movement.Description}
                              </p>
                            )}

                            <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                              {movement.TimeSpent && (
                                <span>⏱️ {formatTime(movement.TimeSpent)}</span>
                              )}
                              {movement.MovementType && (
                                <span className="px-2 py-1 bg-gray-200 dark:bg-gray-600 rounded">
                                  {movement.MovementType}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      ) : (
                        /* Movement without Images - Layout Normal */
                        <>
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {movement.Subject}
                            </h4>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {format(new Date(movement.LogDate), "dd/MM/yyyy HH:mm", { locale: ptBR })}
                              </span>
                              {movement.MovementType !== 'Created' && movement.MovementType !== 'ColumnChange' && movement.MovementType !== 'Completed' && (
                                <>
                                  <button
                                    onClick={() => handleEditMovement(movement.MovementID, movement)}
                                    className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 p-1"
                                    title="Editar movimento"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                    </svg>
                                  </button>
                                  <button
                                    onClick={() => setMovementToDelete(movement.MovementID)}
                                    className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 p-1"
                                    title="Deletar movimento"
                                  >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                  </button>
                                </>
                              )}
                            </div>
                          </div>
                          {movement.Description && (
                            <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                              {movement.Description}
                            </p>
                          )}
                          <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                            {movement.TimeSpent && (
                              <span>⏱️ {formatTime(movement.TimeSpent)}</span>
                            )}
                            {movement.MovementType && (
                              <span className="px-2 py-1 bg-gray-200 dark:bg-gray-600 rounded">
                                {movement.MovementType}
                              </span>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                    Nenhum movimento registrado ainda
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 p-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
          >
            Fechar
          </button>
        </div>
      </div>

      {/* Modal de Confirmação de Exclusão */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Confirmar Exclusão
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Esta ação não pode ser desfeita
                </p>
              </div>
            </div>

            <p className="text-gray-700 dark:text-gray-300 mb-6">
              Tem certeza que deseja deletar o card <strong>"{card.Title}"</strong>?
            </p>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Cancelar
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
              >
                Deletar Card
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Confirmação de Exclusão de Movimento */}
      {movementToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Confirmar Exclusão
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Esta ação não pode ser desfeita
                </p>
              </div>
            </div>

            <p className="text-gray-700 dark:text-gray-300 mb-6">
              Tem certeza que deseja deletar este movimento?
            </p>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setMovementToDelete(null)}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Cancelar
              </button>
              <button
                onClick={handleDeleteMovement}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
              >
                Deletar Movimento
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Visualização de Imagem */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center z-[60] p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-7xl max-h-full">
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute -top-12 right-0 text-white bg-black bg-opacity-50 rounded-full p-3 hover:bg-opacity-70"
              title="Fechar (ESC)"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <img
              src={selectedImage}
              alt="Visualização"
              className="max-w-full max-h-[90vh] object-contain rounded-lg shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            />

            <div className="absolute -bottom-12 left-0 right-0 text-center text-white text-sm">
              <p>Clique fora da imagem ou pressione ESC para fechar</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};