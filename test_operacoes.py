import pytest
from datetime import datetime, date, timedelta

# Importa todas as classes necessárias
import pessoa
import info
import funcionario
import cliente
import servico
import produto
import suprimento
import maquina
import agenda
import venda
import fornecedor
import despesa

serv_teste_2 = servico.Servico(None, "Lavagem de Sofá", 150.00, 30.00)
# --- Fixtures de Pré-requisitos para Testes de Operações ---

@pytest.fixture
def info_contato_base():
    # Informações de contato genéricas para fixtures.
    return info.Informacao("11999990000", "geral@email.com", "Rua Central, 100, Centro, SP, SP", "")

@pytest.fixture
def func_teste(info_contato_base):
    # Funcionário para uso em testes.
    return funcionario.Funcionario(
        None, "Funcionario Teste", "01/01/1985", pessoa.gerar_cpf_valido(), "1234567-89",
        info_contato_base, 3000.00, "01/01/2020", None, "12345678901"
    )

@pytest.fixture
def func_teste_2(info_contato_base):
    # Segundo funcionário para testes de conflito ou múltiplos funcionários.
    return funcionario.Funcionario(
        None, "Funcionario Dois", "01/01/1990", pessoa.gerar_cpf_valido(), "9876543-21",
        info_contato_base, 2800.00, "01/01/2021", None, "10987654321"
    )

@pytest.fixture
def cli_teste(info_contato_base):
    # Cliente para uso em testes.
    return cliente.Cliente(
        None, "Cliente Teste", "10/05/1992", pessoa.gerar_cpf_valido(), info_contato_base
    )

@pytest.fixture
def cli_teste_2(info_contato_base):
    # Segundo cliente para testes de conflito ou múltiplos clientes.
    return cliente.Cliente(
        None, "Cliente Dois", "15/03/1988", pessoa.gerar_cpf_valido(), info_contato_base
    )

@pytest.fixture
def serv_teste():
    # Serviço para uso em testes.
    return servico.Servico(None, "Limpeza Geral", 100.00, 20.00)



@pytest.fixture
def prod_teste():
    # Produto para uso em testes (com estoque).
    return produto.Produto(None, "Cera Protetora", 50.00, 10)

@pytest.fixture
def prod_teste_sem_estoque():
    # Produto com estoque zero para testar validações.
    return produto.Produto(None, "Produto Esgotado", 30.00, 0)

@pytest.fixture
def supr_teste():
    # Suprimento para uso em testes (com estoque float).
    return suprimento.Suprimento(None, "Sabão Líquido", "litro", 10.00, 5.0)

@pytest.fixture
def supr_teste_sem_estoque():
    # Suprimento com estoque zero para testar validações.
    return suprimento.Suprimento(None, "Esponja", "unidade", 2.00, 0.0)

@pytest.fixture
def maq_teste_operando():
    # Máquina em status "Operando".
    return maquina.Maquina(None, "Enceradeira", "ENC-001", 1500.00, maquina.StatusMaquina.OPERANDO)

@pytest.fixture
def maq_teste_manutencao():
    # Máquina em status "Em Manutenção".
    return maquina.Maquina(None, "Aspirador Profissional", "ASP-002", 2000.00, maquina.StatusMaquina.MANUTENCAO)

@pytest.fixture
def forn_teste(info_contato_base):
    # Fornecedor para uso em testes.
    return fornecedor.Fornecedor(
        None, "Fornecedor Teste S.A.", pessoa.gerar_cnpj_valido(), info_contato_base
    )

# --- Testes para a classe Agenda (agenda.py) ---

def test_agenda_criacao_valida(func_teste, cli_teste, serv_teste, prod_teste, supr_teste, maq_teste_operando):
    # Testa a criação de um agendamento válido com todos os tipos de itens.
    itens_agendados = [
        agenda.ItemAgendado(serv_teste, 1, 90.00),
        agenda.ItemAgendado(prod_teste, 2, 45.00)
    ]
    maquinas_agendadas = [maq_teste_operando]
    suprimentos_utilizados = [agenda.SuprimentoAgendado(supr_teste, 0.5)]

    data_hora_inicio = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y %H:%M")
    data_hora_fim = (datetime.now() + timedelta(days=1, hours=1)).strftime("%d/%m/%Y %H:%M")

    ag = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, data_hora_inicio, data_hora_fim,
        itens_agendados, "Comentário da agenda", maquinas_agendadas, suprimentos_utilizados
    )
    assert ag.funcionario == func_teste
    assert ag.cliente == cli_teste
    assert ag.itens_agendados[0].item == serv_teste
    assert ag.itens_agendados[1].item == prod_teste
    assert ag.maquinas_agendadas[0] == maq_teste_operando
    assert ag.suprimentos_utilizados[0].suprimento == supr_teste
    assert ag.valor_total == (90.00 * 1) + (45.00 * 2)
    assert ag.status == agenda.AgendaStatus.AGENDADO
    assert agenda.Agenda.buscar_agenda(ag.id) == ag

