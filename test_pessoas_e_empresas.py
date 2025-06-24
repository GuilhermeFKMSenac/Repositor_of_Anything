import pytest
from datetime import date, datetime, timedelta
import info as mod_info
import pessoa
import cliente
import funcionario
import fornecedor

@pytest.fixture
def info_contato_valida():
    return mod_info.Informacao(
        telefone="11987654321",
        email="teste@dominio.com",
        endereco="Rua Teste, 123, Bairro Teste, Cidade Teste, SP",
        redes_sociais="instagram.com/teste"
    )

@pytest.fixture
def cpf_valido_aleatorio():
    return pessoa.gerar_cpf_valido()

@pytest.fixture
def cnpj_valido_aleatorio():
    return pessoa.gerar_cnpj_valido()

def test_informacao_criacao_valida(info_contato_valida):
    assert isinstance(info_contato_valida, mod_info.Informacao)
    assert info_contato_valida.telefone == "11 9 8765 4321"
    assert info_contato_valida.email == "teste@dominio.com"
    assert info_contato_valida.endereco["nome_rua"] == "Rua Teste"
    assert info_contato_valida.redes_sociais == "instagram.com/teste"

def test_informacao_telefone_invalido():
    # "123" -> ddd="12", num="3". Erro: "Deve ter 8 ou 9 dígitos após o DDD."
    with pytest.raises(ValueError, match=r"Número nacional inválido: Deve ter 8 ou 9 dígitos após o DDD\."):
        mod_info.Informacao("123", "email@test.com", "Rua Teste, 123", "redes")
    # "99999999999999999" -> ddd="99", num="999999999999999". Erro: "Deve ter 8 ou 9 dígitos após o DDD."
    with pytest.raises(ValueError, match=r"Número nacional inválido: Deve ter 8 ou 9 dígitos após o DDD\."):
        mod_info.Informacao("99999999999999999", "email@test.com", "Rua Teste, 123", "redes")
    # "abcdefgh" -> numero_totalmente_limpo="". Erro: "Formato de número de telefone brasileiro inválido."
    with pytest.raises(ValueError, match="Formato de número de telefone brasileiro inválido."):
        mod_info.Informacao("abcdefgh", "email@test.com", "Rua Teste, 123", "redes")
    # "" -> numero_totalmente_limpo="". Erro: "Formato de número de telefone brasileiro inválido."
    with pytest.raises(ValueError, match="Formato de número de telefone brasileiro inválido."):
        mod_info.Informacao("", "email@test.com", "Rua Teste, 123", "redes")
    
    # Caso: Entrada "01 98765 4321"
    # Interpretação: '0' é prefixo, DDD é '19', número é '87654321'.
    # '87654321' é inválido como fixo porque começa com '8'.
    with pytest.raises(ValueError, match=r"Número brasileiro inválido: Fixo de 8 dígitos não pode começar com 6, 7, 8 ou 9 \(parece celular incompleto\)\."):
        mod_info.Informacao("01 98765 4321", "email@test.com", "Rua Teste, 123", "redes")

    # Caso: Entrada "00112345678" para testar DDD "01" inválido
    # Interpretação: '0' é prefixo, DDD é '01'.
    # '01' como DDD é inválido por começar com '0'.
    with pytest.raises(ValueError, match=r"Número brasileiro inválido: DDD '01' inválido \(não pode começar ou terminar com 0\)\."):
        mod_info.Informacao("00112345678", "email@test.com", "Rua Teste, 123", "redes")

    # Caso: Entrada "10 98765 4321"
    # Interpretação: DDD é '10' (não começa com '0' na string original).
    # '10' como DDD é inválido por terminar com '0'.
    with pytest.raises(ValueError, match=r"Número brasileiro inválido: DDD '10' inválido \(não pode começar ou terminar com 0\)\."):
        mod_info.Informacao("10 98765 4321", "email@test.com", "Rua Teste, 123", "redes")

    # Caso: Entrada "01012345678" para testar DDD "10" inválido com prefixo '0'
    # Interpretação: '0' é prefixo, DDD é '10'.
    # '10' como DDD é inválido por terminar com '0'.
    with pytest.raises(ValueError, match=r"Número brasileiro inválido: DDD '10' inválido \(não pode começar ou terminar com 0\)\."):
        mod_info.Informacao("01012345678", "email@test.com", "Rua Teste, 123", "redes")

    # Caso: Celular de 9 dígitos começando com número inválido
    # Interpretação: DDD '11', número '587654321'.
    # '587654321' é celular de 9 dígitos mas começa com '5'.
    with pytest.raises(ValueError, match=r"Número brasileiro inválido: Celular de 9 dígitos deve começar com 6, 7, 8 ou 9\."):
        mod_info.Informacao("11 58765 4321", "email@test.com", "Rua Teste, 123", "redes")

