'use client';

import { useCallback, useEffect, useState } from 'react';

export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'theme';

function readStored(): Theme | null {
  if (typeof window === 'undefined') return null;
  const v = localStorage.getItem(STORAGE_KEY);
  return v === 'dark' || v === 'light' ? v : null;
}

function systemPrefersDark(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  // Suaviza apenas durante a transição para evitar repaints custosos no idle.
  root.classList.add('theme-transition');
  root.classList.toggle('dark', theme === 'dark');
  window.setTimeout(() => root.classList.remove('theme-transition'), 250);
}

export function useTheme() {
  // Inicial = o que o inline script (em layout.tsx) já colocou no <html>.
  const [theme, setThemeState] = useState<Theme>(() => {
    if (typeof window === 'undefined') return 'light';
    return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
  });

  // Mantém o state sincronizado com o sistema, caso o usuário ainda não tenha escolhido.
  useEffect(() => {
    const stored = readStored();
    if (stored) return;
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = () => {
      const next: Theme = mql.matches ? 'dark' : 'light';
      applyTheme(next);
      setThemeState(next);
    };
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  }, []);

  const setTheme = useCallback((next: Theme) => {
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
    setThemeState(next);
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  }, [theme, setTheme]);

  return { theme, setTheme, toggleTheme, systemPrefersDark };
}
