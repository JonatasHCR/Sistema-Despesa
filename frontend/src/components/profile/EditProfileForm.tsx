
'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader, ExternalLink } from 'lucide-react';
import { useState, useEffect } from 'react';
import { type User } from '@/lib/types';
import { updateUser, getCurrentUser } from '@/lib/api';

const profileFormSchema = z.object({
  nome: z.string().min(2, {
    message: 'O nome deve ter pelo menos 2 caracteres.',
  }),
  email: z.string().email({
    message: 'Por favor, insira um e-mail válido.',
  }),
});

type ProfileFormValues = z.infer<typeof profileFormSchema>;

export function EditProfileForm() {
  const router = useRouter();
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      nome: '',
      email: '',
    },
  });
  
  useEffect(() => {
    getCurrentUser().then((userData) => {
      if (userData) {
        setUser(userData);
        form.reset({ nome: userData.nome, email: userData.email });
      } else {
        router.replace('/api/auth/login');
      }
    });
  }, [form, router]);


  async function onSubmit(data: ProfileFormValues) {
    if (!user) return;
    setIsSubmitting(true);
    
    try {
      const updateData: Partial<User> = {
        nome: data.nome,
        email: data.email,
      };

      const updatedUser = await updateUser(user.id, updateData);
      setUser({ ...user, ...updatedUser });

      toast({
        title: 'Sucesso!',
        description: 'Seu perfil foi atualizado.',
      });
      router.refresh();
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Uh oh! Algo deu errado.',
        description:
          (error as Error).message ||
          'Não foi possível atualizar o perfil.',
      });
    } finally {
      setIsSubmitting(false);
    }
  }

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
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-0">
          <CardContent className="space-y-6">
            <FormField
              control={form.control}
              name="nome"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome de Usuário</FormLabel>
                  <FormControl>
                    <Input placeholder="Seu nome" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>E-mail</FormLabel>
                  <FormControl>
                    <Input type="email" placeholder="seu@email.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {/* A senha nao vive mais aqui: quem a guarda e o Keycloak, e trocá-la
                é no Account Console dele. Deixar os campos apenas para
                encaminhar seria pior — sugeriria que este sistema ainda tem
                alguma senha sua. */}
            <div className="rounded-md border bg-muted/40 p-4">
              <p className="text-sm font-medium">Senha</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Sua senha é a mesma dos outros sistemas e é gerenciada em um só
                lugar.
              </p>
              <a
                href="/api/auth/conta"
                className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium underline underline-offset-4"
              >
                Alterar minha senha
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col-reverse sm:flex-row sm:justify-between gap-2 p-4 sm:p-6">
            <Button type="button" variant="outline" className="w-full sm:w-auto" onClick={() => router.back()}>
              Voltar
            </Button>
            <Button type="submit" className="w-full sm:w-auto" disabled={isSubmitting}>
              {isSubmitting && <Loader className="mr-2 h-4 w-4 animate-spin" />}
              Salvar Alterações
            </Button>
          </CardFooter>
        </form>
      </Form>
    </Card>
  );
}
