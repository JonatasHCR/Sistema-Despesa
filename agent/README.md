# Agente de Notificações (Windows)

Mostra um **toast nativo do Windows** com as despesas vencendo/vencidas de quem
está configurado como destinatário. Roda em cada máquina, busca o **digest diário**
no backend e exibe **uma vez por dia**. Ao clicar no toast, abre o painel.

Toda a regra (o que avisar, pra quem, antecedência) fica no backend e é ajustável
em **Meu Perfil → Notificações**. O agente só lê e mostra.

## 1. Pré-requisitos
- Backend e frontend acessíveis na rede local (ex.: `http://192.168.0.10:8000` e `:3000`).
- Um usuário do sistema para cada máquina (o agente faz login com nome+senha).
- A despesa precisa ter a pessoa marcada em **destinatários** para aparecer no digest dela.

## 2. Gerar o executável (uma vez, na máquina de desenvolvimento)
Precisa de Python 3.11+ instalado.

```powershell
cd agent
powershell -ExecutionPolicy Bypass -File build.ps1
```

Saída: `dist\despesa-agent.exe`.

> Detalhe: o `--collect-all win11toast` no build garante que as dependências de
> notificação do Windows sejam empacotadas no `.exe`.

## 3. Instalar em cada máquina
1. Crie uma pasta, ex.: `C:\DespesaAgent\`.
2. Copie para ela: `despesa-agent.exe` e um `config.json`.
3. Crie o `config.json` a partir de `config.example.json`:

```json
{
  "base_url": "http://192.168.0.10:8000",
  "nome": "usuario_da_maquina",
  "senha": "senha_do_usuario",
  "dashboard_url": "http://192.168.0.10:3000",
  "forcar": false
}
```

- `base_url`: URL do **backend** alcançável na rede.
- `dashboard_url`: URL do **frontend** (aberto ao clicar no toast).
- `forcar`: `true` ignora o controle de "uma vez por dia" (útil só para testar).

## 4. Agendar (Agendador de Tarefas do Windows)
O jeito mais simples — rodar no logon e todo dia de manhã. Em um PowerShell **como
administrador**, ajuste o caminho e rode:

```powershell
$exe = "C:\DespesaAgent\despesa-agent.exe"

# No logon do usuário
schtasks /Create /TN "DespesaAgent-Logon" /TR "$exe" /SC ONLOGON /RL LIMITED /F

# Todo dia às 08:00
schtasks /Create /TN "DespesaAgent-Diario" /TR "$exe" /SC DAILY /ST 08:00 /RL LIMITED /F
```

> Importante: a tarefa deve rodar **com o usuário logado** (toasts só aparecem na
> sessão do usuário). Pelo modo GUI do Agendador, use "Executar somente quando o
> usuário estiver conectado". O controle de "uma vez por dia" evita aviso duplicado
> quando ambos os gatilhos disparam.

## 5. Testar
1. No app, marque uma despesa pendente com a sua pessoa em **destinatários** e
   vencimento dentro da janela (ou já vencida).
2. Em **Meu Perfil → Notificações**, confirme que está **ativo**.
3. Ponha `"forcar": true` no `config.json` e execute o `.exe` (duplo clique).
   Deve aparecer o toast. Depois volte `forcar` para `false`.

## 6. Problemas comuns
- **`agent.log` diz "OK" mas o toast não aparece** — as duas causas mais comuns:
  1. **Rodou como administrador.** Toast de processo elevado normalmente NÃO aparece
     na sessão do usuário. Rode o `.exe` com **duplo clique normal** (não "Executar
     como administrador"); a tarefa agendada deve usar `/RL LIMITED` (já é o padrão).
  2. **Notificações desligadas / Assistente de Foco ligado.** Confira em
     *Configurações → Sistema → Notificações* (ligado) e desligue o *Assistente de Foco*.
  - O toast é atribuído ao app "Windows PowerShell" (usamos um AppUserModelID já
    registrado, senão o Windows descarta o toast em silêncio). Para mudar o nome
    exibido, registre um atalho com AUMID próprio e ponha em `config.json` → `"app_id"`.
- **Nada no log / `connection refused`**: o backend não está acessível — confira se a
  stack está no ar (`http://IP:8000/documentation` no navegador) e o firewall/IP.
- **Login falha**: confira `nome`/`senha` e o `base_url`.
- **Avisa todo dia mesmo sem mudança**: é o esperado — é um *digest diário*. Se não
  houver despesas na janela, ele não notifica.

## Segurança
O `config.json` guarda a senha em texto puro (ferramenta interna de LAN). Se for um
problema, crie um usuário dedicado de baixo privilégio por máquina.
