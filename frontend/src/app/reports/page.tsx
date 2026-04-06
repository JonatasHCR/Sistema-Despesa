'use client';

import PageWrapper from '@/components/layout/PageWrapper';
import Header from '@/components/layout/Header';
import { ReportGenerator } from '@/components/reports/ReportGenerator';

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
