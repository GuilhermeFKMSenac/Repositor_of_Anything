import pytest
import sys
import os

# Adiciona o diretório pai (raiz do projeto) ao sys.path
# para que os módulos da aplicação (cliente, funcionario, etc.) possam ser importados.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cliente
import funcionario
import produto
import servico
import agenda
import venda
import fornecedor
import despesa
import suprimento
import maquina

@pytest.fixture(autouse=True)
def limpar_dados_globais():
    # Limpa os dicionários de classe de todas as classes com estado global
    # e redefine seus contadores de ID para garantir testes isolados.

    # Limpar dados de Cliente
    cliente.Cliente._clientes_por_cpf.clear()
    cliente.Cliente._clientes_por_id.clear()
    cliente.Cliente._proximo_id_disponivel = 1

    # Limpar dados de Funcionario
    funcionario.Funcionario._funcionarios_por_cpf.clear()
    funcionario.Funcionario._funcionarios_por_id.clear()
    funcionario.Funcionario._proximo_id_disponivel = 1

    # Limpar dados de Produto
    produto.Produto._produtos_por_nome.clear()
    produto.Produto._produtos_por_id.clear()
    produto.Produto._proximo_id_disponivel = 1

    # Limpar dados de Servico
    servico.Servico._servicos_por_nome.clear()
    servico.Servico._servicos_por_id.clear()
    servico.Servico._proximo_id_disponivel = 1

    # Limpar dados de Agenda
    agenda.Agenda._agendas_por_id.clear()
    agenda.Agenda._proximo_id_disponivel = 1

    # Limpar dados de Venda
    venda.Venda._vendas_por_id.clear()
    venda.Venda._proximo_id_disponivel = 1

    # Limpar dados de Fornecedor
    fornecedor.Fornecedor._fornecedores_por_cnpj.clear()
    fornecedor.Fornecedor._fornecedores_por_id.clear()
    fornecedor.Fornecedor._proximo_id_disponivel = 1

    # Limpar dados de Despesa (base para todas as subclasses)
    despesa.Despesa._despesas_por_id.clear()
    despesa.Despesa._proximo_id_disponivel = 1

    # Limpar dados de Suprimento
    suprimento.Suprimento._suprimentos_por_id.clear()
    suprimento.Suprimento._suprimentos_por_nome.clear()
    suprimento.Suprimento._proximo_id_disponivel = 1

    # Limpar dados de Maquina
    maquina.Maquina._maquinas_por_id.clear()
    maquina.Maquina._maquinas_por_serie.clear()
    maquina.Maquina._proximo_id_disponivel = 1

    # Yield para permitir que o teste seja executado
    yield