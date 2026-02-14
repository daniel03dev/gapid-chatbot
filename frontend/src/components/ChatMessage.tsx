import React from 'react';
import { Message } from '@/types/index';
import styles from '@/styles/Chat.module.css';

interface ChatMessageProps {
  message: Message;
}

/**
 * Componente para renderizar un mensaje individual.
 * Muestra burbujas diferentes para usuario y asistente.
 */
const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div
      className={`${styles.messageWrapper} ${
        isUser ? styles.userMessage : styles.assistantMessage
      }`}
    >
      <div className={styles.messageContent}>
        <div className={styles.messageRole}>
          {isUser ? '👤 Tú' : '🤖 Asistente'}
        </div>
        <div className={styles.messageText}>
          {message.content}
        </div>
        <div className={styles.messageTime}>
          {new Date(message.created_at).toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
