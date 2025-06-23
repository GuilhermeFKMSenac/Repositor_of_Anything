import re
from datetime import date, datetime 
from typing import Union
import random

def gerar_cpf_valido() -> str:
    # Gera um número de CPF formatado e válido.
    nove_digitos: list[str] = [str(random.randint(0, 9)) for _ in range(9)]
    soma_val: int = 0
    for i in range(9):
        soma_val += int(nove_digitos[i]) * (10 - i)
    primeiro_verificador: int = 11 - (soma_val % 11)
    if primeiro_verificador > 9:
        primeiro_verificador = 0
    dez_digitos: list[str] = nove_digitos + [str(primeiro_verificador)]
    soma_val = 0
    for i in range(10):
        soma_val += int(dez_digitos[i]) * (11 - i)
    segundo_verificador: int = 11 - (soma_val % 11)
    if segundo_verificador > 9:
        segundo_verificador = 0

    digitos_cpf_final: str = "".join(nove_digitos + [str(primeiro_verificador), str(segundo_verificador)])
    return f"{digitos_cpf_final[:3]}.{digitos_cpf_final[3:6]}.{digitos_cpf_final[6:9]}-{digitos_cpf_final[9:]}"

def gerar_cnpj_valido() -> str:
    # Gera um número de CNPJ formatado e válido.
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

class Pessoa:
    # Classe base que representa uma pessoa física.
    def __init__(self, nome: str, nascimento: str, cpf: str):
        self.nome = nome
        self.nascimento = nascimento
        self.cpf = cpf

    def __str__(self) -> str:
        data_nascimento_exibicao: str = self._data_nascimento.strftime("%d/%m/%Y") if self._data_nascimento else "N/A"
        return (f"Nome: {self._nome}, Nascimento: {data_nascimento_exibicao}, "
                f"Idade: {self._idade} anos, CPF: {self._cpf}")

    def __repr__(self) -> str:
        return (f"Pessoa(nome={self._nome!r}, nascimento={self._data_nascimento!r}, "
                f"cpf={self._cpf!r})")

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, nome_str: str) -> None:
        nome_limpo: str = nome_str.strip()
        # A validação de nome foi flexibilizada para aceitar um único nome.
        if re.fullmatch(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$", nome_limpo) and len(nome_limpo.split()) >= 1:
            self._nome = nome_limpo
        else:
            raise ValueError("Formato de nome inválido. Deve conter apenas letras, hífens e espaços.")

    @property
    def nascimento(self) -> date:
        return self._data_nascimento

    @nascimento.setter
    def nascimento(self, nascimento_str: str) -> None:
        data_nascimento_obj = Pessoa._parse_data(nascimento_str, is_datetime=False)
        
        hoje: date = date.today()
        idade_calculada: int = hoje.year - data_nascimento_obj.year - ((hoje.month, hoje.day) < (data_nascimento_obj.month, data_nascimento_obj.day))

        if idade_calculada > 110:
            raise ValueError(f"Data de nascimento indica uma idade de {idade_calculada} anos, o que excede o máximo permitido (110 anos).")
        
        if data_nascimento_obj > hoje:
            raise ValueError("Data de nascimento não pode ser no futuro.")

        self._data_nascimento = data_nascimento_obj
        self._idade = idade_calculada

    @property
    def idade(self) -> int:
        return self._idade

    @property
    def cpf(self) -> str:
        return self._cpf
    
    @cpf.setter
    def cpf(self, cpf_str: str) -> None:
        padrao_validacao_cpf: re.Pattern = re.compile(r"^(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})$")

        if not padrao_validacao_cpf.match(cpf_str.strip()):
            raise ValueError("Formato de CPF inválido. Aceito: '999.999.999-99' ou '99999999999'.")
        
        cpf_limpo: str = re.sub(r'\D', '', cpf_str)

        if not Pessoa._eh_cpf_valido(cpf_limpo):
            raise ValueError("CPF inválido: Dígitos verificadores não correspondem ou padrão inválido (ex: todos os dígitos iguais).")

        cpf_formatado: str = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        
        self._cpf = cpf_formatado

    @staticmethod
    def _eh_cpf_valido(numeros_cpf: str) -> bool:
        # Valida os dígitos verificadores de um CPF.
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

    @staticmethod
    def _parse_data(data_str: str, is_datetime: bool = False) -> Union[date, datetime]:
        # Converte uma string de data (ou data/hora) em um objeto date ou datetime.
        padrao_data = r"(?P<dia>\d{1,2})[/\-\s]?(?P<mes>\d{1,2})[/\-\s]?(?P<ano>\d{2}(?:\d{2})?)"
        padrao_hora = r"(?:[\s]?(?P<hora>\d{1,2}):(?P<minuto>\d{1,2}))"

        padrao_completo_str = ""
        if is_datetime:
            padrao_completo_str = f"^{padrao_data}{padrao_hora}$"
        else:
            padrao_completo_str = f"^{padrao_data}$"

        padrao = re.compile(padrao_completo_str, re.VERBOSE)
        correspondencia = padrao.match(data_str.strip())

        if not correspondencia:
            raise ValueError(f"Formato de {'data/hora' if is_datetime else 'data'} inválido.")

        dia: int = int(correspondencia.group('dia'))
        mes: int = int(correspondencia.group('mes'))
        ano_str: str = correspondencia.group('ano')
        
        ano: int
        if len(ano_str) == 2:
            prefixo_ano_atual: int = datetime.now().year // 100 * 100
            ano = int(prefixo_ano_atual) + int(ano_str)
            if ano > datetime.now().year + 50:
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
