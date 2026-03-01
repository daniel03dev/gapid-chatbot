import React, { useState, useEffect } from 'react';
import { conversationAPI } from '../services/api';
import { Conversation } from '../types/index';
import styles from '../styles/ConversationSidebar.module.css';

interface ConversationSidebarProps {
  currentConversationId?: number;
  onSelectConversation: (conversationId: number) => void;
  onNewConversation: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

const ConversationSidebar: React.FC<ConversationSidebarProps> = ({
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  isOpen,
  onToggle,
}) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');

  const loadConversations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await conversationAPI.list();
      // Ordenar por más reciente primero
      setConversations(data.sort((a, b) => {
        const dateA = new Date(a.updated_at).getTime();
        const dateB = new Date(b.updated_at).getTime();
        return dateB - dateA;
      }));
    } catch (err: any) {
      setError('Error al cargar conversaciones');
      console.error('Error loading conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadConversations();
    }
  }, [isOpen]);

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Ahora';
    if (diffMins < 60) return `hace ${diffMins}m`;
    if (diffHours < 24) return `hace ${diffHours}h`;
    if (diffDays < 7) return `hace ${diffDays}d`;

    return date.toLocaleDateString('es-ES', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getConversationPreview = (conv: Conversation): string => {
    if (conv.messages && conv.messages.length > 0) {
      const lastUserMessage = conv.messages.find((m) => m.role === 'user');
      if (lastUserMessage) {
        return lastUserMessage.content.substring(0, 50) + 
               (lastUserMessage.content.length > 50 ? '...' : '');
      }
    }
    return 'Conversación vacía';
  };

  const filteredConversations = conversations.filter((conv) => {
    const searchLower = searchTerm.toLowerCase();
    const preview = getConversationPreview(conv).toLowerCase();
    const idMatch = conv.id.toString().includes(searchLower);
    const previewMatch = preview.includes(searchLower);
    return idMatch || previewMatch;
  });

  return (
    <>
      {/* Toggle button para móvil */}
      <button className={styles.toggleButton} onClick={onToggle}>
        {isOpen ? '✕' : '☰'} Historial
      </button>

      {/* Overlay para móvil */}
      {isOpen && <div className={styles.overlay} onClick={onToggle}></div>}

      {/* Sidebar */}
      <aside className={`${styles.sidebar} ${isOpen ? styles.open : ''}`}>
        <div className={styles.header}>
          <h2 className={styles.title}>💬 Conversaciones</h2>
          <button 
            className={styles.closeButton}
            onClick={onToggle}
            title="Cerrar"
          >
            ✕
          </button>
        </div>

        <button 
          className={styles.newButton}
          onClick={() => {
            onNewConversation();
            onToggle();
          }}
        >
          + Nueva Conversación
        </button>

        <div className={styles.searchContainer}>
          <input
            type="text"
            placeholder="🔍 Buscar conversaciones..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={styles.searchInput}
          />
          {searchTerm && (
            <button
              className={styles.clearButton}
              onClick={() => setSearchTerm('')}
              title="Limpiar búsqueda"
            >
              ✕
            </button>
          )}
        </div>

        <div className={styles.listContainer}>
          {loading && (
            <div className={styles.loadingState}>
              <div className={styles.spinner}></div>
              <p>Cargando...</p>
            </div>
          )}

          {error && (
            <div className={styles.errorState}>
              <p>{error}</p>
              <button 
                onClick={loadConversations}
                className={styles.retryButton}
              >
                Reintentar
              </button>
            </div>
          )}

          {!loading && !error && conversations.length === 0 && (
            <div className={styles.emptyState}>
              <p>No hay conversaciones</p>
            </div>
          )}

          {!loading && !error && conversations.length > 0 && filteredConversations.length === 0 && (
            <div className={styles.emptyState}>
              <p>No se encontraron resultados</p>
            </div>
          )}

          {!loading && !error && filteredConversations.length > 0 && (
            <ul className={styles.list}>
              {filteredConversations.map((conversation) => (
                <li
                  key={conversation.id}
                  className={`${styles.item} ${
                    currentConversationId === conversation.id ? styles.active : ''
                  }`}
                >
                  <button
                    className={styles.itemButton}
                    onClick={() => {
                      onSelectConversation(conversation.id);
                      onToggle();
                    }}
                    title={getConversationPreview(conversation)}
                  >
                    <div className={styles.itemContent}>
                      <div className={styles.itemTitle}>
                        Conv. #{conversation.id}
                      </div>
                      <div className={styles.itemPreview}>
                        {getConversationPreview(conversation)}
                      </div>
                      <div className={styles.itemTime}>
                        {formatDate(conversation.updated_at)}
                      </div>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className={styles.footer}>
          <small>
            {searchTerm 
              ? `${filteredConversations.length} de ${conversations.length} resultados`
              : `Total: ${conversations.length} conversaciones`
            }
          </small>
        </div>
      </aside>
    </>
  );
};

export default ConversationSidebar;
