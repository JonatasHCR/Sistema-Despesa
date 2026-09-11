'use client';

import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader, ExternalLink } from 'lucide-react';
import { useState, useEffect } from 'react';
import { type User } from '@/lib/types';
import { getCurrentUser } from '@/lib/api';

// Nome, email e senha vem do Keycloak e valem para todos os sistemas. Editar
// aqui divergiria em silencio: o login nao reescreve esses campos.
export function EditProfileForm() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    getCurrentUser().then((userData) => {
      if (userData) {
        setUser(userData);
      } else {
        router.replace('/api/auth/login');
      }
    });
  }, [router]);

  if (!user) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <Loader className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Informações do Perfil</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-1">
          <p className="text-sm font-medium">Nome</p>
          <p className="text-sm text-muted-foreground">{user.nome}</p>
        </div>
        <div className="space-y-1">
          <p className="text-sm font-medium">E-mail</p>
          <p className="text-sm text-muted-foreground">{user.email}</p>
        </div>

        <div className="rounded-md border bg-muted/40 p-4">
          <p className="text-sm font-medium">Seus dados e sua senha</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Nome, e-mail e senha são os mesmos em todos os sistemas e ficam
            guardados em um só lugar.
          </p>
          <a
            href="/api/auth/conta"
            className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium underline underline-offset-4"
          >
            Alterar meus dados
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      </CardContent>
      <CardFooter className="p-4 sm:p-6">
        <Button type="button" variant="outline" className="w-full sm:w-auto" onClick={() => router.back()}>
          Voltar
        </Button>
      </CardFooter>
    </Card>
  );
}
