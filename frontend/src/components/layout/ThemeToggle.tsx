'use client';

import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/hooks/use-theme';
import { cn } from '@/lib/utils';

interface ThemeToggleProps {
  className?: string;
}

export function ThemeToggle({ className }: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Evita mismatch de hidratação — o ícone só renderiza após o mount.
  useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = theme === 'dark';

  // O rótulo também depende do tema, e por isso também precisa esperar o mount.
  //
  // O estado inicial de `useTheme` lê a classe do <html>, que só existe no
  // navegador: no servidor sai sempre 'light'. O ícone já era protegido, mas o
  // `title`/`aria-label` não — e um atributo diferente entre servidor e cliente
  // é exatamente o que dispara "Hydration failed because the server rendered
  // HTML didn't match the client".
  const label = !mounted
    ? 'Alternar tema'
    : isDark
      ? 'Mudar para tema claro'
      : 'Mudar para tema escuro';

  return (
    <Button
      type="button"
      variant="outline"
      size="icon"
      onClick={toggleTheme}
      aria-label={label}
      title={label}
      className={cn('shrink-0', className)}
    >
      {mounted ? (
        isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />
      ) : (
        <span className="h-4 w-4" />
      )}
    </Button>
  );
}
