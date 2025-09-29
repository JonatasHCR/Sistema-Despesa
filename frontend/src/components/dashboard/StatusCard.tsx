'use client';

import { type ReactNode, type MouseEvent } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { cn } from '../../lib/utils';
import { type DynamicExpenseStatus } from '../../lib/types';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

interface StatusCardProps {
  title: string;
  count: number;
  icon: ReactNode;
  status: DynamicExpenseStatus;
  isSelected: boolean;
  onClick: () => void;
  dueSoonDays?: number;
  setDueSoonDays?: (days: number) => void;
}

const statusStyles: Record<DynamicExpenseStatus, { text: string }> = {
    overdue: { text: 'text-status-overdue' },
    'due-soon': { text: 'text-status-due-soon' },
    due: { text: 'text-status-due' },
    paid: { text: 'text-status-paid' }
};

export function StatusCard({ title, count, icon, status, isSelected, onClick, dueSoonDays, setDueSoonDays }: StatusCardProps) {
  const styles = statusStyles[status];

  const handleContainerClick = () => {
    onClick();
  }

  const handleInputClick = (e: MouseEvent) => {
    e.stopPropagation();
  }

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all duration-300 ease-in-out hover:shadow-lg hover:-translate-y-1 flex flex-col',
        isSelected ? 'border-accent ring-2 ring-accent bg-accent/10' : 'bg-card'
      )}
      onClick={handleContainerClick}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="font-headline text-base font-medium">{title}</CardTitle>
        <div className={cn('text-muted-foreground', styles.text)}>
            {icon}
        </div>
      </CardHeader>
      <CardContent className="flex-grow flex flex-col justify-center">
        <div className="text-4xl font-bold">{count}</div>
        {status === 'due-soon' && setDueSoonDays && (
          <div className="mt-4 flex items-center gap-2" onClick={handleInputClick}>
            <Label htmlFor="due-soon-days" className="text-xs whitespace-nowrap">Dias para vencer:</Label>
            <Input
                id="due-soon-days"
                type="number"
                value={dueSoonDays || 0}
                onChange={(e) => setDueSoonDays(Math.max(0, parseInt(e.target.value, 10)))}
                className="h-8 w-16"
                min="0"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
