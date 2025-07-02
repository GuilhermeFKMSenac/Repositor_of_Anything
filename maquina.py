from sqlalchemy import Column, Integer, String, Float, Enum
from sqlalchemy.orm import Session, validates
from tabulate import tabulate
from typing import Optional, Any
from enum import Enum as PyEnum

from database import Base

class StatusMaquina(PyEnum):
    OPERANDO = "Operando"
    MANUTENCAO = "Em Manutenção"
    BAIXADO = "Baixado"

class Maquina(Base):
    __tablename__ = 'maquinas'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    numero_serie = Column(String(100), unique=True, index=True, nullable=False)
    custo_aquisicao = Column(Float, nullable=False)
    status = Column(Enum(StatusMaquina), nullable=False)

    def __init__(self, nome: str, numero_serie: str, custo_aquisicao: float, status: StatusMaquina, **kwargs):
        self.nome = nome
        self.numero_serie = numero_serie
        self.custo_aquisicao = custo_aquisicao
        self.status = status

    @validates('nome', 'numero_serie')
    def validate_string_not_empty(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"{key.replace('_', ' ').capitalize()} não pode ser vazio.")
        return value.strip()

    @validates('custo_aquisicao')
    def validate_custo(self, key, value):
        if isinstance(value, str): value = value.replace(",", ".")
        try: valor_num = float(value)
        except (ValueError, TypeError): raise TypeError("Custo de aquisição deve ser um número.")
        if valor_num <= 0: raise ValueError("Custo de aquisição deve ser maior que zero.")
        return valor_num

    @validates('status')
    def validate_status(self, key, value):
        if isinstance(value, StatusMaquina):
            return value
        try:
            return StatusMaquina(value)
        except ValueError:
            raise ValueError(f"Status '{value}' inválido. Use um dos: {[s.value for s in StatusMaquina]}")

# Funções de CRUD para Maquina

def buscar_maquina_id(db: Session, id_maquina: int) -> Optional[Maquina]:
    return db.query(Maquina).filter(Maquina.id == id_maquina).first()

def buscar_maquina_serie(db: Session, numero_serie: str) -> Optional[Maquina]:
    return db.query(Maquina).filter(Maquina.numero_serie == numero_serie.strip()).first() #type: ignore

def listar_maquinas(db: Session) -> list[Maquina]:
    return db.query(Maquina).order_by(Maquina.id).all()

def criar_maquina(db: Session, nome: str, numero_serie: str, custo_aquisicao: float, status: StatusMaquina) -> Maquina:
    if buscar_maquina_serie(db, numero_serie):
        raise ValueError(f"Máquina com número de série '{numero_serie}' já existe.")
    nova_maquina = Maquina(nome=nome, numero_serie=numero_serie, custo_aquisicao=custo_aquisicao, status=status)
    db.add(nova_maquina)
    db.commit()
    db.refresh(nova_maquina)
    return nova_maquina

def atualizar_dados_maquina(db: Session, id_maquina: int, **kwargs: Any) -> Maquina:
    maquina_existente = buscar_maquina_id(db, id_maquina)
    if not maquina_existente:
        raise ValueError(f"Máquina com ID {id_maquina} não encontrada.")
    if 'numero_serie' in kwargs:
        conflito = buscar_maquina_serie(db, kwargs['numero_serie'])
        if conflito and conflito.id != id_maquina: #type: ignore
            raise ValueError(f"Outra máquina já usa o número de série '{kwargs['numero_serie']}'.")
    for chave, valor in kwargs.items():
        setattr(maquina_existente, chave, valor)
    db.commit()
    db.refresh(maquina_existente)
    return maquina_existente

def deletar_maquina(db: Session, id_maquina: int) -> None:
    maquina_a_deletar = buscar_maquina_id(db, id_maquina)
    if not maquina_a_deletar:
        raise ValueError(f"Máquina com ID {id_maquina} não encontrada.")
    db.delete(maquina_a_deletar)
    db.commit()

def _formatar_maquinas_para_tabela(db: Session, maquinas: list[Maquina]) -> str:
    cabecalhos = ["ID", "Nome", "Número de Série", "Custo Aquisição", "Status"]
    dados_tabela = []
    for maq in maquinas:
        dados_tabela.append([
            maq.id, maq.nome, maq.numero_serie, f"R${maq.custo_aquisicao:.2f}", maq.status.value
        ])
    return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")