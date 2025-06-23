from typing import Optional, Any
import re
import pessoa 
import info as mod_info
from tabulate import tabulate

class Cliente(pessoa.Pessoa):
    # Representa um cliente da empresa.
    _clientes_por_cpf: dict[str, 'Cliente'] = {}
    _clientes_por_id: dict[int, 'Cliente'] = {}
    _proximo_id_disponivel: int = 1

    def __init__(self, id_cliente: Optional[int], nome: str, nascimento: str, cpf: str, info_contato: mod_info.Informacao) -> None:
        if id_cliente is None:
            self._id = Cliente._proximo_id_disponivel
        else:
            if not isinstance(id_cliente, int) or id_cliente <= 0:
                raise ValueError("O ID do cliente deve ser um número inteiro positivo.")
            self._id = id_cliente

        super().__init__(nome, nascimento, cpf)
        self.info_contato = info_contato
        
        if Cliente.buscar_cliente_id(self.id) is not None:
            raise ValueError(f"Já existe um cliente com o ID {self.id}.")

        if self.cpf in Cliente._clientes_por_cpf:
            raise ValueError(f"Cliente com CPF {self.cpf} já existe.")

        Cliente._clientes_por_cpf[self.cpf] = self
        Cliente._clientes_por_id[self.id] = self

        if id_cliente is None:
            Cliente._proximo_id_disponivel += 1
        elif self.id >= Cliente._proximo_id_disponivel:
            Cliente._proximo_id_disponivel = self.id + 1

    def __str__(self) -> str:
        base_str: str = super().__str__()
        return (f"ID: {self._id}, {base_str}\n"
                f"  Informações de Contato: {self.info_contato}")

    def __repr__(self) -> str:
        base_repr: str = super().__repr__()
        base_repr_conteudo: str = base_repr[len('Pessoa('):-1]
        return (f"Cliente(id_cliente={self._id!r}, {base_repr_conteudo}, "
                f"info_contato={self.info_contato!r})")

    @property
    def id(self) -> int:
        return self._id

    @property
    def info_contato(self) -> mod_info.Informacao:
        return self._info_contato

    @info_contato.setter
    def info_contato(self, nova_info: mod_info.Informacao) -> None:
        if not isinstance(nova_info, mod_info.Informacao):
            raise TypeError("A informação de contato deve ser uma instância da classe Informacao.")
        self._info_contato = nova_info

    @staticmethod
    def _formatar_cpf_para_busca(cpf_entrada: str) -> Optional[str]:
        cpf_limpo: str = re.sub(r'\D', '', cpf_entrada)
        if len(cpf_limpo) == 11:
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return None

    @staticmethod
    def _inicializar_proximo_id() -> None:
        if Cliente._clientes_por_id:
            Cliente._proximo_id_disponivel = max(Cliente._clientes_por_id.keys()) + 1
        else:
            Cliente._proximo_id_disponivel = 1

    @staticmethod
    def buscar_cliente(cpf: str) -> Optional['Cliente']:
        cpf_formatado: Optional[str] = Cliente._formatar_cpf_para_busca(cpf)
        if cpf_formatado:
            return Cliente._clientes_por_cpf.get(cpf_formatado, None)
        return None

    @staticmethod
    def buscar_cliente_id(id_cliente: int) -> Optional['Cliente']:
        return Cliente._clientes_por_id.get(id_cliente, None)

    @staticmethod
    def buscar_cliente_por_nome_exato(nome: str) -> Optional['Cliente']:
        nome_busca_lower: str = nome.lower().strip()
        for cliente in Cliente._clientes_por_cpf.values():
            if cliente.nome.lower() == nome_busca_lower:
                return cliente
        return None

    @staticmethod
    def buscar_clientes_por_nome_parcial(nome_parcial: str) -> list['Cliente']:
        resultados: list['Cliente'] = []
        nome_parcial_lower: str = nome_parcial.lower().strip()
        for cliente in Cliente._clientes_por_cpf.values():
            if nome_parcial_lower in cliente.nome.lower():
                resultados.append(cliente)
        return resultados

    @staticmethod
    def listar_clientes() -> list['Cliente']:
        return list(Cliente._clientes_por_id.values()) 

    @staticmethod
    def atualizar_dados_cliente(id_cliente: int, **kwargs: Any) -> None: 
        cliente_existente: Optional['Cliente'] = Cliente.buscar_cliente_id(id_cliente) 
        if not cliente_existente:
            raise ValueError(f"Cliente com ID {id_cliente} não encontrado para atualização.")

        for chave, valor in kwargs.items():
            if chave == 'id' or chave == 'cpf': 
                continue
            if hasattr(cliente_existente, chave):
                setattr(cliente_existente, chave, valor)

    @staticmethod
    def atualizar_cpf_cliente(id_cliente: int, novo_cpf: str) -> None:
        cliente: Optional['Cliente'] = Cliente.buscar_cliente_id(id_cliente) 
        if not cliente:
            raise ValueError(f"Cliente com ID {id_cliente} não encontrado para atualização de CPF.")

        cpf_antigo_formatado: str = cliente.cpf
        
        try:
            cpf_limpo = re.sub(r'\D', '', novo_cpf)
            novo_cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

            if novo_cpf_formatado in Cliente._clientes_por_cpf and Cliente._clientes_por_cpf[novo_cpf_formatado] is not cliente:
                raise ValueError(f"Já existe outro cliente com o CPF {novo_cpf_formatado}.")

            del Cliente._clientes_por_cpf[cpf_antigo_formatado]
            cliente.cpf = novo_cpf
            Cliente._clientes_por_cpf[cliente.cpf] = cliente
        except ValueError as e:
            if cpf_antigo_formatado not in Cliente._clientes_por_cpf:
                Cliente._clientes_por_cpf[cpf_antigo_formatado] = cliente
            raise ValueError(f"Erro ao atualizar CPF: {e}")

    @staticmethod
    def deletar_cliente(id_cliente: int) -> None: 
        cliente_a_deletar: Optional['Cliente'] = Cliente.buscar_cliente_id(id_cliente)
        if not cliente_a_deletar:
            raise ValueError(f"Cliente com ID {id_cliente} não encontrado para exclusão.")

        del Cliente._clientes_por_id[id_cliente]
        if cliente_a_deletar.cpf in Cliente._clientes_por_cpf:
            del Cliente._clientes_por_cpf[cliente_a_deletar.cpf]
            

    @staticmethod
    def criar_cliente(nome: str, nascimento: str, cpf: str, info_contato: mod_info.Informacao) -> 'Cliente':
        novo_cliente = Cliente(None, nome, nascimento, cpf, info_contato)
        return novo_cliente

    @staticmethod
    def _formatar_clientes_para_tabela(clientes: list['Cliente']) -> str:
        if not clientes:
            return "Nenhum cliente para exibir."

        cabecalhos = ["ID", "Nome", "CPF", "Nascimento", "Idade", "Telefone", "Email"]
        dados_tabela = []

        for cliente in clientes:
            nascimento_str = cliente.nascimento.strftime('%d/%m/%Y')
            telefone_str = cliente.info_contato.telefone
            email_str = cliente.info_contato.email
            
            dados_tabela.append([
                cliente.id,
                cliente.nome,
                cliente.cpf,
                nascimento_str,
                cliente.idade,
                telefone_str,
                email_str
            ])
        
        return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
