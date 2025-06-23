import re
from typing import Optional, Any
import info as mod_info
from tabulate import tabulate

class Fornecedor:
    # Representa um fornecedor de produtos ou serviços.
    _fornecedores_por_cnpj: dict[str, 'Fornecedor'] = {}
    _fornecedores_por_id: dict[int, 'Fornecedor'] = {}
    _proximo_id_disponivel: int = 1

    def __init__(self, id_fornecedor: Optional[int], nome: str, cnpj: str, info_contato: mod_info.Informacao) -> None:
        if id_fornecedor is None:
            self._id = Fornecedor._proximo_id_disponivel
        else:
            if not isinstance(id_fornecedor, int) or id_fornecedor <= 0:
                raise ValueError("O ID do fornecedor deve ser um número inteiro positivo.")
            self._id = id_fornecedor

        self.nome = nome
        self.cnpj = cnpj
        self.info_contato = info_contato
        
        if Fornecedor.buscar_fornecedor_id(self.id) is not None:
            raise ValueError(f"Já existe um fornecedor com o ID {self.id}.")

        if self.cnpj in Fornecedor._fornecedores_por_cnpj:
            raise ValueError(f"Fornecedor com CNPJ {self.cnpj} já existe.")  
        
        Fornecedor._fornecedores_por_cnpj[self.cnpj] = self
        Fornecedor._fornecedores_por_id[self.id] = self

        if id_fornecedor is None:
            Fornecedor._proximo_id_disponivel += 1
        elif self.id >= Fornecedor._proximo_id_disponivel:
            Fornecedor._proximo_id_disponivel = self.id + 1

    def __str__(self) -> str:
        return (f"ID: {self._id}, Nome: {self._nome}, CNPJ: {self._cnpj}\n"
                f"  Informações de Contato: {self.info_contato}")

    def __repr__(self) -> str:
        return (f"Fornecedor(id_fornecedor={self._id!r}, nome={self._nome!r}, cnpj={self._cnpj!r}, "
                f"info_contato={self.info_contato!r})")

    @property
    def id(self) -> int:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, nome_str: str) -> None:
        nome_limpo = nome_str.strip()
        if not nome_limpo:
            raise ValueError("O nome do fornecedor não pode ser vazio.")
        self._nome = nome_limpo

    @property
    def cnpj(self) -> str:
        return self._cnpj

    @cnpj.setter
    def cnpj(self, cnpj_str: str) -> None:
        cnpj_limpo: str = re.sub(r'\D', '', cnpj_str)
        if len(cnpj_limpo) != 14:
            raise ValueError("CNPJ inválido: Deve conter exatamente 14 dígitos.")
        if not Fornecedor._eh_cnpj_valido(cnpj_limpo):
            raise ValueError("CNPJ inválido: Dígitos verificadores não correspondem ou padrão inválido.")
        cnpj_formatado: str = (
            f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/"
            f"{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
        )
        self._cnpj = cnpj_formatado

    @staticmethod
    def _eh_cnpj_valido(numeros_cnpj: str) -> bool:
        if not numeros_cnpj.isdigit() or len(numeros_cnpj) != 14:
            return False

        if len(set(numeros_cnpj)) == 1:
            return False
        soma1: int = 0
        multiplicadores1: list[int] = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        for i in range(12):
            soma1 += int(numeros_cnpj[i]) * multiplicadores1[i]
        primeiro_dv_calculado: int = 11 - (soma1 % 11)
        if primeiro_dv_calculado > 9:
            primeiro_dv_calculado = 0
        if primeiro_dv_calculado != int(numeros_cnpj[12]):
            return False
        soma2: int = 0
        multiplicadores2: list[int] = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        for i in range(13):
            soma2 += int(numeros_cnpj[i]) * multiplicadores2[i]
        segundo_dv_calculado: int = 11 - (soma2 % 11)
        if segundo_dv_calculado > 9:
            segundo_dv_calculado = 0
        return segundo_dv_calculado == int(numeros_cnpj[13])

    @property
    def info_contato(self) -> mod_info.Informacao:
        return self._info_contato

    @info_contato.setter
    def info_contato(self, nova_info: mod_info.Informacao) -> None:
        if not isinstance(nova_info, mod_info.Informacao):
            raise TypeError("A informação de contato deve ser uma instância da classe Informacao.")
        self._info_contato = nova_info

    @staticmethod
    def _inicializar_proximo_id() -> None:
        if Fornecedor._fornecedores_por_id:
            Fornecedor._proximo_id_disponivel = max(Fornecedor._fornecedores_por_id.keys()) + 1
        else:
            Fornecedor._proximo_id_disponivel = 1

    @staticmethod
    def _formatar_cnpj_para_busca(cnpj_entrada: str) -> Optional[str]:
        cnpj_limpo: str = re.sub(r'\D', '', cnpj_entrada)
        if len(cnpj_limpo) == 14:
            return (
                f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/"
                f"{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
            )
        return None

    @staticmethod
    def buscar_fornecedor(cnpj: str) -> Optional['Fornecedor']:
        cnpj_formatado: Optional[str] = Fornecedor._formatar_cnpj_para_busca(cnpj)
        if cnpj_formatado:
            return Fornecedor._fornecedores_por_cnpj.get(cnpj_formatado, None)
        return None

    @staticmethod
    def buscar_fornecedor_id(id_fornecedor: int) -> Optional['Fornecedor']:
        return Fornecedor._fornecedores_por_id.get(id_fornecedor, None)

    @staticmethod
    def buscar_fornecedor_por_nome_exato(nome: str) -> Optional['Fornecedor']:
        nome_busca_lower: str = nome.lower().strip()
        for fornecedor in Fornecedor._fornecedores_por_cnpj.values():
            if fornecedor.nome.lower() == nome_busca_lower:
                return fornecedor
        return None

    @staticmethod
    def buscar_fornecedores_por_nome_parcial(nome_parcial: str) -> list['Fornecedor']:
        resultados: list['Fornecedor'] = []
        nome_parcial_lower: str = nome_parcial.lower().strip()
        for fornecedor in Fornecedor._fornecedores_por_cnpj.values():
            if nome_parcial_lower in fornecedor.nome.lower():
                resultados.append(fornecedor)
        return resultados

    @staticmethod
    def listar_fornecedores() -> list['Fornecedor']:
        return list(Fornecedor._fornecedores_por_id.values())

    @staticmethod
    def atualizar_dados_fornecedor(id_fornecedor: int, **kwargs: Any) -> None:
        fornecedor_existente: Optional['Fornecedor'] = Fornecedor.buscar_fornecedor_id(id_fornecedor)
        if not fornecedor_existente:
            raise ValueError(f"Fornecedor com ID {id_fornecedor} não encontrado para atualização.")

        for chave, valor in kwargs.items():
            if chave == 'id' or chave == 'cnpj':
                continue
            
            if hasattr(fornecedor_existente, chave):
                try:
                    setattr(fornecedor_existente, chave, valor)
                except (ValueError, TypeError) as e:
                    raise type(e)(f"Erro ao validar '{chave}': {e}")

    @staticmethod
    def atualizar_cnpj_fornecedor(id_fornecedor: int, novo_cnpj: str) -> None:
        fornecedor: Optional['Fornecedor'] = Fornecedor.buscar_fornecedor_id(id_fornecedor)
        if not fornecedor:
            raise ValueError(f"Fornecedor com ID {id_fornecedor} não encontrado para atualização de CNPJ.")

        cnpj_antigo_formatado: str = fornecedor.cnpj
        
        try:
            cnpj_limpo_novo = re.sub(r'\D', '', novo_cnpj)
            novo_cnpj_formatado = (
                f"{cnpj_limpo_novo[:2]}.{cnpj_limpo_novo[2:5]}.{cnpj_limpo_novo[5:8]}/"
                f"{cnpj_limpo_novo[8:12]}-{cnpj_limpo_novo[12:]}"
            )

            if novo_cnpj_formatado in Fornecedor._fornecedores_por_cnpj and Fornecedor._fornecedores_por_cnpj[novo_cnpj_formatado] is not fornecedor:
                raise ValueError(f"Já existe outro fornecedor com o CNPJ {novo_cnpj_formatado}.")

            del Fornecedor._fornecedores_por_cnpj[cnpj_antigo_formatado]
            fornecedor.cnpj = novo_cnpj
            Fornecedor._fornecedores_por_cnpj[fornecedor.cnpj] = fornecedor
        except ValueError as e:
            Fornecedor._fornecedores_por_cnpj[cnpj_antigo_formatado] = fornecedor
            raise ValueError(f"Erro ao atualizar CNPJ: {e}")

    @staticmethod
    def deletar_fornecedor(id_fornecedor: int) -> None:
        fornecedor_a_deletar: Optional['Fornecedor'] = Fornecedor.buscar_fornecedor_id(id_fornecedor)
        if not fornecedor_a_deletar:
            raise ValueError(f"Fornecedor com ID {id_fornecedor} não encontrado para exclusão.")

        del Fornecedor._fornecedores_por_id[id_fornecedor]
        if fornecedor_a_deletar.cnpj in Fornecedor._fornecedores_por_cnpj:
            del Fornecedor._fornecedores_por_cnpj[fornecedor_a_deletar.cnpj]
            

    @staticmethod
    def criar_fornecedor(nome: str, cnpj: str, info_contato: mod_info.Informacao) -> 'Fornecedor':
        novo_fornecedor = Fornecedor(None, nome, cnpj, info_contato)
        return novo_fornecedor

    @staticmethod
    def _formatar_fornecedores_para_tabela(fornecedores: list['Fornecedor']) -> str:
        if not fornecedores:
            return "Nenhum fornecedor para exibir."

        cabecalhos = ["ID", "Nome", "CNPJ", "Telefone", "Email"]
        dados_tabela = []

        for forn in fornecedores:
            telefone_str = forn.info_contato.telefone
            email_str = forn.info_contato.email
            
            dados_tabela.append([
                forn.id,
                forn.nome,
                forn.cnpj,
                telefone_str,
                email_str
            ])
        
        return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
