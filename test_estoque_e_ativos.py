import pytest
# Importa as classes dos módulos que serão testados
import produto
import servico
import suprimento
import maquina

# --- Fixtures Reutilizáveis ---

@pytest.fixture
def produto_valido_base():
    # Retorna um produto básico para ser usado em testes que precisam de um produto existente.
    return produto.Produto(None, "Teclado Mecânico", 350.00, 50)

@pytest.fixture
def servico_valido_base():
    # Retorna um serviço básico para ser usado em testes que precisam de um serviço existente.
    return servico.Servico(None, "Instalação de Software", 150.00, 30.00)

@pytest.fixture
def suprimento_valido_base():
    # Retorna um suprimento básico para ser usado em testes.
    return suprimento.Suprimento(None, "Fita Adesiva", "rolo", 5.00, 100.5)

@pytest.fixture
def maquina_valida_base():
    # Retorna uma máquina básica para ser usada em testes.
    return maquina.Maquina(None, "Furadeira Industrial", "ABC-123-X", 2500.00, maquina.StatusMaquina.OPERANDO)

# --- Testes para a classe Produto (produto.py) ---

def test_produto_criacao_valida():
    # Testa a criação de um produto válido.
    id_inicial = produto.Produto._proximo_id_disponivel
    p = produto.Produto(None, "Monitor Gamer", 1500.00, 10)
    assert p.id == id_inicial
    assert p.nome == "Monitor Gamer"
    assert p.preco == 1500.00
    assert p.estoque == 10
    assert p.custo_compra == 0.0 # Custo inicial é zero
    assert p._historico_custo_compra == []
    assert produto.Produto.buscar_produto_id(p.id) == p
    assert produto.Produto.buscar_produto("Monitor Gamer") == p

def test_produto_criacao_id_especifico():
    # Testa a criação de um produto com ID específico.
    p = produto.Produto(100, "Cadeira Ergonômica", 900.00, 5)
    assert p.id == 100
    assert produto.Produto.buscar_produto_id(100) == p

def test_produto_colisao_nome():
    # Testa a colisão de nome ao criar um novo produto.
    produto.Produto(None, "Mouse Sem Fio", 100.00, 20)
    with pytest.raises(ValueError, match=r"Produto com o nome 'Mouse Sem Fio' já existe."):
        produto.Produto(None, "Mouse Sem Fio", 120.00, 15)
    with pytest.raises(ValueError, match=r"Produto com o nome 'Mouse Sem Fio' já existe."):
        produto.Produto(None, "mouse sem fio", 120.00, 15) # Case-insensitive

def test_produto_colisao_id():
    # Testa a colisão de ID ao criar um novo produto.
    produto.Produto(1, "SSD 1TB", 500.00, 30)
    with pytest.raises(ValueError, match="Já existe um produto com o ID 1."):
        produto.Produto(1, "HD Externo", 400.00, 25)

def test_produto_id_invalido():
    # Testa a criação de produto com ID inválido.
    with pytest.raises(ValueError, match="O ID do produto deve ser um número inteiro positivo."):
        produto.Produto(0, "Produto Zero", 10.00, 1)
    with pytest.raises(ValueError, match="O ID do produto deve ser um número inteiro positivo."):
        produto.Produto(-5, "Produto Negativo", 10.00, 1)
    with pytest.raises(ValueError, match="O ID do produto deve ser um número inteiro positivo."):
        produto.Produto("abc", "Produto String", 10.00, 1)

def test_produto_nome_vazio():
    # Testa a validação de nome vazio para produto.
    with pytest.raises(ValueError, match="O nome do produto não pode ser vazio."):
        produto.Produto(None, " ", 10.00, 1)

def test_produto_preco_invalido():
    # Testa a validação de preço inválido.
    with pytest.raises(ValueError, match="O preço deve ser maior que zero."):
        produto.Produto(None, "Item Zero", 0.00, 1)
    with pytest.raises(ValueError, match="O preço deve ser maior que zero."):
        produto.Produto(None, "Item Negativo", -10.00, 1)
    with pytest.raises(TypeError, match="O preço deve ser um número válido."):
        produto.Produto(None, "Item String", "abc", 1)

