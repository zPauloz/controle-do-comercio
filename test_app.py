import pytest
import app as sistema


@pytest.fixture(autouse=True)
def preparar_banco(tmp_path, monkeypatch):
    sistema.DB = tmp_path / "teste.db"
    sistema.iniciar_banco()


def test_pagina_inicial():
    sistema.app.config["TESTING"] = True
    cliente = sistema.app.test_client()
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert b"Controle do Com" in resposta.data


def test_pagina_produtos():
    sistema.app.config["TESTING"] = True
    cliente = sistema.app.test_client()
    resposta = cliente.get("/produtos")
    assert resposta.status_code == 200


def test_pagina_clientes():
    sistema.app.config["TESTING"] = True
    cliente = sistema.app.test_client()
    resposta = cliente.get("/clientes")
    assert resposta.status_code == 200


def test_pagina_pedidos():
    sistema.app.config["TESTING"] = True
    cliente = sistema.app.test_client()
    resposta = cliente.get("/pedidos")
    assert resposta.status_code == 200
    assert (
        b"Historico de pedidos" in resposta.data
        or b"Hist" in resposta.data
    )
