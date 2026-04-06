
'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
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
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Loader, PlusCircle, Trash2, CalendarIcon } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Calendar } from '@/components/ui/calendar';
import { cn } from '@/lib/utils';
import { format, formatISO, addMonths } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { addExpense, getExpenses } from '@/lib/api';
import { type User, type Expense } from '@/lib/types';
import { Combobox } from '@/components/ui/combobox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';

const singleExpenseSchema = z.object({
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
  descricao: z.string().max(20, 'Máximo 20 caracteres').optional(),
  status: z.enum(['P', 'Q'], {
    required_error: 'O status é obrigatório.',
  }),
  user_id: z.number().int().positive(),
});

const expenseFormSchema = z.object({
  nome: z.string().min(2, {
    message: 'O nome deve ter pelo menos 2 caracteres.',
  }),
  despesas: z.array(singleExpenseSchema).min(1, 'Adicione pelo menos uma despesa.'),
});

type ExpenseFormValues = z.infer<typeof expenseFormSchema>;

export function NewExpenseForm() {
  const router = useRouter();
  const { toast } = useToast();
  const [user, setUser] = useState<User | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [expenseTypes, setExpenseTypes] = useState<string[]>([]);
  const [expenseNames, setExpenseNames] = useState<string[]>([]);
  
  useEffect(() => {
    const session = localStorage.getItem('userSession');
    if (session) {
      const userData: User = JSON.parse(session);
      setUser(userData);
    } else {
        router.replace('/login');
    }
  }, [router]);
  
  const form = useForm<ExpenseFormValues>({
    resolver: zodResolver(expenseFormSchema),
    defaultValues: {
      nome: '',
      despesas: [
        {
          valor: '',
          vencimento: new Date(),
          tipo: '',
          descricao: 'PARCELA ÚNICA',
          status: 'P',
          user_id: 0,
        },
      ],
    },
  });

  useEffect(() => {
    if (user) {
      const despesas = form.getValues('despesas');
      if (despesas.length > 0 && despesas[0].user_id === 0) {
        form.setValue('despesas.0.user_id', user.id);
      }
    }
  }, [user, form]);

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "despesas"
  });

  // Automatically update descriptions based on installments
  useEffect(() => {
    const total = fields.length;
    if (total > 1) {
      fields.forEach((_, index) => {
        form.setValue(`despesas.${index}.descricao`, `PARCELA ${index + 1}/${total}`);
      });
    } else if (total === 1) {
      const currentDesc = form.getValues('despesas.0.descricao');
      // Only reset to 'PARCELA ÚNICA' if it was part of a sequence
      if (currentDesc?.startsWith('PARCELA ') && currentDesc?.includes('/')) {
        form.setValue('despesas.0.descricao', 'PARCELA ÚNICA');
      }
    }
  }, [fields.length, form]);
  
  useEffect(() => {
    async function fetchData() {
        try {
            const expenses = await getExpenses();
            if (expenses) {
                const types = new Set(expenses.map(e => e.tipo));
                const names = new Set(expenses.map(e => e.nome));
                setExpenseTypes(Array.from(types));
                setExpenseNames(Array.from(names));
            }
        } catch (error) {
            console.error("Failed to fetch expense data:", error);
            setExpenseTypes(['BOLETO', 'NOTA']); 
        }
    }
    fetchData();
  }, []);

  async function onSubmit(data: ExpenseFormValues) {
    if (!user) return;
    setIsSubmitting(true);

    try {
      const expensesToCreate = data.despesas.map(d => ({
        ...d,
        nome: data.nome,
        descricao: d.descricao || "PARCELA ÚNICA",
        user_id: user.id,
        vencimento: formatISO(d.vencimento),
      }));

      await addExpense(expensesToCreate as Omit<Expense, 'id' | 'userName' | 'dynamicStatus'>[]);

      toast({
        title: 'Sucesso!',
        description: `${expensesToCreate.length} nova(s) despesa(s) cadastrada(s).`,
      });
      router.push('/');
      router.refresh();
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Uh oh! Algo deu errado.',
        description:
          (error as Error).message ||
          'Não foi possível cadastrar as despesas.',
      });
    } finally {
        setIsSubmitting(false);
    }
  }

  const typeOptions = useMemo(() => expenseTypes.map(type => ({ value: type, label: type })), [expenseTypes]);
  const nameOptions = useMemo(() => expenseNames.map(name => ({ value: name, label: name })), [expenseNames]);
  
  const handleNameChange = (value: string) => {
    form.setValue('nome', value);
    if (value && !expenseNames.includes(value)) {
      setExpenseNames(prev => [...prev, value]);
    }
  };

  const handleTypeChange = (value: string, index: number) => {
    form.setValue(`despesas.${index}.tipo`, value);
    if (value && !expenseTypes.includes(value)) {
      setExpenseTypes(prev => [...prev, value]);
    }
  };

  const addExpenseField = () => {
    if (user) {
        const despesas = form.getValues('despesas');
        const lastExpense = despesas[despesas.length - 1];
        const newVencimento = lastExpense ? addMonths(lastExpense.vencimento, 1) : new Date();

        append({
            valor: lastExpense?.valor || '',
            vencimento: newVencimento,
            tipo: lastExpense?.tipo || '',
            descricao: 'PARCELA ÚNICA', // Will be updated by useEffect
            status: 'P',
            user_id: user.id
        });
    }
  };

  if (!user) {
    return (
        <div className="flex h-screen w-full items-center justify-center">
            <Loader className="h-8 w-8 animate-spin text-primary" />
        </div>
    );
  }

  return (
    <Card>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-0">
          <CardContent className="space-y-6 pt-6">
            <FormField
              control={form.control}
              name="nome"
              render={({ field }) => (
                <FormItem className="flex flex-col">
                  <FormLabel>Nome da Despesa</FormLabel>
                    <Combobox
                        options={nameOptions}
                        value={field.value}
                        onChange={handleNameChange}
                        placeholder="Selecione ou crie uma despesa"
                        searchPlaceholder="Pesquisar ou criar..."
                        emptyMessage="Nenhuma despesa encontrada. Crie uma nova."
                        isCreatable={true}
                    />
                  <FormMessage />
                </FormItem>
              )}
            />

            <Separator />

            {fields.map((field, index) => (
                <div key={field.id} className="space-y-4 rounded-lg border p-4 relative">
                    <h4 className="text-sm font-medium text-muted-foreground">Despesa #{index + 1}</h4>
                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                        <FormField
                            control={form.control}
                            name={`despesas.${index}.valor`}
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
                            name={`despesas.${index}.descricao`}
                            render={({ field }) => (
                                <FormItem>
                                <FormLabel>Descrição (Max 20 carac.)</FormLabel>
                                <FormControl>
                                    <Input placeholder="PARCELA ÚNICA" maxLength={20} {...field} />
                                </FormControl>
                                <FormMessage />
                                </FormItem>
                            )}
                        />
                    </div>
                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                        <Controller
                            control={form.control}
                            name={`despesas.${index}.vencimento`}
                            render={({ field, fieldState }) => (
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
                                <FormMessage>{fieldState.error?.message}</FormMessage>
                                </FormItem>
                            )}
                        />
                         <Controller
                            control={form.control}
                            name={`despesas.${index}.tipo`}
                            render={({ field }) => (
                                <FormItem className="flex flex-col">
                                <FormLabel>Tipo de Despesa</FormLabel>
                                    <Combobox
                                        options={typeOptions}
                                        value={field.value}
                                        onChange={(value) => handleTypeChange(value, index)}
                                        placeholder="Selecione ou crie um tipo"
                                        searchPlaceholder="Pesquisar ou criar..."
                                        emptyMessage="Nenhum tipo encontrado. Crie um novo."
                                        isCreatable={true}
                                    />
                                <FormMessage />
                                </FormItem>
                            )}
                        />
                    </div>
                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                        <FormField
                            control={form.control}
                            name={`despesas.${index}.status`}
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
                     {fields.length > 1 && (
                        <Button
                            type="button"
                            variant="destructive"
                            size="icon"
                            className="absolute -top-3 -right-3 h-7 w-7"
                            onClick={() => remove(index)}
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    )}
                </div>
            ))}
             <Button type="button" variant="outline" onClick={addExpenseField} className="w-full">
              <PlusCircle className="mr-2 h-4 w-4" />
              Adicionar outra despesa
            </Button>
          </CardContent>
          <CardFooter className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isSubmitting || !user}>
              {isSubmitting && <Loader className="mr-2 h-4 w-4 animate-spin" />}
              Cadastrar Despesas
            </Button>
          </CardFooter>
        </form>
      </Form>
    </Card>
  );
}
