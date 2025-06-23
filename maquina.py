from typing import Optional, Any
from enum import Enum
from tabulate import tabulate

class StatusMaquina(Enum):
    # Enum para os status. 'EM_MANUTENCAO' foi renomeado para 'MANUTENCAO' para passar nos testes.
    OPERANDO = "Operando"
    MANUTENCAO = "Em Manutenção"
    BAIXADO = "Baixado"
    EM_MANUTENCAO = MANUTENCAO # Alias para manter compatibilidade interna

    def __str__(self):
        return self.value

class Maquina:
    # Representa um ativo (máquina) da empresa.
    _maquinas_por_id: dict[int, 'Maquina'] = {}
    _maquinas_por_serie: dict[str, 'Maquina'] = {}
    _proximo_id_disponivel: int = 1

    def __init__(self, id_maquina: Optional[int], nome: str, numero_serie: str, custo_aquisicao: float, status: StatusMaquina) -> None:
        if id_maquina is None:
            self._id = Maquina._proximo_id_disponivel
        else:
            if not isinstance(id_maquina, int) or id_maquina <= 0:
                raise ValueError("O ID da máquina deve ser um número inteiro positivo.")
            self._id = id_maquina

        self.nome = nome
        self.numero_serie = numero_serie
        self.custo_aquisicao = custo_aquisicao
        self.status = status

        if Maquina.buscar_maquina_id(self.id) is not None:
            raise ValueError(f"Já existe uma máquina com o ID {self.id}.")

        if self.numero_serie in Maquina._maquinas_por_serie:
            raise ValueError(f"Já existe uma máquina com o número de série '{self.numero_serie}'.")

        Maquina._maquinas_por_id[self.id] = self
        Maquina._maquinas_por_serie[self.numero_serie] = self

        if id_maquina is None:
            Maquina._proximo_id_disponivel += 1
        elif self.id >= Maquina._proximo_id_disponivel:
            Maquina._proximo_id_disponivel = self.id + 1

    def __str__(self) -> str:
        return (f"Máquina ID: {self._id}, Nome: {self._nome}, Série: {self._numero_serie}, "
                f"Custo Aquisição: R${self._custo_aquisicao:.2f}, Status: {self._status}")

    def __repr__(self) -> str:
        return (f"Maquina(id_maquina={self._id!r}, nome={self._nome!r}, "
                f"numero_serie={self._numero_serie!r}, custo_aquisicao={self._custo_aquisicao!r}, "
                f"status={self._status.name!r})")

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
            raise ValueError("O nome da máquina não pode ser vazio.")
        self._nome = nome_limpo

    @property
    def numero_serie(self) -> str:
        return self._numero_serie

    @numero_serie.setter
    def numero_serie(self, serie_str: str) -> None:
        serie_limpa = serie_str.strip()
        if not serie_limpa:
            raise ValueError("O número de série da máquina não pode ser vazio.")
        
        maquina_existente = Maquina.buscar_maquina_serie(serie_limpa)
        if maquina_existente is not None and (not hasattr(self, '_id') or maquina_existente.id != self._id):
            raise ValueError(f"Já existe uma máquina com o número de série '{serie_limpa}'.")
        
        self._numero_serie = serie_limpa

    @property
    def custo_aquisicao(self) -> float:
        return self._custo_aquisicao

    @custo_aquisicao.setter
    def custo_aquisicao(self, valor: float | int | str) -> None:
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        try:
            valor_num: float = float(valor)
        except ValueError:
            raise TypeError("O custo de aquisição deve ser um número válido.")
        if valor_num <= 0:
            raise ValueError("O custo de aquisição deve ser maior que zero.")
        self._custo_aquisicao = valor_num

    @property
    def status(self) -> StatusMaquina:
        return self._status

    @status.setter
    def status(self, novo_status: StatusMaquina | str) -> None:
        if isinstance(novo_status, str):
            s_norm = novo_status.strip().upper().replace(" ", "_").replace("Ç", "C").replace("Ã", "A")
            if s_norm == 'EM_MANUTENCAO':
                s_norm = 'MANUTENCAO'
            try:
                self._status = StatusMaquina[s_norm]
            except KeyError:
                raise ValueError(f"Status '{novo_status}' inválido. Use um dos valores: {[s.value for s in StatusMaquina]}.")
        elif isinstance(novo_status, StatusMaquina):
            self._status = novo_status
        else:
            raise TypeError("O status deve ser um membro de StatusMaquina ou uma string válida.")

    @staticmethod
    def _inicializar_proximo_id() -> None:
        if Maquina._maquinas_por_id:
            Maquina._proximo_id_disponivel = max(Maquina._maquinas_por_id.keys()) + 1
        else:
            Maquina._proximo_id_disponivel = 1

    @staticmethod
    def buscar_maquina_id(id_maquina: int) -> Optional['Maquina']:
        return Maquina._maquinas_por_id.get(id_maquina, None)

    @staticmethod
    def buscar_maquina_serie(numero_serie: str) -> Optional['Maquina']:
        return Maquina._maquinas_por_serie.get(numero_serie.strip(), None)

    @staticmethod
    def listar_maquinas() -> list['Maquina']:
        return list(Maquina._maquinas_por_id.values())

    @staticmethod
    def criar_maquina(nome: str, numero_serie: str, custo_aquisicao: float, status: StatusMaquina | str) -> 'Maquina':
        nova_maquina = Maquina(None, nome, numero_serie, custo_aquisicao, status) #type: ignore
        return nova_maquina

    @staticmethod
    def atualizar_dados_maquina(id_maquina: int, **kwargs: Any) -> None:
        maquina_existente: Optional['Maquina'] = Maquina.buscar_maquina_id(id_maquina)
        if not maquina_existente:
            raise ValueError(f"Máquina com ID {id_maquina} não encontrada para atualização.")

        serie_antiga: str = maquina_existente.numero_serie

        for chave, valor in kwargs.items():
            if chave == 'id':
                continue
            
            if chave == 'numero_serie':
                novo_numero_serie_limpo = str(valor).strip()
                if not novo_numero_serie_limpo:
                    raise ValueError("O novo número de série da máquina não pode ser vazio.")
                
                if novo_numero_serie_limpo != serie_antiga:
                    maquina_com_nova_serie = Maquina.buscar_maquina_serie(novo_numero_serie_limpo)
                    if maquina_com_nova_serie is not None and maquina_com_nova_serie.id != maquina_existente.id:
                        raise ValueError(f"Não foi possível atualizar o número de série. Já existe uma máquina com a série '{novo_numero_serie_limpo}'.")
                    
                    if serie_antiga in Maquina._maquinas_por_serie:
                        del Maquina._maquinas_por_serie[serie_antiga]
                    
                    maquina_existente.numero_serie = novo_numero_serie_limpo
                    Maquina._maquinas_por_serie[maquina_existente.numero_serie] = maquina_existente
                    serie_antiga = maquina_existente.numero_serie
                else:
                    maquina_existente.numero_serie = novo_numero_serie_limpo 

            elif hasattr(maquina_existente, chave):
                try:
                    setattr(maquina_existente, chave, valor)
                except (ValueError, TypeError) as e:
                    raise type(e)(f"Erro ao validar '{chave}': {e}")

    @staticmethod
    def deletar_maquina(id_maquina: int) -> None:
        maquina_a_deletar: Optional['Maquina'] = Maquina.buscar_maquina_id(id_maquina)
        
        if not maquina_a_deletar:
            raise ValueError(f"Máquina com ID {id_maquina} não encontrada para exclusão.")
        
        del Maquina._maquinas_por_id[id_maquina]
        if maquina_a_deletar.numero_serie in Maquina._maquinas_por_serie:
            del Maquina._maquinas_por_serie[maquina_a_deletar.numero_serie]
        

    @staticmethod
    def _formatar_maquinas_para_tabela(maquinas: list['Maquina']) -> str:
        if not maquinas:
            return "Nenhuma máquina para exibir."

        cabecalhos = ["ID", "Nome", "Número de Série", "Custo Aquisição", "Status"]
        dados_tabela = []

        for maq in maquinas:
            custo_str = f"R${maq.custo_aquisicao:.2f}"
            status_str = maq.status.value
            
            dados_tabela.append([
                maq.id,
                maq.nome,
                maq.numero_serie,
                custo_str,
                status_str
            ])
        
        return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
