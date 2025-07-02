from sqlalchemy import Column, Integer, String, Float, JSON, func
from sqlalchemy.orm import Session, synonym
from tabulate import tabulate
from typing import Optional, Any
from datetime import datetime

from database import Base

class Suprimento(Base):
    __tablename__ = 'suprimentos'

    id = Column(Integer, primary_key=True, index=True)
    _nome = Column("nome", String(255), unique=True, index=True, nullable=False)
    _unidade_medida = Column("unidade_medida", String(50), nullable=False)
    _custo_unitario = Column("custo_unitario", Float, nullable=False)
    _estoque = Column("estoque", Float, nullable=False)
    _historico_custo_compra = Column("historico_custo_compra", JSON, nullable=True)

    def __init__(self, nome: str, unidade_medida: str, custo_unitario: float, estoque: float, **kwargs):
        self.nome = nome
        self.unidade_medida = unidade_medida
        self.custo_unitario = custo_unitario
        self.estoque = estoque
        self.historico_custo_compra = kwargs.get('historico_custo_compra', [])

    nome = synonym('_nome', descriptor=property(
        lambda self: self._nome,
        lambda self, valor: setattr(self, '_nome', self._validar_string_nao_vazia(valor))
    ))

    unidade_medida = synonym('_unidade_medida', descriptor=property(
        lambda self: self._unidade_medida,
        lambda self, valor: setattr(self, '_unidade_medida', self._validar_string_nao_vazia(valor))
    ))

    custo_unitario = synonym('_custo_unitario', descriptor=property(
        lambda self: self._custo_unitario,
        lambda self, valor: setattr(self, '_custo_unitario', self._validar_float_positivo(valor, 'custo_unitario'))
    ))

    estoque = synonym('_estoque', descriptor=property(
        lambda self: self._estoque,
        lambda self, valor: setattr(self, '_estoque', self._validar_float_positivo(valor, 'estoque'))
    ))

    historico_custo_compra = synonym('_historico_custo_compra', descriptor=property(
        lambda self: self._historico_custo_compra,
        lambda self, valor: setattr(self, '_historico_custo_compra', valor)
    ))

    def _validar_string_nao_vazia(self, valor_str: str) -> str:
        valor_limpo = valor_str.strip()
        if not valor_limpo:
            raise ValueError("O valor não pode ser vazio.")
        return valor_limpo

    def _validar_float_positivo(self, valor: Any, nome_campo: str) -> float:
        if isinstance(valor, str): valor = valor.replace(",", ".")
        try: valor_num = float(valor)
        except (ValueError, TypeError): raise TypeError(f"{nome_campo.replace('_', ' ')} deve ser um número válido.")
        
        min_val = 0 if nome_campo == 'estoque' else 0.01
        if valor_num < min_val:
            raise ValueError(f"{nome_campo.replace('_', ' ').capitalize()} deve ser maior ou igual a {min_val}.")
        return valor_num

def buscar_suprimento_id(db: Session, id_suprimento: int) -> Optional[Suprimento]:
    return db.query(Suprimento).filter(Suprimento.id == id_suprimento).first()

def buscar_suprimento_nome(db: Session, nome_suprimento: str) -> Optional[Suprimento]:
    return db.query(Suprimento).filter(func.lower(Suprimento._nome) == nome_suprimento.lower().strip()).first()

def listar_suprimentos(db: Session) -> list[Suprimento]:
    return db.query(Suprimento).order_by(Suprimento.id).all()

def criar_suprimento(db: Session, nome: str, unidade_medida: str, custo_unitario: float, estoque: float) -> Suprimento:
    if buscar_suprimento_nome(db, nome):
        raise ValueError(f"Suprimento com nome '{nome}' já existe.")
    novo_suprimento = Suprimento(nome=nome, unidade_medida=unidade_medida, custo_unitario=custo_unitario, estoque=estoque)
    db.add(novo_suprimento)
    db.commit()
    db.refresh(novo_suprimento)
    return novo_suprimento

def atualizar_dados_suprimento(db: Session, id_suprimento: int, **kwargs: Any) -> Suprimento:
    suprimento_existente = buscar_suprimento_id(db, id_suprimento)
    if not suprimento_existente:
        raise ValueError(f"Suprimento com ID {id_suprimento} não encontrado.")
    if 'nome' in kwargs:
        conflito = buscar_suprimento_nome(db, kwargs['nome'])
        if conflito and conflito.id != id_suprimento:
            raise ValueError(f"Outro suprimento já usa o nome '{kwargs['nome']}'.")
    for chave, valor in kwargs.items():
        setattr(suprimento_existente, chave, valor)
    db.commit()
    db.refresh(suprimento_existente)
    return suprimento_existente

def deletar_suprimento(db: Session, id_suprimento: int) -> None:
    suprimento_a_deletar = buscar_suprimento_id(db, id_suprimento)
    if not suprimento_a_deletar:
        raise ValueError(f"Suprimento com ID {id_suprimento} não encontrado.")
    db.delete(suprimento_a_deletar)
    db.commit()

def _formatar_suprimentos_para_tabela(db: Session, suprimentos: list[Suprimento]) -> str:
    cabecalhos = ["ID", "Nome", "Unidade", "Custo Unitário", "Estoque"]
    dados_tabela = []
    for sup in suprimentos:
        dados_tabela.append([
            sup.id, sup.nome, sup.unidade_medida, f"R${sup.custo_unitario:.2f}", f"{sup.estoque:.2f}"
        ])
    return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")

def _formatar_historico_para_tabela(historico: list) -> str:
    if not historico:
        return "Nenhum histórico de compras para este suprimento."
    
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
