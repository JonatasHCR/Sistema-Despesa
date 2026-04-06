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
import { getExpenses } from '@/lib/api';
import { type Expense, type DynamicExpenseStatus, type User } from '@/lib/types';
import { cn } from '@/lib/utils';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ScrollArea } from '@/components/ui/scroll-area';

export function ReportGenerator() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  
  const [startDate, setStartDate] = useState<Date | undefined>();
  const [endDate, setEndDate] = useState<Date | undefined>();
  const [minAmount, setMinAmount] = useState<string>('');
  const [maxAmount, setMaxAmount] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedNames, setSelectedNames] = useState<string[]>([]);
  
  const [includeOverdue, setIncludeOverdue] = useState(true);
  const [includeDueSoon, setIncludeDueSoon] = useState(true);
  const [includeDue, setIncludeDue] = useState(false);
  
  const [dueSoonDays, setDueSoonDays] = useState(6);
  const [reportData, setReportData] = useState<Expense[] | null>(null);

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
    const session = localStorage.getItem('userSession');
    if (session) {
      setCurrentUser(JSON.parse(session));
    }
  }, [fetchExpenses]);

  const types = useMemo(() => {
    const uniqueTypes = new Set(expenses.map(e => e.tipo));
    return Array.from(uniqueTypes).sort();
  }, [expenses]);

  const uniqueNames = useMemo(() => {
    const names = new Set(expenses.map(e => e.nome));
    return Array.from(names).sort();
  }, [expenses]);

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
    setIsGenerating(true);
    
    const filtered = expenses.filter(expense => {
      if (expense.status === 'Q') return false;

      const info = getStatusInfo(expense);
      
      if (!includeOverdue && info.status === 'overdue') return false;
      if (!includeDueSoon && info.status === 'due-soon') return false;
      if (!includeDue && info.status === 'due') return false;

      const expenseDate = parseISO(expense.vencimento);
      if (startDate && expenseDate < startOfDay(startDate)) return false;
      if (endDate && expenseDate > endOfDay(endDate)) return false;
      
      const expenseAmount = expense.valor;
      const min = parseFloat(minAmount.replace(/\./g, '').replace(',', '.'));
      const max = parseFloat(maxAmount.replace(/\./g, '').replace(',', '.'));
      if (!isNaN(min) && expenseAmount < min) return false;
      if (!isNaN(max) && expenseAmount > max) return false;
      
      if (selectedType !== 'all' && expense.tipo !== selectedType) return false;
      if (selectedNames.length > 0 && !selectedNames.includes(expense.nome)) return false;
      
      return true;
    });

    setReportData(filtered.sort((a, b) => {
      if (a.tipo !== b.tipo) return a.tipo.localeCompare(b.tipo);
      return parseISO(a.vencimento).getTime() - parseISO(b.vencimento).getTime();
    }));
    setIsGenerating(false);
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
    setReportData(null);
  };

  const handlePrint = () => {
    window.print();
  };

  const totalAmount = useMemo(() => {
    if (!reportData) return 0;
    return reportData.reduce((sum, e) => sum + Number(e.valor), 0);
  }, [reportData]);

  const groupedData = useMemo(() => {
    if (!reportData) return {};
    return reportData.reduce((acc, expense) => {
      if (!acc[expense.tipo]) acc[expense.tipo] = [];
      acc[expense.tipo].push(expense);
      return acc;
    }, {} as Record<string, Expense[]>);
  }, [reportData]);

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
                <div className="flex items-center space-x-2">
                  <Checkbox id="filter-due-soon" checked={includeDueSoon} onCheckedChange={(val) => setIncludeDueSoon(!!val)} />
                  <Label htmlFor="filter-due-soon" className="text-xs font-bold text-yellow-600">A Vencer</Label>
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
            <div className="flex items-center justify-between">
                <Label className="text-base font-semibold">Selecionar Contas Específicas</Label>
                <Button variant="ghost" size="sm" onClick={handleSelectAllNames}>
                    {selectedNames.length === uniqueNames.length && uniqueNames.length > 0 ? "Desmarcar Todas" : "Selecionar Todas"}
                </Button>
            </div>
            <Card className="bg-muted/30">
                <ScrollArea className="h-48 p-4">
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                        {uniqueNames.map((name) => (
                            <div key={name} className="flex items-center space-x-2">
                                <Checkbox 
                                    id={`name-${name}`} 
                                    checked={selectedNames.includes(name)} 
                                    onCheckedChange={() => handleToggleName(name)} 
                                />
                                <Label 
                                    htmlFor={`name-${name}`} 
                                    className="cursor-pointer text-[11px] font-normal truncate"
                                    title={name}
                                >
                                    {name}
                                </Label>
                            </div>
                        ))}
                    </div>
                </ScrollArea>
            </Card>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="ghost" onClick={clearFilters}>
              <X className="mr-2 h-4 w-4" /> Limpar Filtros
            </Button>
            <Button onClick={handleGenerateReport} disabled={isGenerating}>
              {isGenerating ? <Loader className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
              Gerar Relatório
            </Button>
          </div>
        </CardContent>
      </Card>

      {reportData && (
        <div className="space-y-6">
          <div className="flex items-center justify-between print:hidden">
            <h2 className="text-xl font-semibold">Resultado do Relatório ({reportData.length})</h2>
            <Button variant="outline" onClick={handlePrint}>
              <Printer className="mr-2 h-4 w-4" /> Imprimir Relatório
            </Button>
          </div>

          <Card className="print:border-none print:shadow-none">
            <CardHeader className="relative pb-2">
              <div className="flex flex-col items-center justify-center pt-8">
                <CardTitle className="text-2xl font-headline text-center">Relatório de Despesas Pendentes</CardTitle>
                <CardDescription className="text-xs text-center mt-1">
                    Emitido em {format(new Date(), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                    {currentUser && ` por ${currentUser.nome}`}
                    <div className="mt-1 print:block">
                    {startDate && `Início: ${format(startDate, 'dd/MM/yy')} | `}
                    {endDate && `Fim: ${format(endDate, 'dd/MM/yy')} | `}
                    {selectedType !== 'all' && `Grupo: ${selectedType} | `}
                    </div>
                </CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <div className="mb-6 grid grid-cols-2 gap-4 rounded-lg border bg-muted/30 p-4 print:bg-gray-50">
                <div className="flex flex-col">
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Quantidade</span>
                  <span className="text-lg font-bold">{reportData.length} Itens Pendentes</span>
                </div>
                <div className="flex flex-col text-right">
                  <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Total em Aberto</span>
                  <span className="text-lg font-bold text-destructive">
                    {totalAmount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </span>
                </div>
              </div>

              <div className="space-y-8">
                {Object.entries(groupedData).map(([tipo, items]) => (
                  <div key={tipo} className="space-y-2">
                    <div className="flex items-center justify-between border-b border-primary/30 pb-1">
                      <h3 className="text-[10px] font-bold uppercase tracking-tight text-primary">{tipo}</h3>
                    </div>
                    <Table>
                      <TableHeader className="bg-muted/20">
                        <TableRow className="h-8">
                          <TableHead className="text-[10px] h-8 w-[90px]">Vencimento</TableHead>
                          <TableHead className="text-[10px] h-8">Nome</TableHead>
                          <TableHead className="text-[10px] h-8 w-[100px]">Info</TableHead>
                          <TableHead className="text-[10px] h-8 w-[100px]">Situação</TableHead>
                          <TableHead className="text-[10px] h-8 text-right w-[100px]">Valor</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {items.map((expense) => {
                          const info = getStatusInfo(expense);
                          return (
                            <TableRow key={expense.id} className="h-8 border-b border-muted/30">
                              <TableCell className="text-[10px] py-1">
                                {format(parseISO(expense.vencimento), 'dd/MM/yyyy')}
                              </TableCell>
                              <TableCell className="text-[10px] py-1 font-medium">
                                {expense.nome}
                              </TableCell>
                              <TableCell className="text-[10px] py-1 text-muted-foreground">
                                {expense.descricao || "PARCELA ÚNICA"}
                              </TableCell>
                              <TableCell className="text-[10px] py-1">
                                <span className={cn(
                                  "px-1.5 py-0.5 rounded-sm font-bold border",
                                  info.colorClass
                                )}>
                                  {info.label}
                                </span>
                              </TableCell>
                              <TableCell className="text-[10px] py-1 text-right font-bold">
                                {Number(expense.valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                    <div className="flex justify-end pt-1">
                      <span className="text-[10px] font-bold">
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
