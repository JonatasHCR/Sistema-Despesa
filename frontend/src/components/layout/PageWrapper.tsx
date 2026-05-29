
'use client';

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Loader } from 'lucide-react';

// Persiste entre montagens do componente na mesma sessão SPA. Cada página renderiza
// seu próprio <PageWrapper>, então sem isto o spinner de verificação reaparecia em
// cheio a CADA navegação. Só bloqueamos a renderização na primeira verificação.
let hasVerifiedOnce = false;

export default function PageWrapper({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isVerifying, setIsVerifying] = useState(!hasVerifiedOnce);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const isAuthPage = pathname === '/login';

    if (!token && !isAuthPage) {
      router.replace('/login');
    } else if (token && isAuthPage) {
      router.replace('/');
    }
    else {
      hasVerifiedOnce = true;
      setIsVerifying(false);
    }
  }, [router, pathname]);

  if (isVerifying) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <Loader className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return <>{children}</>;
}
