-- Atualizar caminhos dos menus para incluir /admin/
UPDATE [core].[menus]
SET path = '/admin' + path
WHERE path NOT LIKE '/admin/%'
  AND deleted_at IS NULL;
