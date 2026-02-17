import Head from 'next/head';
import Chat from '@/components/Chat';

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
          content="Asistente conversacional para el Sistema de Programas y Proyectos de Ciencia, Tecnología e Innovación (GAPID) de Cuba"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <Chat />
      </main>
    </>
  );
}