def test_produto_estoque_invalido():
    # Testa a validação de estoque inválido.
    with pytest.raises(ValueError, match="A quantidade em estoque não pode ser negativa."):
        produto.Produto(None, "Item Estoque Negativo", 10.00, -1)
    with pytest.raises(TypeError, match=r"A quantidade em estoque deve ser um número válido \(inteiro ou decimal\)\."):
        produto.Produto(None, "Item Estoque String", 10.00, "abc")
    # Teste de float, que agora é válido
    p_float = produto.Produto(None, "Item Estoque Float", 10.00, 10.5)
    assert p_float.estoque == 10.5

def test_produto_buscar_produto(produto_valido_base):
    # Testa a busca de produto por nome.
    found_p = produto.Produto.buscar_produto("Teclado Mecânico")
    assert found_p == produto_valido_base
    assert produto.Produto.buscar_produto("Produto Inexistente") is None

def test_produto_buscar_produto_id(produto_valido_base):
    # Testa a busca de produto por ID.
    found_p = produto.Produto.buscar_produto_id(produto_valido_base.id)
    assert found_p == produto_valido_base
    assert produto.Produto.buscar_produto_id(9999) is None

def test_produto_listar_produtos(produto_valido_base):
    # Testa a listagem de todos os produtos.
    p2 = produto.Produto(None, "Webcam HD", 200.00, 30)
    all_products = produto.Produto.listar_produtos()
    assert len(all_products) == 2
    assert produto_valido_base in all_products
    assert p2 in all_products

def test_produto_atualizar_dados_produto(produto_valido_base):
    # Testa a atualização de dados de um produto.
    produto.Produto.atualizar_dados_produto(produto_valido_base.id, nome="Teclado Ergonômico", preco=400.00, estoque=60)
    assert produto_valido_base.nome == "Teclado Ergonômico"
    assert produto_valido_base.preco == 400.00
    assert produto_valido_base.estoque == 60
    # Verifica se o nome antigo foi removido do dicionário de nomes
    assert produto.Produto.buscar_produto("Teclado Mecânico") is None
    assert produto.Produto.buscar_produto("Teclado Ergonômico") == produto_valido_base

def test_produto_atualizar_dados_produto_nao_encontrado():
    # Testa a atualização de dados de um produto inexistente.
    with pytest.raises(ValueError, match="Produto com ID 999 não encontrado para atualização."):
        produto.Produto.atualizar_dados_produto(999, nome="Inexistente")

def test_produto_atualizar_nome_colisao(produto_valido_base):
    p_existente = produto.Produto(None, "Fone de Ouvido", 100.00, 10)
    with pytest.raises(ValueError, match=r"Não foi possível atualizar o nome\. Já existe um produto com o nome 'Fone de Ouvido'\."):
        produto.Produto.atualizar_dados_produto(produto_valido_base.id, nome="Fone de Ouvido")

def test_produto_deletar_produto(produto_valido_base):
    # Testa a deleção de um produto.
    produto.Produto.deletar_produto(produto_valido_base.id)
    assert produto.Produto.buscar_produto_id(produto_valido_base.id) is None
    assert produto.Produto.buscar_produto("Teclado Mecânico") is None
    assert produto_valido_base not in produto.Produto.listar_produtos()

def test_produto_deletar_produto_nao_encontrado():
    # Testa a deleção de um produto inexistente.
    with pytest.raises(ValueError, match="Produto com ID 999 não encontrado para exclusão."):
        produto.Produto.deletar_produto(999)

# --- Testes para a classe Servico (servico.py) ---

def test_servico_criacao_valida():
    # Testa a criação de um serviço válido.
    id_inicial = servico.Servico._proximo_id_disponivel
    s = servico.Servico(None, "Manutenção Preventiva", 300.00, 80.00)
    assert s.id == id_inicial
    assert s.nome == "Manutenção Preventiva"
    assert s.valor_venda == 300.00
    assert s.custo == 80.00
    assert servico.Servico.buscar_servico_id(s.id) == s
    assert servico.Servico.buscar_servico("Manutenção Preventiva") == s

