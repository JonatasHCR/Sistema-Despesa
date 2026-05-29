'use client';

import { useEffect, useState } from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import { getUsers, getStoredUser } from '@/lib/api';
import { type User } from '@/lib/types';
import { Loader } from 'lucide-react';

export function RecipientsField({
  value,
  onChange,
}: {
  value: number[];
  onChange: (ids: number[]) => void;
}) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);

  useEffect(() => {
    setCurrentUserId(getStoredUser()?.id ?? null);
    getUsers()
      .then(setUsers)
      .catch(() => setUsers([]))
      .finally(() => setLoading(false));
  }, []);

  const toggle = (id: number) => {
    onChange(value.includes(id) ? value.filter((v) => v !== id) : [...value, id]);
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader className="h-4 w-4 animate-spin" /> Carregando usuários...
      </div>
    );
  }

  return (
    <div className="max-h-44 space-y-2 overflow-y-auto rounded-md border p-3">
      {users.length === 0 ? (
        <p className="text-sm text-muted-foreground">Nenhum usuário encontrado.</p>
      ) : (
        users.map((u) => (
          <label
            key={u.id}
            className="flex cursor-pointer items-center gap-2 text-sm"
          >
            <Checkbox
              checked={value.includes(u.id)}
              onCheckedChange={() => toggle(u.id)}
            />
            <span>
              {u.nome}
              {u.id === currentUserId ? ' (você)' : ''}
            </span>
          </label>
        ))
      )}
    </div>
  );
}