def test_informacao_email_invalido():
    with pytest.raises(ValueError, match="Formato de e-mail inválido."):
        mod_info.Informacao("11987654321", "emailinvalido", "Rua Teste, 123", "redes")
    with pytest.raises(ValueError, match="Formato de e-mail inválido."):
        mod_info.Informacao("11987654321", "email@.com", "Rua Teste, 123", "redes")
    with pytest.raises(ValueError, match="Formato de e-mail inválido."):
        mod_info.Informacao("11987654321", "", "Rua Teste, 123", "redes")

def test_informacao_endereco_invalido():
    with pytest.raises(ValueError, match=r"Formato de endereço inválido\. Esperado: 'Nome da rua, número' ou 'Nome da rua, número, bairro, cidade, estado'"):
        mod_info.Informacao("11987654321", "email@test.com", "Endereco Invalido", "redes")
    with pytest.raises(ValueError, match=r"Formato de endereço inválido\. Esperado: 'Nome da rua, número' ou 'Nome da rua, número, bairro, cidade, estado'"):
        mod_info.Informacao("11987654321", "email@test.com", "Rua Teste 123", "redes")
    with pytest.raises(ValueError, match=r"Formato de endereço inválido\. Esperado: 'Nome da rua, número' ou 'Nome da rua, número, bairro, cidade, estado'"):
        mod_info.Informacao("11987654321", "email@test.com", "Rua Teste, 123, Bairro, Cidade", "redes")
    with pytest.raises(ValueError, match=r"Formato de endereço inválido\. Esperado: 'Nome da rua, número' ou 'Nome da rua, número, bairro, cidade, estado'"):
        mod_info.Informacao("11987654321", "email@test.com", "", "redes")

def test_informacao_endereco_valido_flexivel():
    info_flex = mod_info.Informacao("11987654321", "flex@email.com", "Rua Flex, 456", "redes")
    assert info_flex.endereco["nome_rua"] == "Rua Flex"
    assert info_flex.endereco["numero"] == "456"
    assert info_flex.endereco["bairro"] is None
    assert info_flex.endereco["cidade"] is None
    assert info_flex.endereco["estado"] is None

def test_informacao_atualizar_telefone(info_contato_valida):
    info_contato_valida.telefone = "21998765432"
    assert info_contato_valida.telefone == "21 9 9876 5432"
    # "invalido" -> numero_totalmente_limpo="". Erro: "Formato de número de telefone brasileiro inválido."
    with pytest.raises(ValueError, match="Formato de número de telefone brasileiro inválido."):
        info_contato_valida.telefone = "invalido"

def test_informacao_atualizar_email(info_contato_valida):
    info_contato_valida.email = "novo.email@teste.org"
    assert info_contato_valida.email == "novo.email@teste.org"
    with pytest.raises(ValueError, match="Formato de e-mail inválido."):
        info_contato_valida.email = "email_errado"

def test_informacao_atualizar_endereco(info_contato_valida):
    info_contato_valida.endereco = "Av. Principal, 456, Centro, Rio de Janeiro, RJ"
    assert info_contato_valida.endereco["nome_rua"] == "Av. Principal"
    assert info_contato_valida.endereco["estado"] == "RJ"
    with pytest.raises(ValueError, match=r"Formato de endereço inválido\."):
        info_contato_valida.endereco = "Endereco Invalido"

def test_informacao_atualizar_redes_sociais(info_contato_valida):
    info_contato_valida.redes_sociais = "twitter.com/teste"
    assert info_contato_valida.redes_sociais == "twitter.com/teste"
    info_contato_valida.redes_sociais = ""
    assert info_contato_valida.redes_sociais == ""

def test_informacao_validar_e_formatar_telefone_brasileiro_validos():
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("11987654321") == "11 9 8765 4321"
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("(21)98765-4321") == "21 9 8765 4321"
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("+55 11 98765 4321") == "11 9 8765 4321"
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("4130201000") == "41 3020 1000"
    # Correção do valor esperado para a entrada "021 99876 5432"
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("021 99876 5432") == "21 9 9876 5432"
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("1112345678") == "11 1234 5678"
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("99999999999") == "99 9 9999 9999"
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("+1 234 567-8900") == "+1 234 567-8900"
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("+44 7911 123456") == "+44 7911 123456"

def test_informacao_validar_e_formatar_telefone_brasileiro_invalidos():
    with pytest.raises(ValueError):
        mod_info.Informacao.validar_e_formatar_telefone_brasileiro("123")
    with pytest.raises(ValueError):
        mod_info.Informacao.validar_e_formatar_telefone_brasileiro("119876543210")
    with pytest.raises(ValueError):
        mod_info.Informacao.validar_e_formatar_telefone_brasileiro("abcde12345")
    with pytest.raises(ValueError):
        mod_info.Informacao.validar_e_formatar_telefone_brasileiro("1191234567")
    with pytest.raises(ValueError):
        mod_info.Informacao.validar_e_formatar_telefone_brasileiro("11223456789")
    with pytest.raises(ValueError):
        mod_info.Informacao.validar_e_formatar_telefone_brasileiro("111234567")
    with pytest.raises(ValueError):
        mod_info.Informacao.validar_e_formatar_telefone_brasileiro("01198765432")
    with pytest.raises(ValueError):
        mod_info.Informacao.validar_e_formatar_telefone_brasileiro("11")
    with pytest.raises(ValueError):
        mod_info.Informacao.validar_e_formatar_telefone_brasileiro("+55 11 1234567")
    with pytest.raises(ValueError):
        mod_info.Informacao.validar_e_formatar_telefone_brasileiro("+55 11 9123456789")
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("+54") == "+54"
    assert mod_info.Informacao.validar_e_formatar_telefone_brasileiro("+54 ") == "+54"

