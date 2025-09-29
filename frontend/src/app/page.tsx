'use client';

import { Suspense } from 'react';
import { ExpenseDashboard } from '../components/dashboard/ExpenseDashboard';
import { Loader } from 'lucide-react';
import PageWrapper from '@/components/layout/PageWrapper';
import Header from '@/components/layout/Header';

function Home() {
  
  return (
    <PageWrapper>
      <div className="flex flex-col gap-8">
        <Header 
          title="Painel de Despesas"
          subtitle="Visualize e gerencie suas finanças de forma simples."
          showNewExpenseButton={true}
        />
        <Suspense fallback={<Loader className="mx-auto my-16 h-8 w-8 animate-spin" />}>
          <ExpenseDashboard />
        </Suspense>
      </div>
    </PageWrapper>
  );
}

export default Home;