def test_servico_criacao_id_especifico():
    # Testa a criação de um serviço com ID específico.
    s = servico.Servico(200, "Consultoria de TI", 600.00, 200.00)
    assert s.id == 200
    assert servico.Servico.buscar_servico_id(200) == s

def test_servico_colisao_nome():
    # Testa a colisão de nome ao criar um novo serviço.
    servico.Servico(None, "Formatação de PC", 100.00, 20.00)
    with pytest.raises(ValueError, match=r"Serviço com o nome 'Formatação de PC' já existe."):
        servico.Servico(None, "Formatação de PC", 120.00, 25.00)
    with pytest.raises(ValueError, match=r"Serviço com o nome 'Formatação de PC' já existe."):
        servico.Servico(None, "formatação de pc", 120.00, 25.00) # Case-insensitive

def test_servico_colisao_id():
    # Testa a colisão de ID ao criar um novo serviço.
    servico.Servico(1, "Suporte Remoto", 150.00, 50.00)
    with pytest.raises(ValueError, match="Já existe um serviço com o ID 1."):
        servico.Servico(1, "Instalação de Rede", 200.00, 60.00)

def test_servico_id_invalido():
    # Testa a criação de serviço com ID inválido.
    with pytest.raises(ValueError, match="O ID do serviço deve ser um número inteiro positivo."):
        servico.Servico(0, "Servico Zero", 10.00, 1.00)

def test_servico_nome_vazio():
    # Testa a validação de nome vazio para serviço.
    with pytest.raises(ValueError, match="O nome do serviço não pode ser vazio."):
        servico.Servico(None, " ", 10.00, 1.00)

def test_servico_valor_venda_invalido():
    # Testa a validação de valor de venda inválido.
    with pytest.raises(ValueError, match="O valor de venda deve ser maior que zero."):
        servico.Servico(None, "Servico Zero Venda", 0.00, 1.00)
    with pytest.raises(ValueError, match="O valor de venda deve ser maior que zero."):
        servico.Servico(None, "Servico Negativo Venda", -10.00, 1.00)
    with pytest.raises(TypeError, match="O valor de venda deve ser um número válido."):
        servico.Servico(None, "Servico String Venda", "abc", 1.00)

def test_servico_custo_invalido():
    # Testa a validação de custo inválido.
    with pytest.raises(ValueError, match="O custo deve ser maior que zero."):
        servico.Servico(None, "Servico Zero Custo", 10.00, 0.00)
    with pytest.raises(ValueError, match="O custo deve ser maior que zero."):
        servico.Servico(None, "Servico Negativo Custo", 10.00, -1.00)
    with pytest.raises(TypeError, match="O custo deve ser um número válido."):
        servico.Servico(None, "Servico String Custo", 10.00, "abc")

def test_servico_buscar_servico(servico_valido_base):
    # Testa a busca de serviço por nome.
    found_s = servico.Servico.buscar_servico("Instalação de Software")
    assert found_s == servico_valido_base
    assert servico.Servico.buscar_servico("Servico Inexistente") is None

def test_servico_buscar_servico_id(servico_valido_base):
    # Testa a busca de serviço por ID.
    found_s = servico.Servico.buscar_servico_id(servico_valido_base.id)
    assert found_s == servico_valido_base
    assert servico.Servico.buscar_servico_id(9999) is None

def test_servico_listar_servicos(servico_valido_base):
    # Testa a listagem de todos os serviços.
    s2 = servico.Servico(None, "Recuperação de Dados", 500.00, 150.00)
    all_services = servico.Servico.listar_servicos()
    assert len(all_services) == 2
    assert servico_valido_base in all_services
    assert s2 in all_services

def test_servico_atualizar_dados_servico(servico_valido_base):
    # Testa a atualização de dados de um serviço.
    servico.Servico.atualizar_dados_servico(servico_valido_base.id, nome="Instalação de Aplicativos", valor_venda=180.00, custo=40.00)
    assert servico_valido_base.nome == "Instalação de Aplicativos"
    assert servico_valido_base.valor_venda == 180.00
    assert servico_valido_base.custo == 40.00
    # Verifica se o nome antigo foi removido do dicionário de nomes
    assert servico.Servico.buscar_servico("Instalação de Software") is None
    assert servico.Servico.buscar_servico("Instalação de Aplicativos") == servico_valido_base

