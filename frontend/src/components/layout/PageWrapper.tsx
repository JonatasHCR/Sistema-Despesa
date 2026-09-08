
'use client';

/**
 * Antes este componente decidia se a pessoa estava logada lendo o
 * `localStorage` num `useEffect` — o que só roda DEPOIS de a página montar, e
 * por isso a tela piscava antes de redirecionar. Pior: o `authToken` ficava ao
 * alcance de qualquer script.
 *
 * Agora quem barra é o `src/middleware.ts`, no servidor, antes de a página
 * chegar ao navegador. Aqui não sobrou verificação nenhuma.
 */
export default function PageWrapper({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
