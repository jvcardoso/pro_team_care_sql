// frontend/src/utils/localStorage.js
/**
 * Utilitários para localStorage com tratamento robusto de erros
 */

/**
 * Limpa todos os dados corrompidos do localStorage
 */
export const clearCorruptedData = () => {
  const keysToCheck = ['user', 'access_token', 'pro-team-care-theme'];
  
  keysToCheck.forEach(key => {
    try {
      const value = localStorage.getItem(key);
      if (value === 'undefined' || value === 'null') {
        console.warn(`🧹 Removendo valor corrompido para chave: ${key}`);
        localStorage.removeItem(key);
      }
    } catch (error) {
      console.warn(`🧹 Erro ao verificar chave ${key}, removendo:`, error);
      localStorage.removeItem(key);
    }
  });
};

/**
 * Obtém item do localStorage com tratamento de erro
 */
export const safeGetItem = (key, defaultValue = null) => {
  try {
    const value = localStorage.getItem(key);
    if (!value || value === 'undefined' || value === 'null') {
      return defaultValue;
    }
    return value;
  } catch (error) {
    console.warn(`🧹 Erro ao obter ${key} do localStorage:`, error);
    localStorage.removeItem(key);
    return defaultValue;
  }
};

/**
 * Obtém e faz parse de JSON do localStorage com tratamento de erro
 */
export const safeGetJSON = (key, defaultValue = null) => {
  try {
    const value = safeGetItem(key);
    if (!value) return defaultValue;
    return JSON.parse(value);
  } catch (error) {
    console.warn(`🧹 Erro ao fazer parse JSON de ${key}:`, error);
    localStorage.removeItem(key);
    return defaultValue;
  }
};

/**
 * Define item no localStorage com tratamento de erro
 */
export const safeSetItem = (key, value) => {
  try {
    if (typeof value === 'object') {
      localStorage.setItem(key, JSON.stringify(value));
    } else {
      localStorage.setItem(key, value);
    }
    return true;
  } catch (error) {
    console.error(`❌ Erro ao salvar ${key} no localStorage:`, error);
    return false;
  }
};

/**
 * Executa limpeza automática na inicialização
 */
export const initializeLocalStorage = () => {
  console.log('🔧 Inicializando localStorage...');
  clearCorruptedData();
  console.log('✅ localStorage inicializado');
};