def test_servico_atualizar_dados_servico_nao_encontrado():
    # Testa a atualização de dados de um serviço inexistente.
    with pytest.raises(ValueError, match="Serviço com ID 999 não encontrado para atualização."):
        servico.Servico.atualizar_dados_servico(999, nome="Inexistente")

def test_servico_atualizar_nome_colisao(servico_valido_base):
    s_existente = servico.Servico(None, "Limpeza de Vírus", 250.00, 50.00)
    with pytest.raises(ValueError, match=r"Não foi possível atualizar o nome\. Já existe um serviço com o nome 'Limpeza de Vírus'\."):
        servico.Servico.atualizar_dados_servico(servico_valido_base.id, nome="Limpeza de Vírus")

def test_servico_deletar_servico(servico_valido_base):
    # Testa a deleção de um serviço.
    servico.Servico.deletar_servico(servico_valido_base.id)
    assert servico.Servico.buscar_servico_id(servico_valido_base.id) is None
    assert servico.Servico.buscar_servico("Instalação de Software") is None
    assert servico_valido_base not in servico.Servico.listar_servicos()

def test_servico_deletar_servico_nao_encontrado():
    # Testa a deleção de um serviço inexistente.
    with pytest.raises(ValueError, match="Serviço com ID 999 não encontrado para exclusão."):
        servico.Servico.deletar_servico(999)

# --- Testes para a classe Suprimento (suprimento.py) ---

def test_suprimento_criacao_valida():
    # Testa a criação de um suprimento válido.
    id_inicial = suprimento.Suprimento._proximo_id_disponivel
    s = suprimento.Suprimento(None, "Papel Toalha", "rolo", 12.50, 20.0)
    assert s.id == id_inicial
    assert s.nome == "Papel Toalha"
    assert s.unidade_medida == "rolo"
    assert s.custo_unitario == 12.50
    assert s.estoque == 20.0
    assert s._historico_custo_compra == []
    assert suprimento.Suprimento.buscar_suprimento_id(s.id) == s
    assert suprimento.Suprimento.buscar_suprimento_nome("Papel Toalha") == s

def test_suprimento_criacao_id_especifico():
    # Testa a criação de um suprimento com ID específico.
    s = suprimento.Suprimento(300, "Luvas Descartáveis", "caixa", 25.00, 50.0)
    assert s.id == 300
    assert suprimento.Suprimento.buscar_suprimento_id(300) == s

def test_suprimento_colisao_nome():
    # Testa a colisão de nome ao criar um novo suprimento.
    suprimento.Suprimento(None, "Álcool Gel", "litro", 15.00, 10.0)
    with pytest.raises(ValueError, match=r"Já existe um suprimento com o nome 'Álcool Gel'."):
        suprimento.Suprimento(None, "Álcool Gel", "galão", 50.00, 5.0)
    with pytest.raises(ValueError, match=r"Já existe um suprimento com o nome 'Álcool Gel'."):
        suprimento.Suprimento(None, "álcool gel", "galão", 50.00, 5.0) # Case-insensitive

def test_suprimento_colisao_id():
    # Testa a colisão de ID ao criar um novo suprimento.
    suprimento.Suprimento(1, "Caneta Azul", "unidade", 2.00, 100.0)
    with pytest.raises(ValueError, match="Já existe um suprimento com o ID 1."):
        suprimento.Suprimento(1, "Lápis Preto", "unidade", 1.00, 200.0)

def test_suprimento_id_invalido():
    # Testa a criação de suprimento com ID inválido.
    with pytest.raises(ValueError, match="O ID do suprimento deve ser um número inteiro positivo."):
        suprimento.Suprimento(0, "Sup Zero", "unidade", 1.00, 1.0)

def test_suprimento_nome_vazio():
    # Testa a validação de nome vazio para suprimento.
    with pytest.raises(ValueError, match="O nome do suprimento não pode ser vazio."):
        suprimento.Suprimento(None, " ", "unidade", 1.00, 1.0)

