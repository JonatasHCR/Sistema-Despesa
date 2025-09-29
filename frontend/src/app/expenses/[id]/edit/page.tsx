import { EditExpenseForm } from '../../../../components/expenses/EditExpenseForm';
import { getExpenseById } from '../../../../lib/api';
import { notFound } from 'next/navigation';

export default async function EditExpensePage({ params }: { params: { id: string } }) {
  const { id } = params;
  const expense = await getExpenseById(id);

  if (!expense) {
   notFound();
  }

   return (
     <div className="flex flex-col gap-8">
       <div className="flex flex-col gap-1">
         <h1 className="font-headline text-2xl font-bold md:text-3xl">
           Editar Despesa
         </h1>
         <p className="text-muted-foreground">
           {`Atualize as informações da despesa "${expense.nome}".`}
         </p>
       </div>
       <EditExpenseForm expense={expense} />
     </div>
   );
}
