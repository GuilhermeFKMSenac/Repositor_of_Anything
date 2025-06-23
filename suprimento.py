from tabulate import tabulate
from datetime import datetime
from typing import Optional, Any

class Suprimento:
    # Representa um item de consumo interno ou usado em serviços.
    _suprimentos_por_id: dict[int, 'Suprimento'] = {}
    _suprimentos_por_nome: dict[str, 'Suprimento'] = {}
    _proximo_id_disponivel: int = 1

    def __init__(self, id_suprimento: Optional[int], nome: str, unidade_medida: str, custo_unitario: float, estoque: float) -> None:
        if id_suprimento is None:
            self._id = Suprimento._proximo_id_disponivel
        else:
            if not isinstance(id_suprimento, int) or id_suprimento <= 0:
                raise ValueError("O ID do suprimento deve ser um número inteiro positivo.")
            self._id = id_suprimento

        self.nome = nome
        self.unidade_medida = unidade_medida
        self.custo_unitario = custo_unitario
        self.estoque = estoque
        self._historico_custo_compra: list[tuple[datetime, float, float]] = []

        if Suprimento.buscar_suprimento_id(self.id) is not None:
            raise ValueError(f"Já existe um suprimento com o ID {self.id}.")

        for nome_existente_key in Suprimento._suprimentos_por_nome.keys():
            if self.nome.lower() == nome_existente_key.lower():
                raise ValueError(f"Já existe um suprimento com o nome '{Suprimento._suprimentos_por_nome[nome_existente_key].nome}'.")

        Suprimento._suprimentos_por_id[self.id] = self
        Suprimento._suprimentos_por_nome[self.nome.lower()] = self

        if id_suprimento is None:
            Suprimento._proximo_id_disponivel += 1
        elif self.id >= Suprimento._proximo_id_disponivel:
            Suprimento._proximo_id_disponivel = self.id + 1

    def __str__(self) -> str:
        return (f"Suprimento ID: {self._id}, Nome: {self._nome}, "
                f"Unidade: {self._unidade_medida}, Custo Última Compra: R${self._custo_unitario:.2f}, "
                f"Estoque: {self._estoque:.2f}")

    def __repr__(self) -> str:
        return (f"Suprimento(id_suprimento={self._id!r}, nome={self._nome!r}, "
                f"unidade_medida={self._unidade_medida!r}, custo_unitario={self._custo_unitario!r}, "
                f"estoque={self._estoque!r}, "
                f"historico_custo_compra={self._historico_custo_compra!r})")

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
            raise ValueError("O nome do suprimento não pode ser vazio.")
        self._nome = nome_limpo

    @property
    def unidade_medida(self) -> str:
        return self._unidade_medida

    @unidade_medida.setter
    def unidade_medida(self, unidade_str: str) -> None:
        unidade_limpa = unidade_str.strip()
        if not unidade_limpa:
            raise ValueError("A unidade de medida não pode ser vazia.")
        self._unidade_medida = unidade_limpa

    @property
    def custo_unitario(self) -> float:
        return self._custo_unitario

    @custo_unitario.setter
    def custo_unitario(self, valor: float | int | str) -> None:
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        try:
            valor_num: float = float(valor)
        except ValueError:
            raise TypeError("O custo unitário deve ser um número válido.")
        if valor_num <= 0:
            raise ValueError("O custo unitário deve ser maior que zero.")
        self._custo_unitario = valor_num

    @property
    def estoque(self) -> float:
        return self._estoque

    @estoque.setter
    def estoque(self, quantidade: float | int | str) -> None:
        if isinstance(quantidade, str):
            quantidade = quantidade.replace(",", ".")
        try:
            quantidade_num: float = float(quantidade)
        except ValueError:
            raise TypeError("A quantidade em estoque deve ser um número válido.")
        if quantidade_num < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")
        
        self._estoque = quantidade_num

    @staticmethod
    def _inicializar_proximo_id() -> None:
        if Suprimento._suprimentos_por_id:
            Suprimento._proximo_id_disponivel = max(Suprimento._suprimentos_por_id.keys()) + 1
        else:
            Suprimento._proximo_id_disponivel = 1

    @staticmethod
    def buscar_suprimento_id(id_suprimento: int) -> Optional['Suprimento']:
        return Suprimento._suprimentos_por_id.get(id_suprimento, None)

    @staticmethod
    def buscar_suprimento_nome(nome_suprimento: str) -> Optional['Suprimento']:
        return Suprimento._suprimentos_por_nome.get(nome_suprimento.lower().strip(), None)

    @staticmethod
    def listar_suprimentos() -> list['Suprimento']:
        return list(Suprimento._suprimentos_por_id.values())

    @staticmethod
    def criar_suprimento(nome: str, unidade_medida: str, custo_unitario: float, estoque: float) -> 'Suprimento':
        novo_suprimento = Suprimento(None, nome, unidade_medida, custo_unitario, estoque)
        return novo_suprimento

    @staticmethod
    def atualizar_dados_suprimento(id_suprimento: int, **kwargs: Any) -> None:
        suprimento_existente: Optional['Suprimento'] = Suprimento.buscar_suprimento_id(id_suprimento)
        if not suprimento_existente:
            raise ValueError(f"Suprimento com ID {id_suprimento} não encontrado para atualização.")

        nome_antigo_lower: str = suprimento_existente.nome.lower()

        for chave, valor in kwargs.items():
            if chave == 'id':
                continue
            
            if chave == 'nome':
                novo_nome_limpo = str(valor).strip()
                if not novo_nome_limpo:
                    raise ValueError("O novo nome do suprimento não pode ser vazio.")
                
                if novo_nome_limpo.lower() != nome_antigo_lower:
                    suprimento_com_novo_nome = Suprimento.buscar_suprimento_nome(novo_nome_limpo)
                    if suprimento_com_novo_nome is not None and suprimento_com_novo_nome.id != suprimento_existente.id:
                        raise ValueError(f"Não foi possível atualizar o nome. Já existe um suprimento com o nome '{novo_nome_limpo}'.")
                    
                    if nome_antigo_lower in Suprimento._suprimentos_por_nome:
                        del Suprimento._suprimentos_por_nome[nome_antigo_lower]
                    
                    suprimento_existente.nome = novo_nome_limpo
                    Suprimento._suprimentos_por_nome[suprimento_existente.nome.lower()] = suprimento_existente
                    nome_antigo_lower = suprimento_existente.nome.lower() 
                else: 
                    suprimento_existente.nome = novo_nome_limpo

            elif hasattr(suprimento_existente, chave):
                try:
                    setattr(suprimento_existente, chave, valor)
                except (ValueError, TypeError) as e:
                    raise type(e)(f"Erro ao validar '{chave}': {e}")

    @staticmethod
    def deletar_suprimento(id_suprimento: int) -> None:
        suprimento_a_deletar: Optional['Suprimento'] = Suprimento.buscar_suprimento_id(id_suprimento)
        
        if not suprimento_a_deletar:
            raise ValueError(f"Suprimento com ID {id_suprimento} não encontrado para exclusão.")
        
        del Suprimento._suprimentos_por_id[id_suprimento]
        if suprimento_a_deletar.nome.lower() in Suprimento._suprimentos_por_nome:
            del Suprimento._suprimentos_por_nome[suprimento_a_deletar.nome.lower()]
        

    @staticmethod
    def _formatar_suprimentos_para_tabela(suprimentos: list['Suprimento']) -> str:
        if not suprimentos:
            return "Nenhum suprimento para exibir."

        cabecalhos = ["ID", "Nome", "Unidade", "Custo Última Compra", "Estoque"]
        dados_tabela = []

        for sup in suprimentos:
            custo_str = f"R${sup.custo_unitario:.2f}"
            
            dados_tabela.append([
                sup.id,
                sup.nome,
                sup.unidade_medida,
                custo_str,
                f"{sup.estoque:.2f}"
            ])
        
        return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
