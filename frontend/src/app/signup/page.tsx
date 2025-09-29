'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Loader, UserPlus } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { signUp } from '@/lib/api';
import Link from 'next/link';

export default function SignupPage() {
  const [name, setName] = useState('Administrador');
  const [email, setEmail] = useState('adm@example.com');
  const [password, setPassword] = useState('123456');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await signUp({ name, email, password });
      toast({
        title: 'Sucesso!',
        description: 'Sua conta foi criada. Você será redirecionado para o login.',
      });
      router.push('/login');
    } catch (error) {
      let description = 'Ocorreu um erro ao criar sua conta.';
      if (error instanceof Error) {
          description = error.message;
      }
      
      toast({
        variant: 'destructive',
        title: 'Falha no Cadastro',
        description: description,
      });
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-sm">
        <form onSubmit={handleSubmit}>
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/20 text-primary">
              <UserPlus className="h-8 w-8" />
            </div>
            <CardTitle className="font-headline text-2xl">Criar Nova Conta</CardTitle>
            <CardDescription>Preencha os campos para se registrar.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nome Completo</Label>
              <Input
                id="name"
                type="text"
                placeholder="Seu nome"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                disabled={isSubmitting}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                type="email"
                placeholder="seu-email@exemplo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isSubmitting}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isSubmitting}
              />
            </div>
          </CardContent>
          <CardFooter className="flex-col gap-4">
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting && <Loader className="mr-2 h-4 w-4 animate-spin" />}
              Cadastrar
            </Button>
            <Button variant="link" asChild>
                <Link href="/login">Já tem uma conta? Faça o login</Link>
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
