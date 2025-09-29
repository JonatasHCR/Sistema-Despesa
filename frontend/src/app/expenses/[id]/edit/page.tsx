import { EditExpenseForm } from '@/components/expenses/EditExpenseForm';
import { getExpenseById } from '@/lib/api';

export default async function EditExpensePage({ params: { id } }: { params: { id: string } }) {
  const expense = await getExpenseById(Number(id));

  if (!expense) {
    return <div>Despesa não encontrada</div>;
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-1">
        <h1 className="font-headline text-2xl font-bold md:text-3xl">Editar Despesa</h1>
        <p className="text-muted-foreground">Edite os detalhes da sua despesa.</p>
      </div>
      <EditExpenseForm expense={expense} />
    </div>
  );
}
