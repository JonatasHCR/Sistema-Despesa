import { type NextRequest, NextResponse } from 'next/server'

import { lerSessao } from '@/lib/session'

/**
 * Quem esta logado, para os componentes de cliente.
 *
 * Substitui o `getStoredUser()` que lia o `userSession` do localStorage. Aquele
 * dado vinha do navegador e podia ser editado a mao pelo usuario; este vem do
 * cookie cifrado e do banco.
 *
 * Devolve o usuario LOCAL (com o `id` que as despesas referenciam), nao as
 * claims do Keycloak — o front precisa do id do banco. Nenhum token e exposto.
 */
export const dynamic = 'force-dynamic'

const BACKEND = process.env.INTERNAL_API_BASE_URL ?? 'http://backend:8000'

export async function GET(req: NextRequest) {
  const sessao = await lerSessao(req.cookies)
  if (!sessao?.access_token) {
    return NextResponse.json({ detail: 'Sessão expirada' }, { status: 401 })
  }

  const resposta = await fetch(
    `${BACKEND}/users/email/${encodeURIComponent(sessao.email)}`,
    {
      headers: { Authorization: `Bearer ${sessao.access_token}` },
      cache: 'no-store',
    },
  )

  if (!resposta.ok) {
    return NextResponse.json(
      { detail: 'Não foi possível carregar o usuário' },
      { status: resposta.status },
    )
  }

  return NextResponse.json(await resposta.json())
}
