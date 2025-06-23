from typing import Optional, Any
from tabulate import tabulate
from datetime import datetime

class Produto:
    # Representa um item tangível para venda.
    _produtos_por_nome: dict[str, 'Produto'] = {}
    _produtos_por_id: dict[int, 'Produto'] = {}
    _proximo_id_disponivel: int = 1

    def __init__(self, id_produto: Optional[int], nome: str, preco: float, estoque: float) -> None:
        if id_produto is None:
            self._id = Produto._proximo_id_disponivel
        else:
            if not isinstance(id_produto, int) or id_produto <= 0:
                raise ValueError("O ID do produto deve ser um número inteiro positivo.")
            self._id = id_produto

        self.nome = nome
        self.preco = preco
        self.estoque = estoque
        self._custo_compra: float = 0.0
        self._historico_custo_compra: list[tuple[datetime, float, float]] = []

        if Produto.buscar_produto_id(self.id) is not None:
            raise ValueError(f"Já existe um produto com o ID {self.id}.")

        for nome_existente_key in Produto._produtos_por_nome.keys():
            if self.nome.lower() == nome_existente_key.lower():
                raise ValueError(f"Produto com o nome '{Produto._produtos_por_nome[nome_existente_key].nome}' já existe.")
        
        Produto._produtos_por_nome[self.nome] = self
        Produto._produtos_por_id[self.id] = self

        if id_produto is None:
            Produto._proximo_id_disponivel += 1
        elif self.id >= Produto._proximo_id_disponivel:
            Produto._proximo_id_disponivel = self.id + 1

    def __str__(self) -> str:
        custo_str = f", Custo Última Compra: R${self._custo_compra:.2f}" if self._custo_compra > 0 else ""
        return (f"Produto ID: {self._id}, Nome: {self._nome}, Preço Venda: R${self._preco:.2f}, "
                f"Estoque: {self._estoque:.2f} unidades{custo_str}")

    def __repr__(self) -> str:
        return (f"Produto(id_produto={self._id!r}, nome={self._nome!r}, "
                f"preco={self._preco!r}, estoque={self._estoque!r}, "
                f"custo_compra={self._custo_compra!r}, "
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
            raise ValueError("O nome do produto não pode ser vazio.")
        self._nome = nome_limpo

    @property
    def preco(self) -> float:
        return self._preco

    @preco.setter
    def preco(self, valor: float | int | str) -> None:
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        try:
            valor_num: float = float(valor)
        except ValueError:
            raise TypeError("O preço deve ser um número válido.")
        
        if valor_num <= 0:
            raise ValueError("O preço deve ser maior que zero.")
        
        self._preco = valor_num

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
            raise TypeError("A quantidade em estoque deve ser um número válido (inteiro ou decimal).")
        if quantidade_num < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")
        self._estoque = quantidade_num

    @property
    def custo_compra(self) -> float:
        return self._custo_compra

    @custo_compra.setter
    def custo_compra(self, valor: float | int | str) -> None:
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        try:
            valor_num: float = float(valor)
        except ValueError:
            raise TypeError("O custo de compra deve ser um número válido.")
        
        if valor_num <= 0:
            raise ValueError("O custo de compra deve ser maior que zero.")
        
        self._custo_compra = valor_num
    
    @staticmethod
    def _inicializar_proximo_id() -> None:
        if Produto._produtos_por_id:
            Produto._proximo_id_disponivel = max(Produto._produtos_por_id.keys()) + 1
        else:
            Produto._proximo_id_disponivel = 1

    @staticmethod
    def buscar_produto(nome_produto: str) -> Optional['Produto']:
        nome_busca_lower: str = nome_produto.lower().strip()
        for produto_obj in Produto._produtos_por_nome.values():
            if produto_obj.nome.lower() == nome_busca_lower:
                return produto_obj
        return None

    @staticmethod
    def buscar_produto_id(id_produto: int) -> Optional['Produto']:
        return Produto._produtos_por_id.get(id_produto, None)

    @staticmethod
    def listar_produtos() -> list['Produto']:
        return list(Produto._produtos_por_id.values())

    @staticmethod
    def atualizar_dados_produto(id_produto: int, **kwargs: Any) -> None:
        produto_existente: Optional['Produto'] = Produto.buscar_produto_id(id_produto)
        if not produto_existente:
            raise ValueError(f"Produto com ID {id_produto} não encontrado para atualização.")

        nome_antigo_para_dict: str = produto_existente.nome 

        for chave, valor in kwargs.items():
            if chave == 'id':
                continue

            if chave == 'nome':
                novo_nome_limpo = str(valor).strip()
                if not novo_nome_limpo:
                    raise ValueError("O novo nome do produto não pode ser vazio.")
                
                if novo_nome_limpo.lower() == nome_antigo_para_dict.lower():
                    continue
                
                if Produto.buscar_produto(novo_nome_limpo) is not None:
                    raise ValueError(f"Não foi possível atualizar o nome. Já existe um produto com o nome '{novo_nome_limpo}'.")
                
                del Produto._produtos_por_nome[nome_antigo_para_dict]
                try:
                    produto_existente.nome = novo_nome_limpo
                    Produto._produtos_por_nome[produto_existente.nome] = produto_existente
                except Exception as e:
                    Produto._produtos_por_nome[nome_antigo_para_dict] = produto_existente
                    raise ValueError(f"Erro ao atualizar o nome do produto: {e}")
                
                nome_antigo_para_dict = produto_existente.nome 
            elif hasattr(produto_existente, chave):
                try:
                    setattr(produto_existente, chave, valor)
                except (ValueError, TypeError) as e:
                    raise type(e)(f"Erro ao validar '{chave}': {e}")

    @staticmethod
    def deletar_produto(id_produto: int) -> None:
        produto_a_deletar: Optional['Produto'] = Produto.buscar_produto_id(id_produto)
        
        if not produto_a_deletar:
            raise ValueError(f"Produto com ID {id_produto} não encontrado para exclusão.")
        
        del Produto._produtos_por_id[id_produto]
        if produto_a_deletar.nome in Produto._produtos_por_nome:
            del Produto._produtos_por_nome[produto_a_deletar.nome]
        

    @staticmethod
    def criar_produto(nome: str, preco: float, estoque: float) -> 'Produto':
        novo_produto = Produto(None, nome, preco, estoque)
        return novo_produto

    @staticmethod
    def _formatar_produtos_para_tabela(produtos: list['Produto']) -> str:
        if not produtos:
            return "Nenhum produto para exibir."

        cabecalhos = ["ID", "Nome", "Preço Venda", "Custo Última Compra", "Estoque"]
        dados_tabela = []

        for produto_obj in produtos:
            preco_str = f"R${produto_obj.preco:.2f}"
            custo_compra_str = f"R${produto_obj.custo_compra:.2f}" if produto_obj.custo_compra > 0 else "N/A"
            
            dados_tabela.append([
                produto_obj.id,
                produto_obj.nome,
                preco_str,
                custo_compra_str,
                f"{produto_obj.estoque:.2f}"
            ])
        
        return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
