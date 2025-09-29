/* eslint-disable @typescript-eslint/no-unsafe-assignment */
'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { CalendarIcon } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { Button } from '../ui/button';
import { Calendar } from '../ui/calendar';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '../ui/form';
import { Input } from '../ui/input';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { ptBR } from 'date-fns/locale';
import { addExpense, getExpenses } from '@/lib/api';
import { type User } from '@/lib/types';
import { EXPENSE_STATUSES } from '@/lib/constants';
import { Combobox } from '../ui/combobox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

const FormSchema = z.object({
  nome: z.string({ required_error: 'O nome da despesa é obrigatório.' }),
  valor: z.coerce.number({ required_error: 'O valor da despesa é obrigatório.' }),
  vencimento: z.date({ required_error: 'A data de vencimento é obrigatória.' }),
  tipo: z.string({ required_error: 'O tipo da despesa é obrigatório.' }),
  status: z.enum(EXPENSE_STATUSES, { required_error: 'O status da despesa é obrigatório.' }),
  user_id: z.coerce.number({ required_error: 'O usuário é obrigatório.' }),
});

export function NewExpenseForm({ users }: { users: User[] }) {
  const router = useRouter();

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      nome: '',
      valor: 0,
      vencimento: new Date(),
      tipo: '',
      status: 'P',
      user_id: 0,
    },
  });

  const onSubmit = async (data: z.infer<typeof FormSchema>) => {
    try {
      const newExpense = await addExpense(data);
      if (newExpense) {
        console.log('Despesa adicionada:', newExpense);
        router.push('/');
      }
    } catch (error) {
      console.error('Erro ao adicionar despesa:', error);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="nome"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nome da Despesa</FormLabel>
              <FormControl>
                <Input placeholder="Ex: Aluguel" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="valor"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Valor</FormLabel>
              <FormControl>
                <Input type="number" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="vencimento"
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormLabel>Data de Vencimento</FormLabel>
              <Popover>
                <PopoverTrigger asChild>
                  <FormControl>
                    <Button
                      variant={'outline'}
                      className={cn(
                        'w-[240px] pl-3 text-left font-normal',
                        !field.value && 'text-muted-foreground'
                      )}
                    >
                      {field.value ? (
                        format(field.value, 'PPP', { locale: ptBR })
                      ) : (
                        <span>Escolha uma data</span>
                      )}
                      <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                    </Button>
                  </FormControl>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={field.value}
                    onSelect={field.onChange}
                    disabled={(date) =>
                      date < new Date('1900-01-01') || date > new Date('2100-01-01')
                    }
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="tipo"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Tipo de Despesa</FormLabel>
              <FormControl>
                <Input placeholder="Ex: Moradia" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="status"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Status</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o status" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="P">Pendente</SelectItem>
                  <SelectItem value="Q">Quitada</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="user_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Usuário</FormLabel>
              <FormControl>
                <Combobox
                  options={users.map((user) => ({ value: user.id, label: user.nome }))}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Adicionar Despesa</Button>
      </form>
    </Form>
  );
}
