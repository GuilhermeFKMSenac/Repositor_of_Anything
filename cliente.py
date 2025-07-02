from sqlalchemy import Column, Integer, ForeignKey, func
from sqlalchemy.orm import Session
from tabulate import tabulate
from typing import Optional, Any, List
from datetime import date

from pessoa import Pessoa
import info as mod_info

class Cliente(Pessoa):
    __tablename__ = 'clientes'

    id = Column(Integer, ForeignKey('pessoas.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'cliente',
    }

    def __init__(self, nome: str, nascimento_obj: date, cpf: str, info_contato: mod_info.Informacao, **kwargs):
        self.nome = nome
        self.nascimento = nascimento_obj
        self.cpf = cpf
        self.info_contato = info_contato

    @property
    def info_contato(self) -> mod_info.Informacao:
        return mod_info.Informacao(
            telefone=self.telefone,
            email=self.email,
            endereco=self.endereco_str,
            redes_sociais=self.redes_sociais or ""
        )

    @info_contato.setter
    def info_contato(self, nova_info: mod_info.Informacao):
        self.telefone = nova_info.telefone
        self.email = nova_info.email
        self.redes_sociais = nova_info.redes_sociais
        endereco_dict = nova_info.endereco
        partes = [endereco_dict.get(k) for k in ['nome_rua', 'numero', 'bairro', 'cidade', 'estado']]
        self.endereco_str = ", ".join(filter(None, partes))

# Funções de CRUD para Cliente

def buscar_cliente_id(db: Session, id_cliente: int) -> Optional[Cliente]:
    return db.query(Cliente).filter(Cliente.id == id_cliente).first()

def buscar_cliente_cpf(db: Session, cpf: str) -> Optional[Cliente]:
    try:
        cpf_limpo = "".join(filter(str.isdigit, cpf))
        cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    except IndexError:
        return None
    return db.query(Cliente).filter(Cliente.cpf == cpf_formatado).first()

def buscar_clientes_por_nome(db: Session, nome_parcial: str) -> List[Cliente]:
    nome_lower = f"%{nome_parcial.lower().strip()}%"
    return db.query(Cliente).filter(func.lower(Cliente.nome).like(nome_lower)).all()

def listar_clientes(db: Session) -> list[Cliente]:
    return db.query(Cliente).order_by(Cliente.id).all()

def criar_cliente(db: Session, nome: str, nascimento_obj: date, cpf: str, info_contato: mod_info.Informacao) -> Cliente:
    if buscar_cliente_cpf(db, cpf):
        raise ValueError(f"Cliente com CPF {cpf} já existe.")

    novo_cliente = Cliente(nome=nome, nascimento_obj=nascimento_obj, cpf=cpf, info_contato=info_contato)
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente

def atualizar_dados_cliente(db: Session, id_cliente: int, **kwargs: Any) -> Cliente:
    cliente_existente = buscar_cliente_id(db, id_cliente)
    if not cliente_existente:
        raise ValueError(f"Cliente com ID {id_cliente} não encontrado.")

    if 'cpf' in kwargs:
        conflito = buscar_cliente_cpf(db, kwargs['cpf'])
        if conflito and conflito.id != id_cliente: #type: ignore
            raise ValueError(f"Outro cliente já usa o CPF {kwargs['cpf']}.")

    for chave, valor in kwargs.items():
        setattr(cliente_existente, chave, valor)

    db.commit()
    db.refresh(cliente_existente)
    return cliente_existente

def deletar_cliente(db: Session, id_cliente: int) -> None:
    cliente_a_deletar = buscar_cliente_id(db, id_cliente)
    if not cliente_a_deletar:
        raise ValueError(f"Cliente com ID {id_cliente} não encontrado.")
    db.delete(cliente_a_deletar)
    db.commit()

def _formatar_clientes_para_tabela(db: Session, clientes: list) -> str:
    if not clientes:
        return "Nenhum cliente para exibir."

    cabecalhos = ["ID", "Nome", "CPF", "Nascimento", "Idade", "Telefone", "Email"]
    dados_tabela = []

    for cliente in clientes:
        dados_tabela.append([
            cliente.id, cliente.nome, cliente.cpf, cliente.nascimento.strftime('%d/%m/%Y'),
            cliente.idade, cliente.info_contato.telefone, cliente.info_contato.email
        ])
    return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
