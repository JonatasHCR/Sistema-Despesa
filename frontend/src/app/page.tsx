import { Suspense } from 'react';
import dynamic from 'next/dynamic';
import { Loader } from 'lucide-react';
import PageWrapper from '@/components/layout/PageWrapper';
import Header from '@/components/layout/Header';

const ExpenseDashboard = dynamic(() =>
  import('@/components/dashboard/ExpenseDashboard').then(m => ({ default: m.ExpenseDashboard }))
);

function Home() {
  return (
    <PageWrapper>
      <div className="flex flex-col gap-8">
        <Header
          title="Painel Radar"
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
