import { type NextRequest, NextResponse } from 'next/server'

import { lerSessao } from '@/lib/session'

/**
 * Proxy do navegador para o FastAPI.
 *
 * É a peça central do BFF: o `Authorization` é anexado AQUI, a partir do cookie
 * de sessão cifrado. O navegador nunca vê o access token — ele só fala com este
 * servidor, na mesma origem. Como efeito colateral, o CORS entre navegador e
 * FastAPI deixou de existir.
 */

const BACKEND = process.env.INTERNAL_API_BASE_URL ?? 'http://backend:8000'

async function proxy(req: NextRequest): Promise<NextResponse> {
  const sessao = await lerSessao(req.cookies)
  if (!sessao?.access_token) {
    return NextResponse.json({ detail: 'Sessão expirada' }, { status: 401 })
  }

  const caminho = req.nextUrl.pathname.replace(/^\/api/, '')
  const url = `${BACKEND}${caminho}${req.nextUrl.search}`

  const headers = new Headers(req.headers)
  headers.delete('host')
  headers.delete('connection')
  headers.delete('content-length')
  // O cookie de sessão é assunto deste servidor; o FastAPI não tem o que fazer
  // com ele, e mandá-lo adiante só vazaria a sessão para dentro da rede.
  headers.delete('cookie')
  headers.set('Authorization', `Bearer ${sessao.access_token}`)

  const semCorpo = ['GET', 'HEAD', 'DELETE'].includes(req.method)

  const upstream = await fetch(url, {
    method: req.method,
    headers,
    body: semCorpo ? undefined : await req.arrayBuffer(),
    redirect: 'follow',
  })

  const respHeaders = new Headers(upstream.headers)
  respHeaders.delete('transfer-encoding')
  // O fetch() já descomprime o corpo, então o content-encoding e o
  // content-length originais (que descreviam o tamanho comprimido) ficam
  // inválidos. Removendo os dois, o Next responde em chunks e o navegador não
  // trunca a resposta — vale principalmente para o download de relatórios.
  respHeaders.delete('content-encoding')
  respHeaders.delete('content-length')

  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: respHeaders,
  })
}

export const GET = proxy
export const POST = proxy
export const PUT = proxy
export const DELETE = proxy
export const PATCH = proxy
