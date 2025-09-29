import { NewExpenseForm } from '../../../components/expenses/NewExpenseForm';
import PageWrapper from '@/components/layout/PageWrapper';

export default function NewExpensePage() {
  return (
    <PageWrapper>
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-1">
          <h1 className="font-headline text-2xl font-bold md:text-3xl">
            Cadastrar Nova Despesa
          </h1>
          <p className="text-muted-foreground">
            Preencha os campos abaixo para adicionar uma nova despesa.
          </p>
        </div>
        <NewExpenseForm />
      </div>
    </PageWrapper>
  );
}
