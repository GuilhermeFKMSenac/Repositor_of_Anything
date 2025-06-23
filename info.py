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
        if self._endereco:
            endereco_principal = f"{self._endereco['nome_rua']}, {self._endereco['numero']}"
            partes_endereco_str.append(endereco_principal)

            if self._endereco['bairro'] and self._endereco['cidade'] and self._endereco['estado']:
                endereco_opcional = (
                    f", {self._endereco['bairro']}, {self._endereco['cidade']}, {self._endereco['estado']}"
                )
                partes_endereco_str.append(endereco_opcional)
        
        endereco_exibicao = "".join(partes_endereco_str) if partes_endereco_str else "N/D"

        return (f"Telefone: {self._telefone}, E-mail: {self._email}, "
                f"Endereço: {endereco_exibicao}, Redes Sociais: {self._redes_sociais if self._redes_sociais else 'N/D'}")

    def __repr__(self) -> str:
        return (f"Informacao(telefone={self._telefone!r}, email={self._email!r}, "
                f"endereco={self._endereco!r}, redes_sociais={self._redes_sociais!r})")

    @property
    def telefone(self) -> str:
        return self._telefone

    @telefone.setter
    def telefone(self, numero_telefone_str: str) -> None:
        try:
            self._telefone = Informacao.validar_e_formatar_telefone_brasileiro(numero_telefone_str)
        except ValueError as e:
            raise e

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email_str: str) -> None:
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_str):
            self._email = email_str
        else:
            raise ValueError("Formato de e-mail inválido.")

    @property
    def endereco(self) -> Dict[str, Optional[str]]:
        return self._endereco

    @endereco.setter
    def endereco(self, endereco_str: str) -> None:
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
            nome_rua = correspondencia.group(1).strip()
            numero = correspondencia.group(2).strip()
            bairro = correspondencia.group(3).strip() if correspondencia.group(3) else None
            cidade = correspondencia.group(4).strip() if correspondencia.group(4) else None
            estado = correspondencia.group(5).strip().upper() if correspondencia.group(5) else None

            self._endereco = {
                "nome_rua": nome_rua,
                "numero": numero,
                "bairro": bairro,
                "cidade": cidade,
                "estado": estado
            }
        else:
            raise ValueError("Formato de endereço inválido. Esperado: 'Nome da rua, número' ou 'Nome da rua, número, bairro, cidade, estado'")

    @property
    def redes_sociais(self) -> str:
        return self._redes_sociais

    @redes_sociais.setter
    def redes_sociais(self, redes_sociais_str: str) -> None:
        self._redes_sociais = redes_sociais_str.strip()

    DDDS = {
        "11", "12", "13", "14", "15", "16", "17", "18", "19",
        "21", "22", "24",
        "27", "28",
        "31", "32", "33", "34", "35", "37", "38",
        "41", "42", "43", "44", "45", "46",
        "47", "48", "49",
        "51", "53", "54", "55",
        "61", "62", "63", "64", "65", "66", "67", "68", "69",
        "71", "73", "74", "75", "77", "79",
        "81", "82", "83", "84", "85", "88", "89", "86", "87",
        "91", "92", "93", "94", "95", "96", "97", "98", "99"
    }

    @staticmethod
    def _validar_e_formatar_numero_brasileiro_local(numero_str: str) -> str:
        numero_totalmente_limpo = re.sub(r'\D', '', numero_str)

        if not numero_totalmente_limpo:
            raise ValueError("Formato de número de telefone brasileiro inválido.")

        ddd_identificado = ""
        numero_sem_ddd = ""
        ddd_foi_extraido_com_zero_inicial = False

        # 1. Tenta extrair DDD considerando um '0' inicial no número original
        if numero_str.strip().startswith('0') and len(numero_totalmente_limpo) >= 3:
            # O DDD candidato aqui é o que vem depois do '0'
            ddd_candidato_apos_zero = numero_totalmente_limpo[1:3]
            if ddd_candidato_apos_zero.startswith('0') or ddd_candidato_apos_zero.endswith('0'):
                raise ValueError(f"Número brasileiro inválido: DDD '{ddd_candidato_apos_zero}' inválido (não pode começar ou terminar com 0).")
            if ddd_candidato_apos_zero in Informacao.DDDS:
                ddd_identificado = ddd_candidato_apos_zero
                numero_sem_ddd = numero_totalmente_limpo[3:]
                ddd_foi_extraido_com_zero_inicial = True
            # Se não for um DDD válido após o '0', a lógica abaixo tentará sem o '0'

        # 2. Se não foi extraído com '0' inicial, ou se não começou com '0'
        if not ddd_foi_extraido_com_zero_inicial:
            if len(numero_totalmente_limpo) >= 2:
                ddd_candidato_normal = numero_totalmente_limpo[:2]
                # Verifica se o DDD candidato normal (sem '0' na frente) é problemático
                if ddd_candidato_normal.startswith('0') or ddd_candidato_normal.endswith('0'):
                    # Esta condição só deve ser atingida se o número original não começou com '0'
                    # mas o DDD extraído é tipo "0X" ou "X0", o que é raro, mas possível se a entrada for "01xxxx" sem o zero inicial no numero_str.
                    # Para o caso "01 9...", a primeira lógica já pegaria.
                    raise ValueError(f"Número brasileiro inválido: DDD '{ddd_candidato_normal}' inválido (não pode começar ou terminar com 0).")

                if ddd_candidato_normal in Informacao.DDDS:
                    ddd_identificado = ddd_candidato_normal
                    numero_sem_ddd = numero_totalmente_limpo[2:]
                # else: ddd_identificado permanece vazio
            # else: ddd_identificado permanece vazio

        # 3. Validação final do DDD e do número
        if not ddd_identificado: # Não conseguiu extrair um DDD válido
            # Se o número é muito curto para ter DDD + número mínimo
            if len(numero_totalmente_limpo) < 10: # (2 para DDD + 8 para número)
                raise ValueError("Número nacional inválido: Formato ou comprimento não reconhecido.")
            else: # Tem comprimento, mas o DDD não foi reconhecido
                raise ValueError(f"Número brasileiro inválido: DDD '{numero_totalmente_limpo[:2]}' não reconhecido.")

        if not (len(numero_sem_ddd) == 8 or len(numero_sem_ddd) == 9):
            raise ValueError("Número nacional inválido: Deve ter 8 ou 9 dígitos após o DDD.")

        if len(numero_sem_ddd) == 9:
            if not numero_sem_ddd.startswith(('6', '7', '8', '9')):
                raise ValueError("Número brasileiro inválido: Celular de 9 dígitos deve começar com 6, 7, 8 ou 9.")
            return f"{ddd_identificado} {numero_sem_ddd[0]} {numero_sem_ddd[1:5]} {numero_sem_ddd[5:]}"
        elif len(numero_sem_ddd) == 8:
            if numero_sem_ddd.startswith(('6', '7', '8', '9')):
                raise ValueError("Número brasileiro inválido: Fixo de 8 dígitos não pode começar com 6, 7, 8 ou 9 (parece celular incompleto).")
            return f"{ddd_identificado} {numero_sem_ddd[:4]} {numero_sem_ddd[4:]}"

        # Fallback, teoricamente não alcançável se a lógica acima estiver correta
        raise ValueError("Número nacional inválido: Erro inesperado na formatação.")
    
    @staticmethod
    def validar_e_formatar_telefone_brasileiro(numero_telefone_str: str) -> str:
       padrao_global = re.compile(r"""
           ^
           (?P<ddi_prefix>\+\d{1,3}[\s.]*)? 
           (?P<remaining_number>.*)         
           $
       """, re.VERBOSE)
   
       match = padrao_global.match(numero_telefone_str.strip())
       if not match:
           raise ValueError("Formato de número de telefone brasileiro inválido.")
   
       ddi_prefixo_capturado = match.group('ddi_prefix')
       numero_restante = match.group('remaining_number').strip()

       if not numero_restante:
           if ddi_prefixo_capturado:
               return f"+{re.sub(r'\D', '', ddi_prefixo_capturado)} {numero_restante}".strip()
           else:
               raise ValueError("Formato de número de telefone brasileiro inválido.")

       if ddi_prefixo_capturado:
           ddi_limpo = re.sub(r'\D', '', ddi_prefixo_capturado)
           if ddi_limpo == '55':
               return Informacao._validar_e_formatar_numero_brasileiro_local(numero_restante)
           else:
               return f"+{ddi_limpo} {numero_restante}"
       else:
           return Informacao._validar_e_formatar_numero_brasileiro_local(numero_restante)

if __name__ == "__main__":
    pass
