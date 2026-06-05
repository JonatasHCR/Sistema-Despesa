import { type Expense, type User, type NotificationConfig, type Digest } from './types';
import { parseISO, format } from 'date-fns';

const API_BASE_URL = typeof window === 'undefined'
  ? process.env.INTERNAL_API_BASE_URL || 'http://backend:8000'
  : process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const TOKEN_KEY = 'authToken';
const SESSION_KEY = 'userSession';

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function clearSession() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(SESSION_KEY);
}

export function storeSession(token: string, user: User) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(SESSION_KEY, JSON.stringify(user));
}

export function getStoredUser(): User | null {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem(SESSION_KEY);
  return raw ? (JSON.parse(raw) as User) : null;
}

async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers || {});
  // Para FormData o browser define o Content-Type (com boundary) sozinho.
  if (!headers.has('Content-Type') && init.body && !(init.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  const token = getStoredToken();
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });

  if (response.status === 401 && typeof window !== 'undefined' && token) {
    clearSession();
    if (!window.location.pathname.startsWith('/login')) {
      window.location.replace('/login');
    }
  }

  return response;
}

// --- Auth API ---
export const signIn = async (credentials: { nome: string; senha: string }): Promise<AuthResponse> => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Usuário ou senha inválidos.');
  }

  return response.json();
};

export const signUp = async (input: { name: string; email: string; password: string }): Promise<User> => {
  const response = await fetch(`${API_BASE_URL}/users/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome: input.name, email: input.email, senha: input.password }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Não foi possível criar a conta.');
  }
  return response.json();
};

// --- Users API ---
export const getUserById = async (id: number): Promise<User | null> => {
  const response = await apiFetch(`/users/${id}`);
  if (!response.ok) {
    if (response.status === 404) return null;
    throw new Error('Falha ao buscar usuário.');
  }
  return response.json();
};

export const updateUser = async (id: number, data: Partial<Omit<User, 'id'>>): Promise<User> => {
  const payload: Record<string, unknown> = {
    nome: data.nome,
    email: data.email,
  };
  if (data.senha) payload.senha = data.senha;

  const response = await apiFetch(`/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Não foi possível atualizar o perfil.');
  }

  const updatedUser: User = await response.json();
  if (typeof window !== 'undefined') {
    const stored = getStoredUser();
    if (stored && stored.id === id) {
      localStorage.setItem(SESSION_KEY, JSON.stringify({ ...stored, ...updatedUser }));
    }
  }
  return updatedUser;
};

// --- Expenses API ---
type DespesaApi = Omit<Expense, 'userName' | 'dynamicStatus'> & { user_nome?: string | null };

const adaptExpense = (raw: DespesaApi): Expense => {
  const { user_nome, ...rest } = raw;
  return {
    ...rest,
    userName: user_nome ?? undefined,
  };
};

export const getExpenses = async (): Promise<Expense[]> => {
  const response = await apiFetch(`/despesas/?limit=500`);
  if (!response.ok) throw new Error('Falha ao buscar despesas.');
  const data: DespesaApi[] = await response.json();
  return data.map(adaptExpense);
};

export const getExpenseById = async (id: string): Promise<Expense | null> => {
  const response = await apiFetch(`/despesas/${id}`);
  if (!response.ok) return null;
  const expense: DespesaApi = await response.json();
  const adapted = adaptExpense(expense);
  if (!adapted.userName) {
    const user = await getUserById(adapted.user_id);
    adapted.userName = user ? user.nome : `Usuário ${adapted.user_id}`;
  }
  return adapted;
};

const formatCurrencyValueForAPI = (value: string | number | undefined): number => {
  if (value === undefined || value === null) return 0;
  let valueStr = String(value);
  valueStr = valueStr.replace(/\./g, '').replace(',', '.');
  const num = parseFloat(valueStr);
  return isNaN(num) ? 0 : num;
};

const formatDateForAPI = (date: Date | string): string => {
  if (typeof date === 'string') return format(parseISO(date), 'yyyy-MM-dd');
  return format(date, 'yyyy-MM-dd');
};

