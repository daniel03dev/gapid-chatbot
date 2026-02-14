import React, { useState, useEffect, useRef } from 'react';
import { Message, Conversation } from '@/types/index';
import { conversationAPI, messageAPI } from '@/services/api';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import styles from '@/styles/Chat.module.css';

/**
 * Componente principal de Chat.
 * Maneja el estado de la conversación actual y coordina los mensajes.
 */
const Chat: React.FC = () => {
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
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
    } catch (err) {
      setError('Error al inicializar la conversación');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Enviar un mensaje del usuario
   */
  const handleSendMessage = async (content: string) => {
    if (!conversation || !content.trim()) return;

    try {
      setIsLoading(true);
      setError(null);

      // Crear mensaje del usuario
      const userMessage = await messageAPI.create(
        conversation.id,
        'user',
        content
      );
      setMessages((prev) => [...prev, userMessage]);

      // Simular respuesta del asistente (placeholder)
      // En el futuro, esto llamará al endpoint de ChatService
      setTimeout(async () => {
        const assistantMessage = await messageAPI.create(
          conversation.id,
          'assistant',
          'Esta es una respuesta temporal. En breve integraremos el sistema RAG completo para responder basándose en los documentos del GAPID.'
        );
        setMessages((prev) => [...prev, assistantMessage]);
        setIsLoading(false);
      }, 1000);
    } catch (err) {
      setError('Error al enviar el mensaje');
      console.error(err);
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
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <h1>GAPID Chatbot</h1>
        <p>Asistente conversacional para el Sistema de Programas y Proyectos</p>
        <button 
          onClick={handleClearConversation}
          className={styles.clearButton}
          disabled={isLoading}
        >
          Nueva Conversación
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
  );
};

export default Chat;
