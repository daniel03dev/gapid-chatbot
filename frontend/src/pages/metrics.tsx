import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { metricsAPI, Metrics, QueryLog } from '../services/api';
import MetricsCard from '../components/MetricsCard';
import QueryLogTable from '../components/QueryLogTable';
import styles from '../styles/Metrics.module.css';

const MetricsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [queryLogs, setQueryLogs] = useState<QueryLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const fetchData = async () => {
    try {
      setError(null);
      const [metricsData, logsData] = await Promise.all([
        metricsAPI.getMetrics(),
        metricsAPI.listQueryLogs(20),
      ]);
      setMetrics(metricsData);
      setQueryLogs(logsData.results);
    } catch (err: any) {
      setError(err.message || 'Error al cargar las métricas');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const formatResponseTime = (time: number): string => {
    return `${time.toFixed(3)}s`;
  };

  const formatNumber = (num: number): string => {
    return num.toLocaleString('es-ES');
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Cargando métricas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={handleRefresh} className={styles.retryButton}>
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Métricas y Estadísticas - GAPID Chatbot</title>
        <meta name="description" content="Dashboard de métricas del sistema GAPID Chatbot" />
      </Head>

      <div className={styles.container}>
        <header className={styles.header}>
          <div className={styles.headerContent}>
            <div>
              <h1 className={styles.title}>📊 Dashboard de Métricas</h1>
              <p className={styles.subtitle}>
                Estadísticas y análisis del sistema GAPID Chatbot
              </p>
            </div>
            <div className={styles.headerActions}>
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className={styles.refreshButton}
              >
                {refreshing ? '⏳' : '🔄'} Actualizar
              </button>
              <Link href="/" className={styles.backButton}>
                ← Volver al Chat
              </Link>
            </div>
          </div>
        </header>

        <main className={styles.main}>
          {/* Métricas Generales */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Métricas Generales</h2>
            <div className={styles.metricsGrid}>
              <MetricsCard
                title="Total de Consultas"
                value={formatNumber(metrics?.total_queries || 0)}
                subtitle="Consultas procesadas"
                icon="💬"
              />
              <MetricsCard
                title="Conversaciones"
                value={formatNumber(metrics?.total_conversations || 0)}
                subtitle="Conversaciones creadas"
                icon="👥"
              />
              <MetricsCard
                title="Tiempo Promedio"
                value={formatResponseTime(metrics?.avg_response_time || 0)}
                subtitle="Por respuesta"
                icon="⚡"
              />
              <MetricsCard
                title="Chunks Promedio"
                value={metrics?.avg_chunks_retrieved.toFixed(1) || '0'}
                subtitle="Documentos recuperados"
                icon="📄"
              />
            </div>
          </section>

          {/* Actividad Reciente */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Actividad Reciente</h2>
            <div className={styles.activityGrid}>
              <MetricsCard
                title="Últimas 24 Horas"
                value={formatNumber(metrics?.queries_last_24h || 0)}
                subtitle="Consultas"
                icon="🕐"
                trend={
                  (metrics?.queries_last_24h || 0) > 0 ? 'up' : 'neutral'
                }
              />
              <MetricsCard
                title="Últimos 7 Días"
                value={formatNumber(metrics?.queries_last_7d || 0)}
                subtitle="Consultas"
                icon="📅"
              />
              <MetricsCard
                title="Últimos 30 Días"
                value={formatNumber(metrics?.queries_last_30d || 0)}
                subtitle="Consultas"
                icon="📆"
              />
              <MetricsCard
                title="Total de Errores"
                value={formatNumber(metrics?.total_errors || 0)}
                subtitle="Errores registrados"
                icon="⚠️"
                trend={
                  (metrics?.total_errors || 0) > 0 ? 'down' : 'neutral'
                }
              />
            </div>
          </section>

          {/* Horas Más Activas */}
          {metrics && metrics.most_active_hours.length > 0 && (
            <section className={styles.section}>
              <h2 className={styles.sectionTitle}>Horas Más Activas</h2>
              <div className={styles.activeHours}>
                {metrics.most_active_hours.map((item) => (
                  <div key={item.hour} className={styles.hourCard}>
                    <div className={styles.hourLabel}>
                      {item.hour.toString().padStart(2, '0')}:00
                    </div>
                    <div className={styles.hourBar}>
                      <div
                        className={styles.hourBarFill}
                        style={{
                          width: `${
                            (item.count /
                              Math.max(
                                ...metrics.most_active_hours.map((h) => h.count)
                              )) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                    <div className={styles.hourCount}>{item.count} consultas</div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Calificación Promedio */}
          {metrics?.avg_feedback_score && (
            <section className={styles.section}>
              <h2 className={styles.sectionTitle}>Calificación de Usuarios</h2>
              <div className={styles.feedbackCard}>
                <div className={styles.feedbackScore}>
                  {metrics.avg_feedback_score.toFixed(1)} / 5.0
                </div>
                <div className={styles.feedbackStars}>
                  {'⭐'.repeat(Math.round(metrics.avg_feedback_score))}
                </div>
              </div>
            </section>
          )}

          {/* Consultas Recientes */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>
              Últimas 20 Consultas Registradas
            </h2>
            <QueryLogTable logs={queryLogs} />
          </section>
        </main>
      </div>
    </>
  );
};

export default MetricsPage;
