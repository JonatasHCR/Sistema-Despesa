"""Agente de notificações do Sistema Despesa (Windows).

Roda em cada máquina, pede o digest diário ao backend e mostra um toast nativo
do Windows com as despesas vencendo/vencidas. Ao clicar, abre o painel.

É "burro" de propósito: toda a lógica (o que avisar, pra quem) está no backend.
Pensado para rodar via Agendador de Tarefas (no logon e/ou diariamente).
"""
import datetime
import json
import os
import sys

import requests


def _base_dir() -> str:
    # Empacotado com PyInstaller -> pasta do .exe; senão, pasta do script.
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _log(base_dir: str, mensagem: str) -> None:
    try:
        with open(os.path.join(base_dir, "agent.log"), "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat()} {mensagem}\n")
    except Exception:
        pass


def carregar_config(base_dir: str) -> dict:
    caminho = os.path.join(base_dir, "config.json")
    if not os.path.exists(caminho):
        raise RuntimeError(
            "config.json não encontrado. Copie config.example.json para "
            "config.json e preencha base_url, nome e senha."
        )
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def ja_avisou_hoje(state_path: str) -> bool:
    if not os.path.exists(state_path):
        return False
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("ultimo_aviso") == datetime.date.today().isoformat()
    except Exception:
        return False


def marcar_avisado(state_path: str) -> None:
    try:
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({"ultimo_aviso": datetime.date.today().isoformat()}, f)
    except Exception:
        pass


def login(base_url: str, nome: str, senha: str) -> str:
    resp = requests.post(
        f"{base_url}/auth/login",
        json={"nome": nome, "senha": senha},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def buscar_digest(base_url: str, token: str) -> dict:
    resp = requests.get(
        f"{base_url}/notificacoes/digest",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def montar_mensagem(digest: dict) -> tuple[str, str]:
    partes = []
    if digest.get("vencidas"):
        partes.append(f"{digest['vencidas']} vencida(s)")
    if digest.get("vencendo"):
        partes.append(f"{digest['vencendo']} vencendo")
    titulo = "Despesas: " + (" e ".join(partes) if partes else "lembrete")

    linhas = []
    for item in digest.get("itens", [])[:6]:
        dias = item.get("dias", 0)
        if item.get("situacao") == "vencida":
            quando = f"vencida há {abs(dias)}d"
        elif dias == 0:
            quando = "vence hoje"
        else:
            quando = f"vence em {dias}d"
        linhas.append(f"• {item['nome']} (R$ {item['valor']:.2f}) — {quando}")

    restante = digest.get("total", 0) - 6
    if restante > 0:
        linhas.append(f"…e mais {restante}")

    return titulo, "\n".join(linhas)


def main() -> None:
    base_dir = _base_dir()
    try:
        cfg = carregar_config(base_dir)
        state_path = os.path.join(base_dir, "agent_state.json")
        forcar = bool(cfg.get("forcar", False))

        if not forcar and ja_avisou_hoje(state_path):
            return  # já notificou hoje (digest diário)

        token = login(cfg["base_url"], cfg["nome"], cfg["senha"])
        digest = buscar_digest(cfg["base_url"], token)

        if digest.get("total", 0) == 0:
            marcar_avisado(state_path)
            return

        titulo, corpo = montar_mensagem(digest)

        # win11toast importado aqui para erro de dependência ir ao log, não a um crash.
        from win11toast import toast

        # IMPORTANTE: app_id precisa ser um AppUserModelID REGISTRADO no Windows,
        # senão o toast não aparece (e não dá erro). Usamos o do PowerShell, que
        # existe em qualquer Windows. Pode ser sobrescrito em config.json -> "app_id".
        app_id = cfg.get("app_id") or (
            "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe"
        )
        # toast() é bloqueante: garante a entrega antes do processo encerrar.
        toast(
            titulo,
            corpo,
            on_click=cfg.get("dashboard_url") or None,
            app_id=app_id,
            duration="short",
        )
        marcar_avisado(state_path)
        _log(base_dir, f"OK: notificou {digest['total']} despesa(s)")
    except Exception as e:  # nunca crashar de forma visível numa tarefa agendada
        _log(base_dir, f"ERRO: {e}")


if __name__ == "__main__":
    main()