def test_pessoa_criacao_valida(cpf_valido_aleatorio):
    p = pessoa.Pessoa("Fulano de Tal", "01/01/2000", cpf_valido_aleatorio)
    assert p.nome == "Fulano de Tal"
    assert p.nascimento == date(2000, 1, 1)
    assert p.cpf == cpf_valido_aleatorio
    assert p.idade >= (date.today().year - 2000) - (1 if date.today().month < 1 or (date.today().month == 1 and date.today().day < 1) else 0)

def test_pessoa_nome_invalido(cpf_valido_aleatorio):
    pessoa.Pessoa("Fulano", "01/01/2000", cpf_valido_aleatorio)
    with pytest.raises(ValueError, match="Deve conter apenas letras, hífens e espaços."):
        pessoa.Pessoa("  ", "01/01/2000", cpf_valido_aleatorio)
    with pytest.raises(ValueError, match="Deve conter apenas letras, hífens e espaços."):
        pessoa.Pessoa("123 Silva", "01/01/2000", cpf_valido_aleatorio)
    p = pessoa.Pessoa("Nome Teste", "01/01/2000", cpf_valido_aleatorio)
    p.nome = "Um Nome"
    assert p.nome == "Um Nome"

def test_pessoa_nascimento_invalido(cpf_valido_aleatorio):
    with pytest.raises(ValueError, match="Data de nascimento não pode ser no futuro."):
        pessoa.Pessoa("Fulano de Tal", (date.today() + timedelta(days=1)).strftime("%d/%m/%Y"), cpf_valido_aleatorio)
    with pytest.raises(ValueError, match="Data de nascimento indica uma idade de .* anos, o que excede o máximo permitido."):
        pessoa.Pessoa("Fulano de Tal", "01/01/1800", cpf_valido_aleatorio)
    with pytest.raises(ValueError, match="Formato de data inválido."):
        pessoa.Pessoa("Fulano de Tal", "data invalida", cpf_valido_aleatorio)
    with pytest.raises(ValueError, match="Data inválida: month must be in 1..12."):
        p = pessoa.Pessoa("Fulano de Tal", "01/01/2000", cpf_valido_aleatorio)
        p.nascimento = "01/13/2000"

def test_pessoa_cpf_invalido():
    with pytest.raises(ValueError, match="Formato de CPF inválido."):
        pessoa.Pessoa("Fulano de Tal", "01/01/2000", "123")
    with pytest.raises(ValueError, match="Formato de CPF inválido."):
        pessoa.Pessoa("Fulano de Tal", "01/01/2000", "123.456.789-0")
    with pytest.raises(ValueError, match="CPF inválido: Dígitos verificadores não correspondem ou padrão inválido."):
        pessoa.Pessoa("Fulano de Tal", "01/01/2000", "111.111.111-11")
    with pytest.raises(ValueError, match="CPF inválido: Dígitos verificadores não correspondem ou padrão inválido."):
        pessoa.Pessoa("Fulano de Tal", "01/01/2000", "12345678900")
    with pytest.raises(ValueError, match="Formato de CPF inválido."):
        p = pessoa.Pessoa("Fulano de Tal", "01/01/2000", pessoa.gerar_cpf_valido())
        p.cpf = "invalido"

def test_pessoa_atualizar_nome(cpf_valido_aleatorio):
    p = pessoa.Pessoa("Nome Antigo", "01/01/2000", cpf_valido_aleatorio)
    p.nome = "Novo Nome Completo"
    assert p.nome == "Novo Nome Completo"

def test_pessoa_atualizar_nascimento(cpf_valido_aleatorio):
    p = pessoa.Pessoa("Nome Teste", "01/01/2000", cpf_valido_aleatorio)
    p.nascimento = "15/05/1990"
    assert p.nascimento == date(1990, 5, 15)

def test_pessoa_atualizar_cpf(cpf_valido_aleatorio):
    p = pessoa.Pessoa("Nome Teste", "01/01/2000", cpf_valido_aleatorio)
    novo_cpf = pessoa.gerar_cpf_valido()
    p.cpf = novo_cpf
    assert p.cpf == novo_cpf

def test_pessoa_eh_cpf_valido_validos():
    assert pessoa.Pessoa._eh_cpf_valido("21547733039") is True 
    assert pessoa.Pessoa._eh_cpf_valido("00000000000") is False

