import app as sistema

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