def test_suprimento_unidade_medida_vazia():
    # Testa a validação de unidade de medida vazia.
    with pytest.raises(ValueError, match="A unidade de medida não pode ser vazia."):
        suprimento.Suprimento(None, "Bateria AA", " ", 5.00, 10.0)

def test_suprimento_custo_unitario_invalido():
    # Testa a validação de custo unitário inválido.
    with pytest.raises(ValueError, match="O custo unitário deve ser maior que zero."):
        suprimento.Suprimento(None, "Sup Zero Custo", "unidade", 0.00, 1.0)
    with pytest.raises(TypeError, match="O custo unitário deve ser um número válido."):
        suprimento.Suprimento(None, "Sup String Custo", "unidade", "abc", 1.0)

def test_suprimento_estoque_invalido():
    # Testa a validação de estoque inválido (float).
    with pytest.raises(ValueError, match="A quantidade em estoque não pode ser negativa."):
        suprimento.Suprimento(None, "Sup Estoque Negativo", "unidade", 1.00, -1.0)
    with pytest.raises(TypeError, match="A quantidade em estoque deve ser um número válido."):
        suprimento.Suprimento(None, "Sup Estoque String", "unidade", 1.00, "abc")

def test_suprimento_buscar_suprimento_id(suprimento_valido_base):
    # Testa a busca de suprimento por ID.
    found_s = suprimento.Suprimento.buscar_suprimento_id(suprimento_valido_base.id)
    assert found_s == suprimento_valido_base
    assert suprimento.Suprimento.buscar_suprimento_id(9999) is None

def test_suprimento_buscar_suprimento_nome(suprimento_valido_base):
    # Testa a busca de suprimento por nome.
    found_s = suprimento.Suprimento.buscar_suprimento_nome("Fita Adesiva")
    assert found_s == suprimento_valido_base
    assert suprimento.Suprimento.buscar_suprimento_nome("suprimento inexistente") is None

def test_suprimento_listar_suprimentos(suprimento_valido_base):
    # Testa a listagem de todos os suprimentos.
    s2 = suprimento.Suprimento(None, "Papel Sulfite", "pacote", 25.00, 50.0)
    all_sups = suprimento.Suprimento.listar_suprimentos()
    assert len(all_sups) == 2
    assert suprimento_valido_base in all_sups
    assert s2 in all_sups

def test_suprimento_atualizar_dados_suprimento(suprimento_valido_base):
    # Testa a atualização de dados de um suprimento.
    suprimento.Suprimento.atualizar_dados_suprimento(suprimento_valido_base.id, nome="Fita Crepe", unidade_medida="metro", custo_unitario=6.00, estoque=120.0)
    assert suprimento_valido_base.nome == "Fita Crepe"
    assert suprimento_valido_base.unidade_medida == "metro"
    assert suprimento_valido_base.custo_unitario == 6.00
    assert suprimento_valido_base.estoque == 120.0
    # Verifica se o nome antigo foi removido do dicionário de nomes
    assert suprimento.Suprimento.buscar_suprimento_nome("Fita Adesiva") is None
    assert suprimento.Suprimento.buscar_suprimento_nome("Fita Crepe") == suprimento_valido_base

def test_suprimento_atualizar_dados_suprimento_nao_encontrado():
    # Testa a atualização de dados de um suprimento inexistente.
    with pytest.raises(ValueError, match="Suprimento com ID 999 não encontrado para atualização."):
        suprimento.Suprimento.atualizar_dados_suprimento(999, nome="Inexistente")

def test_suprimento_atualizar_nome_colisao(suprimento_valido_base):
    s_existente = suprimento.Suprimento(None, "Grampos", "caixa", 3.00, 50.0)
    with pytest.raises(ValueError, match=r"Não foi possível atualizar o nome\. Já existe um suprimento com o nome 'Grampos'\."):
        suprimento.Suprimento.atualizar_dados_suprimento(suprimento_valido_base.id, nome="Grampos")

def test_suprimento_deletar_suprimento(suprimento_valido_base):
    # Testa a deleção de um suprimento.
    suprimento.Suprimento.deletar_suprimento(suprimento_valido_base.id)
    assert suprimento.Suprimento.buscar_suprimento_id(suprimento_valido_base.id) is None
    assert suprimento.Suprimento.buscar_suprimento_nome("Fita Adesiva") is None
    assert suprimento_valido_base not in suprimento.Suprimento.listar_suprimentos()

