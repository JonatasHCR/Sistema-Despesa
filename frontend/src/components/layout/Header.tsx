
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { PlusCircle, User, LogOut, Settings, FileText, LayoutDashboard } from 'lucide-react';
import { type User as UserType } from '@/lib/types';
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
    const session = localStorage.getItem('userSession');
    if (session) {
      setUser(JSON.parse(session));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('userSession');
    router.push('/login');
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
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="font-headline text-2xl font-bold md:text-3xl">
            {title}
          </h1>
          <p className="text-muted-foreground">{subtitle}</p>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2 sm:gap-4">
        {pathname !== '/' && (
            <Button variant="outline" onClick={() => router.push('/')}>
                <LayoutDashboard className="h-4 w-4" />
                <span className="hidden sm:inline">Dashboard</span>
            </Button>
        )}
        {pathname !== '/reports' && (
            <Button variant="outline" onClick={() => router.push('/reports')}>
                <FileText className="h-4 w-4" />
                <span className="hidden sm:inline">Relatórios</span>
            </Button>
        )}
        {showNewExpenseButton && (
            <Button onClick={() => router.push('/expenses/new')}>
                <PlusCircle className="h-4 w-4" />
                <span>Nova Despesa</span>
            </Button>
        )}
        {user && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
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
                  <p className="text-xs leading-none text-muted-foreground">
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
