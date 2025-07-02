from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import Session, validates
from tabulate import tabulate
from typing import Optional, Any, List

from database import Base
import info as mod_info

class Fornecedor(Base):
    __tablename__ = 'fornecedores'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True, index=True, nullable=False)
    
    telefone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    endereco_str = Column("endereco", String(255), nullable=False)
    redes_sociais = Column(String(255), nullable=True)

    def __init__(self, nome: str, cnpj: str, info_contato: mod_info.Informacao, **kwargs):
        self.nome = nome
        self.cnpj = cnpj
        self.info_contato = info_contato

    def __str__(self) -> str:
        return (f"ID: {self.id}, Nome: {self.nome}, CNPJ: {self.cnpj}\n"
                f"  Informações de Contato: {self.info_contato}")

    @property
    def info_contato(self) -> mod_info.Informacao:
        return mod_info.Informacao(
            telefone=self.telefone, #type: ignore
            email=self.email, #type: ignore
            endereco=self.endereco_str, #type: ignore
            redes_sociais=self.redes_sociais or "" #type: ignore
        )

    @info_contato.setter
    def info_contato(self, nova_info: mod_info.Informacao):
        if not isinstance(nova_info, mod_info.Informacao):
            raise TypeError("A informação de contato deve ser um objeto da classe Informacao.")
            
        self.telefone = nova_info.telefone
        self.email = nova_info.email
        self.redes_sociais = nova_info.redes_sociais
        
        endereco_dict = nova_info.endereco
        partes = [
            endereco_dict.get('nome_rua'),
            endereco_dict.get('numero'),
            endereco_dict.get('bairro'),
            endereco_dict.get('cidade'),
            endereco_dict.get('estado')
        ]
        self.endereco_str = ", ".join(filter(None, partes))

    @validates('nome')
    def validar_nome(self, key, nome_str):
        nome_limpo = nome_str.strip()
        if not nome_limpo:
            raise ValueError("O nome do fornecedor não pode ser vazio.")
        return nome_limpo

    @validates('cnpj')
    def validar_cnpj(self, key, cnpj_str):
        cnpj_limpo = "".join(filter(str.isdigit, cnpj_str))
        if not Fornecedor._eh_cnpj_valido(cnpj_limpo):
            raise ValueError("CNPJ inválido: Dígitos verificadores não correspondem ou padrão inválido.")
        
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"

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

# Funções de CRUD para Fornecedor

def buscar_fornecedor(db: Session, cnpj: str) -> Optional[Fornecedor]:
    try:
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        if len(cnpj_limpo) != 14: return None
        cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    except IndexError:
        return None
    return db.query(Fornecedor).filter(Fornecedor.cnpj == cnpj_formatado).first() #type: ignore

def buscar_fornecedor_id(db: Session, id_fornecedor: int) -> Optional[Fornecedor]:
    return db.query(Fornecedor).filter(Fornecedor.id == id_fornecedor).first()

def buscar_fornecedores_por_nome(db: Session, nome_parcial: str) -> List[Fornecedor]:
    nome_lower = f"%{nome_parcial.lower().strip()}%"
    return db.query(Fornecedor).filter(func.lower(Fornecedor.nome).like(nome_lower)).all()

def listar_fornecedores(db: Session) -> list[Fornecedor]:
    return db.query(Fornecedor).order_by(Fornecedor.id).all()

def criar_fornecedor(db: Session, nome: str, cnpj: str, info_contato: mod_info.Informacao) -> Fornecedor:
    if buscar_fornecedor(db, cnpj):
        raise ValueError(f"Fornecedor com CNPJ {cnpj} já existe.")

    novo_fornecedor = Fornecedor(nome=nome, cnpj=cnpj, info_contato=info_contato)
    db.add(novo_fornecedor)
    db.commit()
    db.refresh(novo_fornecedor)
    return novo_fornecedor

def atualizar_dados_fornecedor(db: Session, id_fornecedor: int, **kwargs: Any) -> Fornecedor:
    fornecedor_existente = buscar_fornecedor_id(db, id_fornecedor)
    if not fornecedor_existente:
        raise ValueError(f"Fornecedor com ID {id_fornecedor} não encontrado.")

    if 'cnpj' in kwargs:
        conflito = buscar_fornecedor(db, kwargs['cnpj'])
        if conflito and conflito.id != id_fornecedor: #type: ignore
            raise ValueError(f"Não é possível atualizar. Outro fornecedor já usa o CNPJ {kwargs['cnpj']}.")

    for chave, valor in kwargs.items():
        setattr(fornecedor_existente, chave, valor)

    db.commit()
    db.refresh(fornecedor_existente)
    return fornecedor_existente

def deletar_fornecedor(db: Session, id_fornecedor: int) -> None:
    fornecedor_a_deletar = buscar_fornecedor_id(db, id_fornecedor)
    if not fornecedor_a_deletar:
        raise ValueError(f"Fornecedor com ID {id_fornecedor} não encontrado.")
    db.delete(fornecedor_a_deletar)
    db.commit()

def _formatar_fornecedores_para_tabela(db: Session, fornecedores: list[Fornecedor]) -> str:
    if not fornecedores:
        return "Nenhum fornecedor para exibir."

    cabecalhos = ["ID", "Nome", "CNPJ"]
    dados_tabela = []
    for forn in fornecedores:
        dados_tabela.append([
            forn.id, forn.nome, forn.cnpj
        ])
    return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
