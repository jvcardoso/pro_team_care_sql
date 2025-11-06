/**
 * Hook para gerenciar estado do Kanban Board
 */

import { useState, useCallback } from 'react';
import { useToast } from '@/components/ui/use-toast';
import {
  kanbanService,
  Board,
  Card,
  CardWithAI,
  CardWithDetails,
  CardCreateData,
  ValidatedCardData,
  MovementCreateData
} from '../services/kanbanService';



interface KanbanState {
  board: Board | null;
  loading: boolean;
  error: string | null;
  currentCard: CardWithDetails | null;
  aiSuggestions: any;
}

export const useKanban = () => {
  const { toast } = useToast();
  const [state, setState] = useState<KanbanState>({
    board: null,
    loading: false,
    error: null,
    currentCard: null,
    aiSuggestions: null
  });

  /**
   * Carrega board completo
   */
  const loadBoard = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const board = await kanbanService.getBoard();
      setState(prev => ({ ...prev, board, loading: false }));
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao carregar board';
      setState(prev => ({ ...prev, loading: false, error: errorMsg }));

      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });
    }
  }, [toast]);



  /**
   * Cria card com IA
   */
  const createCard = useCallback(async (data: CardCreateData): Promise<CardWithAI | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const result = await kanbanService.createCard(data);
      
      setState(prev => ({
        ...prev,
        loading: false,
        aiSuggestions: result.ai_suggestions
      }));

      toast({
        title: 'Sucesso!',
        description: 'Card criado e analisado pela IA.',
        variant: 'default'
      });

      return result;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao criar card';
      
      setState(prev => ({ ...prev, loading: false, error: errorMsg }));
      
      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return null;
    }
  }, [toast]);

  /**
   * Salva dados validados
   */
  const saveValidatedData = useCallback(async (
    cardId: number,
    validatedData: ValidatedCardData
  ): Promise<boolean> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      await kanbanService.saveValidatedData(cardId, validatedData);
      
      setState(prev => ({
        ...prev,
        loading: false,
        aiSuggestions: null
      }));

      toast({
        title: 'Sucesso!',
        description: 'Dados validados salvos com sucesso.',
        variant: 'default'
      });

      // Recarregar board
      await loadBoard();

      return true;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao salvar dados';
      
      setState(prev => ({ ...prev, loading: false, error: errorMsg }));
      
      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return false;
    }
  }, [toast, loadBoard]);

  /**
   * Move card (drag & drop)
   */
  const moveCard = useCallback(async (
    cardId: number,
    newColumnId: number,
    newPosition?: number
  ): Promise<boolean> => {
    try {
      await kanbanService.moveCard(cardId, newColumnId, newPosition);

      // Atualizar board localmente
      setState(prev => {
        if (!prev.board) return prev;

        const newCardsByColumn = { ...prev.board.cards_by_column };
        
        // Encontrar card e coluna antiga
        let movedCard: Card | null = null;
        let oldColumnId: number | null = null;

        for (const [colId, cards] of Object.entries(newCardsByColumn)) {
          const cardIndex = cards.findIndex(c => c.CardID === cardId);
          if (cardIndex !== -1) {
            movedCard = cards[cardIndex];
            oldColumnId = parseInt(colId);
            newCardsByColumn[oldColumnId] = cards.filter(c => c.CardID !== cardId);
            break;
          }
        }

        // Adicionar na nova coluna
        if (movedCard) {
          movedCard.ColumnID = newColumnId;
          newCardsByColumn[newColumnId] = [
            ...(newCardsByColumn[newColumnId] || []),
            movedCard
          ];
        }

        return {
          ...prev,
          board: {
            ...prev.board,
            cards_by_column: newCardsByColumn
          }
        };
      });

      return true;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao mover card';
      
      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return false;
    }
  }, [toast]);

  /**
   * Busca card com detalhes
   */
  const getCard = useCallback(async (cardId: number): Promise<CardWithDetails | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const card = await kanbanService.getCard(cardId);
      setState(prev => ({ ...prev, currentCard: card, loading: false }));
      return card;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao buscar card';
      setState(prev => ({ ...prev, loading: false, error: errorMsg }));
      
      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return null;
    }
  }, [toast]);

  /**
   * Adiciona movimento
   */
  const addMovement = useCallback(async (
    cardId: number,
    data: MovementCreateData
  ): Promise<boolean> => {
    try {
      await kanbanService.addMovement(cardId, data);

      toast({
        title: 'Sucesso!',
        description: 'Movimento adicionado com sucesso.',
        variant: 'default'
      });

      // Recarregar card atual se for o mesmo
      if (state.currentCard?.CardID === cardId) {
        await getCard(cardId);
      }

      return true;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao adicionar movimento';
      
      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return false;
    }
  }, [toast, state.currentCard, getCard]);

  /**
   * Deleta card
   */
  const deleteCard = useCallback(async (cardId: number): Promise<boolean> => {
    try {
      await kanbanService.deleteCard(cardId);

      toast({
        title: 'Sucesso!',
        description: 'Card excluído com sucesso.',
        variant: 'default'
      });

      // Recarregar board
      await loadBoard();

      return true;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao excluir card';
      
      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return false;
    }
  }, [toast, loadBoard]);

  /**
   * Marca card como concluído
   */
  const completeCard = useCallback(async (cardId: number): Promise<boolean> => {
    try {
      await kanbanService.completeCard(cardId);

      toast({
        title: 'Sucesso!',
        description: 'Card marcado como concluído.',
        variant: 'default'
      });

      // Recarregar board
      await loadBoard();

      return true;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao concluir card';
      
      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return false;
    }
  }, [toast, loadBoard]);

  /**
   * Atualiza card
   */
  const updateCard = useCallback(async (
    cardId: number,
    data: Partial<Card>
  ): Promise<boolean> => {
    try {
      await kanbanService.updateCard(cardId, data);

      toast({
        title: 'Sucesso!',
        description: 'Card atualizado com sucesso.',
        variant: 'default'
      });

      // Atualizar card atual se for o mesmo
      if (state.currentCard?.CardID === cardId) {
        await getCard(cardId);
      }

      return true;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Erro ao atualizar card';
      
      toast({
        title: 'Erro',
        description: errorMsg,
        variant: 'destructive'
      });

      return false;
    }
  }, [toast, state.currentCard, getCard]);

  /**
   * Limpa sugestões da IA
   */
  const clearAISuggestions = useCallback(() => {
    setState(prev => ({
      ...prev,
      aiSuggestions: null,
      currentCard: null
    }));
  }, []);

  return {
    // Estado
    ...state,

    // Ações
    loadBoard,
    createCard,
    saveValidatedData,
    moveCard,
    getCard,
    updateCard,
    addMovement,
    deleteCard,
    completeCard,
    clearAISuggestions
  };
};