def test_agenda_criacao_sem_itens(func_teste, cli_teste): # Adicionado fixtures como argumentos
    # Testa a criação de agendamento sem itens agendados (deve falhar).
    with pytest.raises(ValueError, match="A agenda deve conter pelo menos um item agendado na lista."):
        agenda.Agenda(None, func_teste, cli_teste, "01/01/2025 10:00", "01/01/2025 11:00", [], "Comentário")

def test_agenda_conflito_horario_funcionario(func_teste, cli_teste, serv_teste):
    # Testa conflito de horário para o mesmo funcionário.
    agenda.Agenda.criar_agenda(
        func_teste, cli_teste, "01/01/2025 10:00", "01/01/2025 12:00",
        [agenda.ItemAgendado(serv_teste, 1)]
    )
    with pytest.raises(ValueError, match="Conflito de horário: Funcionário, Cliente ou Máquina já possui agendamento neste período."):
        agenda.Agenda.criar_agenda(
            func_teste, cli_teste, "01/01/2025 11:00", "01/01/2025 13:00",
            [agenda.ItemAgendado(serv_teste, 1)]
        )

def test_agenda_conflito_horario_cliente(func_teste, cli_teste, serv_teste, func_teste_2):
    # Testa conflito de horário para o mesmo cliente.
    agenda.Agenda.criar_agenda(
        func_teste, cli_teste, "01/01/2025 10:00", "01/01/2025 12:00",
        [agenda.ItemAgendado(serv_teste, 1)]
    )
    with pytest.raises(ValueError, match="Conflito de horário: Funcionário, Cliente ou Máquina já possui agendamento neste período."):
        agenda.Agenda.criar_agenda(
            func_teste_2, cli_teste, "01/01/2025 11:00", "01/01/2025 13:00",
            [agenda.ItemAgendado(serv_teste, 1)]
        )

def test_agenda_conflito_horario_maquina(func_teste, cli_teste, serv_teste, maq_teste_operando, func_teste_2, cli_teste_2):
    # Testa conflito de horário para a mesma máquina.
    agenda.Agenda.criar_agenda(
        func_teste, cli_teste, "01/01/2025 10:00", "01/01/2025 12:00",
        [agenda.ItemAgendado(serv_teste, 1)], maquinas_agendadas=[maq_teste_operando]
    )
    with pytest.raises(ValueError, match="Conflito de horário: Funcionário, Cliente ou Máquina já possui agendamento neste período."):
        agenda.Agenda.criar_agenda(
            func_teste_2, cli_teste_2, "01/01/2025 11:00", "01/01/2025 13:00",
            [agenda.ItemAgendado(serv_teste, 1)], maquinas_agendadas=[maq_teste_operando]
        )

def test_agenda_maquina_nao_operando(func_teste, cli_teste, serv_teste, maq_teste_manutencao):
    # Testa agendamento com máquina em manutenção (não deve ser possível).
    data_hora_inicio = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y %H:%M")
    data_hora_fim = (datetime.now() + timedelta(days=1, hours=1)).strftime("%d/%m/%Y %H:%M")
    with pytest.raises(ValueError, match=f"Máquina '{maq_teste_manutencao.nome}' .* não está em status 'Operando' e não pode ser agendada."):
        agenda.Agenda.criar_agenda(
            func_teste, cli_teste, data_hora_inicio, data_hora_fim,
            [agenda.ItemAgendado(serv_teste, 1)], maquinas_agendadas=[maq_teste_manutencao]
        )

def test_agenda_estoque_insuficiente_suprimento(func_teste, cli_teste, serv_teste, supr_teste_sem_estoque):
    # Testa criação de agenda com suprimento sem estoque (deve falhar se status AGENDADO).
    data_hora_inicio = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y %H:%M")
    data_hora_fim = (datetime.now() + timedelta(days=1, hours=1)).strftime("%d/%m/%Y %H:%M")
    with pytest.raises(ValueError, match=f"Estoque insuficiente para o suprimento '{supr_teste_sem_estoque.nome}' ao AGENDAR."):
        agenda.Agenda.criar_agenda(
            func_teste, cli_teste, data_hora_inicio, data_hora_fim,
            [agenda.ItemAgendado(serv_teste, 1)], suprimentos_utilizados=[agenda.SuprimentoAgendado(supr_teste_sem_estoque, 1.0)]
        )

