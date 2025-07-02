from sqlalchemy import Column, Integer, String, Float, JSON, func
from sqlalchemy.orm import Session, synonym
from datetime import datetime
from tabulate import tabulate
from typing import Optional, Any

from database import Base

class Produto(Base):
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True, index=True)
    _nome = Column("nome", String(255), unique=True, index=True, nullable=False)
    _preco = Column("preco", Float, nullable=False)
    _estoque = Column("estoque", Float, nullable=False, default=0.0)
    _custo_compra = Column("custo_compra", Float, nullable=False, default=0.0)
    _historico_custo_compra = Column("historico_custo_compra", JSON, nullable=True)

    def __init__(self, nome: str, preco: float, estoque: float, **kwargs):
        self.nome = nome
        self.preco = preco
        self.estoque = estoque
        self.custo_compra = kwargs.get('custo_compra', 0.0)
        self.historico_custo_compra = kwargs.get('historico_custo_compra', [])

    def __str__(self) -> str:
        custo_str = f", Custo Última Compra: R${self.custo_compra:.2f}" if self.custo_compra > 0 else ""
        return (f"Produto ID: {self.id}, Nome: {self.nome}, Preço Venda: R${self.preco:.2f}, "
                f"Estoque: {self.estoque:.2f} unidades{custo_str}")

    nome = synonym('_nome', descriptor=property(
        lambda self: self._nome,
        lambda self, valor: setattr(self, '_nome', self._valida_nome(valor))
    ))

    preco = synonym('_preco', descriptor=property(
        lambda self: self._preco,
        lambda self, valor: setattr(self, '_preco', self._valida_preco(valor))
    ))

    estoque = synonym('_estoque', descriptor=property(
        lambda self: self._estoque,
        lambda self, valor: setattr(self, '_estoque', self._valida_estoque(valor))
    ))

    custo_compra = synonym('_custo_compra', descriptor=property(
        lambda self: self._custo_compra,
        lambda self, valor: setattr(self, '_custo_compra', self._valida_custo_compra(valor))
    ))

    historico_custo_compra = synonym('_historico_custo_compra', descriptor=property(
        lambda self: self._historico_custo_compra,
        lambda self, valor: setattr(self, '_historico_custo_compra', valor)
    ))

    def _valida_nome(self, nome_str: str) -> str:
        nome_limpo = nome_str.strip()
        if not nome_limpo:
            raise ValueError("O nome do produto não pode ser vazio.")
        return nome_limpo

    def _valida_preco(self, valor: float | int | str) -> float:
        if isinstance(valor, str): valor = valor.replace(",", ".")
        try: valor_num = float(valor)
        except ValueError: raise TypeError("O preço deve ser um número válido.")
        if valor_num <= 0: raise ValueError("O preço deve ser maior que zero.")
        return valor_num

    def _valida_estoque(self, quantidade: float | int | str) -> float: 
        if isinstance(quantidade, str): quantidade = quantidade.replace(",", ".")
        try: quantidade_num = float(quantidade) 
        except ValueError: raise TypeError("A quantidade em estoque deve ser um número.")
        if quantidade_num < 0: raise ValueError("A quantidade em estoque não pode ser negativa.")
        return quantidade_num

    def _valida_custo_compra(self, valor: float | int | str) -> float:
        if isinstance(valor, str): valor = valor.replace(",", ".")
        try: valor_num = float(valor)
        except ValueError: raise TypeError("O custo de compra deve ser um número válido.")
        if valor_num < 0: raise ValueError("O custo de compra não pode ser negativo.")
        return valor_num

def buscar_produto(db: Session, nome_produto: str) -> Optional[Produto]:
    nome_busca_lower = nome_produto.lower().strip()
    return db.query(Produto).filter(func.lower(Produto._nome) == nome_busca_lower).first()

def buscar_produto_id(db: Session, id_produto: int) -> Optional[Produto]:
    return db.query(Produto).filter(Produto.id == id_produto).first()

def listar_produtos(db: Session) -> list[Produto]:
    return db.query(Produto).order_by(Produto.id).all()

def criar_produto(db: Session, nome: str, preco: float, estoque: float) -> Produto:
    produto_existente = buscar_produto(db, nome)
    if produto_existente:
        raise ValueError(f"Produto com o nome '{produto_existente.nome}' já existe.")

    novo_produto = Produto(nome=nome, preco=preco, estoque=estoque)
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto

def atualizar_dados_produto(db: Session, id_produto: int, **kwargs: Any) -> Produto:
    produto_existente = buscar_produto_id(db, id_produto)
    if not produto_existente:
        raise ValueError(f"Produto com ID {id_produto} não encontrado para atualização.")
    
    if 'nome' in kwargs:
        novo_nome = str(kwargs['nome']).strip()
        conflito = buscar_produto(db, novo_nome)
        if conflito and conflito.id != id_produto:
            raise ValueError(f"Não foi possível atualizar. Já existe um produto com o nome '{novo_nome}'.")

    for chave, valor in kwargs.items():
        if hasattr(produto_existente, chave):
            setattr(produto_existente, chave, valor)

    db.commit()
    db.refresh(produto_existente)
    return produto_existente

def deletar_produto(db: Session, id_produto: int) -> None:
    produto_a_deletar = buscar_produto_id(db, id_produto)
    if not produto_a_deletar:
        raise ValueError(f"Produto com ID {id_produto} não encontrado para exclusão.")
    
    db.delete(produto_a_deletar)
    db.commit()

def _formatar_produtos_para_tabela(db: Session, produtos: list[Produto]) -> str:
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

def _formatar_historico_para_tabela(historico: list) -> str:
    if not historico:
        return "Nenhum histórico de compras para este produto."
    
    cabecalhos = ["Data", "Quantidade", "Valor Unitário", "Fornecedor"]
    dados_tabela = []

    for registro in historico:
        dados_tabela.append([
            datetime.fromisoformat(registro["data"]).strftime("%d/%m/%Y"),
            registro["quantidade"],
            f"R${registro['valor_unitario']:.2f}",
            registro.get("fornecedor_nome", "N/A")
        ])
    
    return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