def test_pessoa_eh_cpf_valido_invalidos():
    assert pessoa.Pessoa._eh_cpf_valido("123") is False
    assert pessoa.Pessoa._eh_cpf_valido("123456789098") is False
    assert pessoa.Pessoa._eh_cpf_valido("12345678901") is False
    assert pessoa.Pessoa._eh_cpf_valido("11111111111") is False
    assert pessoa.Pessoa._eh_cpf_valido("abcdefghijk") is False
    assert pessoa.Pessoa._eh_cpf_valido("39577898009") is True

def test_pessoa_parse_data_date_validos():
    assert pessoa.Pessoa._parse_data("01/01/2000", is_datetime=False) == date(2000, 1, 1)
    assert pessoa.Pessoa._parse_data("15-03-1995", is_datetime=False) == date(1995, 3, 15)
    assert pessoa.Pessoa._parse_data("28022023", is_datetime=False) == date(2023, 2, 28)
    assert pessoa.Pessoa._parse_data("05 06 99", is_datetime=False) == date(1999, 6, 5)
    assert pessoa.Pessoa._parse_data("05 06 2099", is_datetime=False) == date(2099, 6, 5)

def test_pessoa_parse_data_datetime_validos():
    assert pessoa.Pessoa._parse_data("01/01/2000 10:30", is_datetime=True) == datetime(2000, 1, 1, 10, 30)
    assert pessoa.Pessoa._parse_data("15-03-1995 23:59", is_datetime=True) == datetime(1995, 3, 15, 23, 59)
    assert pessoa.Pessoa._parse_data("28022023 00:00", is_datetime=True) == datetime(2023, 2, 28, 0, 0)

def test_pessoa_parse_data_invalidos():
    with pytest.raises(ValueError, match="Formato de data inválido."):
        pessoa.Pessoa._parse_data("data invalida", is_datetime=False)
    with pytest.raises(ValueError, match="Formato de data/hora inválido."):
        pessoa.Pessoa._parse_data("01/01/2000", is_datetime=True)
    with pytest.raises(ValueError, match="Data inválida: day is out of range for month."):
        pessoa.Pessoa._parse_data("30/02/2023", is_datetime=False)
    with pytest.raises(ValueError, match="Data inválida: hour must be in 0..23."):
        pessoa.Pessoa._parse_data("01/01/2000 25:00", is_datetime=True)
    with pytest.raises(ValueError, match="Data inválida: minute must be in 0..59."):
        pessoa.Pessoa._parse_data("01/01/2000 10:65", is_datetime=True)

@pytest.fixture
def funcionario_valido(info_contato_valida, cpf_valido_aleatorio):
    return funcionario.Funcionario(
        None, "Funcionario Teste Completo", "01/01/1990", cpf_valido_aleatorio, "1234567-89",
        info_contato_valida, 2500.00, "01/01/2020", None, "12345678901"
    )

def test_funcionario_criacao_valida(funcionario_valido, info_contato_valida, cpf_valido_aleatorio):
    id_esperado = funcionario_valido.id
    assert funcionario_valido.id == id_esperado
    assert funcionario_valido.nome == "Funcionario Teste Completo"
    assert funcionario_valido.nascimento == date(1990, 1, 1)
    assert funcionario_valido.cpf == cpf_valido_aleatorio
    assert funcionario_valido.ctps == "1234567-89"
    assert funcionario_valido.informacao_contato == info_contato_valida
    assert funcionario_valido.salario == 2500.00
    assert funcionario_valido.data_admissao == date(2020, 1, 1)
    assert funcionario_valido.data_demissao is None
    assert funcionario_valido.nis == "12345678901"
    assert funcionario.Funcionario.buscar_funcionario_por_id(id_esperado) == funcionario_valido
    assert funcionario.Funcionario.buscar_funcionario_por_cpf(cpf_valido_aleatorio) == funcionario_valido

def test_funcionario_criacao_id_especifico(info_contato_valida, cpf_valido_aleatorio):
    f = funcionario.Funcionario(
        100, "Funcionario ID Especifico", "01/01/1990", cpf_valido_aleatorio, "1111111-11",
        info_contato_valida, 2000.00, "01/01/2021", None, None
    )
    assert f.id == 100
    assert funcionario.Funcionario.buscar_funcionario_por_id(100) == f

def test_funcionario_colisao_cpf(funcionario_valido, info_contato_valida):
    with pytest.raises(ValueError, match=f"Funcionário com CPF {funcionario_valido.cpf} já existe."):
        funcionario.Funcionario(
            None, "Nome Duplicado CPF", "01/01/1990", funcionario_valido.cpf, "2222222-22",
            info_contato_valida, 1000.00, "01/01/2022", None, None
        )

def test_funcionario_colisao_id(funcionario_valido, info_contato_valida):
    with pytest.raises(ValueError, match=f"Já existe funcionário com o ID {funcionario_valido.id}."):
        funcionario.Funcionario(
            funcionario_valido.id, "Duplicado ID", "01/01/1990", pessoa.gerar_cpf_valido(), "3333333-33",
            info_contato_valida, 1000.00, "01/01/2022", None, None
        )

