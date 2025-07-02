from sqlalchemy import Column, Integer, String, Float, func
from sqlalchemy.orm import Session, synonym
from tabulate import tabulate
from typing import Optional, Any

from database import Base

class Servico(Base):
    __tablename__ = 'servicos'

    id = Column(Integer, primary_key=True, index=True)
    _nome = Column("nome", String(255), unique=True, index=True, nullable=False)
    _valor_venda = Column("valor_venda", Float, nullable=False)
    _custo = Column("custo", Float, nullable=False)

    def __init__(self, nome: str, valor_venda: float, custo: float, **kwargs):
        self.nome = nome
        self.valor_venda = valor_venda
        self.custo = custo

    def __str__(self) -> str:
        return (f"Serviço ID: {self.id}, Nome: {self.nome}, Valor de Venda: R${self.valor_venda:.2f}, "
                f"Custo: R${self.custo:.2f}")

    def __repr__(self) -> str:
        return (f"Servico(id={self.id!r}, nome={self.nome!r}, "
                f"valor_venda={self.valor_venda!r}, custo={self.custo!r})")

    nome = synonym('_nome', descriptor=property(
        lambda self: self._nome,
        lambda self, nome_str: setattr(self, '_nome', self._validar_nome(nome_str))
    ))

    valor_venda = synonym('_valor_venda', descriptor=property(
        lambda self: self._valor_venda,
        lambda self, valor: setattr(self, '_valor_venda', self._validar_valor_venda(valor))
    ))

    custo = synonym('_custo', descriptor=property(
        lambda self: self._custo,
        lambda self, valor: setattr(self, '_custo', self._validar_custo(valor))
    ))

    def _validar_nome(self, nome_str: str) -> str:
        nome_limpo = nome_str.strip()
        if not nome_limpo:
            raise ValueError("O nome do serviço não pode ser vazio.")
        return nome_limpo

    def _validar_valor_venda(self, valor: float | int | str) -> float:
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        try:
            valor_num = float(valor)
        except ValueError:
            raise TypeError("O valor de venda deve ser um número válido.")
        if valor_num <= 0:
            raise ValueError("O valor de venda deve ser maior que zero.")
        return valor_num

    def _validar_custo(self, valor: float | int | str) -> float:
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        try:
            valor_num = float(valor)
        except ValueError:
            raise TypeError("O custo deve ser um número válido.")
        if valor_num <= 0:
            raise ValueError("O custo deve ser maior que zero.")
        return valor_num

def buscar_servico(db: Session, nome_servico: str) -> Optional[Servico]:
    nome_busca_lower = nome_servico.lower().strip()
    return db.query(Servico).filter(func.lower(Servico.nome) == nome_busca_lower).first()

def buscar_servico_id(db: Session, id_servico: int) -> Optional[Servico]:
    return db.query(Servico).filter(Servico.id == id_servico).first()

def listar_servicos(db: Session) -> list[Servico]:
    return db.query(Servico).order_by(Servico.id).all()

def criar_servico(db: Session, nome: str, valor_venda: float, custo: float) -> Servico:
    servico_existente = buscar_servico(db, nome)
    if servico_existente:
        raise ValueError(f"Serviço com o nome '{servico_existente.nome}' já existe.")

    novo_servico = Servico(nome=nome, valor_venda=valor_venda, custo=custo)
    db.add(novo_servico)
    db.commit()
    db.refresh(novo_servico)
    return novo_servico

def atualizar_dados_servico(db: Session, id_servico: int, **kwargs: Any) -> Servico:
    servico_existente = buscar_servico_id(db, id_servico)
    if not servico_existente:
        raise ValueError(f"Serviço com ID {id_servico} não encontrado para atualização.")
    
    if 'nome' in kwargs:
        novo_nome = str(kwargs['nome']).strip()
        conflito = buscar_servico(db, novo_nome)
        if conflito and conflito.id != id_servico: #type: ignore
            raise ValueError(f"Não foi possível atualizar. Já existe outro serviço com o nome '{novo_nome}'.")

    for chave, valor in kwargs.items():
        if hasattr(servico_existente, chave):
            setattr(servico_existente, chave, valor)

    db.commit()
    db.refresh(servico_existente)
    return servico_existente

def deletar_servico(db: Session, id_servico: int) -> None:
    servico_a_deletar = buscar_servico_id(db, id_servico)
    if not servico_a_deletar:
        raise ValueError(f"Serviço com ID {id_servico} não encontrado para exclusão.")
    
    db.delete(servico_a_deletar)
    db.commit()

def _formatar_servicos_para_tabela(db: Session, servicos: list[Servico]) -> str:
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
