from typing import Optional
from datetime import date
import re
import pessoa
import info as mod_info
from tabulate import tabulate

class Funcionario(pessoa.Pessoa):
    # Representa um funcionário da empresa.
    _funcionarios_por_cpf: dict[str, 'Funcionario'] = {}
    _funcionarios_por_id: dict[int, 'Funcionario'] = {}
    _proximo_id_disponivel: int = 1

    def __init__(self, id_funcionario: Optional[int], nome: str, nascimento: str, cpf: str, ctps: str,
                 informacao_contato: mod_info.Informacao, salario: float, data_admissao: str,
                 data_demissao: Optional[str] = None, nis: Optional[str] = None) -> None:
        if id_funcionario is None:
            self._id = Funcionario._proximo_id_disponivel
        else:
            if not isinstance(id_funcionario, int) or id_funcionario <= 0:
                raise ValueError("ID do funcionário deve ser um número inteiro positivo.")
            self._id = id_funcionario

        super().__init__(nome, nascimento, cpf)
        self.ctps = ctps
        self.informacao_contato = informacao_contato
        self.salario = salario
        self.data_admissao = data_admissao
        self.data_demissao = data_demissao
        self.nis = nis

        if Funcionario.buscar_funcionario_por_id(self.id) is not None:
            raise ValueError(f"Já existe funcionário com o ID {self.id}.")

        if self.cpf in Funcionario._funcionarios_por_cpf:
            raise ValueError(f"Funcionário com CPF {self.cpf} já existe.")

        Funcionario._funcionarios_por_cpf[self.cpf] = self
        Funcionario._funcionarios_por_id[self.id] = self

        if id_funcionario is None:
            Funcionario._proximo_id_disponivel += 1
        elif self.id >= Funcionario._proximo_id_disponivel:
            Funcionario._proximo_id_disponivel = self.id + 1

    def __str__(self) -> str:
        base_str = super().__str__()
        demissao_str = f", Demissão: {self._data_demissao.strftime('%d/%m/%Y')}" if self._data_demissao else ""
        nis_str = f", NIS: {self._nis}" if self._nis else ""
        return (f"ID: {self._id}, {base_str}\n"
                f"  CTPS: {self._ctps}, Salário: R${self._salario:.2f}, "
                f"Admissão: {self._data_admissao.strftime('%d/%m/%Y')}{demissao_str}{nis_str}\n"
                f"  Informações de Contato: {self.informacao_contato}")

    def __repr__(self) -> str:
        base_repr = super().__repr__()
        base_repr_conteudo = base_repr[len('Pessoa('):-1]

        data_demissao_repr = repr(self._data_demissao) if self._data_demissao is not None else 'None'
        nis_repr = repr(self._nis) if self._nis is not None else 'None'

        return (f"Funcionario(id_funcionario={self._id!r}, {base_repr_conteudo}, "
                f"ctps={self._ctps!r}, informacao_contato={self._informacao_contato!r}, salario={self._salario!r}, "
                f"data_admissao={self._data_admissao!r}, data_demissao={data_demissao_repr}, "
                f"nis={nis_repr})")

    @property
    def id(self) -> int:
        return self._id

    @property
    def ctps(self) -> str:
        return self._ctps

    @ctps.setter
    def ctps(self, ctps_str: str) -> None:
        ctps_limpa = ctps_str.strip()
        if not ctps_limpa:
            raise ValueError("CTPS não pode ser vazia.")
        self._ctps = ctps_limpa

    @property
    def informacao_contato(self) -> mod_info.Informacao:
        return self._informacao_contato

    @informacao_contato.setter
    def informacao_contato(self, nova_informacao: mod_info.Informacao) -> None:
        if not isinstance(nova_informacao, mod_info.Informacao):
            raise TypeError("Informação de contato deve ser uma instância da classe Informacao.")
        self._informacao_contato = nova_informacao

    @property
    def salario(self) -> float:
        return self._salario

    @salario.setter
    def salario(self, valor: float) -> None:
        if not isinstance(valor, (int, float)):
            raise TypeError("Salário deve ser um número válido.")
        if valor < 0:
            raise ValueError("Salário deve ser um número não negativo.")
        self._salario = float(valor)

    @property
    def data_admissao(self) -> date:
        return self._data_admissao

    @data_admissao.setter
    def data_admissao(self, data_str: str) -> None:
        try:
            data_parseada = pessoa.Pessoa._parse_data(data_str, is_datetime=False)
        except ValueError as e:
            raise ValueError(f"Data de admissão inválida: {e}")
        if data_parseada > date.today():
            raise ValueError("Data de admissão não pode ser no futuro.")
        self._data_admissao = data_parseada

    @property
    def data_demissao(self) -> Optional[date]:
        return self._data_demissao

    @data_demissao.setter
    def data_demissao(self, data_str: Optional[str]) -> None:
        if data_str is None:
            self._data_demissao = None
            return
        try:
            data_parseada = pessoa.Pessoa._parse_data(data_str, is_datetime=False)
        except ValueError as e:
            raise ValueError(f"Data de demissão inválida: {e}")

        if data_parseada < self.data_admissao:
            raise ValueError("Data de demissão não pode ser anterior à data de admissão.")
        self._data_demissao = data_parseada

    @property
    def nis(self) -> Optional[str]:
        return self._nis

    @nis.setter
    def nis(self, nis_str: Optional[str]) -> None:
        if nis_str is None or not nis_str.strip():
            self._nis = None
            return

        nis_limpo = re.sub(r'\D', '', nis_str)
        if not nis_limpo.isdigit() or len(nis_limpo) != 11:
            raise ValueError("NIS inválido: Deve conter exatamente 11 dígitos numéricos.")

        self._nis = nis_limpo

    @staticmethod
    def _inicializar_proximo_id() -> None:
        if Funcionario._funcionarios_por_id:
            Funcionario._proximo_id_disponivel = max(Funcionario._funcionarios_por_id.keys()) + 1
        else:
            Funcionario._proximo_id_disponivel = 1

    @staticmethod
    def buscar_funcionario_por_cpf(cpf: str) -> Optional['Funcionario']:
        cpf = str(cpf).strip()
        cpf_limpo = re.sub(r'\D', '', cpf)
        if len(cpf_limpo) != 11:
            return None
        cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return Funcionario._funcionarios_por_cpf.get(cpf_formatado, None)

    @staticmethod
    def buscar_funcionario_por_id(id_func: int) -> Optional['Funcionario']:
        return Funcionario._funcionarios_por_id.get(id_func, None)

    @staticmethod
    def buscar_funcionario_por_nome_exato(nome: str) -> Optional['Funcionario']:
        nome_busca_lower = nome.lower().strip()
        for func in Funcionario._funcionarios_por_cpf.values():
            if func.nome.lower() == nome_busca_lower:
                return func
        return None

    @staticmethod
    def listar_funcionarios() -> list['Funcionario']:
        return list(Funcionario._funcionarios_por_id.values())

    @staticmethod
    def atualizar_cpf(cpf_antigo: str, novo_cpf: str) -> None:
        func = Funcionario.buscar_funcionario_por_cpf(cpf_antigo)
        if not func:
            raise ValueError(f"Funcionário com CPF {cpf_antigo} não encontrado para atualização.")

        cpf_antigo_formatado = func.cpf

        novo_cpf_limpo = re.sub(r'\D', '', novo_cpf)
        if not pessoa.Pessoa._eh_cpf_valido(novo_cpf_limpo):
            raise ValueError("Novo CPF inválido: Dígitos verificadores não correspondem ou padrão inválido.")
        novo_cpf_formatado = f"{novo_cpf_limpo[:3]}.{novo_cpf_limpo[3:6]}.{novo_cpf_limpo[6:9]}-{novo_cpf_limpo[9:]}"

        if novo_cpf_formatado in Funcionario._funcionarios_por_cpf and Funcionario._funcionarios_por_cpf[novo_cpf_formatado] is not func:
            raise ValueError(f"Já existe outro funcionário com o CPF {novo_cpf_formatado}.")

        del Funcionario._funcionarios_por_cpf[cpf_antigo_formatado]

        try:
            func.cpf = novo_cpf_formatado
            Funcionario._funcionarios_por_cpf[func.cpf] = func
        except ValueError as e:
            Funcionario._funcionarios_por_cpf[cpf_antigo_formatado] = func
            raise ValueError(f"Erro ao atualizar CPF: {e}")

    @staticmethod
    def atualizar_nome_por_id(id_func: int, novo_nome: str) -> None:
        func = Funcionario.buscar_funcionario_por_id(id_func)
        if not func:
            raise ValueError(f"Funcionário com ID {id_func} não encontrado.")
        func.nome = novo_nome

    @staticmethod
    def atualizar_data_nascimento_por_id(id_func: int, nova_data_nascimento: str) -> None:
        func = Funcionario.buscar_funcionario_por_id(id_func)
        if not func:
            raise ValueError(f"Funcionário com ID {id_func} não encontrado.")
        func.nascimento = nova_data_nascimento

    @staticmethod
    def atualizar_ctps_por_id(id_func: int, nova_ctps: str) -> None:
        func = Funcionario.buscar_funcionario_por_id(id_func)
        if not func:
            raise ValueError(f"Funcionário com ID {id_func} não encontrado.")
        func.ctps = nova_ctps

    @staticmethod
    def atualizar_informacao_contato(cpf: str, nova_informacao: mod_info.Informacao) -> None:
        func = Funcionario.buscar_funcionario_por_cpf(cpf)
        if not func:
            raise ValueError(f"Funcionário com CPF {cpf} não encontrado.")
        func.informacao_contato = nova_informacao

    @staticmethod
    def atualizar_salario_por_cpf(cpf: str, novo_salario: float) -> None:
        func = Funcionario.buscar_funcionario_por_cpf(cpf)
        if not func:
            raise ValueError(f"Funcionário com CPF {cpf} não encontrado.")
        func.salario = novo_salario

    @classmethod
    def atualizar_salario_por_id(cls, id_funcionario, novo_salario):
        funcionario = cls.buscar_funcionario_por_id(id_funcionario)
        if funcionario is None:
            raise ValueError(f"Funcionário com ID {id_funcionario} não encontrado.")
        if not isinstance(novo_salario, (int, float)):
            raise TypeError("Salário deve ser um número válido.")
        if novo_salario < 0:
            raise ValueError("Salário deve ser um número não negativo.")
        funcionario.salario = novo_salario

    @staticmethod
    def atualizar_data_admissao_por_cpf(cpf: str, nova_data_admissao: str) -> None:
        func = Funcionario.buscar_funcionario_por_cpf(cpf)
        if not func:
            raise ValueError(f"Funcionário com CPF {cpf} não encontrado.")
        func.data_admissao = nova_data_admissao

    @classmethod
    def atualizar_data_admissao_por_id(cls, id_funcionario, nova_data_admissao):
        funcionario = cls.buscar_funcionario_por_id(id_funcionario)
        if funcionario is None:
            raise ValueError(f"Funcionário com ID {id_funcionario} não encontrado.")
        funcionario.data_admissao = nova_data_admissao

    @staticmethod
    def atualizar_data_demissao_por_cpf(cpf: str, nova_data_demissao: Optional[str]) -> None:
        func = Funcionario.buscar_funcionario_por_cpf(cpf)
        if not func:
            raise ValueError(f"Funcionário com CPF {cpf} não encontrado.")
        func.data_demissao = nova_data_demissao

    @classmethod
    def atualizar_data_demissao_por_id(cls, id_funcionario, nova_data_demissao):
        funcionario = cls.buscar_funcionario_por_id(id_funcionario)
        if funcionario is None:
            raise ValueError(f"Funcionário com ID {id_funcionario} não encontrado.")
        try:
            funcionario.data_demissao = nova_data_demissao
        except Exception as e:
            raise ValueError(f"Erro ao atualizar data de demissão: {e}")

    @staticmethod
    def atualizar_nis_por_id(id_func: int, novo_nis: Optional[str]) -> None:
        func = Funcionario.buscar_funcionario_por_id(id_func)
        if not func:
            raise ValueError(f"Funcionário com ID {id_func} não encontrado.")
        func.nis = novo_nis

    @staticmethod
    def deletar_funcionario_por_cpf(cpf: str) -> None:
        func_a_deletar = Funcionario.buscar_funcionario_por_cpf(cpf)
        if not func_a_deletar:
            raise ValueError(f"Funcionário com CPF {cpf} não encontrado para exclusão.")

        del Funcionario._funcionarios_por_cpf[func_a_deletar.cpf]
        del Funcionario._funcionarios_por_id[func_a_deletar.id]

    @staticmethod
    def deletar_funcionario_por_id(id_func: int) -> None:
        func_a_deletar = Funcionario.buscar_funcionario_por_id(id_func)
        if not func_a_deletar:
            raise ValueError(f"Funcionário com ID {id_func} não encontrado para exclusão.")

        del Funcionario._funcionarios_por_id[id_func]
        if func_a_deletar.cpf in Funcionario._funcionarios_por_cpf:
            del Funcionario._funcionarios_por_cpf[func_a_deletar.cpf]

    @staticmethod
    def _formatar_funcionarios_para_tabela(funcionarios: list['Funcionario']) -> str:
        if not funcionarios:
            return "Nenhum funcionário para exibir."

        cabecalhos = ["ID", "Nome", "CPF", "Nascimento", "Idade", "CTPS", "NIS", "Salário", "Admissão", "Demissão", "Telefone", "Email"]
        dados_tabela = []

        for func in funcionarios:
            nascimento_str = func.nascimento.strftime('%d/%m/%Y')
            admissao_str = func.data_admissao.strftime('%d/%m/%Y')
            demissao_str = func.data_demissao.strftime('%d/%m/%Y') if func.data_demissao else "Ativo"
            telefone_str = func.informacao_contato.telefone
            email_str = func.informacao_contato.email
            nis_str = func.nis if func.nis else "N/A"

            dados_tabela.append([
                func.id,
                func.nome,
                func.cpf,
                nascimento_str,
                func.idade,
                func.ctps,
                nis_str,
                f"R${func.salario:.2f}",
                admissao_str,
                demissao_str,
                telefone_str,
                email_str
            ])

        return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
