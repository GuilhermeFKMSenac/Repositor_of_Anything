from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import validates
from datetime import date, datetime
import random
import re
from typing import Union
from database import Base

def analisar_data_flexivel(data_str: str, is_datetime: bool = False) -> Union[date, datetime]:
    padrao_data = r"(?P<dia>\d{1,2})[/\-\s]?(?P<mes>\d{1,2})[/\-\s]?(?P<ano>\d{2}(?:\d{2})?)"
    padrao_hora = r"(?:[\s]?(?P<hora>\d{1,2}):(?P<minuto>\d{1,2}))"

    padrao_completo_str = f"^{padrao_data}{padrao_hora}$" if is_datetime else f"^{padrao_data}$"

    padrao = re.compile(padrao_completo_str, re.VERBOSE)
    correspondencia = padrao.match(data_str.strip())

    if not correspondencia:
        raise ValueError(f"Formato de {'data/hora' if is_datetime else 'data'} inválido.")

    dia: int = int(correspondencia.group('dia'))
    mes: int = int(correspondencia.group('mes'))
    ano_str: str = correspondencia.group('ano')
    
    ano: int
    if len(ano_str) == 2:
        ano_atual = datetime.now().year
        prefixo_seculo = ano_atual // 100 * 100
        ano = prefixo_seculo + int(ano_str)
        if ano > ano_atual + 50:
            ano -= 100
    else:
        ano = int(ano_str)

    try:
        if is_datetime:
            hora = int(correspondencia.group('hora'))
            minuto = int(correspondencia.group('minuto'))
            return datetime(ano, mes, dia, hora, minuto)
        else:
            return date(ano, mes, dia)
    except ValueError as e:
        raise ValueError(f"Data inválida: {e}. Verifique dia, mês, ano e hora/minuto.")

def formatar_validar_nome_completo(nome_str: str) -> str:
    nome_limpo = nome_str.strip()
    if len(nome_limpo.split()) < 2:
        raise ValueError("O nome deve ser completo (pelo menos duas palavras).")
    return nome_limpo.title()

class Pessoa(Base):
    __tablename__ = 'pessoas'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    nascimento = Column(Date, nullable=False)
    cpf = Column(String(14), unique=True, index=True, nullable=False)
    tipo = Column(String(50))

    telefone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    endereco_str = Column("endereco", String(255), nullable=True)
    redes_sociais = Column(String(255), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'pessoa',
        'polymorphic_on': tipo
    }

    @property
    def idade(self) -> int:
        hoje = date.today()
        return hoje.year - self.nascimento.year - ((hoje.month, hoje.day) < (self.nascimento.month, self.nascimento.day))

    @validates('nome')
    def validar_nome_basico(self, key, nome_str):
        if not nome_str or not nome_str.strip():
            raise ValueError("O nome não pode ser vazio.")
        return nome_str

    @validates('nascimento')
    def validar_nascimento(self, key, nascimento_obj: date):
        if not isinstance(nascimento_obj, date):
             raise TypeError("Nascimento deve ser um objeto do tipo date.")
        hoje = date.today()
        idade_calculada = hoje.year - nascimento_obj.year - ((hoje.month, hoje.day) < (nascimento_obj.month, nascimento_obj.day))
        if idade_calculada > 110:
            raise ValueError("Idade excede o máximo permitido (110 anos).")
        if nascimento_obj > hoje:
            raise ValueError("Data de nascimento não pode ser no futuro.")
        return nascimento_obj

    @validates('cpf')
    def validar_cpf(self, key, cpf_str):
        cpf_limpo = "".join(filter(str.isdigit, cpf_str))
        if not Pessoa._eh_cpf_valido(cpf_limpo):
            raise ValueError("CPF inválido.")
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

    @staticmethod
    def _eh_cpf_valido(numeros_cpf: str) -> bool:
        if not numeros_cpf.isdigit() or len(numeros_cpf) != 11:
            return False
        if len(set(numeros_cpf)) == 1:
            return False
        
        soma_val: int = 0
        for i in range(9):
            soma_val += int(numeros_cpf[i]) * (10 - i)
        primeiro_verificador: int = 11 - (soma_val % 11)
        if primeiro_verificador > 9:
            primeiro_verificador = 0
        if primeiro_verificador != int(numeros_cpf[9]):
            return False
        
        soma_val = 0
        for i in range(10):
            soma_val += int(numeros_cpf[i]) * (11 - i)
        segundo_verificador: int = 11 - (soma_val % 11)
        if segundo_verificador > 9:
            segundo_verificador = 0
        return segundo_verificador == int(numeros_cpf[10])

def gerar_cpf_valido() -> str:
    nove_digitos = [str(random.randint(0, 9)) for _ in range(9)]
    soma_val = sum(int(nove_digitos[i]) * (10 - i) for i in range(9))
    primeiro_verificador = 11 - (soma_val % 11)
    if primeiro_verificador > 9: primeiro_verificador = 0
    
    dez_digitos = nove_digitos + [str(primeiro_verificador)]
    soma_val = sum(int(dez_digitos[i]) * (11 - i) for i in range(10))
    segundo_verificador = 11 - (soma_val % 11)
    if segundo_verificador > 9: segundo_verificador = 0

    cpf_final = "".join(dez_digitos + [str(segundo_verificador)])
    return cpf_final

def gerar_cnpj_valido() -> str:
    doze_digitos: list[str] = [str(random.randint(0, 9)) for _ in range(12)]

    soma_val1: int = 0
    multiplicadores1: list[int] = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for i in range(12):
        soma_val1 += int(doze_digitos[i]) * multiplicadores1[i]
    primeiro_dv: int = 11 - (soma_val1 % 11)
    if primeiro_dv > 9:
        primeiro_dv = 0

    treze_digitos: list[str] = doze_digitos + [str(primeiro_dv)]

    soma_val2: int = 0
    multiplicadores2: list[int] = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for i in range(13):
        soma_val2 += int(treze_digitos[i]) * multiplicadores2[i]
    segundo_dv: int = 11 - (soma_val2 % 11)
    if segundo_dv > 9:
        segundo_dv = 0

    cnpj_completo_digitos: str = "".join(doze_digitos + [str(primeiro_dv), str(segundo_dv)])
    
    return f"{cnpj_completo_digitos[:2]}.{cnpj_completo_digitos[2:5]}.{cnpj_completo_digitos[5:8]}/{cnpj_completo_digitos[8:12]}-{cnpj_completo_digitos[12:]}"
