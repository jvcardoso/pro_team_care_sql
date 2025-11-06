/**
 * Service para o sistema Kanban Board
 */

import api from './api';

// ============================================================================
// Types
// ============================================================================

export interface CardColumn {
  ColumnID: number;
  ColumnName: string;
  DisplayOrder: number;
  Color: string;
  IsActive: boolean;
  CompanyID: number;
  CreatedAt: string;
}

export interface Card {
  CardID: number;
  CompanyID: number;
  UserID: number;
  ColumnID: number;
  Title: string;
  Description: string | null;
  OriginalText: string | null;
  SubStatus: string | null;
  Priority: string;
  StartDate: string | null;
  DueDate: string | null;
  CompletedDate: string | null;
  CreatedAt: string;
  IsDeleted: boolean;
}

export interface CardMovement {
  MovementID: number;
  CardID: number;
  UserID: number;
  LogDate: string;
  Subject: string;
  Description: string | null;
  TimeSpent: number | null;
  MovementType: string | null;
  OldColumnID: number | null;
  NewColumnID: number | null;
  OldSubStatus: string | null;
  NewSubStatus: string | null;
  images?: MovementImage[];
}

export interface CardAssignee {
  AssigneeID: number;
  CardID: number;
  PersonName: string;
  PersonID: number | null;
  AssignedAt: string;
}

export interface CardTag {
  CardTagID: number;
  CardID: number;
  TagName: string;
  TagColor: string | null;
  CreatedAt: string;
}

export interface CardImage {
  CardImageID: number;
  CardID: number;
  ImagePath: string;
  ImageType: string;
  Description: string;
  UploadedBy: number;
  UploadedAt: string;
}

export interface MovementImage {
  MovementImageID: number;
  MovementID: number;
  ImagePath: string;
  ImageType: string;
  Description: string;
  AIAnalysis?: string;
  UploadedAt: string;
}

export interface CardWithDetails extends Card {
  assignees: CardAssignee[];
  tags: CardTag[];
  movements: CardMovement[];
  images: CardImage[];
  total_time_spent: number | null;
}

export interface CardWithAI extends Card {
  ai_suggestions: {
    description: string;
    assignees: string[];
    systems: string[];
    tags: string[];
    priority: string;
    sub_status: string | null;
    due_date: string | null;
    movements: Array<{
      subject: string;
      description: string;
      estimated_time: number | null;
      assignee: string | null;
    }>;
  };
}

export interface Board {
  columns: CardColumn[];
  cards_by_column: Record<number, Card[]>;
}

export interface CardCreateData {
  Title: string;
  OriginalText: string;
  ColumnID?: number;
  Priority?: string;
  DueDate?: string | null;
}

export interface ValidatedCardData {
  description?: string;
  assignees?: string[];
  systems?: string[];
  tags?: string[];
  priority?: string;
  sub_status?: string | null;
  due_date?: string | null;
  movements?: Array<{
    subject: string;
    description: string;
    estimated_time: number | null;
    assignee: string | null;
  }>;
}

export interface MovementCreateData {
  Subject: string;
  Description?: string;
  TimeSpent?: number;
}

// ============================================================================
// API Calls
// ============================================================================

/**
 * Busca board completo com colunas e cards
 */
export const getBoard = async (): Promise<Board> => {
  const response = await api.get('/api/v1/kanban/board');
  return response.data;
};



/**
 * Lista colunas do board
 */
export const getColumns = async (): Promise<CardColumn[]> => {
  const response = await api.get('/api/v1/kanban/columns');
  return response.data;
};

/**
 * Cria card com análise da IA
 */
export const createCard = async (data: CardCreateData): Promise<CardWithAI> => {
  const response = await api.post('/api/v1/kanban/cards', data);
  return response.data;
};

/**
 * Lista cards
 */
export const listCards = async (
  columnId?: number,
  skip: number = 0,
  limit: number = 100
): Promise<Card[]> => {
  const params: any = { skip, limit };
  if (columnId) params.column_id = columnId;
  
  const response = await api.get('/api/v1/kanban/cards', { params });
  return response.data;
};

/**
 * Busca card com detalhes
 */
export const getCard = async (cardId: number): Promise<CardWithDetails> => {
  const response = await api.get(`/api/v1/kanban/cards/${cardId}`);
  return response.data;
};

/**
 * Atualiza card
 */
export const updateCard = async (
  cardId: number,
  data: Partial<Card>
): Promise<Card> => {
  const response = await api.put(`/api/v1/kanban/cards/${cardId}`, data);
  return response.data;
};

/**
 * Deleta card
 */
export const deleteCard = async (cardId: number): Promise<void> => {
  await api.delete(`/api/v1/kanban/cards/${cardId}`);
};

/**
 * Move card para outra coluna (drag & drop)
 */
export const moveCard = async (
  cardId: number,
  newColumnId: number,
  newPosition?: number
): Promise<Card> => {
  const response = await api.post(`/api/v1/kanban/cards/${cardId}/move`, {
    CardID: cardId,
    NewColumnID: newColumnId,
    NewDisplayOrder: newPosition
  });
  return response.data;
};

/**
 * Salva dados validados após análise da IA
 */
export const saveValidatedData = async (
  cardId: number,
  validatedData: ValidatedCardData
): Promise<void> => {
  await api.post(`/api/v1/kanban/cards/${cardId}/validate`, validatedData);
};

/**
 * Adiciona movimento/lançamento ao card
 */
export const addMovement = async (
  cardId: number,
  data: MovementCreateData
): Promise<CardMovement> => {
  const response = await api.post(`/api/v1/kanban/cards/${cardId}/movements`, data);
  return response.data;
};

/**
 * Atualiza movimento/lançamento
 */
export const updateMovement = async (
  movementId: number,
  data: MovementCreateData
): Promise<CardMovement> => {
  // Remove campos undefined/null para não enviar no request
  const cleanData = Object.fromEntries(
    Object.entries(data).filter(([_, value]) => value !== undefined && value !== null)
  );
  const response = await api.put(`/api/v1/kanban/movements/${movementId}`, cleanData);
  return response.data;
};

/**
 * Deleta movimento/lançamento
 */
export const deleteMovement = async (movementId: number): Promise<void> => {
  await api.delete(`/api/v1/kanban/movements/${movementId}`);
};

/**
 * Marca card como concluído
 */
export const completeCard = async (cardId: number): Promise<Card> => {
  const response = await api.post(`/api/v1/kanban/cards/${cardId}/complete`);
  return response.data;
};

/**
 * Adiciona tag ao card
 */
export const addTag = async (cardId: number, tagName: string): Promise<void> => {
  await api.post(`/api/v1/kanban/cards/${cardId}/tags`, {
    TagName: tagName
  });
};

/**
 * Remove tag do card
 */
export const removeTag = async (tagId: number): Promise<void> => {
  await api.delete(`/api/v1/kanban/tags/${tagId}`);
};

// ============================================================================
// Export
// ============================================================================

export const kanbanService = {
  getBoard,
  getColumns,
  createCard,
  listCards,
  getCard,
  updateCard,
  deleteCard,
  moveCard,
  saveValidatedData,
  addMovement,
  updateMovement,
  deleteMovement,
  completeCard,
  addTag,
  removeTag
};
