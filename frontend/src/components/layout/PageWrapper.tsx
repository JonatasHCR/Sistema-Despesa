
'use client';

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Loader } from 'lucide-react';

export default function PageWrapper({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isVerifying, setIsVerifying] = useState(true);

  useEffect(() => {
    const session = localStorage.getItem('userSession');
    const isAuthPage = pathname === '/login';

    if (!session && !isAuthPage) {
      router.replace('/login');
    } else if (session && isAuthPage) {
      router.replace('/');
    }
    else {
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
