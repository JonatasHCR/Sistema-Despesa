
'use client';

import { type ReactNode, type MouseEvent, useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { cn } from '../../lib/utils';
import { type DynamicExpenseStatus } from '../../lib/types';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

interface StatusCardProps {
  title: string;
  count: number;
  total: number;
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

export function StatusCard({ title, count, total, icon, status, isSelected, onClick, dueSoonDays, setDueSoonDays }: StatusCardProps) {
  const styles = statusStyles[status];
  const [inputValue, setInputValue] = useState(String(dueSoonDays ?? ''));

  useEffect(() => {
    if (dueSoonDays !== undefined && String(dueSoonDays) !== inputValue) {
      setInputValue(String(dueSoonDays));
    }
  }, [dueSoonDays, inputValue]);

  const handleContainerClick = () => {
    onClick();
  }

  const handleInputClick = (e: MouseEvent) => {
    e.stopPropagation();
  }

  const updateDueSoonDays = useCallback(() => {
    if (setDueSoonDays) {
      const value = inputValue === '' ? 0 : parseInt(inputValue, 10);
      const finalValue = Math.max(0, isNaN(value) ? (dueSoonDays ?? 0) : value);
      setDueSoonDays(finalValue);
      if (String(finalValue) !== inputValue) {
          setInputValue(String(finalValue));
      }
    }
  }, [setDueSoonDays, inputValue, dueSoonDays]);
  
  const handleDueSoonDaysChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  }
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      updateDueSoonDays();
      e.currentTarget.blur();
    }
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
      <CardContent className="flex-grow flex flex-col justify-center gap-2">
        <div className="text-4xl font-bold">{count}</div>
         <div className="text-xl font-semibold">
            Total: {total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </div>
        {status === 'due-soon' && setDueSoonDays && (
          <div className="mt-2 flex items-center gap-2" onClick={handleInputClick}>
            <Label htmlFor="due-soon-days" className="text-xs whitespace-nowrap">Dias para vencer:</Label>
            <Input
                id="due-soon-days"
                type="number"
                value={inputValue}
                onChange={handleDueSoonDaysChange}
                onBlur={updateDueSoonDays}
                onKeyDown={handleKeyDown}
                className="h-8 w-20"
                min="0"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