def test_agenda_marcar_como_realizado_deduz_estoque(func_teste, cli_teste, prod_teste, supr_teste):
    # Testa a marcação de agendamento como REALIZADO e a dedução de estoque.
    initial_prod_estoque = prod_teste.estoque
    initial_supr_estoque = supr_teste.estoque

    # Cria a agenda com data passada para que a dedução ocorra no .marcar_como_realizado()
    past_date_time = datetime.now() - timedelta(days=1, hours=2)
    future_date_time = datetime.now() - timedelta(days=1, hours=1)

    ag = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, 
        past_date_time.strftime("%d/%m/%Y %H:%M"), 
        future_date_time.strftime("%d/%m/%Y %H:%M"),
        [agenda.ItemAgendado(prod_teste, 2), agenda.ItemAgendado(serv_teste_2, 1)], # serv_teste_2 
        suprimentos_utilizados=[agenda.SuprimentoAgendado(supr_teste, 0.5)]
    )
    assert ag.status == agenda.AgendaStatus.AGENDADO

    # Marca como realizado - a dedução deve ocorrer aqui
    ag.marcar_como_realizado()
    assert ag.status == agenda.AgendaStatus.REALIZADO
    assert prod_teste.estoque == initial_prod_estoque - 2
    assert supr_teste.estoque == initial_supr_estoque - 0.5

def test_agenda_marcar_como_realizado_estoque_insuficiente(func_teste, cli_teste, prod_teste_sem_estoque, supr_teste):
    # Testa marcação como REALIZADO com estoque de produto insuficiente.
    # Cria a agenda com status AGENDADO (não deduz estoque na criação)
    ag = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, 
        (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y %H:%M"), 
        (datetime.now() + timedelta(days=1, hours=1)).strftime("%d/%m/%Y %H:%M"),
        [agenda.ItemAgendado(prod_teste_sem_estoque, 1)], # Tenta usar produto sem estoque
        suprimentos_utilizados=[agenda.SuprimentoAgendado(supr_teste, 0.1)]
    )
    assert ag.status == agenda.AgendaStatus.AGENDADO
    
    with pytest.raises(ValueError, match=rf"Estoque insuficiente\. Produto '{prod_teste_sem_estoque.nome}'."):
        ag.marcar_como_realizado()
    assert ag.status == agenda.AgendaStatus.AGENDADO # Status deve permanecer AGENDADO

def test_agenda_marcar_como_nao_realizado_reverte_estoque(func_teste, cli_teste, prod_teste, supr_teste):
    # Testa a marcação de agendamento como NÃO REALIZADO e a reversão de estoque.
    initial_prod_estoque = prod_teste.estoque
    initial_supr_estoque = supr_teste.estoque

    # Cria e marca agenda como REALIZADO primeiro (para que o estoque seja deduzido)
    past_date_time = datetime.now() - timedelta(days=2)
    future_date_time = datetime.now() - timedelta(days=1)
    
    ag = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, 
        past_date_time.strftime("%d/%m/%Y %H:%M"), 
        future_date_time.strftime("%d/%m/%Y %H:%M"),
        [agenda.ItemAgendado(prod_teste, 1)],
        suprimentos_utilizados=[agenda.SuprimentoAgendado(supr_teste, 0.2)],
        status=agenda.AgendaStatus.REALIZADO # Cria como realizado para deduzir estoque no init
    )
    assert ag.status == agenda.AgendaStatus.REALIZADO
    assert prod_teste.estoque == initial_prod_estoque - 1
    assert supr_teste.estoque == initial_supr_estoque - 0.2

    # Marca como não realizado - o estoque deve ser revertido
    ag.marcar_como_nao_realizado()
    assert ag.status == agenda.AgendaStatus.NAO_REALIZADO
    assert prod_teste.estoque == initial_prod_estoque
    assert supr_teste.estoque == initial_supr_estoque

def test_agenda_atualizar_dados(func_teste, cli_teste, serv_teste, prod_teste, func_teste_2, cli_teste_2):
    # Testa a atualização de diversos dados de uma agenda.
    ag = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, "01/01/2025 10:00", "01/01/2025 11:00",
        [agenda.ItemAgendado(serv_teste, 1)]
    )
    assert ag.status == agenda.AgendaStatus.AGENDADO

    # Atualiza com novos dados
    nova_data_inicio = "02/01/2025 09:00"
    nova_data_fim = "02/01/2025 10:30"
    agenda.Agenda.atualizar_dados_agenda(
        ag.id,
        funcionario=func_teste_2,
        cliente=cli_teste_2,
        data_hora_inicio=nova_data_inicio,
        data_hora_fim=nova_data_fim,
        comentario="Novo comentário",
        status=agenda.AgendaStatus.NAO_REALIZADO
    )
    
    assert ag.funcionario == func_teste_2
    assert ag.cliente == cli_teste_2
    assert ag.data_hora_inicio == datetime(2025, 1, 2, 9, 0)
    assert ag.data_hora_fim == datetime(2025, 1, 2, 10, 30)
    assert ag.comentario == "Novo comentário"
    assert ag.status == agenda.AgendaStatus.NAO_REALIZADO

