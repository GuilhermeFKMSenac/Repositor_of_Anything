from typing import Optional, Any
from tabulate import tabulate

class Servico:
    # Representa um serviço prestado pela empresa.
    _servicos_por_nome: dict[str, 'Servico'] = {}
    _servicos_por_id: dict[int, 'Servico'] = {}
    _proximo_id_disponivel: int = 1

    def __init__(self, id_servico: Optional[int], nome: str, valor_venda: float, custo: float) -> None:
        if id_servico is None:
            self._id = Servico._proximo_id_disponivel
        else:
            if not isinstance(id_servico, int) or id_servico <= 0:
                raise ValueError("O ID do serviço deve ser um número inteiro positivo.")
            self._id = id_servico

        self.nome = nome
        self.valor_venda = valor_venda
        self.custo = custo

        if Servico.buscar_servico_id(self.id) is not None:
            raise ValueError(f"Já existe um serviço com o ID {self.id}.")

        for nome_existente_key in Servico._servicos_por_nome.keys():
            if self.nome.lower() == nome_existente_key.lower():
                raise ValueError(f"Serviço com o nome '{Servico._servicos_por_nome[nome_existente_key].nome}' já existe.")
        
        Servico._servicos_por_nome[self.nome] = self
        Servico._servicos_por_id[self.id] = self

        if id_servico is None:
            Servico._proximo_id_disponivel += 1
        elif self.id >= Servico._proximo_id_disponivel:
            Servico._proximo_id_disponivel = self.id + 1

    def __str__(self) -> str:
        return (f"Serviço ID: {self._id}, Nome: {self._nome}, Valor de Venda: R${self._valor_venda:.2f}, "
                f"Custo: R${self._custo:.2f}")

    def __repr__(self) -> str:
        return (f"Servico(id_servico={self._id!r}, nome={self._nome!r}, valor_venda={self._valor_venda!r}, "
                f"custo={self._custo!r})")

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
            raise ValueError("O nome do serviço não pode ser vazio.")
        self._nome = nome_limpo

    @property
    def valor_venda(self) -> float:
        return self._valor_venda

    @valor_venda.setter
    def valor_venda(self, valor: float | int | str) -> None:
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        try:
            valor_num: float = float(valor)
        except ValueError:
            raise TypeError("O valor de venda deve ser um número válido.")
        
        if valor_num <= 0:
            raise ValueError("O valor de venda deve ser maior que zero.")
        
        self._valor_venda = valor_num

    @property
    def custo(self) -> float:
        return self._custo

    @custo.setter
    def custo(self, valor: float | int | str) -> None:
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        try:
            valor_num: float = float(valor)
        except ValueError:
            raise TypeError("O custo deve ser um número válido.")
        
        if valor_num <= 0:
            raise ValueError("O custo deve ser maior que zero.")
        
        self._custo = valor_num

    @staticmethod
    def _inicializar_proximo_id() -> None:
        if Servico._servicos_por_id:
            Servico._proximo_id_disponivel = max(Servico._servicos_por_id.keys()) + 1
        else:
            Servico._proximo_id_disponivel = 1

    @staticmethod
    def buscar_servico(nome_servico: str) -> Optional['Servico']:
        nome_busca_lower: str = nome_servico.lower().strip()
        for servico_obj in Servico._servicos_por_nome.values():
            if servico_obj.nome.lower() == nome_busca_lower:
                return servico_obj
        return None

    @staticmethod
    def buscar_servico_id(id_servico: int) -> Optional['Servico']:
        return Servico._servicos_por_id.get(id_servico, None)

    @staticmethod
    def listar_servicos() -> list['Servico']:
        return list(Servico._servicos_por_id.values())

    @staticmethod
    def atualizar_dados_servico(id_servico: int, **kwargs: Any) -> None:
        servico_existente: Optional['Servico'] = Servico.buscar_servico_id(id_servico)
        if not servico_existente:
            raise ValueError(f"Serviço com ID {id_servico} não encontrado para atualização.") 

        nome_antigo_para_dict: str = servico_existente.nome
        for chave, valor in kwargs.items():
            if chave == 'id':
                continue
            
            if chave == 'nome':
                novo_nome_limpo = str(valor).strip()
                if not novo_nome_limpo:
                    raise ValueError("O novo nome do serviço não pode ser vazio.")
                
                if novo_nome_limpo.lower() == nome_antigo_para_dict.lower():
                    continue
                
                if Servico.buscar_servico(novo_nome_limpo) is not None:
                    raise ValueError(f"Não foi possível atualizar o nome. Já existe um serviço com o nome '{novo_nome_limpo}'.")
                
                del Servico._servicos_por_nome[nome_antigo_para_dict]
                try:
                    servico_existente.nome = novo_nome_limpo
                    Servico._servicos_por_nome[servico_existente.nome] = servico_existente
                except Exception as e:
                    Servico._servicos_por_nome[nome_antigo_para_dict] = servico_existente
                    raise ValueError(f"Erro ao atualizar o nome do serviço: {e}")
                
                nome_antigo_para_dict = servico_existente.nome 
            elif hasattr(servico_existente, chave):
                try:
                    setattr(servico_existente, chave, valor)
                except (ValueError, TypeError) as e:
                    raise type(e)(f"Erro ao validar '{chave}': {e}")

    @staticmethod
    def deletar_servico(id_servico: int) -> None:
        servico_a_deletar: Optional['Servico'] = Servico.buscar_servico_id(id_servico)
        
        if not servico_a_deletar:
            raise ValueError(f"Serviço com ID {id_servico} não encontrado para exclusão.")
        
        del Servico._servicos_por_id[id_servico]
        if servico_a_deletar.nome in Servico._servicos_por_nome:
            del Servico._servicos_por_nome[servico_a_deletar.nome]
        

    @staticmethod
    def criar_servico(nome: str, valor_venda: float, custo: float) -> 'Servico':
        novo_servico = Servico(None, nome, valor_venda, custo)
        return novo_servico

    @staticmethod
    def _formatar_servicos_para_tabela(servicos: list['Servico']) -> str:
        if not servicos:
            return "Nenhum serviço para exibir."

        cabecalhos = ["ID", "Nome", "Valor de Venda", "Custo"]
        dados_tabela = []

        for srv in servicos:
            valor_venda_str = f"R${srv.valor_venda:.2f}"
            custo_str = f"R${srv.custo:.2f}"
            
            dados_tabela.append([
                srv.id,
                srv.nome,
                valor_venda_str,
                custo_str
            ])
        
        return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