def test_suprimento_deletar_suprimento_nao_encontrado():
    # Testa a deleção de um suprimento inexistente.
    with pytest.raises(ValueError, match="Suprimento com ID 999 não encontrado para exclusão."):
        suprimento.Suprimento.deletar_suprimento(999)

# --- Testes para a classe Maquina (maquina.py) ---

def test_maquina_criacao_valida():
    # Testa a criação de uma máquina válida.
    id_inicial = maquina.Maquina._proximo_id_disponivel
    m = maquina.Maquina(None, "Fresadora CNC", "CNC-FRES-001", 15000.00, maquina.StatusMaquina.OPERANDO)
    assert m.id == id_inicial
    assert m.nome == "Fresadora CNC"
    assert m.numero_serie == "CNC-FRES-001"
    assert m.custo_aquisicao == 15000.00
    assert m.status == maquina.StatusMaquina.OPERANDO
    assert maquina.Maquina.buscar_maquina_id(m.id) == m
    assert maquina.Maquina.buscar_maquina_serie("CNC-FRES-001") == m

def test_maquina_criacao_id_especifico():
    # Testa a criação de uma máquina com ID específico.
    m = maquina.Maquina(400, "Impressora 3D", "PRN-3D-XYZ", 5000.00, maquina.StatusMaquina.MANUTENCAO)
    assert m.id == 400
    assert maquina.Maquina.buscar_maquina_id(400) == m

def test_maquina_colisao_numero_serie():
    # Testa a colisão de número de série ao criar uma nova máquina.
    maquina.Maquina(None, "Serra Circular", "SERRA-ABC-001", 800.00, maquina.StatusMaquina.OPERANDO)
    with pytest.raises(ValueError, match="Já existe uma máquina com o número de série 'SERRA-ABC-001'."):
        maquina.Maquina(None, "Esmerilhadeira", "SERRA-ABC-001", 600.00, maquina.StatusMaquina.BAIXADO)

def test_maquina_colisao_id():
    # Testa a colisão de ID ao criar uma nova máquina.
    maquina.Maquina(1, "Lixadeira Orbital", "LIX-ORB-001", 300.00, maquina.StatusMaquina.OPERANDO)
    with pytest.raises(ValueError, match="Já existe uma máquina com o ID 1."):
        maquina.Maquina(1, "Plaina Elétrica", "PLA-ELE-001", 400.00, maquina.StatusMaquina.MANUTENCAO)

def test_maquina_id_invalido():
    # Testa a criação de máquina com ID inválido.
    with pytest.raises(ValueError, match="O ID da máquina deve ser um número inteiro positivo."):
        maquina.Maquina(0, "Maq Zero", "ZERO-001", 10.00, maquina.StatusMaquina.OPERANDO)

def test_maquina_nome_vazio():
    # Testa a validação de nome vazio para máquina.
    with pytest.raises(ValueError, match="O nome da máquina não pode ser vazio."):
        maquina.Maquina(None, " ", "VAZIO-001", 10.00, maquina.StatusMaquina.OPERANDO)

def test_maquina_numero_serie_vazio():
    # Testa a validação de número de série vazio.
    with pytest.raises(ValueError, match="O número de série da máquina não pode ser vazio."):
        maquina.Maquina(None, "Máquina Sem Série", " ", 10.00, maquina.StatusMaquina.OPERANDO)

def test_maquina_custo_aquisicao_invalido():
    # Testa a validação de custo de aquisição inválido.
    with pytest.raises(ValueError, match="O custo de aquisição deve ser maior que zero."):
        maquina.Maquina(None, "Maq Zero Custo", "ZERO-CUSTO", 0.00, maquina.StatusMaquina.OPERANDO)
    with pytest.raises(TypeError, match="O custo de aquisição deve ser um número válido."):
        maquina.Maquina(None, "Maq String Custo", "STR-CUSTO", "abc", maquina.StatusMaquina.OPERANDO)

