import dynamic from 'next/dynamic';
import PageWrapper from '@/components/layout/PageWrapper';
import Header from '@/components/layout/Header';

const ReportGenerator = dynamic(() =>
  import('@/components/reports/ReportGenerator').then(m => ({ default: m.ReportGenerator }))
);

export default function ReportsPage() {
  return (
    <PageWrapper>
      <div className="flex flex-col gap-8">
        <div className="print:hidden">
          <Header
            title="Relatórios"
            subtitle="Gere relatórios detalhados das suas despesas."
          />
        </div>
        <ReportGenerator />
      </div>
    </PageWrapper>
  );
}
