/**
 * Testes para ActivityValidationModal
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ActivityValidationModal } from '../../../components/activities/ActivityValidationModal';
import { AISuggestions } from '../../../services/activityService';

const mockAiSuggestions: AISuggestions = {
  pessoas: ['João Silva', 'Maria Santos'],
  sistemas: ['SAP', 'Jira'],
  tags: ['Gestão de Mudanças', 'Aprovação'],
  pendencias: [
    {
      descricao: 'Enviar documentação técnica',
      responsavel: 'João Silva',
      impedimento: null
    }
  ]
};

const mockProps = {
  isOpen: true,
  onClose: jest.fn(),
  aiSuggestions: mockAiSuggestions,
  onSave: jest.fn(),
  loading: false
};

describe('ActivityValidationModal', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deve renderizar corretamente com dados da IA', () => {
    render(<ActivityValidationModal {...mockProps} />);

    expect(screen.getByText('Validar Dados Sugeridos pela IA')).toBeInTheDocument();
    expect(screen.getByText('João Silva')).toBeInTheDocument();
    expect(screen.getByText('Maria Santos')).toBeInTheDocument();
    expect(screen.getByText('SAP')).toBeInTheDocument();
    expect(screen.getByText('Jira')).toBeInTheDocument();
    expect(screen.getByText('Gestão de Mudanças')).toBeInTheDocument();
    expect(screen.getByText('Enviar documentação técnica')).toBeInTheDocument();
  });

  it('deve permitir adicionar nova pessoa', async () => {
    render(<ActivityValidationModal {...mockProps} />);

    const input = screen.getByPlaceholderText('Adicionar pessoa...');
    const addButton = screen.getByRole('button', { name: '+' });

    fireEvent.change(input, { target: { value: 'Pedro Costa' } });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByText('Pedro Costa')).toBeInTheDocument();
    });
  });

  it('deve permitir adicionar novo sistema', async () => {
    render(<ActivityValidationModal {...mockProps} />);

    const input = screen.getByPlaceholderText('Adicionar sistema...');
    const addButton = screen.getAllByRole('button', { name: '+' })[1]; // Segundo botão +

    fireEvent.change(input, { target: { value: 'Teams' } });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByText('Teams')).toBeInTheDocument();
    });
  });

  it('deve permitir adicionar nova tag', async () => {
    render(<ActivityValidationModal {...mockProps} />);

    const input = screen.getByPlaceholderText('Adicionar tag...');
    const addButton = screen.getAllByRole('button', { name: '+' })[2]; // Terceiro botão +

    fireEvent.change(input, { target: { value: 'Urgente' } });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByText('Urgente')).toBeInTheDocument();
    });
  });

  it('deve permitir adicionar nova pendência', async () => {
    render(<ActivityValidationModal {...mockProps} />);

    const descricaoInput = screen.getByPlaceholderText('Descrição da pendência...');
    const responsavelInput = screen.getByPlaceholderText('Responsável (opcional)');
    const addButton = screen.getByRole('button', { name: 'Adicionar Pendência' });

    fireEvent.change(descricaoInput, { target: { value: 'Revisar código' } });
    fireEvent.change(responsavelInput, { target: { value: 'Ana Paula' } });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByText('Revisar código')).toBeInTheDocument();
    });
  });

  it('deve permitir remover pessoa', async () => {
    render(<ActivityValidationModal {...mockProps} />);

    const removeButton = screen.getAllByText('×')[0]; // Primeiro botão de remover
    fireEvent.click(removeButton);

    await waitFor(() => {
      expect(screen.queryByText('João Silva')).not.toBeInTheDocument();
    });
  });

  it('deve chamar onSave com dados validados', async () => {
    render(<ActivityValidationModal {...mockProps} />);

    const saveButton = screen.getByRole('button', { name: 'Salvar Dados Validados' });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockProps.onSave).toHaveBeenCalledWith({
        pessoas: ['João Silva', 'Maria Santos'],
        sistemas: ['SAP', 'Jira'],
        tags: ['Gestão de Mudanças', 'Aprovação'],
        pendencias: [
          {
            descricao: 'Enviar documentação técnica',
            responsavel: 'João Silva',
            impedimento: null
          }
        ]
      });
    });
  });
});