def test_funcionario_id_invalido(info_contato_valida, cpf_valido_aleatorio):
    with pytest.raises(ValueError, match="ID do funcionário deve ser um número inteiro positivo."):
        funcionario.Funcionario(
            0, "Zero ID", "01/01/1990", cpf_valido_aleatorio, "1234567-89",
            info_contato_valida, 2500.00, "01/01/2020", None, "12345678901"
        )
    with pytest.raises(ValueError, match="ID do funcionário deve ser um número inteiro positivo."):
        funcionario.Funcionario(
            "abc", "String ID", "01/01/1990", cpf_valido_aleatorio, "1234567-89",
            info_contato_valida, 2500.00, "01/01/2020", None, "12345678901"
        )

def test_funcionario_ctps_invalida(info_contato_valida, cpf_valido_aleatorio):
    with pytest.raises(ValueError, match="CTPS não pode ser vazia."):
        funcionario.Funcionario(
            None, "Nome Teste Completo", "01/01/1990", cpf_valido_aleatorio, "",
            info_contato_valida, 2500.00, "01/01/2020", None, None
        )
    f = funcionario.Funcionario(None, "Nome Teste Completo", "01/01/1990", pessoa.gerar_cpf_valido(), "1234567-89", info_contato_valida, 2500.00, "01/01/2020", None, None)
    with pytest.raises(ValueError, match="CTPS não pode ser vazia."):
        f.ctps = " "

def test_funcionario_info_contato_tipo_invalido(cpf_valido_aleatorio):
    with pytest.raises(TypeError, match="Informação de contato deve ser uma instância da classe Informacao."):
        funcionario.Funcionario(
            None, "Nome Teste Completo", "01/01/1990", cpf_valido_aleatorio, "1234567-89",
            "nao_info", 2500.00, "01/01/2020", None, None
        )
    f = funcionario.Funcionario(None, "Nome Teste Completo", "01/01/1990", pessoa.gerar_cpf_valido(), "1234567-89", mod_info.Informacao("11987654321", "email@test.com", "Rua A, 1", ""), 2500.00, "01/01/2020", None, None)
    with pytest.raises(TypeError, match="Informação de contato deve ser uma instância da classe Informacao."):
        f.informacao_contato = "string"

def test_funcionario_salario_invalido(info_contato_valida, cpf_valido_aleatorio):
    with pytest.raises(ValueError, match="Salário deve ser um número não negativo."):
        funcionario.Funcionario(
            None, "Nome Teste Completo", "01/01/1990", cpf_valido_aleatorio, "1234567-89",
            info_contato_valida, -100.00, "01/01/2020", None, None
        )
    f = funcionario.Funcionario(None, "Nome Teste Completo", "01/01/1990", pessoa.gerar_cpf_valido(), "1234567-89", info_contato_valida, 2500.00, "01/01/2020", None, None)
    with pytest.raises(ValueError, match="Salário deve ser um número não negativo."):
        f.salario = -50.00
    with pytest.raises(TypeError, match="Salário deve ser um número válido."):
        f.salario = "abc"

def test_funcionario_data_admissao_invalida(info_contato_valida, cpf_valido_aleatorio):
    with pytest.raises(ValueError, match="Data de admissão não pode ser no futuro."):
        funcionario.Funcionario(
            None, "Nome Teste Completo", "01/01/1990", cpf_valido_aleatorio, "1234567-89",
            info_contato_valida, 2500.00, (date.today() + timedelta(days=1)).strftime("%d/%m/%Y"), None, None
        )
    f = funcionario.Funcionario(None, "Nome Teste Completo", "01/01/1990", pessoa.gerar_cpf_valido(), "1234567-89", info_contato_valida, 2500.00, "01/01/2020", None, None)
    with pytest.raises(ValueError, match="Data de admissão inválida: Formato de data inválido."):
        f.data_admissao = "data_errada"

def test_funcionario_data_demissao_invalida(info_contato_valida, cpf_valido_aleatorio):
    with pytest.raises(ValueError, match="Data de demissão não pode ser anterior à data de admissão."):
        funcionario.Funcionario(
            None, "Nome Teste Completo", "01/01/1990", cpf_valido_aleatorio, "1234567-89",
            info_contato_valida, 2500.00, "01/01/2020", "01/01/2019", None
        )
    f = funcionario.Funcionario(None, "Nome Teste Completo", "01/01/1990", pessoa.gerar_cpf_valido(), "1234567-89", info_contato_valida, 2500.00, "01/01/2020", None, None)
    with pytest.raises(ValueError, match="Data de demissão inválida: Formato de data inválido."):
        f.data_demissao = "data_errada"

