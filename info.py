import re
from typing import Dict, Optional

class Informacao:	
    def __init__(self, telefone: str, email: str, endereco: str, redes_sociais: str) -> None:
        self.telefone = telefone
        self.email = email
        self.endereco = endereco
        self.redes_sociais = redes_sociais

    def __str__(self) -> str:
        partes_endereco_str = []
        if hasattr(self, '_endereco') and self._endereco:
            endereco_principal = f"{self._endereco.get('nome_rua', '')}, {self._endereco.get('numero', '')}"
            partes_endereco_str.append(endereco_principal)

            bairro = self._endereco.get('bairro')
            cidade = self._endereco.get('cidade')
            estado = self._endereco.get('estado')
            if bairro and cidade and estado:
                endereco_opcional = f", {bairro}, {cidade}, {estado}"
                partes_endereco_str.append(endereco_opcional)
        
        endereco_exibicao = "".join(partes_endereco_str) if partes_endereco_str else "N/D"

        return (f"Telefone: {getattr(self, '_telefone', 'N/D')}, E-mail: {getattr(self, '_email', 'N/D')}, "
                f"Endereço: {endereco_exibicao}, Redes Sociais: {getattr(self, '_redes_sociais', 'N/D')}")

    @property
    def telefone(self) -> str:
        return self._telefone

    @telefone.setter
    def telefone(self, numero_telefone_str: Optional[str]) -> None:
        if not numero_telefone_str:
            self._telefone = ""
            return
        try:
            self._telefone = Informacao.validar_e_formatar_telefone(numero_telefone_str)
        except ValueError as e:
            raise e

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email_str: str) -> None:
        if not email_str:
            self._email = ""
            return
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_str):
            self._email = email_str
        else:
            raise ValueError("Formato de e-mail inválido.")

    @property
    def endereco(self) -> Dict[str, Optional[str]]:
        return self._endereco

    @endereco.setter
    def endereco(self, endereco_str: str) -> None:
        if not endereco_str:
            self._endereco = {}
            return
        padrao_endereco = re.compile(r"""
            ^\s*
            ([^,]+?)            
            \s*,\s*
            ([\w\s./-]+?)       
            (?:                 
                \s*,\s*
                ([^,]+?)            
                \s*,\s*
                ([^,]+?)            
                \s*,\s*
                ([A-Z]{2})          
            )?                  
            \s*$
        """, re.VERBOSE)

        correspondencia = padrao_endereco.match(endereco_str)

        if correspondencia:
            self._endereco = {
                "nome_rua": correspondencia.group(1).strip(),
                "numero": correspondencia.group(2).strip(),
                "bairro": correspondencia.group(3).strip() if correspondencia.group(3) else None,
                "cidade": correspondencia.group(4).strip() if correspondencia.group(4) else None,
                "estado": correspondencia.group(5).strip().upper() if correspondencia.group(5) else None
            }
        else:
            raise ValueError("Formato de endereço inválido. Esperado: 'Rua, número' ou 'Rua, número, bairro, cidade, UF'")

    @property
    def redes_sociais(self) -> str:
        return self._redes_sociais

    @redes_sociais.setter
    def redes_sociais(self, redes_sociais_str: str) -> None:
        if not redes_sociais_str:
            self._redes_sociais = ""
            return
        self._redes_sociais = redes_sociais_str.strip()

    DDDS_BRASIL = {
        "11", "12", "13", "14", "15", "16", "17", "18", "19",
        "21", "22", "24", "27", "28", "31", "32", "33", "34",
        "35", "37", "38", "41", "42", "43", "44", "45", "46",
        "47", "48", "49", "51", "53", "54", "55", "61", "62",
        "63", "64", "65", "66", "67", "68", "69", "71", "73",
        "74", "75", "77", "79", "81", "82", "83", "84", "85",
        "86", "87", "88", "89", "91", "92", "93", "94", "95",
        "96", "97", "98", "99"
    }

    @staticmethod
    def validar_e_formatar_telefone(numero_telefone_str: str) -> str:
        numeros_limpos = re.sub(r'\D', '', numero_telefone_str)

        if not (10 <= len(numeros_limpos) <= 13):
            raise ValueError("O número de telefone deve possuir de 10 a 13 dígitos, incluindo DDI e DDD, sem contar espaços e caracteres especiais [ Ex: + e () ]")

        if len(numeros_limpos) >= 12 and numeros_limpos.startswith('55'):
            ddd = numeros_limpos[2:4]
            numero_local = numeros_limpos[4:]
            if ddd not in Informacao.DDDS_BRASIL:
                raise ValueError(f"DDD brasileiro '{ddd}' inválido.")
            
            if len(numero_local) == 9: # Celular
                return f"+55 ({ddd}) {numero_local[0:5]}-{numero_local[5:]}"
            elif len(numero_local) == 8: # Fixo
                return f"+55 ({ddd}) {numero_local[0:4]}-{numero_local[4:]}"
            else:
                raise ValueError("Número brasileiro após DDI +55 e DDD deve ter 8 ou 9 dígitos.")

        elif len(numeros_limpos) in [10, 11]:
            ddd = numeros_limpos[0:2]
            numero_local = numeros_limpos[2:]
            if ddd not in Informacao.DDDS_BRASIL:
                raise ValueError(f"DDD brasileiro '{ddd}' inválido.")
            
            if len(numero_local) == 9: # Celular
                return f"({ddd}) {numero_local[0:5]}-{numero_local[5:]}"
            elif len(numero_local) == 8: # Fixo
                return f"({ddd}) {numero_local[0:4]}-{numero_local[4:]}"
            else:
                 raise ValueError("Número brasileiro após DDD deve ter 8 ou 9 dígitos.")
        
        else:
            return f"+{numeros_limpos}"
