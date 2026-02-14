import axios, { AxiosInstance, AxiosError } from 'axios';
import { Conversation, Message, ChatResponse } from '@/types/index';

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

export default apiClient;
