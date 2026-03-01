import React from 'react';
import { QueryLog } from '../services/api';
import styles from '../styles/QueryLogTable.module.css';

interface QueryLogTableProps {
  logs: QueryLog[];
  onViewDetail?: (logId: number) => void;
}

const QueryLogTable: React.FC<QueryLogTableProps> = ({ logs, onViewDetail }) => {
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatResponseTime = (time: number): string => {
    return `${time.toFixed(3)}s`;
  };

  return (
    <div className={styles.tableContainer}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Consulta</th>
            <th>Respuesta</th>
            <th>Tiempo</th>
            <th>Chunks</th>
            <th>Fecha</th>
            <th>Rating</th>
            {onViewDetail && <th>Acciones</th>}
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 ? (
            <tr>
              <td colSpan={onViewDetail ? 8 : 7} className={styles.noData}>
                No hay consultas registradas
              </td>
            </tr>
          ) : (
            logs.map((log) => (
              <tr key={log.id} className={styles.row}>
                <td className={styles.idCell}>{log.id}</td>
                <td className={styles.textCell} title={log.query_preview}>
                  {log.query_preview}
                </td>
                <td className={styles.textCell} title={log.response_preview}>
                  {log.response_preview}
                </td>
                <td className={styles.timeCell}>
                  {formatResponseTime(log.response_time)}
                </td>
                <td className={styles.chunksCell}>{log.chunks_retrieved}</td>
                <td className={styles.dateCell}>{formatDate(log.created_at)}</td>
                <td className={styles.ratingCell}>
                  {log.feedback_score ? (
                    <span className={styles.rating}>
                      {'⭐'.repeat(log.feedback_score)}
                    </span>
                  ) : (
                    <span className={styles.noRating}>-</span>
                  )}
                </td>
                {onViewDetail && (
                  <td className={styles.actionsCell}>
                    <button
                      onClick={() => onViewDetail(log.id)}
                      className={styles.viewButton}
                    >
                      Ver
                    </button>
                  </td>
                )}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default QueryLogTable;
