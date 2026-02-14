import React, { useState, KeyboardEvent } from 'react';
import styles from '@/styles/Chat.module.css';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

/**
 * Componente de entrada de texto para el chat.
 * Maneja el envío con Enter y botón.
 */
const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.inputContainer}>
      <textarea
        className={styles.inputField}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Escribe tu pregunta sobre GAPID..."
        disabled={disabled}
        rows={3}
      />
      <button
        className={styles.sendButton}
        onClick={handleSend}
        disabled={disabled || !inputValue.trim()}
      >
        Enviar ➤
      </button>
    </div>
  );
};

export default ChatInput;
