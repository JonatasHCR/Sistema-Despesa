import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { type Expense } from '@/lib/types';
import { ExpenseCard } from './ExpenseCard';

export const ExpenseDashboard = ({ expenses }: { expenses: Expense[] }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Despesas</CardTitle>
        <CardDescription>A lista de todas as suas despesas.</CardDescription>
      </CardHeader>
      <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {expenses.map((expense) => (
          <ExpenseCard key={expense.id} expense={expense} />
        ))}
      </CardContent>
      <CardFooter>
        <p>Total de despesas: {expenses.length}</p>
      </CardFooter>
    </Card>
  );
};
