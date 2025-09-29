import { NewExpenseForm } from '@/components/expenses/NewExpenseForm';
import { getUsers } from '@/lib/api';

export default async function NewExpensePage() {
  const users = await getUsers();

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-1">
        <h1 className="font-headline text-2xl font-bold md:text-3xl">Nova Despesa</h1>
        <p className="text-muted-foreground">Crie uma nova despesa para rastrear seus gastos.</p>
      </div>
      <NewExpenseForm users={users} />
    </div>
  );
}
