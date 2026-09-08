import datetime

import pytest


URL_DESPESA = "/despesas/"
URL_CONFIG = "/notificacoes/config"
URL_DIGEST = "/notificacoes/digest"


def _despesa(nome, vencimento, destinatarios, status="P", valor=100.0, tipo="BOLETO"):
    return {
        "nome": nome,
        "tipo": tipo,
        "status": status,
        "valor": valor,
        "vencimento": vencimento,
        "destinatarios": destinatarios,
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_config_default_and_update(async_client, auth):
    headers = auth["headers"]

    r = await async_client.get(URL_CONFIG, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json() == {
        "ativo": True,
        "dias_antecedencia": 5,
        "avisar_vencidas": True,
    }

    r = await async_client.put(
        URL_CONFIG,
        json={"dias_antecedencia": 10, "avisar_vencidas": False},
        headers=headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["dias_antecedencia"] == 10
    assert body["avisar_vencidas"] is False
    assert body["ativo"] is True  # não enviado -> inalterado

    r = await async_client.get(URL_CONFIG, headers=headers)
    assert r.json()["dias_antecedencia"] == 10


@pytest.mark.asyncio
@pytest.mark.integration
async def test_despesa_destinatarios_roundtrip(async_client, auth):
    headers = auth["headers"]
    uid = auth["user"]["id"]
    venc = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()

    r = await async_client.post(URL_DESPESA, json=_despesa("Conta", venc, [uid]), headers=headers)
    assert r.status_code == 201, r.text
    despesa_id = r.json()["id"]
    assert r.json()["destinatarios"] == [uid]

    r = await async_client.get(f"{URL_DESPESA}{despesa_id}", headers=headers)
    assert r.json()["destinatarios"] == [uid]

    # Atualizar substitui a lista (vazio = ninguém)
    r = await async_client.put(
        f"{URL_DESPESA}{despesa_id}", json={"destinatarios": []}, headers=headers
    )
    assert r.status_code == 200
    r = await async_client.get(f"{URL_DESPESA}{despesa_id}", headers=headers)
    assert r.json()["destinatarios"] == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_digest_window_and_situacao(async_client, auth):
    headers = auth["headers"]
    uid = auth["user"]["id"]
    hoje = datetime.date.today()
    soon = (hoje + datetime.timedelta(days=2)).isoformat()
    far = (hoje + datetime.timedelta(days=60)).isoformat()
    overdue = (hoje - datetime.timedelta(days=3)).isoformat()

    await async_client.post(URL_DESPESA, json=_despesa("Soon", soon, [uid]), headers=headers)
    await async_client.post(URL_DESPESA, json=_despesa("Far", far, [uid]), headers=headers)
    await async_client.post(URL_DESPESA, json=_despesa("Overdue", overdue, [uid]), headers=headers)

    r = await async_client.get(URL_DIGEST, headers=headers)
    assert r.status_code == 200
    body = r.json()
    itens = {i["nome"]: i for i in body["itens"]}

    assert "Soon" in itens and "Overdue" in itens
    assert "Far" not in itens  # fora da janela de 5 dias
    assert itens["Soon"]["situacao"] == "vencendo"
    assert itens["Overdue"]["situacao"] == "vencida"
    assert body["vencidas"] >= 1 and body["vencendo"] >= 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_digest_targeting_por_despesa(async_client, auth, outro_auth):
    headers = auth["headers"]

    other_id = outro_auth["user"]["id"]
    other_headers = outro_auth["headers"]

    venc = (datetime.date.today() + datetime.timedelta(days=2)).isoformat()
    # Criada por A, mas só o outro (B) é destinatário.
    await async_client.post(
        URL_DESPESA, json=_despesa("SoDoOutro", venc, [other_id]), headers=headers
    )

    ra = await async_client.get(URL_DIGEST, headers=headers)
    assert "SoDoOutro" not in {i["nome"] for i in ra.json()["itens"]}

    rb = await async_client.get(URL_DIGEST, headers=other_headers)
    assert "SoDoOutro" in {i["nome"] for i in rb.json()["itens"]}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_digest_respeita_ativo_false(async_client, auth):
    headers = auth["headers"]
    uid = auth["user"]["id"]
    venc = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

    await async_client.post(URL_DESPESA, json=_despesa("X", venc, [uid]), headers=headers)
    await async_client.put(URL_CONFIG, json={"ativo": False}, headers=headers)

    r = await async_client.get(URL_DIGEST, headers=headers)
    assert r.json()["total"] == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_digest_respeita_avisar_vencidas_false(async_client, auth):
    headers = auth["headers"]
    uid = auth["user"]["id"]
    hoje = datetime.date.today()
    overdue = (hoje - datetime.timedelta(days=3)).isoformat()
    soon = (hoje + datetime.timedelta(days=2)).isoformat()

    await async_client.post(URL_DESPESA, json=_despesa("Vencida", overdue, [uid]), headers=headers)
    await async_client.post(URL_DESPESA, json=_despesa("Vencendo", soon, [uid]), headers=headers)
    await async_client.put(URL_CONFIG, json={"avisar_vencidas": False}, headers=headers)

    r = await async_client.get(URL_DIGEST, headers=headers)
    nomes = {i["nome"] for i in r.json()["itens"]}
    assert "Vencendo" in nomes
    assert "Vencida" not in nomes
