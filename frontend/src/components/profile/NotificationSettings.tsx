'use client';

import { useCallback, useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Bell, Loader } from 'lucide-react';
import { getNotificationConfig, updateNotificationConfig } from '@/lib/api';
import { type NotificationConfig } from '@/lib/types';

export function NotificationSettings() {
  const { toast } = useToast();
  const [config, setConfig] = useState<NotificationConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const carregar = useCallback(() => {
    setLoading(true);
    setError(null);
    getNotificationConfig()
      .then(setConfig)
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  const save = async () => {
    if (!config) return;
    setSaving(true);
    try {
      const updated = await updateNotificationConfig(config);
      setConfig(updated);
      toast({ title: 'Configuração de notificações salva.' });
    } catch (e) {
      toast({
        variant: 'destructive',
        title: 'Erro ao salvar',
        description: (e as Error).message,
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center gap-2 p-6 text-muted-foreground">
          <Loader className="h-4 w-4 animate-spin" /> Carregando...
        </CardContent>
      </Card>
    );
  }

  if (error || !config) {
    return (
      <Card>
        <CardContent className="flex flex-col items-start gap-3 p-6">
          <p className="text-sm text-destructive">
            Não foi possível carregar a configuração de notificações.
            {error ? ` (${error})` : ''}
          </p>
          <Button variant="outline" size="sm" onClick={carregar}>
            Tentar novamente
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-xl sm:text-2xl">
          <Bell className="h-5 w-5 text-primary" />
          Notificações
        </CardTitle>
        <CardDescription>
          Avisos de despesas vencendo/vencidas, exibidos pelo aplicativo de
          notificação no Windows.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <label className="flex cursor-pointer items-center gap-2">
          <Checkbox
            checked={config.ativo}
            onCheckedChange={(c) => setConfig({ ...config, ativo: c === true })}
          />
          <span className="text-sm">Ativar notificações</span>
        </label>
        <label className="flex cursor-pointer items-center gap-2">
          <Checkbox
            checked={config.avisar_vencidas}
            onCheckedChange={(c) =>
              setConfig({ ...config, avisar_vencidas: c === true })
            }
          />
          <span className="text-sm">Avisar despesas já vencidas</span>
        </label>
        <div className="flex items-center gap-2">
          <Label htmlFor="dias" className="whitespace-nowrap text-sm">
            Avisar com antecedência de
          </Label>
          <Input
            id="dias"
            type="number"
            min={0}
            max={365}
            className="h-8 w-20"
            value={config.dias_antecedencia}
            onChange={(e) =>
              setConfig({
                ...config,
                dias_antecedencia: Math.max(0, parseInt(e.target.value, 10) || 0),
              })
            }
          />
          <span className="text-sm text-muted-foreground">dia(s)</span>
        </div>
      </CardContent>
      <CardFooter className="justify-end">
        <Button onClick={save} disabled={saving}>
          {saving && <Loader className="mr-2 h-4 w-4 animate-spin" />}
          Salvar
        </Button>
      </CardFooter>
    </Card>
  );
}
