import React, { useState, useEffect, useRef } from 'react';
import { Message, Conversation } from '../types/index';
import { conversationAPI, messageAPI } from '../services/api';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import ConversationSidebar from './ConversationSidebar';
import styles from '../styles/Chat.module.css';

/**
 * Componente principal de Chat.
 * Maneja el estado de la conversación actual y coordina los mensajes.
 */
const Chat: React.FC = () => {
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * Inicializar conversación al montar el componente
   */
  useEffect(() => {
    initializeConversation();
  }, []);

  /**
   * Auto-scroll al final cuando se agregan mensajes
   */
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  /**
   * Crear una nueva conversación
   */
  const initializeConversation = async () => {
    try {
      setIsLoading(true);
      const newConversation = await conversationAPI.create();
      setConversation(newConversation);
      setMessages([]);
      setError(null);
      setSidebarOpen(false);
    } catch (err) {
      setError('Error al inicializar la conversación');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Cargar una conversación existente
   */
  const handleLoadConversation = async (conversationId: number) => {
    try {
      setIsLoading(true);
      const loadedConversation = await conversationAPI.get(conversationId);
      setConversation(loadedConversation);
      setMessages(loadedConversation.messages || []);
      setError(null);
    } catch (err) {
      setError('Error al cargar la conversación');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Enviar un mensaje del usuario
   */
  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    try {
      setIsLoading(true);
      setError(null);

      // Crear conversación si no existe
      if (!conversation) {
        const newConversation = await conversationAPI.create();
        setConversation(newConversation);
      }

      // Crear mensaje del usuario en la UI
      const userMessage: Message = {
        id: Math.random(),
        role: 'user',
        role_display: 'Tú',
        content: content,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Enviar mensaje al backend y obtener respuesta
      const response = await messageAPI.chat(
        conversation?.id || 0,
        content
      );

      // Agregar respuesta del asistente
      const assistantMessage: Message = {
        id: Math.random(),
        role: 'assistant',
        role_display: 'Asistente',
        content: response.answer,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    } catch (err) {
      setError(`Error al enviar el mensaje: ${err instanceof Error ? err.message : 'Error desconocido'}`);
      console.error('Chat error:', err);
      setIsLoading(false);
    }
  };

  /**
   * Limpiar conversación y empezar de nuevo
   */
  const handleClearConversation = () => {
    initializeConversation();
  };

  return (
    <div className={styles.chatWrapper}>
      <ConversationSidebar
        currentConversationId={conversation?.id}
        onSelectConversation={handleLoadConversation}
        onNewConversation={initializeConversation}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      <div className={styles.chatContainer}>
        <div className={styles.chatHeader}>
          <div className={styles.headerContent}>
            <h1>GAPID Chatbot</h1>
            <p>Asistente conversacional para el Sistema de Programas y Proyectos</p>
          </div>
          <button 
            onClick={() => initializeConversation()}
            className={styles.clearButton}
            disabled={isLoading}
            title="Crear nueva conversación"
          >
            + Nueva
          </button>
        </div>

        <div className={styles.messagesContainer}>
          {messages.length === 0 && (
            <div className={styles.welcomeMessage}>
              <h2>¡Bienvenido!</h2>
              <p>
                Pregúntame sobre el Sistema de Programas y Proyectos de CTI,
                niveles de madurez tecnológica (TRL), o cualquier tema relacionado
                con GAPID.
              </p>
              <p className={styles.tip}>
                💡 Usa el botón "☰ Historial" para ver tus conversaciones anteriores
              </p>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}

          {isLoading && (
            <div className={styles.loadingIndicator}>
              <span>●</span>
              <span>●</span>
              <span>●</span>
            </div>
          )}

          {error && (
            <div className={styles.errorMessage}>
              ⚠️ {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <ChatInput 
          onSendMessage={handleSendMessage}
          disabled={isLoading || !conversation}
        />
      </div>
    </div>
  );
};

export default Chat;
