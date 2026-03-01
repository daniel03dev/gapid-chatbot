import axios, { AxiosInstance, AxiosError } from 'axios';
import { Conversation, Message, ChatResponse } from '../types/index';

/**
 * Servicio API para comunicación con el backend Django.
 * Gestiona conversaciones, mensajes y consultas al chatbot.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Interceptor para manejo de errores
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error('API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

/**
 * CONVERSACIONES
 */

export const conversationAPI = {
  /**
   * Listar todas las conversaciones
   */
  async list(): Promise<Conversation[]> {
    try {
      const response = await apiClient.get<Conversation[]>('/conversations/');
      return response.data;
    } catch (error) {
      console.error('Error listing conversations:', error);
      throw error;
    }
  },

  /**
   * Crear una nueva conversación
   */
  async create(): Promise<Conversation> {
    try {
      const response = await apiClient.post<Conversation>('/conversations/');
      return response.data;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  },

  /**
   * Obtener detalles de una conversación (incluye mensajes)
   */
  async get(conversationId: number): Promise<Conversation> {
    try {
      const response = await apiClient.get<Conversation>(
        `/conversations/${conversationId}/`
      );
      return response.data;
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw error;
    }
  },

  /**
   * Actualizar una conversación
   */
  async update(conversationId: number, data: Partial<Conversation>): Promise<Conversation> {
    try {
      const response = await apiClient.put<Conversation>(
        `/conversations/${conversationId}/`,
        data
      );
      return response.data;
    } catch (error) {
      console.error('Error updating conversation:', error);
      throw error;
    }
  },

  /**
   * Eliminar una conversación
   */
  async delete(conversationId: number): Promise<void> {
    try {
      await apiClient.delete(`/conversations/${conversationId}/`);
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  },
};

/**
 * MENSAJES
 */

export const messageAPI = {
  /**
   * Listar mensajes de una conversación
   */
  async list(conversationId: number): Promise<Message[]> {
    try {
      const response = await apiClient.get<Message[]>(
        `/conversations/${conversationId}/messages/`
      );
      return response.data;
    } catch (error) {
      console.error('Error listing messages:', error);
      throw error;
    }
  },

  /**
   * Crear un nuevo mensaje en una conversación
   */
  async create(
    conversationId: number,
    role: 'user' | 'assistant',
    content: string
  ): Promise<Message> {
    try {
      const response = await apiClient.post<Message>(
        `/conversations/${conversationId}/messages/`,
        {
          role,
          content,
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error creating message:', error);
      throw error;
    }
  },

  /**
   * Enviar un mensaje y obtener respuesta del chatbot RAG
   */
  async chat(
    conversationId: number,
    message: string
  ): Promise<ChatResponse> {
    try {
      const response = await apiClient.post<ChatResponse>(
        '/chat/',
        {
          message,
          conversation_id: conversationId || undefined,
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error in chat:', error);
      throw error;
    }
  },
};

/**
 * CHAT (Sistema RAG)
 */

export const chatAPI = {
  /**
   * Enviar una consulta al chatbot y obtener respuesta
   * (Endpoint futuro para integración con ChatService)
   */
  async ask(conversationId: number, query: string): Promise<ChatResponse> {
    try {
      // Este endpoint será implementado en versiones futuras
      // Por ahora, retorna respuesta simulada
      const response = await apiClient.post<ChatResponse>(
        `/conversations/${conversationId}/ask/`,
        { query }
      );
      return response.data;
    } catch (error) {
      console.error('Error asking question:', error);
      throw error;
    }
  },
};

/**
 * HEALTH CHECK
 */

export const healthAPI = {
  /**
   * Verificar que el backend está operacional
   */
  async check(): Promise<boolean> {
    try {
      const response = await apiClient.get('/status/');
      return response.status === 200;
    } catch (error) {
      console.error('Backend is not available');
      return false;
    }
  },
};

/**
 * MÉTRICAS Y LOGS
 */

export interface Metrics {
  total_queries: number;
  total_conversations: number;
  avg_response_time: number;
  avg_chunks_retrieved: number;
  queries_last_24h: number;
  queries_last_7d: number;
  queries_last_30d: number;
  avg_feedback_score: number | null;
  total_errors: number;
  most_active_hours: Array<{ hour: number; count: number }>;
}

export interface QueryLog {
  id: number;
  conversation_id: number | null;
  query_preview: string;
  response_preview: string;
  response_time: number;
  chunks_retrieved: number;
  created_at: string;
  feedback_score: number | null;
}

export interface QueryLogDetail {
  id: number;
  conversation_id: number | null;
  user_query: string;
  assistant_response: string;
  response_time: number;
  chunks_retrieved: number;
  context_used: string;
  created_at: string;
  ip_address: string | null;
  user_agent: string;
  feedback_score: number | null;
}

export interface QueryLogsResponse {
  count: number;
  results: QueryLog[];
}

export const metricsAPI = {
  /**
   * Obtener métricas y estadísticas del sistema
   */
  async getMetrics(): Promise<Metrics> {
    try {
      const response = await apiClient.get<Metrics>('/metrics/');
      return response.data;
    } catch (error) {
      console.error('Error fetching metrics:', error);
      throw error;
    }
  },

  /**
   * Listar consultas registradas
   */
  async listQueryLogs(limit: number = 50, conversationId?: number): Promise<QueryLogsResponse> {
    try {
      const params: any = { limit };
      if (conversationId) params.conversation_id = conversationId;
      
      const response = await apiClient.get<QueryLogsResponse>('/logs/queries/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching query logs:', error);
      throw error;
    }
  },

  /**
   * Obtener detalle de una consulta específica
   */
  async getQueryLogDetail(logId: number): Promise<QueryLogDetail> {
    try {
      const response = await apiClient.get<QueryLogDetail>(`/logs/queries/${logId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching query log detail:', error);
      throw error;
    }
  },
};

export default apiClient;
