'use client';

import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '../ui/dropdown-menu';
import { type Expense, type ExpenseStatus } from '../../lib/types';
import { CalendarDays, MoreVertical, Pencil, User, Loader, Trash2, Check, X } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { cn } from '../../lib/utils';
import { Badge } from '../ui/badge';
import Link from 'next/link';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "../ui/alert-dialog"
import { useState } from 'react';
import { useToast } from '../../hooks/use-toast';
import { deleteExpense, updateExpense } from '../../lib/api';

interface ExpenseCardProps {
  expense: Expense;
  onUpdate: () => void;
}

const statusConfig: Record<ExpenseStatus, { label: string; className: string }> = {
    P: { label: 'Pendente', className: 'bg-status-due-soon/20 text-status-due-soon-foreground' },
    Q: { label: 'Quitada', className: 'bg-status-paid/20 text-status-paid-foreground' },
};


export function ExpenseCard({ expense, onUpdate }: ExpenseCardProps) {
  const dueDate = parseISO(expense.vencimento);
  const { toast } = useToast();
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [isDeleteAlertOpen, setIsDeleteAlertOpen] = useState(false);
  const [isStatusAlertOpen, setIsStatusAlertOpen] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteExpense(String(expense.id));
      toast({
          title: 'Sucesso!',
          description: 'A despesa foi excluída.',
      });
      onUpdate();
    } catch (error) {
        toast({
            variant: 'destructive',
            title: 'Uh oh! Algo deu errado.',
            description: (error as Error).message || 'Não foi possível excluir a despesa.',
        });
    } finally {
        setIsDeleting(false);
        setIsDeleteAlertOpen(false);
    }
  };

  const handleStatusChange = async () => {
    setIsUpdatingStatus(true);
    const newStatus = expense.status === 'P' ? 'Q' : 'P';
    const successMessage = newStatus === 'Q' ? 'Despesa marcada como paga.' : 'Despesa marcada como pendente.';

    try {
        await updateExpense(String(expense.id), { ...expense, status: newStatus });
        toast({
            title: 'Sucesso!',
            description: successMessage,
        });
        onUpdate();
    } catch (error) {
         toast({
            variant: 'destructive',
            title: 'Uh oh! Algo deu errado.',
            description: (error as Error).message || 'Não foi possível atualizar o status da despesa.',
        });
    } finally {
        setIsUpdatingStatus(false);
        setIsStatusAlertOpen(false);
    }
  }

  const currentStatus = statusConfig[expense.status] ?? { label: 'Desconhecido', className: 'bg-muted text-muted-foreground' };

  return (
    <Card className={cn("flex flex-col justify-between h-full transition-shadow hover:shadow-md border-l-4", {
      'border-l-status-paid': expense.status === 'Q',
      'border-l-primary': expense.status === 'P'
    })}>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
            <div className="flex flex-col gap-2">
                <CardTitle className="font-headline text-lg font-semibold">{expense.nome}</CardTitle>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="w-fit">{expense.tipo}</Badge>
                  <Badge variant="outline" className={cn("w-fit", currentStatus.className)}>{currentStatus.label}</Badge>
                </div>
            </div>
            <div className="flex items-center gap-1">
                <div className={cn("flex items-center gap-1.5 text-lg font-bold")}>
                    <span>
                        {expense.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </span>
                </div>
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreVertical className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuItem asChild>
                          <Link href={`/expenses/${expense.id}/edit`}>
                            <Pencil className="mr-2 h-4 w-4" />
                            Editar
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <AlertDialog open={isDeleteAlertOpen} onOpenChange={setIsDeleteAlertOpen}>
                            <AlertDialogTrigger asChild>
                                <DropdownMenuItem onSelect={(e) => e.preventDefault()} className="text-destructive focus:text-destructive">
                                    <Trash2 className="mr-2 h-4 w-4" />
                                    Excluir
                                </DropdownMenuItem>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                                <AlertDialogHeader>
                                <AlertDialogTitle>Confirmar Exclusão</AlertDialogTitle>
                                <AlertDialogDescription>
                                    {`Tem certeza que deseja excluir permanentemente a despesa "${expense.nome}"? Esta ação não pode ser desfeita.`}
                                </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                <AlertDialogCancel disabled={isDeleting}>Cancelar</AlertDialogCancel>
                                <AlertDialogAction onClick={handleDelete} disabled={isDeleting} className="bg-destructive hover:bg-destructive/90">
                                    {isDeleting && <Loader className="mr-2 h-4 w-4 animate-spin" />}
                                    Excluir
                                </AlertDialogAction>
                                </AlertDialogFooter>
                            </AlertDialogContent>
                        </AlertDialog>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow pt-0">
            <div className="flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                        <CalendarDays className="h-4 w-4" />
                        <span>
                            Vencimento: {format(dueDate, "dd 'de' MMMM, yyyy", { locale: ptBR })}
                        </span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                        <User className="h-4 w-4" />
                        <span>
                            Criado por: {expense.userName || `Usuário ${expense.user_id}`}
                        </span>
                    </div>
                </div>
            </div>
      </CardContent>
       <CardFooter className="pt-4">
        <AlertDialog open={isStatusAlertOpen} onOpenChange={setIsStatusAlertOpen}>
            <AlertDialogTrigger asChild>
                 <Button 
                    variant={expense.status === 'P' ? 'default' : 'outline'} 
                    className="w-full"
                    >
                    {expense.status === 'P' ? <Check className="mr-2 h-4 w-4" /> : <X className="mr-2 h-4 w-4" />}
                    {expense.status === 'P' ? 'Marcar como Paga' : 'Marcar como Pendente'}
                </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Confirmar Alteração de Status</AlertDialogTitle>
                    <AlertDialogDescription>
                        {`Tem certeza que deseja marcar a despesa "${expense.nome}" como ${expense.status === 'P' ? 'paga' : 'pendente'}?`}
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel disabled={isUpdatingStatus}>Cancelar</AlertDialogCancel>
                    <AlertDialogAction onClick={handleStatusChange} disabled={isUpdatingStatus}>
                        {isUpdatingStatus && <Loader className="mr-2 h-4 w-4 animate-spin" />}
                        Confirmar
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
      </CardFooter>
    </Card>
  );
}