def test_agenda_atualizar_com_conflito(func_teste, cli_teste, serv_teste, func_teste_2, cli_teste_2):
    # Testa atualização de agenda que resultaria em conflito.
    ag1 = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, "01/01/2025 10:00", "01/01/2025 12:00",
        [agenda.ItemAgendado(serv_teste, 1)]
    )
    # Cria uma segunda agenda usando o mesmo funcionário da primeira, mas em outro horário
    ag2 = agenda.Agenda.criar_agenda(
        func_teste, cli_teste_2, "01/01/2025 14:00", "01/01/2025 16:00",
        [agenda.ItemAgendado(serv_teste, 1)]
    )
    # Tenta atualizar ag2 para o horário de ag1, usando o mesmo funcionário (deve gerar conflito)
    with pytest.raises(ValueError, match="Conflito de horário detectado para a Agenda ID .*"):
        agenda.Agenda.atualizar_dados_agenda(
            ag2.id,
            funcionario=func_teste, # Usando o mesmo funcionário de ag1 para forçar conflito
            data_hora_inicio="01/01/2025 11:00", # Conflita com ag1
            data_hora_fim="01/01/2025 13:00"
        )
    with pytest.raises(ValueError, match="Conflito de horário detectado para a Agenda ID .*"):
        agenda.Agenda.atualizar_dados_agenda(
            ag2.id,
            data_hora_inicio="01/01/2025 11:00", # Conflita com ag1
            data_hora_fim="01/01/2025 13:00"
        )