def test_funcionario_nis_invalido(info_contato_valida, cpf_valido_aleatorio):
    with pytest.raises(ValueError, match="NIS inválido: Deve conter exatamente 11 dígitos numéricos."):
        funcionario.Funcionario(
            None, "Nome Teste Completo", "01/01/1990", cpf_valido_aleatorio, "1234567-89",
            info_contato_valida, 2500.00, "01/01/2020", None, "123"
        )
    f = funcionario.Funcionario(None, "Nome Teste Completo", "01/01/1990", pessoa.gerar_cpf_valido(), "1234567-89", info_contato_valida, 2500.00, "01/01/2020", None, None)
    with pytest.raises(ValueError, match="NIS inválido: Deve conter exatamente 11 dígitos numéricos."):
        f.nis = "abc"

def test_funcionario_buscar_por_cpf(funcionario_valido):
    found_f = funcionario.Funcionario.buscar_funcionario_por_cpf(funcionario_valido.cpf)
    assert found_f == funcionario_valido
    assert funcionario.Funcionario.buscar_funcionario_por_cpf("999.999.999-99") is None
    assert funcionario.Funcionario.buscar_funcionario_por_cpf("cpf_invalido_format") is None

def test_funcionario_buscar_por_id(funcionario_valido):
    found_f = funcionario.Funcionario.buscar_funcionario_por_id(funcionario_valido.id)
    assert found_f == funcionario_valido
    assert funcionario.Funcionario.buscar_funcionario_por_id(9999) is None

def test_funcionario_buscar_por_nome_exato(funcionario_valido):
    found_f = funcionario.Funcionario.buscar_funcionario_por_nome_exato("Funcionario Teste Completo")
    assert found_f == funcionario_valido
    assert funcionario.Funcionario.buscar_funcionario_por_nome_exato("funcionario teste completo") == funcionario_valido
    assert funcionario.Funcionario.buscar_funcionario_por_nome_exato("Nome Inexistente") is None

def test_funcionario_listar_funcionarios(funcionario_valido, info_contato_valida, cpf_valido_aleatorio):
    f2 = funcionario.Funcionario(
        None, "Outro Funcionario", "01/01/1990", pessoa.gerar_cpf_valido(), "9876543-21",
        info_contato_valida, 2000.00, "01/01/2021", None, None
    )
    all_funcs = funcionario.Funcionario.listar_funcionarios()
    assert len(all_funcs) == 2
    assert funcionario_valido in all_funcs
    assert f2 in all_funcs

def test_funcionario_atualizar_cpf(funcionario_valido):
    cpf_antigo = funcionario_valido.cpf
    id_func = funcionario_valido.id
    novo_cpf = pessoa.gerar_cpf_valido()
    funcionario.Funcionario.atualizar_cpf(cpf_antigo, novo_cpf)
    assert funcionario_valido.cpf == novo_cpf
    assert funcionario.Funcionario.buscar_funcionario_por_cpf(novo_cpf) == funcionario_valido
    assert funcionario.Funcionario.buscar_funcionario_por_cpf(cpf_antigo) is None

def test_funcionario_atualizar_cpf_nao_encontrado():
    cpf_nao_encontrado = "999"
    with pytest.raises(ValueError, match=f"Funcionário com CPF {cpf_nao_encontrado} não encontrado para atualização."):
        funcionario.Funcionario.atualizar_cpf(cpf_nao_encontrado, pessoa.gerar_cpf_valido())

def test_funcionario_atualizar_cpf_invalido(funcionario_valido):
    with pytest.raises(ValueError, match="Novo CPF inválido: Dígitos verificadores não correspondem ou padrão inválido."):
        funcionario.Funcionario.atualizar_cpf(funcionario_valido.cpf, "111.111.111-11")

def test_funcionario_atualizar_cpf_colisao(funcionario_valido, info_contato_valida):
    f_dup = funcionario.Funcionario(None, "Duplicado CPF", "01/01/1990", pessoa.gerar_cpf_valido(), "4444444-44", info_contato_valida, 1000.00, "01/01/2022", None, None)
    with pytest.raises(ValueError, match=f"Já existe outro funcionário com o CPF {f_dup.cpf}."):
        funcionario.Funcionario.atualizar_cpf(funcionario_valido.cpf, f_dup.cpf)

def test_funcionario_atualizar_nome_por_id(funcionario_valido):
    funcionario.Funcionario.atualizar_nome_por_id(funcionario_valido.id, "Nome Atualizado")
    assert funcionario_valido.nome == "Nome Atualizado"
    with pytest.raises(ValueError, match="Deve conter apenas letras, hífens e espaços."):
        funcionario.Funcionario.atualizar_nome_por_id(funcionario_valido.id, "Nome123")

def test_funcionario_atualizar_nome_por_id_nao_encontrado():
    with pytest.raises(ValueError, match="Funcionário com ID 999 não encontrado."):
        funcionario.Funcionario.atualizar_nome_por_id(999, "Nome Inexistente")

def test_funcionario_atualizar_data_nascimento_por_id(funcionario_valido):
    funcionario.Funcionario.atualizar_data_nascimento_por_id(funcionario_valido.id, "15/07/1985")
    assert funcionario_valido.nascimento == date(1985, 7, 15)
    with pytest.raises(ValueError, match="Data de nascimento não pode ser no futuro."):
        funcionario.Funcionario.atualizar_data_nascimento_por_id(funcionario_valido.id, (date.today() + timedelta(days=1)).strftime("%d/%m/%Y"))

