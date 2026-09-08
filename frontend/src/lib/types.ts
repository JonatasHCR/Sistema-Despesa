export type ExpenseStatus = 'P' | 'Q';
export type DynamicExpenseStatus = 'overdue' | 'due-soon' | 'due' | 'paid';


export interface Expense {
  id: number;
  nome: string;
  tipo: string;
  valor: number;
  vencimento: string; // ISO string
  status: ExpenseStatus;
  descricao?: string;
  user_id: number;
  userName?: string;
  dynamicStatus?: DynamicExpenseStatus;
  destinatarios?: number[]; // IDs dos usuários a notificar
}

export interface User {
    id: number;
    nome: string;
    email: string;
    senha?: string;
  admin?: boolean;
}

export interface NotificationConfig {
  ativo: boolean;
  dias_antecedencia: number;
  avisar_vencidas: boolean;
}

export interface DigestItem {
  id: number;
  nome: string;
  tipo: string;
  valor: number;
  vencimento: string;
  descricao?: string;
  situacao: 'vencida' | 'vencendo';
  dias: number;
}

export interface Digest {
  data: string;
  total: number;
  vencidas: number;
  vencendo: number;
  itens: DigestItem[];
}