def test_agenda_deletar(func_teste, cli_teste, serv_teste, prod_teste, supr_teste):
    # Testa a deleção de um agendamento, incluindo reversão de estoque se REALIZADO.
    initial_prod_estoque = prod_teste.estoque
    initial_supr_estoque = supr_teste.estoque

    # Cria uma agenda que será REALIZADA
    ag = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, 
        (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y %H:%M"), 
        (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y %H:%M"),
        [agenda.ItemAgendado(prod_teste, 1)],
        suprimentos_utilizados=[agenda.SuprimentoAgendado(supr_teste, 0.2)],
        status=agenda.AgendaStatus.REALIZADO
    )
    assert ag.status == agenda.AgendaStatus.REALIZADO
    assert prod_teste.estoque == initial_prod_estoque - 1
    assert supr_teste.estoque == initial_supr_estoque - 0.2

    # Deleta a agenda
    agenda.Agenda.deletar_agenda(ag.id)
    assert agenda.Agenda.buscar_agenda(ag.id) is None
    # Verifica se o estoque foi revertido
    assert prod_teste.estoque == initial_prod_estoque
    assert supr_teste.estoque == initial_supr_estoque

def test_agenda_filtrar(func_teste, cli_teste, serv_teste, func_teste_2, cli_teste_2):
    # Testa a filtragem de agendamentos.
    ag1 = agenda.Agenda.criar_agenda(func_teste, cli_teste, "01/01/2024 10:00", "01/01/2024 11:00", [agenda.ItemAgendado(serv_teste, 1)], status=agenda.AgendaStatus.AGENDADO)
    ag2 = agenda.Agenda.criar_agenda(func_teste_2, cli_teste, "05/01/2024 14:00", "05/01/2024 15:00", [agenda.ItemAgendado(serv_teste, 1)], status=agenda.AgendaStatus.REALIZADO)
    ag3 = agenda.Agenda.criar_agenda(func_teste, cli_teste_2, "10/01/2024 09:00", "10/01/2024 10:00", [agenda.ItemAgendado(serv_teste, 1)], status=agenda.AgendaStatus.AGENDADO)
    ag4 = agenda.Agenda.criar_agenda(func_teste_2, cli_teste_2, "15/01/2024 11:00", "15/01/2024 12:00", [agenda.ItemAgendado(serv_teste, 1)], status=agenda.AgendaStatus.NAO_REALIZADO)

    # Filtro por período
    res = agenda.Agenda.filtrar_agendas("01/01/2024", "05/01/2024")
    assert len(res) == 2
    assert ag1 in res
    assert ag2 in res

    # Filtro por funcionário e período
    res = agenda.Agenda.filtrar_agendas("01/01/2024", "15/01/2024", funcionario_obj=func_teste)
    assert len(res) == 2
    assert ag1 in res
    assert ag3 in res

    # Filtro por status e período
    res = agenda.Agenda.filtrar_agendas("01/01/2024", "15/01/2024", status_agenda=agenda.AgendaStatus.REALIZADO)
    assert len(res) == 1
    assert ag2 in res

    # Filtro combinado
    res = agenda.Agenda.filtrar_agendas("01/01/2024", "15/01/2024", cliente_obj=cli_teste_2, status_agenda="NAO REALIZADO")
    assert len(res) == 1
    assert ag4 in res

# --- Testes para a classe Venda (venda.py) ---

def test_venda_criacao_valida_avulsa(func_teste, cli_teste, prod_teste, serv_teste):
    # Testa a criação de uma venda avulsa.
    initial_prod_estoque = prod_teste.estoque
    
    itens_venda = [
        venda.ItemVenda(prod_teste, 1, 48.00), # 1 unidade de produto
        venda.ItemVenda(serv_teste, 1, 95.00)  # 1 serviço
    ]
    
    v = venda.Venda.criar_venda(func_teste, cli_teste, itens_venda, "01/07/2024")
    
    assert v.funcionario == func_teste
    assert v.cliente == cli_teste
    assert v.data_venda == date(2024, 7, 1)
    assert v.itens_venda[0].item == prod_teste
    assert v.itens_venda[0].quantidade == 1
    assert v.itens_venda[0].preco_unitario_vendido == 48.00
    assert v.itens_venda[1].item == serv_teste
    assert v.itens_venda[1].quantidade == 1
    assert v.itens_venda[1].preco_unitario_vendido == 95.00
    assert v.valor_total == 48.00 + 95.00
    assert v.agenda is None
    assert prod_teste.estoque == initial_prod_estoque - 1 # Estoque do produto deve ser deduzido
    assert venda.Venda.buscar_venda(v.id) == v

def test_venda_criacao_com_agenda(func_teste, cli_teste, serv_teste, prod_teste, supr_teste):
    # Testa a criação de uma venda associada a um agendamento.
    initial_prod_estoque = prod_teste.estoque
    initial_supr_estoque = supr_teste.estoque

    # Cria uma agenda com itens e suprimentos
    ag = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, 
        (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y %H:%M"), # Data passada
        (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y %H:%M"),
        [agenda.ItemAgendado(serv_teste, 1, 90.00), agenda.ItemAgendado(prod_teste, 1, 45.00)],
        suprimentos_utilizados=[agenda.SuprimentoAgendado(supr_teste, 0.5)]
    )
    assert ag.status == agenda.AgendaStatus.AGENDADO # Inicialmente AGENDADO
    
    # Cria a venda associando a agenda
    v = venda.Venda.criar_venda(func_teste, cli_teste, [], "01/07/2024", agenda_obj=ag)
    
    assert v.agenda == ag
    assert ag.status == agenda.AgendaStatus.REALIZADO # Status da agenda deve mudar para REALIZADO
    assert prod_teste.estoque == initial_prod_estoque - 1 # Estoque do produto da agenda deduzido
    assert supr_teste.estoque == initial_supr_estoque - 0.5 # Estoque do suprimento da agenda deduzido
    assert v.valor_total == ag.valor_total # Valor total da venda deve ser o da agenda

def test_venda_criacao_sem_itens_e_sem_agenda(func_teste, cli_teste): # Adicionado fixtures como argumentos
    # Testa a criação de uma venda sem itens e sem agenda (deve falhar).
    with pytest.raises(ValueError, match="A venda deve conter pelo menos um ItemVenda ou estar associada a uma Agenda."):
        venda.Venda(None, func_teste, cli_teste, [], "01/07/2024", agenda_obj=None)

def test_venda_estoque_insuficiente_avulsa(func_teste, cli_teste, prod_teste_sem_estoque):
    # Testa a criação de venda avulsa com produto sem estoque (deve falhar).
    with pytest.raises(ValueError, match=f"Estoque insuficiente para o produto '{prod_teste_sem_estoque.nome}'."):
        venda.Venda.criar_venda(func_teste, cli_teste, [venda.ItemVenda(prod_teste_sem_estoque, 1)], "01/07/2024")

def test_venda_deletar_venda_reverte_estoque_avulsa(func_teste, cli_teste, prod_teste, serv_teste):
    # Testa a deleção de uma venda avulsa e a reversão de estoque de produtos.
    initial_prod_estoque = prod_teste.estoque
    
    v = venda.Venda.criar_venda(func_teste, cli_teste, [venda.ItemVenda(prod_teste, 1)], "01/07/2024")
    assert prod_teste.estoque == initial_prod_estoque - 1
    
    venda.Venda.deletar_venda(v.id)
    assert venda.Venda.buscar_venda(v.id) is None
    assert prod_teste.estoque == initial_prod_estoque # Estoque deve ser revertido

def test_venda_deletar_venda_com_agenda_nao_reverte_agenda_status(func_teste, cli_teste, serv_teste, prod_teste, supr_teste):
    # Testa deleção de venda associada a agenda (status da agenda não deve ser revertido automaticamente).
    initial_prod_estoque = prod_teste.estoque
    initial_supr_estoque = supr_teste.estoque

    ag = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, 
        (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y %H:%M"), 
        (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y %H:%M"),
        [agenda.ItemAgendado(serv_teste, 1), agenda.ItemAgendado(prod_teste, 1)],
        suprimentos_utilizados=[agenda.SuprimentoAgendado(supr_teste, 0.5)]
    )
    v = venda.Venda.criar_venda(func_teste, cli_teste, [], "01/07/2024", agenda_obj=ag)
    
    assert ag.status == agenda.AgendaStatus.REALIZADO
    assert prod_teste.estoque == initial_prod_estoque - 1
    assert supr_teste.estoque == initial_supr_estoque - 0.5

    venda.Venda.deletar_venda(v.id)
    assert venda.Venda.buscar_venda(v.id) is None
    assert ag.status == agenda.AgendaStatus.REALIZADO # Status da agenda permanece REALIZADO
    assert prod_teste.estoque == initial_prod_estoque - 1 # Estoque não é revertido por deleção da venda
    assert supr_teste.estoque == initial_supr_estoque - 0.5

def test_venda_atualizar_dados(func_teste, cli_teste, prod_teste, serv_teste, func_teste_2, cli_teste_2):
    # Testa a atualização de dados da venda.
    v = venda.Venda.criar_venda(func_teste, cli_teste, [venda.ItemVenda(serv_teste, 1)], "01/07/2024")
    
    venda.Venda.atualizar_dados_venda(
        v.id,
        funcionario=func_teste_2,
        cliente=cli_teste_2,
        data_venda="05/07/2024",
        comentario="Venda atualizada"
    )
    assert v.funcionario == func_teste_2
    assert v.cliente == cli_teste_2
    assert v.data_venda == date(2024, 7, 5)
    assert v.comentario == "Venda atualizada"

def test_venda_atualizar_agenda_para_nova_agenda(func_teste, cli_teste, serv_teste, prod_teste, supr_teste, func_teste_2, cli_teste_2):
    # Testa a atualização de uma venda para associar a uma nova agenda.
    # Cria primeira agenda (não associada inicialmente)
    ag1 = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, 
        (datetime.now() - timedelta(days=5)).strftime("%d/%m/%Y %H:%M"), 
        (datetime.now() - timedelta(days=4)).strftime("%d/%m/%Y %H:%M"),
        [agenda.ItemAgendado(serv_teste, 1), agenda.ItemAgendado(prod_teste, 1)],
        suprimentos_utilizados=[agenda.SuprimentoAgendado(supr_teste, 0.5)]
    )
    # Cria segunda agenda (será a nova agenda da venda)
    ag2 = agenda.Agenda.criar_agenda(
        func_teste_2, cli_teste_2, 
        (datetime.now() - timedelta(days=3)).strftime("%d/%m/%Y %H:%M"), 
        (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y %H:%M"),
        [agenda.ItemAgendado(serv_teste, 0.5), agenda.ItemAgendado(prod_teste, 2)],
        suprimentos_utilizados=[agenda.SuprimentoAgendado(supr_teste, 0.1)]
    )
    
    initial_prod_estoque = prod_teste.estoque # Estoque antes de qualquer dedução
    initial_supr_estoque = supr_teste.estoque

    # Cria uma venda avulsa
    v = venda.Venda.criar_venda(func_teste, cli_teste, [venda.ItemVenda(prod_teste, 1)], "01/07/2024")
    assert v.agenda is None
    assert prod_teste.estoque == initial_prod_estoque - 1 # Produto da venda avulsa deduzido

    # Atualiza a venda para associar à ag2
    venda.Venda.atualizar_dados_venda(v.id, agenda_obj=ag2)

    assert v.agenda == ag2
    assert ag2.status == agenda.AgendaStatus.REALIZADO # Nova agenda deve ser marcada como REALIZADO
    # Estoques devem refletir a dedução da AG2
    assert prod_teste.estoque == (initial_prod_estoque - 1) - 2 # -1 da venda avulsa, -2 da ag2
    assert supr_teste.estoque == initial_supr_estoque - 0.1 # -0.1 da ag2

    # Funcionário e cliente da venda devem ser atualizados para os da agenda
    assert v.funcionario == func_teste_2
    assert v.cliente == cli_teste_2

def test_venda_atualizar_agenda_para_remover_agenda(func_teste, cli_teste, serv_teste, prod_teste, supr_teste):
    # Testa a atualização de uma venda para remover uma agenda associada.
    initial_prod_estoque = prod_teste.estoque
    initial_supr_estoque = supr_teste.estoque

    # Cria agenda e associa a uma venda (agenda será REALIZADO)
    ag = agenda.Agenda.criar_agenda(
        func_teste, cli_teste, 
        (datetime.now() - timedelta(days=5)).strftime("%d/%m/%Y %H:%M"), 
        (datetime.now() - timedelta(days=4)).strftime("%d/%m/%Y %H:%M"),
        [agenda.ItemAgendado(serv_teste, 1), agenda.ItemAgendado(prod_teste, 1)],
        suprimentos_utilizados=[agenda.SuprimentoAgendado(supr_teste, 0.5)]
    )
    v = venda.Venda.criar_venda(func_teste, cli_teste, [], "01/07/2024", agenda_obj=ag)
    
    assert ag.status == agenda.AgendaStatus.REALIZADO
    assert prod_teste.estoque == initial_prod_estoque - 1
    assert supr_teste.estoque == initial_supr_estoque - 0.5

    # Atualiza a venda para remover a agenda (e reverter o status da agenda)
    venda.Venda.atualizar_dados_venda(v.id, agenda_obj=None)

    assert v.agenda is None
    assert ag.status == agenda.AgendaStatus.AGENDADO # Agenda deve voltar para AGENDADO
    assert prod_teste.estoque == initial_prod_estoque # Estoques devem ser revertidos
    assert supr_teste.estoque == initial_supr_estoque

# --- Testes para a classe Despesa (despesa.py) ---

def test_despesa_compra_criacao_valida(forn_teste, prod_teste, supr_teste, maq_teste_operando):
    # Testa a criação de uma despesa de compra.
    initial_prod_estoque = prod_teste.estoque
    initial_supr_estoque = supr_teste.estoque

    # Compra um produto
    c1 = despesa.Compra(None, forn_teste, prod_teste, 5, 40.00, "01/07/2024", "Compra de produtos")
    assert c1.valor_total == 200.00
    assert c1.item_comprado == prod_teste
    assert prod_teste.estoque == initial_prod_estoque + 5 # Estoque do produto deve aumentar
    assert prod_teste.custo_compra == 40.00 # Custo de compra atualizado
    assert len(prod_teste._historico_custo_compra) == 1 # Acessa o atributo interno

    # Compra um suprimento
    c2 = despesa.Compra(None, forn_teste, supr_teste, 1.5, 9.00, "02/07/2024", "Compra de suprimentos")
    assert c2.valor_total == 13.50
    assert c2.item_comprado == supr_teste
    assert supr_teste.estoque == initial_supr_estoque + 1.5 # Estoque do suprimento deve aumentar
    assert supr_teste.custo_unitario == 9.00 # Custo unitário atualizado
    assert len(supr_teste._historico_custo_compra) == 1 # Acessa o atributo interno

    # Compra uma máquina (não altera estoque)
    c3 = despesa.Compra(None, forn_teste, maq_teste_operando, 1, 1400.00, "03/07/2024", "Compra de máquina")
    assert c3.valor_total == 1400.00
    assert c3.item_comprado == maq_teste_operando

def test_despesa_fixo_terceiro_criacao_valida(forn_teste):
    # Testa a criação de uma despesa fixa/terceiro.
    df1 = despesa.FixoTerceiro(None, 1200.00, "Aluguel", forn_teste, "05/07/2024")
    assert df1.valor_total == 1200.00
    assert df1.tipo_despesa_str == "Aluguel"
    assert df1.fornecedor_obj == forn_teste

    df2 = despesa.FixoTerceiro(None, 300.00, "Conta de Luz", None, "06/07/2024")
    assert df2.fornecedor_obj is None

def test_despesa_salario_criacao_valida(func_teste):
    # Testa a criação de uma despesa de salário.
    ds = despesa.Salario(None, func_teste, 3000.00, 500.00, "10/07/2024")
    assert ds.valor_total == 2500.00 # Salário Bruto - Descontos
    assert ds.funcionario_obj == func_teste
    assert ds.salario_bruto == 3000.00
    assert ds.descontos == 500.00

def test_despesa_comissao_criacao_valida(func_teste):
    # Testa a criação de uma despesa de comissão.
    dc = despesa.Comissao(None, func_teste, 10000.00, 5000.00, 0.05, 0.02, "15/07/2024")
    assert dc.valor_total == (10000 * 0.05) + (5000 * 0.02) # 500 + 100 = 600
    assert dc.funcionario_obj == func_teste
    assert dc.valor_soma_servicos == 10000.00
    assert dc.taxa_servicos == 0.05

def test_despesa_outros_criacao_valida():
    # Testa a criação de uma despesa de outros.
    do = despesa.Outros(None, 150.00, "Material de Escritório", "20/07/2024")
    assert do.valor_total == 150.00
    assert do.tipo_despesa_str == "Material de Escritório"

def test_despesa_atualizar_dados(forn_teste):
    # Testa a atualização de dados de uma despesa genérica.
    d = despesa.FixoTerceiro(None, 500.00, "Manutenção", forn_teste, "01/01/2024")
    despesa.Despesa.atualizar_dados_despesa(d.id, valor_total=600.00, comentario="Comentário atualizado", data_despesa="02/01/2024")
    assert d.valor_total == 600.00
    assert d.comentario == "Comentário atualizado"
    assert d.data_despesa == date(2024, 1, 2)

def test_despesa_deletar(forn_teste, prod_teste):
    # Testa a deleção de uma despesa.
    initial_prod_estoque = prod_teste.estoque

    # Cria uma compra para testar deleção e não reversão de estoque (pois a compra não altera estoque na deleção)
    c = despesa.Compra(None, forn_teste, prod_teste, 2, 30.00, "01/07/2024")
    assert prod_teste.estoque == initial_prod_estoque + 2 # Estoque aumentou na criação

    despesa.Despesa.deletar_despesa(c.id)
    assert despesa.Despesa.buscar_despesa(c.id) is None
    assert prod_teste.estoque == initial_prod_estoque + 2 # Estoque não deve ser revertido (deleção de compra não reverte)

def test_despesa_filtrar(forn_teste, func_teste, prod_teste, supr_teste, maq_teste_operando):
    # Testa a filtragem de despesas.
    # Despesas de Julho
    d1 = despesa.Compra(None, forn_teste, prod_teste, 1, 10.0, "01/07/2024", "Compra de prod X")
    d2 = despesa.FixoTerceiro(None, 500.0, "Internet", forn_teste, "05/07/2024")
    d3 = despesa.Salario(None, func_teste, 2000.0, 200.0, "10/07/2024", "Salário mensal")
    d4 = despesa.Outros(None, 100.0, "Limpeza", "15/07/2024", "Serviço de limpeza externa")
    # Despesa de Agosto
    d5 = despesa.Compra(None, forn_teste, supr_teste, 1, 5.0, "01/08/2024", "Compra de sup Y")

    # Filtro por período
    res = despesa.Despesa.filtrar_despesas("01/07/2024", "31/07/2024")
    assert len(res) == 4
    assert d1 in res and d2 in res and d3 in res and d4 in res

    # Filtro por tipo
    res = despesa.Despesa.filtrar_despesas("01/07/2024", "01/08/2024", tipo_despesa_str="COMPRA")
    assert len(res) == 2
    assert d1 in res and d5 in res

    # Filtro por fornecedor
    res = despesa.Despesa.filtrar_despesas("01/07/2024", "01/08/2024", fornecedor_obj=forn_teste)
    assert len(res) == 3 # d1, d2, d5
    assert d1 in res and d2 in res and d5 in res

    # Filtro por funcionário
    res = despesa.Despesa.filtrar_despesas("01/07/2024", "01/08/2024", funcionario_obj=func_teste)
    assert len(res) == 1
    assert d3 in res

    # Filtro por item de compra (produto específico)
    res = despesa.Despesa.filtrar_despesas("01/07/2024", "01/08/2024", item_compra_obj=prod_teste)
    assert len(res) == 1
    assert d1 in res

    # Filtro por comentário parcial
    res = despesa.Despesa.filtrar_despesas("01/07/2024", "01/08/2024", comentario_parcial="compra")
    assert len(res) == 2
    assert d1 in res and d5 in res

    # Filtro combinado complexo
    res = despesa.Despesa.filtrar_despesas(
        "01/07/2024", "31/07/2024",
        tipo_despesa_str=["FIXOTERCEIRO", "OUTROS"],
        fornecedor_obj = forn_teste,
        comentario_parcial="limpeza"
    )
    assert len(res) == 0

    
    res = despesa.Despesa.filtrar_despesas(
        "01/07/2024", "31/07/2024",
        tipo_despesa_str=["FIXOTERCEIRO", "OUTROS"],
        fornecedor_obj=forn_teste # d4 não tem forn_teste
    )
    assert len(res) == 1 # d2 (FixoTerceiro com forn_teste)
    assert d2 in res

    # Teste com um item de compra que é uma string
    compra_str_item = despesa.Compra(None, forn_teste, "Licença de Software", 1, 500.0, "01/07/2024")
    res = despesa.Despesa.filtrar_despesas("01/07/2024", "31/07/2024", item_compra_obj="Licença de Software")
    assert len(res) == 1
    assert compra_str_item in res