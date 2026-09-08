import { redirect } from 'next/navigation';

/**
 * Nao existe mais tela de login aqui: quem pede a senha e o Keycloak.
 *
 * A rota continua existindo porque links e favoritos antigos apontam para ela,
 * e porque `/api/auth/login` e uma route handler — nao da para apontar um
 * usuario direto para ela num link de navegacao sem passar por aqui.
 */
export default function LoginPage() {
  redirect('/api/auth/login');
}
