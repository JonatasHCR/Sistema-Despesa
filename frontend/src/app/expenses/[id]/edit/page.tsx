'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Loader } from 'lucide-react';

import { EditExpenseForm } from '@/components/expenses/EditExpenseForm';
import { getExpenseById } from '@/lib/api';
import { type Expense } from '@/lib/types';

export default function EditExpensePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [expense, setExpense] = useState<Expense | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const data = await getExpenseById(params.id);
      if (cancelled) return;
      if (!data) {
        router.replace('/');
        return;
      }
      setExpense(data);
      setLoading(false);
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [params.id, router]);

  if (loading || !expense) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
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
