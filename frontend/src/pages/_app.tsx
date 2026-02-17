import type { AppProps } from 'next/app';
import '@/styles/globals.css';

/**
 * Componente raíz de la aplicación Next.js.
 * Configura estilos globales y wrappers comunes.
 */
function MyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}

export default MyApp;