def test_maquina_status_invalido():
    # Testa a validação de status inválido.
    with pytest.raises(ValueError, match=r"Status 'INVALIDO' inválido\. Use um dos valores: \['Operando', 'Em Manutenção', 'Baixado'\]\."):
        maquina.Maquina(None, "Maq Status Inv", "INV-STAT", 100.00, "INVALIDO")
    with pytest.raises(TypeError, match="O status deve ser um membro de StatusMaquina ou uma string válida."):
        maquina.Maquina(None, "Maq Status Type", "TYPE-STAT", 100.00, 123)

def test_maquina_buscar_maquina_id(maquina_valida_base):
    # Testa a busca de máquina por ID.
    found_m = maquina.Maquina.buscar_maquina_id(maquina_valida_base.id)
    assert found_m == maquina_valida_base
    assert maquina.Maquina.buscar_maquina_id(9999) is None

def test_maquina_buscar_maquina_serie(maquina_valida_base):
    # Testa a busca de máquina por número de série.
    found_m = maquina.Maquina.buscar_maquina_serie("ABC-123-X")
    assert found_m == maquina_valida_base
    assert maquina.Maquina.buscar_maquina_serie("SERIE-INEXISTENTE") is None

def test_maquina_listar_maquinas(maquina_valida_base):
    # Testa a listagem de todas as máquinas.
    m2 = maquina.Maquina(None, "Prensa Hidráulica", "PREN-HYD-001", 10000.00, maquina.StatusMaquina.OPERANDO)
    all_machines = maquina.Maquina.listar_maquinas()
    assert len(all_machines) == 2
    assert maquina_valida_base in all_machines
    assert m2 in all_machines

def test_maquina_atualizar_dados_maquina(maquina_valida_base):
    # Testa a atualização de dados de uma máquina.
    maquina.Maquina.atualizar_dados_maquina(maquina_valida_base.id, nome="Furadeira de Bancada", numero_serie="BANC-456-Y", custo_aquisicao=2800.00, status="MANUTENCAO")
    assert maquina_valida_base.nome == "Furadeira de Bancada"
    assert maquina_valida_base.numero_serie == "BANC-456-Y"
    assert maquina_valida_base.custo_aquisicao == 2800.00
    assert maquina_valida_base.status == maquina.StatusMaquina.MANUTENCAO
    # Verifica se a série antiga foi removida do dicionário de séries
    assert maquina.Maquina.buscar_maquina_serie("ABC-123-X") is None
    assert maquina.Maquina.buscar_maquina_serie("BANC-456-Y") == maquina_valida_base

def test_maquina_atualizar_dados_maquina_nao_encontrada():
    # Testa a atualização de dados de uma máquina inexistente.
    with pytest.raises(ValueError, match="Máquina com ID 999 não encontrada para atualização."):
        maquina.Maquina.atualizar_dados_maquina(999, nome="Inexistente")

def test_maquina_atualizar_numero_serie_colisao(maquina_valida_base):
    # Testa a atualização de número de série para um número já existente.
    m_existente = maquina.Maquina(None, "Retificadora", "RET-XYZ-002", 7000.00, maquina.StatusMaquina.OPERANDO)
    with pytest.raises(ValueError, match=r"Não foi possível atualizar o número de série\. Já existe uma máquina com a série 'RET-XYZ-002'\."):
        maquina.Maquina.atualizar_dados_maquina(maquina_valida_base.id, numero_serie="RET-XYZ-002")

def test_maquina_deletar_maquina(maquina_valida_base):
    # Testa a deleção de uma máquina.
    maquina.Maquina.deletar_maquina(maquina_valida_base.id)
    assert maquina.Maquina.buscar_maquina_id(maquina_valida_base.id) is None
    assert maquina.Maquina.buscar_maquina_serie("ABC-123-X") is None
    assert maquina_valida_base not in maquina.Maquina.listar_maquinas()

def test_maquina_deletar_maquina_nao_encontrada():
    # Testa a deleção de uma máquina inexistente.
    with pytest.raises(ValueError, match="Máquina com ID 999 não encontrada para exclusão."):
        maquina.Maquina.deletar_maquina(999)