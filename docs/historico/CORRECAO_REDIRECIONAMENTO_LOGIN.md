# 🔧 CORREÇÃO - REDIRECIONAMENTO DINÂMICO NO LOGIN

**Data:** 23/10/2025 00:25 BRT  
**Problema:** Login redireciona sempre para `/admin` ao invés de usar contexto do usuário

---

## 🔍 PROBLEMA IDENTIFICADO

### **Sintoma:**
Após fazer login com `atendente@proteamcare.com.br`, o sistema redireciona para `/admin` ao invés de usar o contexto correto do usuário.

### **Causa Raiz:**
No arquivo `LoginPage.jsx` (linha 116), o código usava a variável `user` do estado do `useAuth()`, que ainda estava `null` ou com dados antigos no momento do redirecionamento.

```javascript
// ❌ CÓDIGO ERRADO (linha 116)
const contextPath = getUserContextPath(user);  // user está null ou desatualizado
```

O usuário correto está em `result.user` retornado pela função `login()`.

---

## ✅ CORREÇÃO APLICADA

### **Arquivo:** `frontend/src/pages/LoginPage.jsx`

**Mudança:**
```javascript
// ✅ CÓDIGO CORRETO
const loggedUser = result.user;  // Usar dados retornados pelo login
const contextPath = getUserContextPath(loggedUser);
```

**Logs adicionados:**
```javascript
console.log("📊 Dados do usuário logado:", {
  email: loggedUser?.email_address,
  context_type: loggedUser?.context_type,
  is_system_admin: loggedUser?.is_system_admin,
  company_name: loggedUser?.company_name
});

console.log(
  `✅ Redirecionando para ${contextPath} (contexto: ${loggedUser?.context_type})`
);
```

---

## 🎯 COMO FUNCIONA O REDIRECIONAMENTO

### **Fluxo Completo:**

1. **Usuário faz login** → `LoginPage.jsx` chama `login(email, password)`
2. **AuthContext executa login** → Chama API `/api/v1/auth/login`
3. **Backend retorna token** → Frontend salva no localStorage
4. **Frontend busca dados do usuário** → Chama API `/api/v1/auth/me`
5. **Backend retorna dados completos** → Incluindo `context_type`
6. **AuthContext retorna resultado** → `{ success: true, user: userData }`
7. **LoginPage mapeia contexto** → Usa `getUserContextPath(result.user)`
8. **Sistema redireciona** → Para a rota correta do contexto

---

## 📋 MAPEAMENTO DE CONTEXTOS

### **Função:** `getUserContextPath(user)`

```javascript
switch (user.context_type.toLowerCase()) {
  case "admin":
  case "system":
    return "/admin";
  
  case "professional":
    return "/professional";
  
  case "patient":
    return "/patient";
  
  case "client":
    return "/client";
  
  default:
    console.warn(`⚠️ Contexto desconhecido: ${user.context_type}`);
    return "/admin";  // Fallback
}
```

---

## 🗄️ COMO O CONTEXT_TYPE É DEFINIDO

### **Banco de Dados:**

**Tabela:** `[core].[users]`  
**Coluna:** `context_type NVARCHAR(255)`

**Valores possíveis:**
- `"system"` → Administrador do sistema
- `"admin"` → Administrador da empresa
- `"professional"` → Profissional (médico, terapeuta, etc)
- `"patient"` → Paciente
- `"client"` → Cliente
- `NULL` → Usa fallback `/admin`

### **Stored Procedure:**

**Procedure:** `[core].[sp_get_user_me_data]`  
**Retorna:** JSON com `context_type` do usuário

```sql
SELECT
    u.id, u.email_address, ...,
    u.context_type,  -- ✅ Campo retornado
    ...
FROM [core].[users] u
WHERE u.id = @user_id_input
FOR JSON PATH, WITHOUT_ARRAY_WRAPPER;
```

---

## 🧪 COMO TESTAR

### **1. Verificar context_type no banco:**

```sql
SELECT 
    email_address,
    context_type,
    is_system_admin,
    is_active
FROM [core].[users]
WHERE email_address = 'atendente@proteamcare.com.br';
```

**Resultado esperado:**
```
email_address                    | context_type | is_system_admin | is_active
---------------------------------|--------------|-----------------|----------
atendente@proteamcare.com.br     | professional | 0               | 1
```

### **2. Testar login no frontend:**

1. Abrir http://192.168.11.83:3000/login
2. Abrir DevTools (F12) → Console
3. Fazer login com `atendente@proteamcare.com.br`
4. Verificar logs no console:

**Logs esperados:**
```
🔄 Buscando dados do usuário...
✅ Login realizado com sucesso: { email_address: "atendente@...", context_type: "professional", ... }
📊 Dados do usuário logado: { email: "atendente@...", context_type: "professional", ... }
✅ Redirecionando para /professional (contexto: professional)
```

5. Verificar URL após redirecionamento: `http://192.168.11.83:3000/professional`

---

## ⚠️ PROBLEMA POSSÍVEL: CONTEXT_TYPE NULL

### **Se o usuário não tem context_type definido:**

**Sintoma:**
```
⚠️ Contexto desconhecido: null, usando /admin
✅ Redirecionando para /admin (contexto: null)
```

**Solução:** Atualizar o banco de dados

```sql
-- Definir context_type para o usuário
UPDATE [core].[users]
SET context_type = 'professional'  -- ou 'admin', 'patient', 'client'
WHERE email_address = 'atendente@proteamcare.com.br';
```

**Valores recomendados por tipo de usuário:**
- **Administrador do sistema:** `'system'` (já definido automaticamente se `is_system_admin = 1`)
- **Administrador da empresa:** `'admin'`
- **Profissional (médico, terapeuta):** `'professional'`
- **Atendente/Recepcionista:** `'professional'` ou criar novo contexto `'receptionist'`
- **Paciente:** `'patient'`
- **Cliente:** `'client'`

---

## 🔐 PRÓXIMO PASSO: PROTEGER ROTAS

### **Problema Atual:**
Mesmo com redirecionamento correto, um usuário `professional` pode acessar `/admin/companies` digitando a URL manualmente.

### **Solução: Implementar "Porteiro" (ProtectedRoute)**

**Arquivo:** `frontend/src/components/auth/ProtectedRoute.jsx`

```javascript
// ✅ Verificar se usuário tem permissão para acessar a rota
const ProtectedRoute = ({ children, allowedContexts }) => {
  const { user } = useAuth();
  const location = useLocation();
  
  // Se não está autenticado, redirecionar para login
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  // Se contexto do usuário não está na lista de permitidos
  if (allowedContexts && !allowedContexts.includes(user.context_type)) {
    console.warn(`⚠️ Acesso negado: ${user.context_type} tentou acessar ${location.pathname}`);
    return <Navigate to={`/${user.context_type}`} replace />;
  }
  
  return children;
};
```

**Uso em App.jsx:**
```javascript
<Route path="/admin/*" element={
  <ProtectedRoute allowedContexts={['system', 'admin']}>
    <AdminLayout />
  </ProtectedRoute>
} />

<Route path="/professional/*" element={
  <ProtectedRoute allowedContexts={['professional']}>
    <ProfessionalLayout />
  </ProtectedRoute>
} />
```

---

## 📊 CHECKLIST DE VALIDAÇÃO

### **Login Funciona:**
- [ ] Login com admin@proteamcare.com.br redireciona para `/admin`
- [ ] Login com atendente@proteamcare.com.br redireciona para `/professional`
- [ ] Logs mostram `context_type` correto
- [ ] Redirecionamento usa `result.user` ao invés de `user` do estado

### **Context_Type no Banco:**
- [ ] Coluna `context_type` existe na tabela `users`
- [ ] Usuário admin tem `context_type = 'system'`
- [ ] Usuário atendente tem `context_type` definido (não NULL)
- [ ] Stored procedure `sp_get_user_me_data` retorna `context_type`

### **Proteção de Rotas (Próximo Passo):**
- [ ] ProtectedRoute implementado
- [ ] Rotas `/admin/*` protegidas
- [ ] Rotas `/professional/*` protegidas
- [ ] Usuário não consegue acessar rota de outro contexto

---

## 🎉 RESULTADO ESPERADO

### **Cenário 1: Admin**
```
Login: admin@proteamcare.com.br
Context: system
Redireciona: /admin
Pode acessar: /admin/*, /professional/*, /patient/* (todos)
```

### **Cenário 2: Profissional**
```
Login: atendente@proteamcare.com.br
Context: professional
Redireciona: /professional
Pode acessar: /professional/* (apenas seu contexto)
Bloqueado: /admin/* (acesso negado)
```

### **Cenário 3: Paciente**
```
Login: paciente@example.com
Context: patient
Redireciona: /patient
Pode acessar: /patient/* (apenas seu contexto)
Bloqueado: /admin/*, /professional/* (acesso negado)
```

---

**✅ Correção aplicada com sucesso!**  
**⏳ Próximo passo: Implementar ProtectedRoute para segurança**