// `valor` chega como string formatada (locale BR) ou número; a API normaliza.
type ExpenseCreation = Omit<Expense, 'id' | 'userName' | 'dynamicStatus' | 'valor'> & {
  valor: string | number;
};

export const addExpense = async (data: ExpenseCreation | ExpenseCreation[]): Promise<Expense | Expense[]> => {
  const dataAsArray = Array.isArray(data) ? data : [data];

  const results = await Promise.all(dataAsArray.map(item => {
    const payload: Record<string, unknown> = {
      nome: item.nome,
      tipo: item.tipo,
      status: item.status,
      descricao: item.descricao || 'PARCELA ÚNICA',
      valor: formatCurrencyValueForAPI(item.valor),
      vencimento: formatDateForAPI(item.vencimento),
    };
    if (item.destinatarios !== undefined) payload.destinatarios = item.destinatarios;
    return apiFetch(`/despesas/`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }).then(async res => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Falha ao criar despesa');
      }
      return res.json();
    });
  }));

  return Array.isArray(data) ? results : results[0];
};

export const updateExpense = async (
  id: string,
  data: Partial<Omit<Expense, 'id' | 'userName' | 'dynamicStatus' | 'valor'>> & { valor?: string | number }
): Promise<Expense> => {
  // Backend aceita update parcial — só enviamos campos definidos.
  const payload: Record<string, unknown> = {};
  if (data.nome !== undefined) payload.nome = data.nome;
  if (data.tipo !== undefined) payload.tipo = data.tipo;
  if (data.descricao !== undefined) payload.descricao = data.descricao;
  if (data.status !== undefined) payload.status = data.status;
  if (data.valor !== undefined) payload.valor = formatCurrencyValueForAPI(data.valor as unknown as string);
  if (data.vencimento !== undefined) payload.vencimento = formatDateForAPI(data.vencimento);
  if (data.destinatarios !== undefined) payload.destinatarios = data.destinatarios;

  const response = await apiFetch(`/despesas/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Não foi possível atualizar a despesa.');
  }

  return adaptExpense(await response.json());
};

export const deleteExpense = async (id: string): Promise<void> => {
  const response = await apiFetch(`/despesas/${id}`, { method: 'DELETE' });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Não foi possível excluir a despesa.');
  }
};

// --- Importação via Excel ---
export interface ImportRowError {
  linha: number;
  erro: string;
}

export interface ImportResult {
  total_linhas: number;
  criadas: number;
  falhas: number;
  erros: ImportRowError[];
}

export const importExpensesFromExcel = async (file: File): Promise<ImportResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiFetch('/despesas/import', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Não foi possível importar a planilha.');
  }

  return response.json();
};

// --- Usuários (para seletor de destinatários) ---
export const getUsers = async (): Promise<User[]> => {
  const response = await apiFetch('/users/');
  if (!response.ok) throw new Error('Falha ao buscar usuários.');
  return response.json();
};

// --- Notificações ---
export const getNotificationConfig = async (): Promise<NotificationConfig> => {
  const response = await apiFetch('/notificacoes/config');
  if (!response.ok) throw new Error('Falha ao buscar a configuração de notificações.');
  return response.json();
};

export const updateNotificationConfig = async (
  data: Partial<NotificationConfig>
): Promise<NotificationConfig> => {
  const response = await apiFetch('/notificacoes/config', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Não foi possível salvar a configuração.');
  }
  return response.json();
};

export const getDigest = async (): Promise<Digest> => {
  const response = await apiFetch('/notificacoes/digest');
  if (!response.ok) throw new Error('Falha ao buscar o resumo de notificações.');
  return response.json();
};

export const downloadExpenseTemplate = async (): Promise<void> => {
  const response = await apiFetch('/despesas/import/modelo');
  if (!response.ok) throw new Error('Não foi possível baixar o modelo.');

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'modelo_despesas.xlsx';
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};
