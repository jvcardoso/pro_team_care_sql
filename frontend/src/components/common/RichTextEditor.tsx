/**
 * Editor de texto rico (WYSIWYG) usando @uiw/react-md-editor
 * Suporta markdown, preview, e formatação rica com upload de imagens
 */

import React, { useCallback } from 'react';
import MDEditor, { commands } from '@uiw/react-md-editor';
import '@uiw/react-md-editor/markdown-editor.css';

interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  minHeight?: string;
}

export const RichTextEditor: React.FC<RichTextEditorProps> = ({
  value,
  onChange,
  placeholder = 'Digite aqui...',
  disabled = false,
  minHeight = '200px'
}) => {


  // Handler para paste - removido processamento de imagens
  // (Imagens devem ser enviadas via sistema de upload separado)
  const handlePaste = useCallback(async (event: React.ClipboardEvent) => {
    // Não processar imagens aqui - usar sistema de upload separado
    const items = event.clipboardData?.items;
    if (items) {
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          event.preventDefault();
          console.log('💡 Imagem detectada! Use o sistema de upload na aba "Imagens" do card.');
          return;
        }
      }
    }
  }, []);

  // Handler para drop - removido processamento de imagens
  const handleDrop = useCallback((event: React.DragEvent) => {
    // Não processar imagens aqui - usar sistema de upload separado
    const files = event.dataTransfer?.files;
    if (files) {
      for (let i = 0; i < files.length; i++) {
        if (files[i].type.indexOf('image') !== -1) {
          event.preventDefault();
          console.log('💡 Imagem detectada! Use o sistema de upload na aba "Imagens" do card.');
          return;
        }
      }
    }
  }, []);

  return (
    <div 
      className="rich-text-editor" 
      data-color-mode="auto"
      onPaste={handlePaste}
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      <MDEditor
        value={value}
        onChange={(val) => onChange(val || '')}
        preview="edit"
        hideToolbar={false}
        textareaProps={{
          placeholder: placeholder + ' (💡 Para imagens, use o botão "Imagens" na aba do card)',
          disabled,
        }}
        height={parseInt(minHeight)}
        commands={[
          commands.bold,
          commands.italic,
          commands.strikethrough,
          commands.hr,
          commands.title,
          commands.divider,
          commands.link,
          commands.quote,
          commands.code,
          commands.image,
          commands.divider,
          commands.unorderedListCommand,
          commands.orderedListCommand,
          commands.checkedListCommand,
        ]}
      />

      <style>{`
        .rich-text-editor .w-md-editor {
          background: white;
          border-radius: 0.375rem;
          border: 1px solid #d1d5db;
        }

        .rich-text-editor .w-md-editor-text-pre,
        .rich-text-editor .w-md-editor-text {
          min-height: ${minHeight};
          font-size: 14px;
        }

        .rich-text-editor .w-md-editor-bar {
          background: #f9fafb;
          border-top-left-radius: 0.375rem;
          border-top-right-radius: 0.375rem;
        }

        /* Preview de imagens */
        .rich-text-editor .w-md-editor-preview img {
          max-width: 100%;
          height: auto;
          border-radius: 0.375rem;
          margin: 0.5rem 0;
        }

        .dark .rich-text-editor .w-md-editor {
          background: #1f2937;
          border-color: #4b5563;
        }

        .dark .rich-text-editor:hover .w-md-editor {
          border-color: #60a5fa;
        }

        .dark .rich-text-editor .w-md-editor-bar {
          background: #374151;
        }

        .dark .rich-text-editor .w-md-editor-text-pre,
        .dark .rich-text-editor .w-md-editor-text {
          background: #1f2937;
          color: #f9fafb;
        }

        .dark .rich-text-editor .w-md-editor-text-pre::before {
          color: #9ca3af;
        }


      `}</style>
    </div>
  );
};
