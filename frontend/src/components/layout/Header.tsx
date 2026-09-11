
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { PlusCircle, User, LogOut, Settings, FileText, LayoutDashboard, ExternalLink } from 'lucide-react';
import { type User as UserType } from '@/lib/types';
import { getCurrentUser } from '@/lib/api';
import { ThemeToggle } from './ThemeToggle';
import { TrocarSistema } from './TrocarSistema';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface HeaderProps {
    title: string;
    subtitle: string;
    showNewExpenseButton?: boolean;
}

export default function Header({ title, subtitle, showNewExpenseButton = false }: HeaderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<UserType | null>(null);

  useEffect(() => {
    // O usuário vem do cookie de sessão, pelo servidor — não mais de um JSON
    // no localStorage, que o próprio navegador podia editar.
    getCurrentUser().then(setUser);
  }, []);

  const handleLogout = () => {
    // Logout RP-initiated: encerra a sessão no Keycloak também, deslogando dos
    // três sistemas. Apagar só o cookie daqui deixaria o próximo acesso entrar
    // direto, sem pedir senha.
    window.location.href = '/api/auth/logout';
  };

  const getInitials = (name: string | undefined) => {
    if (!name) return '?';
    return name
      .split(' ')
      .slice(0, 2)
      .map((n) => n[0])
      .join('');
  };

  return (
    <div className="flex flex-col gap-3 sm:gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1 min-w-0">
          <h1 className="font-headline text-xl sm:text-2xl md:text-3xl font-bold leading-tight">
            {title}
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">{subtitle}</p>
        </div>
        {/* Toggle de tema + avatar à direita no mobile (acessíveis sem scroll) */}
        <div className="flex items-center gap-2 sm:hidden">
          <ThemeToggle />
          {user && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full shrink-0">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={`https://avatar.vercel.sh/${user.email}.png`} alt={user.nome} />
                    <AvatarFallback>{getInitials(user.nome)}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user.nome}</p>
                    <p className="text-xs leading-none text-muted-foreground truncate">{user.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild className="cursor-pointer">
                  <Link href="/profile">
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Meu Perfil</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild className="cursor-pointer">
                  <a href="/api/auth/conta">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    <span>Minha conta</span>
                  </a>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Sair</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2 sm:gap-3">
        {user?.admin && (
          <Button
            variant="outline"
            size="sm"
            className="flex-1 sm:flex-initial sm:size-default"
            onClick={() => router.push('/administracao')}
          >
            <Settings className="h-4 w-4 sm:mr-2" />
            <span className="ml-2 sm:ml-0 hidden sm:inline">Administração</span>
          </Button>
        )}
        <TrocarSistema />
        <ThemeToggle className="hidden sm:inline-flex" />
        {pathname !== '/' && (
            <Button variant="outline" size="sm" className="flex-1 sm:flex-initial sm:size-default" onClick={() => router.push('/')}>
                <LayoutDashboard className="h-4 w-4 sm:mr-2" />
                <span className="hidden sm:inline">Dashboard</span>
                <span className="sm:hidden ml-2">Painel</span>
            </Button>
        )}
        {pathname !== '/reports' && (
            <Button variant="outline" size="sm" className="flex-1 sm:flex-initial sm:size-default" onClick={() => router.push('/reports')}>
                <FileText className="h-4 w-4 sm:mr-2" />
                <span className="ml-2 sm:ml-0">Relatórios</span>
            </Button>
        )}
        {showNewExpenseButton && (
            <Button size="sm" className="flex-1 sm:flex-initial sm:size-default" onClick={() => router.push('/expenses/new')}>
                <PlusCircle className="h-4 w-4 sm:mr-2" />
                <span className="ml-2 sm:ml-0">Nova Despesa</span>
            </Button>
        )}
        {user && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full hidden sm:inline-flex">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={`https://avatar.vercel.sh/${user.email}.png`} alt={user.nome} />
                  <AvatarFallback>{getInitials(user.nome)}</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{user.nome}</p>
                  <p className="text-xs leading-none text-muted-foreground truncate">
                    {user.email}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild className="cursor-pointer">
                <Link href="/profile">
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Meu Perfil</span>
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild className="cursor-pointer">
                <a href="/api/auth/conta">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  <span>Minha conta</span>
                </a>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
                <LogOut className="mr-2 h-4 w-4" />
                <span>Sair</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </div>
  );
}
