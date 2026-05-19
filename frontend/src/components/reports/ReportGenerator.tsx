'use client';

import { useState, useMemo, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { format, parseISO, startOfDay, endOfDay, isPast, isToday, differenceInDays } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { CalendarIcon, Printer, Loader, Search, X, RefreshCw } from 'lucide-react';
import { getExpenses, getStoredUser } from '@/lib/api';
import { type Expense, type DynamicExpenseStatus, type User } from '@/lib/types';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ScrollArea } from '@/components/ui/scroll-area';

interface ReportSnapshot {
  expenses: Expense[];
  generatedAt: Date;
  filters: {
    startDate?: Date;
    endDate?: Date;
    selectedType: string;
    dueSoonDays: number;
  };
}

export function ReportGenerator() {
  const { toast } = useToast();
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const [startDate, setStartDate] = useState<Date | undefined>();
  const [endDate, setEndDate] = useState<Date | undefined>();
  const [minAmount, setMinAmount] = useState<string>('');
  const [maxAmount, setMaxAmount] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedNames, setSelectedNames] = useState<string[]>([]);
  const [nameSearch, setNameSearch] = useState('');

  const [includeOverdue, setIncludeOverdue] = useState(true);
  const [includeDueSoon, setIncludeDueSoon] = useState(true);
  const [includeDue, setIncludeDue] = useState(false);

  const [dueSoonDays, setDueSoonDays] = useState(6);
  const [report, setReport] = useState<ReportSnapshot | null>(null);

  const fetchExpenses = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getExpenses();
      setExpenses(data || []);
    } catch (error) {
      console.error("Erro ao carregar despesas:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchExpenses();
    setCurrentUser(getStoredUser());
  }, [fetchExpenses]);

  const types = useMemo(() => {
    const uniqueTypes = new Set(expenses.map(e => e.tipo));
    return Array.from(uniqueTypes).sort();
  }, [expenses]);

  const uniqueNames = useMemo(() => {
    const names = new Set(expenses.map(e => e.nome));
    return Array.from(names).sort();
  }, [expenses]);

  const filteredNameOptions = useMemo(() => {
    if (!nameSearch.trim()) return uniqueNames;
    const needle = nameSearch.toLowerCase();
    return uniqueNames.filter(n => n.toLowerCase().includes(needle));
  }, [uniqueNames, nameSearch]);

  const handleToggleName = (name: string) => {
    setSelectedNames(prev => 
      prev.includes(name) 
        ? prev.filter(n => n !== name) 
        : [...prev, name]
    );
  };

  const handleSelectAllNames = () => {
    if (selectedNames.length === uniqueNames.length) {
      setSelectedNames([]);
    } else {
      setSelectedNames([...uniqueNames]);
    }
  };

  const getStatusInfo = (expense: Expense): { status: DynamicExpenseStatus; label: string; colorClass: string } => {
    const dueDate = parseISO(expense.vencimento);
    const daysUntilDue = differenceInDays(dueDate, startOfDay(new Date()));
    
    if (isPast(dueDate) && !isToday(dueDate)) {
        return { status: 'overdue', label: 'Vencida', colorClass: 'bg-red-100 text-red-600 border-red-200' };
    }
    if (daysUntilDue >= 0 && daysUntilDue <= dueSoonDays) {
        return { status: 'due-soon', label: 'A Vencer', colorClass: 'bg-yellow-100 text-yellow-700 border-yellow-200' };
    }
    return { status: 'due', label: 'Futura', colorClass: 'bg-green-100 text-green-700 border-green-200' };
  };

  const handleGenerateReport = () => {
    const min = parseFloat(minAmount.replace(/\./g, '').replace(',', '.'));
    const max = parseFloat(maxAmount.replace(/\./g, '').replace(',', '.'));
    const startBoundary = startDate ? startOfDay(startDate) : null;
    const endBoundary = endDate ? endOfDay(endDate) : null;

    const filtered = expenses.filter(expense => {
      if (expense.status === 'Q') return false;

      const info = getStatusInfo(expense);

      if (!includeOverdue && info.status === 'overdue') return false;
      if (!includeDueSoon && info.status === 'due-soon') return false;
      if (!includeDue && info.status === 'due') return false;

      const expenseDate = parseISO(expense.vencimento);
      if (startBoundary && expenseDate < startBoundary) return false;
      if (endBoundary && expenseDate > endBoundary) return false;

      if (!isNaN(min) && expense.valor < min) return false;
      if (!isNaN(max) && expense.valor > max) return false;

      if (selectedType !== 'all' && expense.tipo !== selectedType) return false;
      if (selectedNames.length > 0 && !selectedNames.includes(expense.nome)) return false;

      return true;
    });

    if (filtered.length === 0) {
      toast({
        title: 'Nenhuma despesa encontrada',
        description: 'Ajuste os filtros e tente novamente.',
      });
      setReport(null);
      return;
    }

    const sorted = filtered.sort((a, b) => {
      if (a.tipo !== b.tipo) return a.tipo.localeCompare(b.tipo);
      return parseISO(a.vencimento).getTime() - parseISO(b.vencimento).getTime();
    });

    setReport({
      expenses: sorted,
      generatedAt: new Date(),
      filters: { startDate, endDate, selectedType, dueSoonDays },
    });
  };

  const clearFilters = () => {
    setStartDate(undefined);
    setEndDate(undefined);
    setMinAmount('');
    setMaxAmount('');
    setSelectedType('all');
    setSelectedNames([]);
    setIncludeOverdue(true);
    setIncludeDueSoon(true);
    setIncludeDue(false);
    setReport(null);
  };

  const handlePrint = () => {
    window.print();
  };

  const totalAmount = useMemo(() => {
    if (!report) return 0;
    return report.expenses.reduce((sum, e) => sum + Number(e.valor), 0);
  }, [report]);

  const groupedData = useMemo(() => {
    if (!report) return {};
    return report.expenses.reduce((acc, expense) => {
      if (!acc[expense.tipo]) acc[expense.tipo] = [];
      acc[expense.tipo].push(expense);
      return acc;
    }, {} as Record<string, Expense[]>);
  }, [report]);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 pb-10">
      <Card className="print:hidden">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Configurar Relatório</CardTitle>
            <CardDescription>Escolha os critérios para filtrar as despesas pendentes.</CardDescription>
          </div>
          <Button variant="outline" size="icon" onClick={fetchExpenses} title="Atualizar dados">
            <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-2">
              <Label>Situação</Label>
              <div className="flex flex-col gap-2 pt-2">
                <div className="flex items-center space-x-2">
                  <Checkbox id="filter-overdue" checked={includeOverdue} onCheckedChange={(val) => setIncludeOverdue(!!val)} />
                  <Label htmlFor="filter-overdue" className="text-xs font-bold text-red-600">Vencidas</Label>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  <Checkbox id="filter-due-soon" checked={includeDueSoon} onCheckedChange={(val) => setIncludeDueSoon(!!val)} />
                  <Label htmlFor="filter-due-soon" className="text-xs font-bold text-yellow-600">A Vencer em até</Label>
                  <Input
                    type="number"
                    min={0}
                    className="h-7 w-14"
                    value={dueSoonDays}
                    onChange={(e) => {
                      const v = parseInt(e.target.value, 10);
                      setDueSoonDays(isNaN(v) || v < 0 ? 0 : v);
                    }}
                  />
                  <span className="text-xs text-muted-foreground">dias</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="filter-due" checked={includeDue} onCheckedChange={(val) => setIncludeDue(!!val)} />
                  <Label htmlFor="filter-due" className="text-xs font-bold text-green-600">Outras Futuras</Label>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Período de Vencimento</Label>
              <div className="flex gap-2">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !startDate && "text-muted-foreground")}>
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {startDate ? format(startDate, 'dd/MM/yy') : "Início"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar mode="single" selected={startDate} onSelect={setStartDate} initialFocus />
                  </PopoverContent>
                </Popover>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !endDate && "text-muted-foreground")}>
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {endDate ? format(endDate, 'dd/MM/yy') : "Fim"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar mode="single" selected={endDate} onSelect={setEndDate} initialFocus />
                  </PopoverContent>
                </Popover>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Faixa de Valor (R$)</Label>
              <div className="flex gap-2">
                <Input placeholder="Mínimo" value={minAmount} onChange={(e) => setMinAmount(e.target.value)} />
                <Input placeholder="Máximo" value={maxAmount} onChange={(e) => setMaxAmount(e.target.value)} />
              </div>
            </div>

             <div className="space-y-2">
              <Label>Grupo (Tipo)</Label>
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os tipos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os tipos</SelectItem>
                  {types.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <Label className="text-base font-semibold">Selecionar Contas Específicas</Label>
                <Button variant="ghost" size="sm" onClick={handleSelectAllNames}>
                    {selectedNames.length === uniqueNames.length && uniqueNames.length > 0 ? "Desmarcar Todas" : "Selecionar Todas"}
                </Button>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Pesquisar conta..."
                value={nameSearch}
                onChange={(e) => setNameSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <Card className="bg-muted/30">
                <ScrollArea className="h-48 p-4">
                    {filteredNameOptions.length === 0 ? (
                        <p className="text-center text-xs text-muted-foreground py-8">
                            Nenhuma conta corresponde à busca.
                        </p>
                    ) : (
                        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                            {filteredNameOptions.map((name) => (
                                <div key={name} className="flex items-center space-x-2">
                                    <Checkbox
                                        id={`name-${name}`}
                                        checked={selectedNames.includes(name)}
                                        onCheckedChange={() => handleToggleName(name)}
                                    />
                                    <Label
                                        htmlFor={`name-${name}`}
                                        className="cursor-pointer text-xs font-normal truncate"
                                        title={name}
                                    >
                                        {name}
                                    </Label>
                                </div>
                            ))}
                        </div>
                    )}
                </ScrollArea>
            </Card>
          </div>

          <div className="flex flex-col gap-2 pt-4 sm:flex-row sm:justify-end">
            <Button variant="ghost" onClick={clearFilters}>
              <X className="mr-2 h-4 w-4" /> Limpar Filtros
            </Button>
            <Button onClick={handleGenerateReport}>
              <Search className="mr-2 h-4 w-4" />
              Gerar Relatório
            </Button>
          </div>
        </CardContent>
      </Card>

      {report && (
        <div className="space-y-6">
          <div className="flex flex-col gap-2 print:hidden sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-xl font-semibold">Resultado do Relatório ({report.expenses.length})</h2>
            <Button variant="outline" onClick={handlePrint}>
              <Printer className="mr-2 h-4 w-4" /> Imprimir Relatório
            </Button>
          </div>

          <Card className="print:border-none print:shadow-none">
            <CardHeader className="relative pb-2">
              <div className="flex flex-col items-center justify-center pt-8">
                <CardTitle className="text-xl sm:text-2xl font-headline text-center">Relatório de Despesas Pendentes</CardTitle>
                <CardDescription className="text-xs text-center mt-1">
                    Emitido em {format(report.generatedAt, "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                    {currentUser && ` por ${currentUser.nome}`}
                    <div className="mt-1 print:block">
                    {report.filters.startDate && `Início: ${format(report.filters.startDate, 'dd/MM/yy')} | `}
                    {report.filters.endDate && `Fim: ${format(report.filters.endDate, 'dd/MM/yy')} | `}
                    {report.filters.selectedType !== 'all' && `Grupo: ${report.filters.selectedType} | `}
                    </div>
                </CardDescription>
              </div>
            </CardHeader>
            <CardContent className="px-2 sm:px-6">
              <div className="mb-6 grid grid-cols-2 gap-4 rounded-lg border bg-muted/30 p-4 print:bg-gray-50">
                <div className="flex flex-col">
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Quantidade</span>
                  <span className="text-base sm:text-lg font-bold">{report.expenses.length} Itens Pendentes</span>
                </div>
                <div className="flex flex-col text-right">
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Total em Aberto</span>
                  <span className="text-base sm:text-lg font-bold text-destructive">
                    {totalAmount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </span>
                </div>
              </div>

              <div className="space-y-8">
                {Object.entries(groupedData).map(([tipo, items]) => (
                  <div key={tipo} className="space-y-2">
                    <div className="flex items-center justify-between border-b border-primary/30 pb-1">
                      <h3 className="text-xs print:text-[10px] font-bold uppercase tracking-tight text-primary">{tipo}</h3>
                    </div>
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader className="bg-muted/20">
                          <TableRow className="h-8">
                            <TableHead className="text-xs print:text-[10px] h-8 w-[90px]">Vencimento</TableHead>
                            <TableHead className="text-xs print:text-[10px] h-8">Nome</TableHead>
                            <TableHead className="text-xs print:text-[10px] h-8 w-[100px]">Info</TableHead>
                            <TableHead className="text-xs print:text-[10px] h-8 w-[100px]">Situação</TableHead>
                            <TableHead className="text-xs print:text-[10px] h-8 text-right w-[100px]">Valor</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {items.map((expense) => {
                            const info = getStatusInfo(expense);
                            return (
                              <TableRow key={expense.id} className="h-8 border-b border-muted/30">
                                <TableCell className="text-xs print:text-[10px] py-1">
                                  {format(parseISO(expense.vencimento), 'dd/MM/yyyy')}
                                </TableCell>
                                <TableCell className="text-xs print:text-[10px] py-1 font-medium">
                                  {expense.nome}
                                </TableCell>
                                <TableCell className="text-xs print:text-[10px] py-1 text-muted-foreground">
                                  {expense.descricao || "PARCELA ÚNICA"}
                                </TableCell>
                                <TableCell className="text-xs print:text-[10px] py-1">
                                  <span className={cn(
                                    "px-1.5 py-0.5 rounded-sm font-bold border whitespace-nowrap",
                                    info.colorClass
                                  )}>
                                    {info.label}
                                  </span>
                                </TableCell>
                                <TableCell className="text-xs print:text-[10px] py-1 text-right font-bold whitespace-nowrap">
                                  {Number(expense.valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </TableCell>
                              </TableRow>
                            );
                          })}
                        </TableBody>
                      </Table>
                    </div>
                    <div className="flex justify-end pt-1">
                      <span className="text-xs print:text-[10px] font-bold">
                        Subtotal {tipo}: {items.reduce((sum, i) => sum + Number(i.valor), 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-12 hidden border-t pt-2 text-center text-[9px] text-muted-foreground print:block">
                Controle interno de pagamentos - UFC Engenharia.
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
