'use client';

import { useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import {
  Download,
  Upload,
  FileSpreadsheet,
  Loader,
  CheckCircle2,
  AlertTriangle,
  X,
} from 'lucide-react';
import {
  downloadExpenseTemplate,
  importExpensesFromExcel,
  type ImportResult,
} from '@/lib/api';

export function ImportExpensesCard() {
  const router = useRouter();
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);

  const resetFile = () => {
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDownloadTemplate = async () => {
    setIsDownloading(true);
    try {
      await downloadExpenseTemplate();
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Erro ao baixar o modelo',
        description: (error as Error).message,
      });
    } finally {
      setIsDownloading(false);
    }
  };

  const handleImport = async () => {
    if (!file) return;
    setIsImporting(true);
    setResult(null);
    try {
      const data = await importExpensesFromExcel(file);
      setResult(data);

      if (data.criadas > 0) {
        toast({
          title: 'Importação concluída',
          description: `${data.criadas} despesa(s) criada(s)${
            data.falhas > 0 ? `, ${data.falhas} com erro.` : '.'
          }`,
        });
      } else {
        toast({
          variant: 'destructive',
          title: 'Nenhuma despesa importada',
          description:
            data.falhas > 0
              ? 'Todas as linhas tiveram erro. Confira os detalhes abaixo.'
              : 'A planilha não tinha linhas para importar.',
        });
      }
      resetFile();
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Falha na importação',
        description: (error as Error).message,
      });
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-xl sm:text-2xl">
          <FileSpreadsheet className="h-5 w-5 text-primary" />
          Importar de Excel
        </CardTitle>
        <CardDescription>
          Cadastre várias despesas de uma vez a partir de uma planilha .xlsx.
          Baixe o modelo, preencha e envie. Colunas: nome, tipo, valor,
          vencimento, status, descricao.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Button
            type="button"
            variant="outline"
            onClick={handleDownloadTemplate}
            disabled={isDownloading}
            className="w-full sm:w-auto"
          >
            {isDownloading ? (
              <Loader className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Download className="mr-2 h-4 w-4" />
            )}
            Baixar modelo
          </Button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx"
            className="hidden"
            onChange={(e) => {
              setResult(null);
              setFile(e.target.files?.[0] ?? null);
            }}
          />
          <Button
            type="button"
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            className="w-full sm:w-auto"
          >
            <FileSpreadsheet className="mr-2 h-4 w-4" />
            {file ? 'Trocar arquivo' : 'Selecionar arquivo'}
          </Button>

          <Button
            type="button"
            onClick={handleImport}
            disabled={!file || isImporting}
            className="w-full sm:w-auto"
          >
            {isImporting ? (
              <Loader className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Upload className="mr-2 h-4 w-4" />
            )}
            Importar
          </Button>
        </div>

        {file && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <FileSpreadsheet className="h-4 w-4 shrink-0" />
            <span className="truncate">{file.name}</span>
            <button
              type="button"
              onClick={resetFile}
              className="ml-auto rounded p-1 hover:bg-muted"
              aria-label="Remover arquivo"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {result && (
          <div className="space-y-3 rounded-lg border bg-muted/30 p-4">
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
              <span className="flex items-center gap-1.5 font-medium text-green-600 dark:text-green-500">
                <CheckCircle2 className="h-4 w-4" />
                {result.criadas} criada(s)
              </span>
              {result.falhas > 0 && (
                <span className="flex items-center gap-1.5 font-medium text-destructive">
                  <AlertTriangle className="h-4 w-4" />
                  {result.falhas} com erro
                </span>
              )}
              <span className="text-muted-foreground">
                de {result.total_linhas} linha(s)
              </span>
            </div>

            {result.erros.length > 0 && (
              <div className="max-h-48 space-y-1 overflow-y-auto rounded border bg-background p-2 text-sm">
                {result.erros.map((e) => (
                  <div key={e.linha} className="flex gap-2">
                    <span className="shrink-0 font-mono text-muted-foreground">
                      Linha {e.linha}:
                    </span>
                    <span className="text-destructive">{e.erro}</span>
                  </div>
                ))}
              </div>
            )}

            {result.criadas > 0 && (
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() => router.push('/')}
              >
                Ver no painel
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
