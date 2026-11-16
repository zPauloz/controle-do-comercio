# Controle do Comércio

MVP desenvolvido em Python 3 e Flask para auxiliar pequenos comércios no controle de produtos, clientes, pedidos e estoque.

## Funcionalidades
- Cadastro de produtos e estoque
- Cadastro de clientes
- Registro de pedidos
- Validação da quantidade disponível
- Atualização do estoque após o pedido
- Histórico de pedidos

## Tecnologias
- Python
- Flask
- SQLite
- HTML e CSS

## Como executar no Ubuntu

1. Instale Python 3, venv e pip.
2. Crie e ative o ambiente virtual:
   python3 -m venv .venv
   source .venv/bin/activate
3. Instale as dependências:
   pip install -r requirements.txt
4. Inicie a aplicação:
   python app.py
5. Acesse http://127.0.0.1:5000

## Validações do sistema
- O preço do produto deve ser maior que zero.
- O estoque inicial não pode ser negativo.
- A quantidade do pedido deve ser positiva.
- Pedidos acima do estoque disponível são recusados.

## Testes automatizados

Para executar os testes, ative o ambiente virtual e rode:

    python -m pytest -v

Os testes verificam se as páginas inicial, de produtos e de clientes respondem corretamente.
## Revisão técnica

O MVP foi revisado considerando a organização do código, a legibilidade,
a validação dos dados e o funcionamento das principais páginas.

Os testes automatizados ajudam a verificar se as funcionalidades
continuam funcionando após alterações no sistema.
