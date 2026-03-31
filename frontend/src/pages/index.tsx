import Head from 'next/head';
import Link from 'next/link';
import Chat from '../components/Chat';
import styles from '../styles/Home.module.css';

/**
 * Página principal del frontend.
 * Renderiza el componente de chat como página única.
 */
export default function Home() {
  return (
    <>
      <Head>
        <title>GAPID Chatbot - Sistema Conversacional Inteligente</title>
        <meta
          name="description"
          content="Asistente conversacional para la Plataforma GAPID de Cuba, orientado a la consulta normativa y la gestión administrativa"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className={styles.mainContainer}>
        <Link href="/metrics" className={styles.metricsLink}>
          📊 Ver Métricas
        </Link>
        <Chat />
      </main>
    </>
  );
}