def test_funcionario_atualizar_data_nascimento_por_id_nao_encontrado():
    with pytest.raises(ValueError, match="Funcionário com ID 999 não encontrado."):
        funcionario.Funcionario.atualizar_data_nascimento_por_id(999, "01/01/1990")

def test_funcionario_atualizar_ctps_por_id(funcionario_valido):
    funcionario.Funcionario.atualizar_ctps_por_id(funcionario_valido.id, "9988776-65")
    assert funcionario_valido.ctps == "9988776-65"
    with pytest.raises(ValueError, match="CTPS não pode ser vazia."):
        funcionario.Funcionario.atualizar_ctps_por_id(funcionario_valido.id, " ")

def test_funcionario_atualizar_ctps_por_id_nao_encontrado():
    with pytest.raises(ValueError, match="Funcionário com ID 999 não encontrado."):
        funcionario.Funcionario.atualizar_ctps_por_id(999, "1234567-89")

def test_funcionario_atualizar_informacao_contato(funcionario_valido):
    nova_info = mod_info.Informacao("31912345678", "novo@email.com", "Rua Z, 789, Centro, BH, MG", "")
    funcionario.Funcionario.atualizar_informacao_contato(funcionario_valido.cpf, nova_info)
    assert funcionario_valido.informacao_contato.email == "novo@email.com"
    with pytest.raises(TypeError, match="Informação de contato deve ser uma instância da classe Informacao."):
        funcionario.Funcionario.atualizar_informacao_contato(funcionario_valido.cpf, "string")

def test_funcionario_atualizar_informacao_contato_nao_encontrado():
    with pytest.raises(ValueError, match="Funcionário com CPF 999 não encontrado."):
        funcionario.Funcionario.atualizar_informacao_contato("999", mod_info.Informacao("11987654321", "email@test.com", "Rua A, 1", ""))

def test_funcionario_atualizar_salario_por_id(funcionario_valido):
    funcionario.Funcionario.atualizar_salario_por_id(funcionario_valido.id, 3000.00)
    assert funcionario_valido.salario == 3000.00
    with pytest.raises(ValueError, match="Salário deve ser um número não negativo."):
        funcionario.Funcionario.atualizar_salario_por_id(funcionario_valido.id, -100.00)

def test_funcionario_atualizar_salario_por_id_nao_encontrado():
    with pytest.raises(ValueError, match="Funcionário com ID 999 não encontrado."):
        funcionario.Funcionario.atualizar_salario_por_id(999, 1000.00)

def test_funcionario_atualizar_data_admissao_por_id(funcionario_valido):
    funcionario.Funcionario.atualizar_data_admissao_por_id(funcionario_valido.id, "01/01/2018")
    assert funcionario_valido.data_admissao == date(2018, 1, 1)
    with pytest.raises(ValueError, match="Data de admissão não pode ser no futuro."):
        funcionario.Funcionario.atualizar_data_admissao_por_id(funcionario_valido.id, (date.today() + timedelta(days=1)).strftime("%d/%m/%Y"))

def test_funcionario_atualizar_data_admissao_por_id_nao_encontrado():
    with pytest.raises(ValueError, match="Funcionário com ID 999 não encontrado."):
        funcionario.Funcionario.atualizar_data_admissao_por_id(999, "01/01/2020")

def test_funcionario_atualizar_data_demissao_por_id(funcionario_valido):
    funcionario.Funcionario.atualizar_data_demissao_por_id(funcionario_valido.id, "01/01/2023")
    assert funcionario_valido.data_demissao == date(2023, 1, 1)
    funcionario.Funcionario.atualizar_data_demissao_por_id(funcionario_valido.id, None)
    assert funcionario_valido.data_demissao is None
    with pytest.raises(ValueError, match="Data de demissão não pode ser anterior à data de admissão."):
        funcionario.Funcionario.atualizar_data_demissao_por_id(funcionario_valido.id, "01/01/2000")

def test_funcionario_atualizar_data_demissao_por_id_nao_encontrado():
    with pytest.raises(ValueError, match="Funcionário com ID 999 não encontrado."):
        funcionario.Funcionario.atualizar_data_demissao_por_id(999, "01/01/2023")

def test_funcionario_atualizar_nis_por_id(funcionario_valido):
    funcionario.Funcionario.atualizar_nis_por_id(funcionario_valido.id, "99887766554")
    assert funcionario_valido.nis == "99887766554"
    funcionario.Funcionario.atualizar_nis_por_id(funcionario_valido.id, None)
    assert funcionario_valido.nis is None
    with pytest.raises(ValueError, match="NIS inválido: Deve conter exatamente 11 dígitos numéricos."):
        funcionario.Funcionario.atualizar_nis_por_id(funcionario_valido.id, "123")

def test_funcionario_atualizar_nis_por_id_nao_encontrado():
    with pytest.raises(ValueError, match="Funcionário com ID 999 não encontrado."):
        funcionario.Funcionario.atualizar_nis_por_id(999, "12345678901")

