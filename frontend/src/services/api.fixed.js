// frontend/src/services/api.fixed.js
/**
 * Configuração de API atualizada e alinhada com backend funcional
 * Inclui interceptors robustos e tratamento de erros
 */

import axios from 'axios';

// ========================================
// CONFIGURAÇÃO BASE
// ========================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// ========================================
// INTERCEPTORS DE REQUEST
// ========================================

api.interceptors.request.use(
  (config) => {
    // Adicionar token de autenticação se existir
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log de debug em desenvolvimento
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data
      });
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// ========================================
// INTERCEPTORS DE RESPONSE
// ========================================

api.interceptors.response.use(
  (response) => {
    // Log de debug em desenvolvimento
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data
      });
    }
    
    return response;
  },
  (error) => {
    // Log de erro
    console.error('❌ API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data
    });
    
    // Tratamento específico por status code
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Token expirado ou inválido
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          
          // Redirecionar para login se não estiver na página de login
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
          
          throw new Error('Sessão expirada. Faça login novamente.');
          
        case 403:
          throw new Error('Acesso negado. Você não tem permissão para esta ação.');
          
        case 404:
          throw new Error('Recurso não encontrado.');
          
        case 422:
          // Erro de validação - extrair mensagens específicas
          if (data?.detail) {
            if (Array.isArray(data.detail)) {
              const messages = data.detail.map(err => err.msg || err.message).join(', ');
              throw new Error(`Erro de validação: ${messages}`);
            } else {
              throw new Error(`Erro de validação: ${data.detail}`);
            }
          }
          throw new Error('Dados inválidos fornecidos.');
          
        case 429:
          throw new Error('Muitas tentativas. Tente novamente em alguns minutos.');
          
        case 500:
          // Erro interno do servidor - pode ser problema na stored procedure
          if (data?.detail?.includes('rollback silencioso')) {
            throw new Error('Erro interno: Falha na operação do banco de dados. Contate o suporte.');
          }
          throw new Error('Erro interno do servidor. Tente novamente mais tarde.');
          
        case 502:
        case 503:
        case 504:
          throw new Error('Serviço temporariamente indisponível. Tente novamente em alguns minutos.');
          
        default:
          throw new Error(data?.detail || data?.message || `Erro HTTP ${status}`);
      }
    } else if (error.request) {
      // Erro de rede
      throw new Error('Erro de conexão. Verifique sua internet e tente novamente.');
    } else {
      // Erro na configuração da requisição
      throw new Error('Erro na configuração da requisição.');
    }
  }
);

// ========================================
// SERVIÇOS DE AUTENTICAÇÃO
// ========================================

export const authService = {
  /**
   * Realiza login
   */
  async login(credentials) {
    const response = await api.post('/api/v1/auth/login', credentials);
    const { access_token, user } = response.data;
    
    // Armazenar token e dados do usuário
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  },
  
  /**
   * Realiza logout
   */
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },
  
  /**
   * Verifica se usuário está autenticado
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },
  
  /**
   * Obtém dados do usuário atual
   */
  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  
  /**
   * Verifica token e renova se necessário
   */
  async checkToken() {
    try {
      const response = await api.get('/api/v1/auth/me');
      return response.data;
    } catch (error) {
      this.logout();
      throw error;
    }
  }
};

// ========================================
// UTILITÁRIOS
// ========================================

/**
 * Wrapper para requisições com retry automático
 */
export const apiWithRetry = {
  async request(config, maxRetries = 3) {
    let lastError;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await api.request(config);
      } catch (error) {
        lastError = error;
        
        // Não fazer retry em erros de cliente (4xx)
        if (error.response?.status >= 400 && error.response?.status < 500) {
          throw error;
        }
        
        // Aguardar antes de tentar novamente (backoff exponencial)
        if (attempt < maxRetries) {
          const delay = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s...
          await new Promise(resolve => setTimeout(resolve, delay));
          
          console.log(`🔄 Tentativa ${attempt + 1}/${maxRetries} em ${delay}ms...`);
        }
      }
    }
    
    throw lastError;
  },
  
  get: (url, config) => apiWithRetry.request({ ...config, method: 'GET', url }),
  post: (url, data, config) => apiWithRetry.request({ ...config, method: 'POST', url, data }),
  put: (url, data, config) => apiWithRetry.request({ ...config, method: 'PUT', url, data }),
  patch: (url, data, config) => apiWithRetry.request({ ...config, method: 'PATCH', url, data }),
  delete: (url, config) => apiWithRetry.request({ ...config, method: 'DELETE', url })
};

// ========================================
// MOCK PARA DESENVOLVIMENTO
// ========================================

/**
 * Ativa mocks para desenvolvimento quando backend não estiver disponível
 */
export const enableMockMode = () => {
  console.warn('🚧 Modo Mock ativado - APIs serão simuladas');
  
  // Interceptor para simular respostas
  api.interceptors.response.use(
    response => response,
    async (error) => {
      // Se erro de conexão, usar mock
      if (!error.response && error.code === 'ECONNREFUSED') {
        const { method, url } = error.config;
        
        // Simular delay de rede
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Mocks básicos
        if (method === 'get' && url.includes('/companies')) {
          return {
            data: {
              items: [],
              total: 0,
              page: 1,
              size: 10,
              pages: 0
            }
          };
        }
        
        if (method === 'get' && url.includes('/cnpj/')) {
          return {
            data: {
              cnpj: '14337098000185',
              razao_social: 'HOSPITAL MOCK LTDA',
              nome_fantasia: 'HOSPITAL MOCK',
              situacao_cadastral: 'ATIVA'
            }
          };
        }
      }
      
      throw error;
    }
  );
};

// Ativar modo mock se variável de ambiente estiver definida
if (import.meta.env.VITE_ENABLE_MOCK === 'true') {
  enableMockMode();
}

export default api;
