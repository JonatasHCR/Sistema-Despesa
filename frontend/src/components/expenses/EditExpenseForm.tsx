/* eslint-disable @typescript-eslint/no-unsafe-assignment */
'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { CalendarIcon } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { ptBR } from 'date-fns/locale';
import { updateExpense } from '@/lib/api';
import { EXPENSE_STATUSES } from '@/lib/constants';
import { type Expense } from '@/lib/types';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const FormSchema = z.object({
  nome: z.string({ required_error: 'O nome da despesa é obrigatório.' }).min(1, 'O nome da despesa é obrigatório.'),
  valor: z.string().transform((val, ctx) => {
    const parsed = parseFloat(val.replace(',', '.'));
    if (isNaN(parsed)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Valor inválido. Use números e separe os centavos com vírgula ou ponto.',
      });
      return z.NEVER;
    }
    if (parsed <= 0) {
        ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: 'O valor deve ser maior que zero.',
        });
        return z.NEVER;
    }
    return parsed;
  }),
  vencimento: z.date({ required_error: 'A data de vencimento é obrigatória.' }),
  tipo: z.string({ required_error: 'O tipo da despesa é obrigatório.' }).min(1, 'O tipo da despesa é obrigatório.'),
  status: z.enum(EXPENSE_STATUSES, { required_error: 'O status da despesa é obrigatório.' }),
});

export function EditExpenseForm({ expense }: { expense: Expense }) {
  const router = useRouter();

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      nome: expense.nome,
      valor: String(expense.valor).replace('.', ','), // Format for display
      vencimento: new Date(expense.vencimento),
      tipo: expense.tipo,
      status: expense.status,
    },
  });

  const onSubmit = async (data: z.infer<typeof FormSchema>) => {
    try {
      const updatedExpense = await updateExpense(expense.id, data);
      if (updatedExpense) {
        console.log('Despesa atualizada:', updatedExpense);
        router.push('/');
      }
    } catch (error) {
      console.error('Erro ao atualizar despesa:', error);
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
                <Input type="text" inputMode='decimal' placeholder="123,45" {...field} />
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
                    // Re-enable date disabling if needed
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
        <Button type="submit">Salvar Alterações</Button>
      </form>
    </Form>
  );
}