def test_funcionario_deletar_funcionario_por_cpf(funcionario_valido):
    funcionario.Funcionario.deletar_funcionario_por_cpf(funcionario_valido.cpf)
    assert funcionario.Funcionario.buscar_funcionario_por_cpf(funcionario_valido.cpf) is None
    assert funcionario.Funcionario.buscar_funcionario_por_id(funcionario_valido.id) is None

def test_funcionario_deletar_funcionario_por_cpf_nao_encontrado():
    with pytest.raises(ValueError, match="Funcionário com CPF 999.999.999-99 não encontrado para exclusão."):
        funcionario.Funcionario.deletar_funcionario_por_cpf("999.999.999-99")

def test_funcionario_deletar_funcionario_por_id(info_contato_valida):
    f_new = funcionario.Funcionario(
        None, "Para Deletar Teste", "01/01/1995", pessoa.gerar_cpf_valido(), "5555555-55",
        info_contato_valida, 1800.00, "01/01/2022", None, None
    )
    funcionario.Funcionario.deletar_funcionario_por_id(f_new.id)
    assert funcionario.Funcionario.buscar_funcionario_por_id(f_new.id) is None
    assert funcionario.Funcionario.buscar_funcionario_por_cpf(f_new.cpf) is None

def test_funcionario_deletar_funcionario_por_id_nao_encontrado():
    with pytest.raises(ValueError, match="Funcionário com ID 999 não encontrado para exclusão."):
        funcionario.Funcionario.deletar_funcionario_por_id(999)

def test_funcionario_inicializar_proximo_id_vazio():
    funcionario.Funcionario._funcionarios_por_id.clear()
    funcionario.Funcionario._proximo_id_disponivel = 0
    funcionario.Funcionario._inicializar_proximo_id()
    assert funcionario.Funcionario._proximo_id_disponivel == 1

def test_funcionario_inicializar_proximo_id_populado(info_contato_valida):
    f1 = funcionario.Funcionario(10, "Func A", "01/01/1990", pessoa.gerar_cpf_valido(), "1111111-11", info_contato_valida, 1000.0, "01/01/2020", None, None)
    f2 = funcionario.Funcionario(5, "Func B", "01/01/1990", pessoa.gerar_cpf_valido(), "2222222-22", info_contato_valida, 1000.0, "01/01/2020", None, None)
    funcionario.Funcionario._proximo_id_disponivel = 0
    funcionario.Funcionario._inicializar_proximo_id()
    assert funcionario.Funcionario._proximo_id_disponivel == 11

def test_fornecedor_eh_cnpj_valido_validos():
    assert fornecedor.Fornecedor._eh_cnpj_valido("25750788000184") is True
    assert fornecedor.Fornecedor._eh_cnpj_valido(pessoa.gerar_cnpj_valido().replace('.', '').replace('/', '').replace('-', '')) is True

def test_fornecedor_eh_cnpj_valido_invalidos():
    assert fornecedor.Fornecedor._eh_cnpj_valido("123") is False
    assert fornecedor.Fornecedor._eh_cnpj_valido("11111111111111") is False
    assert fornecedor.Fornecedor._eh_cnpj_valido("00000000000000") is False
    assert fornecedor.Fornecedor._eh_cnpj_valido("12345678901234") is False
    assert fornecedor.Fornecedor._eh_cnpj_valido("abcdefghijklmn") is False

def test_fornecedor_atualizar_dados_fornecedor(info_contato_valida, cnpj_valido_aleatorio):
    f = fornecedor.Fornecedor(None, "Forn Antigo", cnpj_valido_aleatorio, info_contato_valida)

    novo_info_contato = mod_info.Informacao(
        telefone="11999998888", 
        email="novo.email@forn.com",
        endereco="Rua Nova do Fornecedor, 789, Outro Bairro, Outra Cidade, SC",
        redes_sociais=""
    )

    fornecedor.Fornecedor.atualizar_dados_fornecedor(f.id, nome="Fornecedor Novo", info_contato=novo_info_contato)
    
    f_atualizado = fornecedor.Fornecedor.buscar_fornecedor_id(f.id)
    assert f_atualizado.nome == "Fornecedor Novo"
    assert f_atualizado.info_contato.telefone == "11 9 9999 8888"
    assert f_atualizado.info_contato.email == "novo.email@forn.com"
    assert f_atualizado.info_contato.endereco["nome_rua"] == "Rua Nova do Fornecedor"

def test_fornecedor_atualizar_cnpj_fornecedor_invalido(info_contato_valida, cnpj_valido_aleatorio):
    f = fornecedor.Fornecedor(None, "Forn CNPJ Inv", cnpj_valido_aleatorio, info_contato_valida)
    with pytest.raises(ValueError, match=r"Erro ao atualizar CNPJ: CNPJ inválido: Deve conter exatamente 14 dígitos."):
        fornecedor.Fornecedor.atualizar_cnpj_fornecedor(f.id, "123")