import io

import pytest
from openpyxl import Workbook


XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _build_xlsx(rows: list[list]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(["nome", "tipo", "valor", "vencimento", "status", "descricao"])
    for row in rows:
        ws.append(row)
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_import_excel_partial(async_client, auth):
    headers = auth["headers"]
    content = _build_xlsx(
        [
            ["Conta de Luz", "BOLETO", "150,75", "31/12/2026", "Pendente", "PARCELA ÚNICA"],
            ["Internet", "BOLETO", "abc", "31/12/2026", "Pendente", ""],  # valor inválido
            ["Aluguel", "BOLETO", "1.200,00", "10/01/2027", "Quitada", ""],
        ]
    )

    response = await async_client.post(
        "/despesas/import",
        files={"file": ("modelo.xlsx", content, XLSX_MEDIA)},
        headers=headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total_linhas"] == 3
    assert body["criadas"] == 2
    assert body["falhas"] == 1
    # 2ª linha de dados (Internet) está na linha 3 da planilha (1 = cabeçalho).
    assert body["erros"][0]["linha"] == 3

    listagem = await async_client.get("/despesas/?limit=500", headers=headers)
    nomes = {d["nome"] for d in listagem.json()}
    assert {"Conta de Luz", "Aluguel"}.issubset(nomes)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_import_defaults_status_to_pendente(async_client, auth):
    headers = auth["headers"]
    content = _build_xlsx([["Água", "BOLETO", "80,00", "05/02/2027", "", ""]])

    response = await async_client.post(
        "/despesas/import",
        files={"file": ("modelo.xlsx", content, XLSX_MEDIA)},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["criadas"] == 1

    listagem = await async_client.get("/despesas/?limit=500", headers=headers)
    agua = next(d for d in listagem.json() if d["nome"] == "Água")
    assert agua["status"] == "P"
    assert agua["descricao"] == "PARCELA ÚNICA"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_import_rejects_non_xlsx(async_client, auth):
    response = await async_client.post(
        "/despesas/import",
        files={"file": ("dados.csv", b"nome,tipo,valor", "text/csv")},
        headers=auth["headers"],
    )
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_import_missing_required_columns(async_client, auth):
    wb = Workbook()
    ws = wb.active
    ws.append(["nome", "tipo"])  # faltam valor e vencimento
    ws.append(["X", "BOLETO"])
    buffer = io.BytesIO()
    wb.save(buffer)

    response = await async_client.post(
        "/despesas/import",
        files={"file": ("ruim.xlsx", buffer.getvalue(), XLSX_MEDIA)},
        headers=auth["headers"],
    )
    assert response.status_code == 400
    assert "obrigat" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_import_template_download(async_client, auth):
    response = await async_client.get("/despesas/import/modelo", headers=auth["headers"])
    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]
    assert len(response.content) > 0
