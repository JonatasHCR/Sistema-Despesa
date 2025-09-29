'use client';

import { useState, useMemo, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { type Expense, type ExpenseStatus, type DynamicExpenseStatus } from '../../lib/types';
import { ExpenseCard } from './ExpenseCard';
import { StatusCard } from './StatusCard';
import { Ban, Loader, ChevronLeft, ChevronRight, Search, Filter, CalendarIcon, Receipt, Hourglass, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Skeleton } from '../ui/skeleton';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { Calendar } from '../ui/calendar';
import { format, isSameDay, parseISO, differenceInDays, isPast, isToday } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { cn } from '../../lib/utils';
import { getExpenses } from '../../lib/api';

type FilterField = 'nome' | 'tipo' | 'vencimento' | 'userName' | 'status';

function DashboardSkeleton() {
    return (
        <div className="flex flex-col gap-8">
             <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <CardSkeleton />
                <CardSkeleton />
                <CardSkeleton />
                <CardSkeleton />
            </div>
            <div className="rounded-xl border bg-card text-card-foreground shadow-sm">
                <div className="flex flex-col space-y-1.5 p-6">
                    <Skeleton className="h-8 w-48" />
                    <Skeleton className="h-6 w-32" />
                </div>
                <div className="p-6 pt-0">
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                        {[...Array(3)].map((_, i) => (
                           <CardSkeleton key={i} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

function CardSkeleton() {
    return (
      <div className="flex flex-col space-y-3">
        <Skeleton className="h-[125px] w-full rounded-xl" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-[250px]" />
          <Skeleton className="h-4 w-[200px]" />
        </div>
      </div>
    )
  }

const getDynamicStatus = (expense: Expense, dueSoonDays: number): DynamicExpenseStatus => {
    if (expense.status === 'Q') return 'paid';
    
    const daysUntilDue = differenceInDays(parseISO(expense.vencimento), new Date());
    
    if (isPast(parseISO(expense.vencimento)) && !isToday(parseISO(expense.vencimento))) return 'overdue';
    if (daysUntilDue >= 0 && daysUntilDue <= dueSoonDays) return 'due-soon';
    return 'due';
};

export function ExpenseDashboard() {
  const [rawExpenses, setRawExpenses] = useState<Expense[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(6);
  const [filterField, setFilterField] = useState<FilterField>('nome');
  const [filterValue, setFilterValue] = useState<string | Date | undefined>('');
  const [selectedStatus, setSelectedStatus] = useState<DynamicExpenseStatus | 'all'>('all');
  const [dueSoonDays, setDueSoonDays] = useState(5);

  const fetchAndSetExpenses = useCallback(async () => {
    // Keep loading indicator only for the first load.
    if (rawExpenses.length === 0) {
      setIsLoading(true);
    }
    try {
        const data = await getExpenses();
        setRawExpenses(data || []);
    } catch (error) {
        console.error("Failed to fetch expenses:", error);
        setRawExpenses([]);
    } finally {
        setIsLoading(false);
    }
  }, [rawExpenses.length]);

  useEffect(() => {
    fetchAndSetExpenses();

    const interval = setInterval(() => {
        fetchAndSetExpenses();
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval); // Cleanup interval on component unmount
  }, [fetchAndSetExpenses]);

  const expensesWithDynamicStatus = useMemo(() => {
    return rawExpenses.map(e => ({
        ...e,
        dynamicStatus: getDynamicStatus(e, dueSoonDays)
    }));
  }, [rawExpenses, dueSoonDays]);

  const statusCounts = useMemo(() => {
    return expensesWithDynamicStatus.reduce(
      (acc, e) => {
        acc[e.dynamicStatus]++;
        return acc;
      },
      { overdue: 0, 'due-soon': 0, due: 0, paid: 0 }
    );
  }, [expensesWithDynamicStatus]);


  const expenseTypes = useMemo(() => {
    const types = new Set(rawExpenses.map(e => e.tipo));
    return ['Todos', ...Array.from(types)];
  }, [rawExpenses]);

  const expenseStatuses: { value: ExpenseStatus | 'Todos', label: string }[] = [
    { value: 'Todos', label: 'Todos' },
    { value: 'P', label: 'Pendente' },
    { value: 'Q', label: 'Quitada' },
  ];
  
  useEffect(() => {
    if (filterField === 'vencimento') {
      setFilterValue(undefined);
    } else if (filterField === 'tipo' || filterField === 'status') {
      setFilterValue('Todos');
    } else {
      setFilterValue('');
    }
  }, [filterField]);

  const filteredExpenses = useMemo(() => {
    let filtered = expensesWithDynamicStatus;

    if (selectedStatus !== 'all') {
        filtered = filtered.filter(e => e.dynamicStatus === selectedStatus);
    }
    
    return filtered.filter((e) => {
        if (filterValue === undefined || filterValue === '' || filterValue === 'Todos') return true;

        switch (filterField) {
            case 'nome':
                return typeof filterValue === 'string' && e.nome.toLowerCase().startsWith(filterValue.toLowerCase());
            case 'userName':
                return typeof filterValue === 'string' && (e.userName?.toLowerCase().startsWith(filterValue.toLowerCase()) ?? false);
            case 'tipo':
                 return e.tipo === filterValue;
            case 'status':
                return e.status === filterValue;
            case 'vencimento':
                return filterValue instanceof Date && isSameDay(parseISO(e.vencimento), filterValue);
            default:
                return true;
        }
    });
  }, [expensesWithDynamicStatus, filterField, filterValue, selectedStatus]);
  
  useEffect(() => {
    setCurrentPage(1);
  }, [itemsPerPage, filterField, filterValue, selectedStatus]);

  const totalPages = Math.ceil(filteredExpenses.length / itemsPerPage) || 1;
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentExpenses = filteredExpenses.slice(indexOfFirstItem, indexOfLastItem);

  const totalAmount = useMemo(() => {
    return currentExpenses.reduce((sum, expense) => sum + expense.valor, 0);
  }, [currentExpenses]);
  
  const renderFilterInput = () => {
    switch (filterField) {
        case 'vencimento':
            return (
                <Popover>
                    <PopoverTrigger asChild>
                        <Button
                            variant={'outline'}
                            className={cn(
                                'w-full sm:w-64 justify-start text-left font-normal',
                                !filterValue && 'text-muted-foreground'
                            )}
                        >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {filterValue instanceof Date ? format(filterValue, 'PPP', { locale: ptBR }) : <span>Escolha uma data</span>}
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                        <Calendar
                            mode="single"
                            selected={filterValue instanceof Date ? filterValue : undefined}
                            onSelect={(date) => setFilterValue(date)}
                            initialFocus
                        />
                    </PopoverContent>
                </Popover>
            );
        case 'tipo':
            return (
                 <Select value={filterValue as string || 'Todos'} onValueChange={(value) => setFilterValue(value)}>
                    <SelectTrigger className="w-full sm:w-64">
                        <SelectValue placeholder="Filtrar por tipo" />
                    </SelectTrigger>
                    <SelectContent>
                        {expenseTypes.map((type) => (
                            <SelectItem key={type} value={type}>{type}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            );
        case 'status':
            return (
                <Select value={filterValue as string || 'Todos'} onValueChange={(value) => setFilterValue(value)}>
                    <SelectTrigger className="w-full sm:w-64">
                        <SelectValue placeholder="Filtrar por status" />
                    </SelectTrigger>
                    <SelectContent>
                        {expenseStatuses.map((status) => (
                            <SelectItem key={status.value} value={status.value}>{status.label}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            );
        case 'nome':
        case 'userName':
        default:
            return (
                <div className="relative w-full sm:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        type="search"
                        placeholder="Pesquisar..."
                        value={filterValue as string || ''}
                        onChange={(e) => setFilterValue(e.target.value)}
                        className="pl-10"
                    />
                </div>
            );
    }
  }

  if (isLoading && rawExpenses.length === 0) {
    return <DashboardSkeleton />;
  }

  const handleStatusCardClick = (status: DynamicExpenseStatus) => {
    setSelectedStatus(prev => prev === status ? 'all' : status);
  };

  return (
    <div className="flex flex-col gap-8">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatusCard 
                title="Vencidos"
                icon={<AlertTriangle className="h-5 w-5" />}
                count={statusCounts.overdue}
                status="overdue"
                isSelected={selectedStatus === 'overdue'}
                onClick={() => handleStatusCardClick('overdue')}
            />
            <StatusCard 
                title="Vencendo"
                icon={<Hourglass className="h-5 w-5" />}
                count={statusCounts['due-soon']}
                status="due-soon"
                isSelected={selectedStatus === 'due-soon'}
                onClick={() => handleStatusCardClick('due-soon')}
                dueSoonDays={dueSoonDays}
                setDueSoonDays={setDueSoonDays}
            />
            <StatusCard 
                title="A vencer"
                icon={<Receipt className="h-5 w-5" />}
                count={statusCounts.due}
                status="due"
                isSelected={selectedStatus === 'due'}
                onClick={() => handleStatusCardClick('due')}
            />
            <StatusCard 
                title="Pagos"
                icon={<CheckCircle2 className="h-5 w-5" />}
                count={statusCounts.paid}
                status="paid"
                isSelected={selectedStatus === 'paid'}
                onClick={() => handleStatusCardClick('paid')}
            />
        </div>
      <div className="rounded-xl border bg-card text-card-foreground shadow-sm relative">
        {isLoading && rawExpenses.length > 0 && (
          <div className="absolute inset-0 bg-background/50 flex items-center justify-center z-10">
            <Loader className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}
        <div className="flex flex-col space-y-4 p-6">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <h3 className="font-headline text-2xl font-semibold leading-none tracking-tight w-full sm:w-auto">
                    Despesas
                </h3>
                <div className="flex items-center gap-4 w-full sm:w-auto flex-wrap">
                    <div className="flex items-center gap-2">
                        <Filter className="h-4 w-4 text-muted-foreground" />
                        <Select value={filterField} onValueChange={(value) => setFilterField(value as FilterField)}>
                            <SelectTrigger className="w-full sm:w-48">
                                <SelectValue placeholder="Filtrar por..." />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="nome">Nome da Despesa</SelectItem>
                                <SelectItem value="tipo">Tipo</SelectItem>
                                <SelectItem value="status">Status</SelectItem>
                                <SelectItem value="vencimento">Data de Vencimento</SelectItem>
                                <SelectItem value="userName">Criado por</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    {renderFilterInput()}
                </div>
            </div>
             <div className="flex items-center justify-end gap-2 text-lg font-semibold text-muted-foreground">
                <span>
                    {totalAmount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </span>
            </div>
        </div>
        <div className="p-6 pt-0">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentPage + itemsPerPage + filterField + String(filterValue) + selectedStatus}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="min-h-[300px]"
            >
              {currentExpenses.length > 0 ? (
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {currentExpenses.map((expense, index) => (
                    <motion.div
                      key={expense.id}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <ExpenseCard expense={expense} onUpdate={fetchAndSetExpenses} />
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="flex h-full min-h-[300px] flex-col items-center justify-center gap-4 rounded-lg border-2 border-dashed border-border bg-background/50 p-12 text-center">
                    <div className="rounded-full bg-secondary p-4">
                        <Ban className="h-12 w-12 text-muted-foreground" />
                    </div>
                    <p className="font-headline text-lg font-medium text-muted-foreground">
                        Nenhuma despesa encontrada
                    </p>
                    <p className="max-w-xs text-sm text-muted-foreground">
                        Tente ajustar seus filtros ou cadastre uma nova despesa.
                    </p>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
        {filteredExpenses.length > 0 && (
          <div className="flex items-center justify-between border-t p-4">
            <div className="flex items-center gap-2">
              <Label htmlFor="items-per-page" className="text-sm text-muted-foreground">Itens por página:</Label>
              <Input
                id="items-per-page"
                type="number"
                value={itemsPerPage}
                onChange={(e) => setItemsPerPage(Math.max(1, parseInt(e.target.value, 10) || 1))}
                className="h-8 w-20"
                min="1"
              />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                Página {currentPage} de {totalPages}
              </span>
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
