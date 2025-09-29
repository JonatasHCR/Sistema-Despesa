
'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Button } from '../ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '../ui/form';
import { Input } from '../ui/input';
import { useToast } from '../../hooks/use-toast';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardFooter } from '../ui/card';
import { Loader } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { CalendarIcon } from 'lucide-react';
import { Calendar } from '../ui/calendar';
import { cn } from '../../lib/utils';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { addExpense, getExpenses } from '../../lib/api';
import { type User, EXPENSE_STATUSES } from '../../lib/types';
import { Combobox } from '../ui/combobox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

const expenseFormSchema = z.object({
  nome: z.string().min(2, {
    message: 'O nome deve ter pelo menos 2 caracteres.',
  }),
  valor: z.string().refine((val) => {
    if (!val) return false;
    const formattedVal = val.replace(/\./g, '').replace(',', '.');
    return !isNaN(parseFloat(formattedVal));
  }, {
    message: 'O valor deve ser um número.',
  }),
  vencimento: z.date({
    required_error: 'A data de vencimento é obrigatória.',
  }),
  tipo: z.string().min(1, {
    message: 'Selecione ou crie um tipo de despesa.',
  }),
  status: z.enum(EXPENSE_STATUSES, {
    required_error: 'O status é obrigatório.',
  }),
  user_id: z.number().int().positive({
    message: 'ID do usuário é inválido.'
  }),
});

type ExpenseFormValues = z.infer<typeof expenseFormSchema>;

export function NewExpenseForm() {
  const router = useRouter();
  const { toast } = useToast();
  const [user, setUser] = useState<User | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [expenseTypes, setExpenseTypes] = useState<string[]>([]);
  
  const form = useForm<ExpenseFormValues & { userName?: string }>({
    resolver: zodResolver(expenseFormSchema),
    defaultValues: {
      nome: '',
      tipo: '',
      valor: '',
      status: 'P',
      vencimento: undefined,
      user_id: 0,
      userName: '',
    },
  });

  useEffect(() => {
    const session = localStorage.getItem('userSession');
    if (session) {
      const userData: User = JSON.parse(session);
      setUser(userData);
      form.setValue('user_id', userData.id);
      form.setValue('userName', userData.nome);
    }
  }, [form]);
  
  useEffect(() => {
    async function fetchExpenseTypes() {
        try {
            const expenses = await getExpenses();
            const types = new Set(expenses.map(e => e.tipo));
            setExpenseTypes(Array.from(types));
        } catch (error) {
            console.error("Failed to fetch expense types:", error);
            setExpenseTypes(['BOLETO', 'NOTA']);
        }
    }
    fetchExpenseTypes();
  }, []);

  async function onSubmit(data: ExpenseFormValues) {
    if (!user) return;
    setIsSubmitting(true);
    try {
      // Sanitize and convert form data before sending to the API
      const sanitizedValue = data.valor.replace(/\./g, '').replace(',', '.');
      const numericValue = parseFloat(sanitizedValue);

      if (isNaN(numericValue)) {
        toast({
          variant: 'destructive',
          title: 'Valor Inválido',
          description: 'O valor da despesa não é um número válido.',
        });
        setIsSubmitting(false);
        return;
      }
      
      const expensePayload = {
        ...data,
        valor: numericValue,
        vencimento: data.vencimento.toISOString().split('T')[0], // Format as YYYY-MM-DD
      };
      
      await addExpense(expensePayload);

      toast({
        title: 'Sucesso!',
        description: 'Nova despesa cadastrada.',
      });
      router.push('/');
      router.refresh();
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Uh oh! Algo deu errado.',
        description:
          (error as Error).message ||
          'Não foi possível cadastrar a despesa.',
      });
    } finally {
        setIsSubmitting(false);
    }
  }

  const comboboxOptions = useMemo(() => expenseTypes.map(type => ({ value: type, label: type })), [expenseTypes]);
  
  const handleTypeChange = (value: string) => {
    form.setValue('tipo', value);
    if (value && !expenseTypes.includes(value)) {
      setExpenseTypes(prev => [...prev, value]);
    }
  };

  return (
    <Card>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-0">
          <CardContent className="space-y-6 pt-6">
            <FormField
              control={form.control}
              name="nome"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome da Despesa</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Ex: Conta de Luz"
                      {...field}
                      onChange={(e) => field.onChange(e.target.value.toUpperCase())}
                      className="uppercase"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <FormField
                control={form.control}
                name="valor"
                render={({ field }) => (
                    <FormItem>
                    <FormLabel>Valor (R$)</FormLabel>
                    <FormControl>
                        <Input type="text" placeholder="150,75" {...field} />
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
                                'pl-3 text-left font-normal',
                                !field.value && 'text-muted-foreground'
                              )}
                            >
                              {field.value ? (
                                format(field.value, 'dd/MM/yyyy', { locale: ptBR })
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
                              date < new Date('1900-01-01')
                            }
                            initialFocus
                          />
                        </PopoverContent>
                      </Popover>
                      <FormMessage />
                    </FormItem>
                  )}
                />
            </div>
             <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <FormField
                control={form.control}
                name="tipo"
                render={({ field }) => (
                    <FormItem className="flex flex-col">
                    <FormLabel>Tipo de Despesa</FormLabel>
                        <Combobox
                        options={comboboxOptions}
                        value={field.value}
                        onChange={handleTypeChange}
                        placeholder="Selecione ou crie um tipo"
                        searchPlaceholder="Pesquisar ou criar..."
                        emptyMessage="Nenhum tipo encontrado. Crie um novo."
                        isCreatable={true}
                        />
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
            </div>
            <FormField
              control={form.control}
              name="userName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Usuário</FormLabel>
                  <FormControl>
                    <Input placeholder="Seu nome" {...field} disabled />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </CardContent>
          <CardFooter className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isSubmitting || !user}>
              {isSubmitting && <Loader className="mr-2 h-4 w-4 animate-spin" />}
              Cadastrar Despesa
            </Button>
          </CardFooter>
        </form>
      </Form>
    </Card>
  );
}
