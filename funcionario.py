from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, func
from sqlalchemy.orm import Session, validates
from tabulate import tabulate
from typing import Optional, Any, List
from datetime import date

from pessoa import Pessoa
import info as mod_info

class Funcionario(Pessoa):
    __tablename__ = 'funcionarios'

    id = Column(Integer, ForeignKey('pessoas.id'), primary_key=True)

    ctps = Column(String(20), nullable=False)
    salario = Column(Float, nullable=False)
    data_admissao = Column(Date, nullable=False)
    data_demissao = Column(Date, nullable=True)
    nis = Column(String(11), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'funcionario',
    }

    def __init__(self, nome: str, nascimento_obj: date, cpf: str, ctps: str,
                 informacao_contato: mod_info.Informacao, salario: float, data_admissao_obj: date,
                 data_demissao_obj: Optional[date] = None, nis: Optional[str] = None, **kwargs):
        self.nome = nome
        self.nascimento = nascimento_obj
        self.cpf = cpf
        self.ctps = ctps
        self.informacao_contato = informacao_contato
        self.salario = salario
        self.data_admissao = data_admissao_obj
        self.data_demissao = data_demissao_obj
        self.nis = nis

    @property
    def info_contato(self) -> mod_info.Informacao:
        return mod_info.Informacao(
            telefone=self.telefone, email=self.email,
            endereco=self.endereco_str, redes_sociais=self.redes_sociais or ""
        )

    @info_contato.setter
    def info_contato(self, nova_info: mod_info.Informacao):
        self.telefone = nova_info.telefone
        self.email = nova_info.email
        self.redes_sociais = nova_info.redes_sociais
        endereco_dict = nova_info.endereco
        partes = [endereco_dict.get(k) for k in ['nome_rua', 'numero', 'bairro', 'cidade', 'estado']]
        self.endereco_str = ", ".join(filter(None, partes))

    @validates('ctps')
    def validar_ctps(self, _, ctps_str):
        ctps_limpa:str = ctps_str.strip()
        if not ctps_limpa: raise ValueError("CTPS não pode ser vazia.")
        return ctps_limpa

    @validates('salario')
    def validar_salario(self, _, valor):
        if not isinstance(valor, (int, float)): raise TypeError("Salário deve ser um número.")
        if valor < 0: raise ValueError("Salário não pode ser negativo.")
        return float(valor)

    @validates('data_admissao')
    def validar_data_admissao(self, _, data_obj):
        if data_obj > date.today(): raise ValueError("Data de admissão não pode ser no futuro.")
        return data_obj

    @validates('data_demissao')
    def validar_data_demissao(self, _, data_obj):
        if data_obj and data_obj < self.data_admissao:
            raise ValueError("Data de demissão não pode ser anterior à data de admissão.")
        return data_obj

    @validates('nis')
    def validar_nis(self, _, nis_str):
        if nis_str is None or not nis_str.strip(): return None
        nis_limpo = "".join(filter(str.isdigit, nis_str))
        if len(nis_limpo) != 11: raise ValueError("NIS deve conter 11 dígitos.")
        return nis_limpo

# Funções de CRUD para Funcionario

def buscar_funcionario_por_cpf(db: Session, cpf: str) -> Optional[Funcionario]:
    try:
        cpf_limpo = "".join(filter(str.isdigit, cpf))
        cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    except IndexError: return None
    return db.query(Funcionario).filter(Funcionario.cpf == cpf_formatado).first()

def buscar_funcionario_por_id(db: Session, id_func: int) -> Optional[Funcionario]:
    return db.query(Funcionario).filter(Funcionario.id == id_func).first()

def buscar_funcionarios_por_nome(db: Session, nome_parcial: str) -> List[Funcionario]:
    nome_lower = f"%{nome_parcial.lower().strip()}%"
    return db.query(Funcionario).filter(func.lower(Funcionario.nome).like(nome_lower)).all()

def listar_funcionarios(db: Session) -> list[Funcionario]:
    return db.query(Funcionario).order_by(Funcionario.id).all()

def criar_funcionario(db: Session, **kwargs) -> Funcionario:
    if buscar_funcionario_por_cpf(db, kwargs['cpf']):
        raise ValueError(f"Funcionário com CPF {kwargs['cpf']} já existe.")
    
    novo_funcionario = Funcionario(**kwargs)
    db.add(novo_funcionario)
    db.commit()
    db.refresh(novo_funcionario)
    return novo_funcionario

def atualizar_dados_funcionario(db: Session, id_func: int, **kwargs: Any) -> Funcionario:
    func_existente = buscar_funcionario_por_id(db, id_func)
    if not func_existente:
        raise ValueError(f"Funcionário com ID {id_func} não encontrado.")

    if 'cpf' in kwargs:
        conflito = buscar_funcionario_por_cpf(db, kwargs['cpf'])
        if conflito and conflito.id != id_func:
            raise ValueError(f"Outro funcionário já usa o CPF {kwargs['cpf']}.")

    for chave, valor in kwargs.items():
        setattr(func_existente, chave, valor)

    db.commit()
    db.refresh(func_existente)
    return func_existente

def deletar_funcionario_por_id(db: Session, id_func: int) -> None:
    funcionario_a_deletar = buscar_funcionario_por_id(db, id_func)
    if not funcionario_a_deletar:
        raise ValueError(f"Funcionário com ID {id_func} não encontrado.")
    db.delete(funcionario_a_deletar)
    db.commit()

def _formatar_funcionarios_para_tabela(db: Session, funcionarios: list[Funcionario]) -> str:
    cabecalhos = ["ID", "Nome", "CPF", "Admissão", "Demissão", "Salário"]
    dados_tabela = []
    for func in funcionarios:
        dados_tabela.append([
            func.id, 
            func.nome, 
            func.cpf,
            func.data_admissao.strftime('%d/%m/%Y'),
            func.data_demissao.strftime('%d/%m/%Y') if func.data_demissao else "Não demitido",
            f"R${func.salario:.2f}",
        ])
    return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
