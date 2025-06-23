from typing import Optional, Any, Union
from datetime import datetime
from enum import Enum
import funcionario as mod_funcionario
import cliente as mod_cliente
import servico
import produto
import pessoa
import suprimento as mod_suprimento
import maquina as mod_maquina
from tabulate import tabulate

class AgendaStatus(Enum):   
    # Enum para os status possíveis de uma agenda. Renomeado de StatusAgenda.
    AGENDADO = "Agendado"
    REALIZADO = "Realizado"
    NAO_REALIZADO = "Não Realizado"

    def __str__(self):
        return self.value

    @staticmethod
    def de_string(s: str) -> 'AgendaStatus':
        # Converte uma string para um membro do Enum AgendaStatus.
        s_norm = s.strip().upper().replace(" ", "_").replace("Ã", "A").replace("Õ", "O").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace("Ç", "C")

        for membro in AgendaStatus:
            if membro.name == s_norm:
                return membro

        for membro in AgendaStatus:
            valor_membro_norm = membro.value.strip().upper().replace(" ", "_").replace("Ã", "A").replace("Õ", "O").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace("Ç", "C")
            if valor_membro_norm == s_norm:
                return membro

        raise ValueError(f"Status '{s}' inválido. Valores aceitos: {[s.value for s in AgendaStatus]}")

class ItemAgendado:
    # Representa um serviço ou produto dentro de um agendamento.
    def __init__(self, item: Union[servico.Servico, produto.Produto], quantidade: float, valor_negociado: Optional[float] = None) -> None:
        if not isinstance(item, (servico.Servico, produto.Produto)):
            raise TypeError("O item agendado deve ser uma instância de Servico ou Produto.")

        if not isinstance(quantidade, (int, float)) or quantidade <= 0:
            raise ValueError("A quantidade do item agendado deve ser um número maior que zero.")

        self._item = item
        self._quantidade = float(quantidade)

        if valor_negociado is None:
            if isinstance(item, servico.Servico):
                self._valor_negociado = item.valor_venda
            elif isinstance(item, produto.Produto):
                self._valor_negociado = item.preco
        else:
            if not isinstance(valor_negociado, (int, float)) or valor_negociado <= 0:
                raise ValueError("O valor negociado deve ser um número maior que zero.")
            self._valor_negociado = float(valor_negociado)

        self._subtotal = self._quantidade * self._valor_negociado

    def __str__(self) -> str:
        tipo_item = "Serviço" if isinstance(self._item, servico.Servico) else "Produto"
        return (f"{tipo_item}: {self._item.nome} (Qtd: {self._quantidade:.2f}, "
                f"Valor Neg.: R${self._valor_negociado:.2f}, Subtotal: R${self._subtotal:.2f})")

    def __repr__(self) -> str:
        return (f"ItemAgendado(item={self._item.nome!r}, quantidade={self._quantidade!r}, "
                f"valor_negociado={self._valor_negociado!r})")

    @property
    def item(self) -> Union[servico.Servico, produto.Produto]:
        return self._item

    @property
    def quantidade(self) -> float:
        return self._quantidade

    @property
    def valor_negociado(self) -> float:
        return self._valor_negociado

    @property
    def subtotal(self) -> float:
        return self._subtotal

    def atualizar_quantidade(self, nova_quantidade: float) -> None:
        if not isinstance(nova_quantidade, (int, float)) or nova_quantidade <= 0:
            raise ValueError("A nova quantidade deve ser um número maior que zero.")
        self._quantidade = float(nova_quantidade)
        self._subtotal = self._quantidade * self._valor_negociado

    def atualizar_valor_negociado(self, novo_valor: float) -> None:
        if not isinstance(novo_valor, (int, float)) or novo_valor <= 0:
            raise ValueError("O novo valor negociado deve ser um número maior que zero.")
        self._valor_negociado = float(novo_valor)
        self._subtotal = self._quantidade * self._valor_negociado

class SuprimentoAgendado:
    # Representa um suprimento e sua quantidade a ser usada em um agendamento.
    def __init__(self, suprimento: mod_suprimento.Suprimento, quantidade: float) -> None:
        if not isinstance(suprimento, mod_suprimento.Suprimento):
            raise TypeError("O suprimento agendado deve ser uma instância de Suprimento.")

        if not isinstance(quantidade, (int, float)) or quantidade <= 0:
            raise ValueError("A quantidade do suprimento agendado deve ser um número maior que zero.")

        self._suprimento = suprimento
        self._quantidade = float(quantidade)

    def __str__(self) -> str:
        return (f"Suprimento: {self._suprimento.nome} (Qtd: {self._quantidade:.2f} {self._suprimento.unidade_medida}, "
                f"Custo Unit.: R${self._suprimento.custo_unitario:.2f})")

    def __repr__(self) -> str:
        return (f"SuprimentoAgendado(suprimento={self._suprimento.nome!r}, quantidade={self._quantidade!r})")

    @property
    def suprimento(self) -> mod_suprimento.Suprimento:
        return self._suprimento

    @property
    def quantidade(self) -> float:
        return self._quantidade

    def atualizar_quantidade(self, nova_quantidade: float) -> None:
        if not isinstance(nova_quantidade, (int, float)) or nova_quantidade <= 0:
            raise ValueError("A nova quantidade deve ser um número maior que zero.")
        self._quantidade = float(nova_quantidade)

class Agenda:
    # Gerencia os agendamentos de serviços.
    _agendas_por_id: dict[int, 'Agenda'] = {}
    _proximo_id_disponivel: int = 1

    def __init__(self, id_agenda: Optional[int], funcionario_obj: mod_funcionario.Funcionario, 
                 cliente_obj: mod_cliente.Cliente, data_hora_inicio: str, data_hora_fim: str, 
                 itens_agendados: list[ItemAgendado], comentario: Optional[str] = None,
                 maquinas_agendadas: Optional[list[mod_maquina.Maquina]] = None,
                 suprimentos_utilizados: Optional[list[SuprimentoAgendado]] = None,
                 status: Union[str, AgendaStatus] = AgendaStatus.AGENDADO
                 ) -> None:

        if id_agenda is None:
            self._id = Agenda._proximo_id_disponivel
        else:
            if not isinstance(id_agenda, int) or id_agenda <= 0:
                raise ValueError("O ID da agenda deve ser um número inteiro positivo.")
            self._id = id_agenda

        status_inicial_resolvido: AgendaStatus
        if isinstance(status, str):
            try:
                status_inicial_resolvido = AgendaStatus.de_string(status)
            except ValueError as e:
                raise ValueError(f"Status inicial inválido: {e}")
        elif isinstance(status, AgendaStatus):
            status_inicial_resolvido = status
        else:
            raise TypeError("O status inicial deve ser um membro de AgendaStatus ou uma string válida.")

        self._status = status_inicial_resolvido

        if not isinstance(funcionario_obj, mod_funcionario.Funcionario):
            raise TypeError("O funcionário da agenda deve ser uma instância da classe Funcionario.")
        if not isinstance(cliente_obj, mod_cliente.Cliente):
            raise TypeError("O cliente da agenda deve ser uma instância da classe Cliente.")

        if not isinstance(itens_agendados, list) or not itens_agendados:
            raise ValueError("A agenda deve conter pelo menos um item agendado na lista.")
        for item in itens_agendados:
            if not isinstance(item, ItemAgendado):
                raise TypeError("Todos os itens na lista 'itens_agendados' devem ser instâncias de ItemAgendado.")

        self._maquinas_agendadas = []
        if maquinas_agendadas:
            if not isinstance(maquinas_agendadas, list):
                raise TypeError("As máquinas agendadas devem ser fornecidas como uma lista de Maquina.")
            for maq in maquinas_agendadas:
                if not isinstance(maq, mod_maquina.Maquina):
                    raise TypeError("Todos os itens na lista 'maquinas_agendadas' devem ser instâncias de Maquina.")
                if maq.status != mod_maquina.StatusMaquina.OPERANDO:
                    raise ValueError(f"Máquina '{maq.nome}' (Série: {maq.numero_serie}) não está em status 'Operando' e não pode ser agendada.")
            self._maquinas_agendadas.extend(maquinas_agendadas)

        self._suprimentos_utilizados = []
        if suprimentos_utilizados:
            if not isinstance(suprimentos_utilizados, list):
                raise TypeError("Os suprimentos utilizados devem ser fornecidos como uma lista de SuprimentoAgendado.")
            for sup_ag in suprimentos_utilizados:
                if not isinstance(sup_ag, SuprimentoAgendado):
                    raise TypeError("Todos os itens na lista 'suprimentos_utilizados' devem ser instâncias de SuprimentoAgendado.")
                if status_inicial_resolvido == AgendaStatus.AGENDADO and sup_ag.suprimento.estoque < sup_ag.quantidade:
                     raise ValueError(f"Estoque insuficiente para o suprimento '{sup_ag.suprimento.nome}' ao AGENDAR. Disponível: {sup_ag.suprimento.estoque}, Necessário: {sup_ag.quantidade}.")
            self._suprimentos_utilizados.extend(suprimentos_utilizados)

        self._funcionario = funcionario_obj
        self._cliente = cliente_obj
        self._comentario = comentario.strip() if comentario else None
        self._itens_agendados = []
        self._valor_total = 0.0

        self.data_hora_inicio = data_hora_inicio
        self.data_hora_fim = data_hora_fim

        if Agenda.buscar_agenda(self.id) is not None:
            raise ValueError(f"Já existe uma agenda com o ID {self.id}.")

        if Agenda._verificar_conflito(self.funcionario, self.cliente, self.maquinas_agendadas,
                                      self.data_hora_inicio, self.data_hora_fim, self.id):
             raise ValueError("Conflito de horário: Funcionário, Cliente ou Máquina já possui agendamento neste período.")

        self.adicionar_itens(itens_agendados)

        Agenda._agendas_por_id[self.id] = self

        if id_agenda is None:
            Agenda._proximo_id_disponivel += 1
        elif self.id >= Agenda._proximo_id_disponivel:
            Agenda._proximo_id_disponivel = self.id + 1

        if status_inicial_resolvido == AgendaStatus.REALIZADO:
            if self.data_hora_fim < datetime.now(): 
                self._deduzir_estoque_realizacao()

    def __str__(self) -> str:
        itens_str = "\n    ".join([str(item) for item in self._itens_agendados])
        maquinas_str = "\n    ".join([f"Máquina: {m.nome} (Série: {m.numero_serie})" for m in self._maquinas_agendadas]) if self._maquinas_agendadas else "Nenhuma"
        suprimentos_str = "\n    ".join([str(s) for s in self._suprimentos_utilizados]) if self._suprimentos_utilizados else "Nenhum"
        comentario_str = f"\n  Comentário: {self._comentario}" if self._comentario else ""

        return (f"Agenda ID: {self._id}, Início: {self._data_hora_inicio.strftime('%d/%m/%Y %H:%M')}, "
                f"Fim: {self._data_hora_fim.strftime('%d/%m/%Y %H:%M')}, Status: {self._status}\n"
                f"  Funcionário: {self._funcionario.nome} (CPF: {self._funcionario.cpf}, ID: {self._funcionario.id})\n"
                f"  Cliente: {self._cliente.nome} (CPF: {self._cliente.cpf}, ID: {self._cliente.id})\n"
                f"  Itens Agendados (Serviços/Produtos):\n    {itens_str}\n"
                f"  Máquinas Agendadas:\n    {maquinas_str}\n"
                f"  Suprimentos a Utilizar:\n    {suprimentos_str}\n"
                f"  Valor Total: R${self._valor_total:.2f}{comentario_str}")

    def __repr__(self) -> str:
        maquinas_repr_ids = [m.id for m in self._maquinas_agendadas]
        suprimentos_repr = [(s.suprimento.id, s.quantidade) for s in self._suprimentos_utilizados]
        return (f"Agenda(id_agenda={self._id!r}, funcionario_obj={self._funcionario.cpf!r}, "
                f"cliente_obj={self._cliente.cpf!r}, data_hora_inicio={self._data_hora_inicio!r}, "
                f"data_hora_fim={self._data_hora_fim!r}, "
                f"itens_agendados_count={len(self._itens_agendados)!r}, "
                f"maquinas_agendadas_ids={maquinas_repr_ids!r}, "
                f"suprimentos_utilizados_data={suprimentos_repr!r}, "
                f"status={self._status.name!r}, "
                f"comentario={self._comentario!r})")

    @property
    def id(self) -> int:
        return self._id

    @property
    def funcionario(self) -> mod_funcionario.Funcionario:
        return self._funcionario

    @funcionario.setter
    def funcionario(self, novo_funcionario: mod_funcionario.Funcionario) -> None:
        if not isinstance(novo_funcionario, mod_funcionario.Funcionario):
            raise TypeError("O funcionário deve ser uma instância da classe Funcionario.")
        self._funcionario = novo_funcionario

    @property
    def cliente(self) -> mod_cliente.Cliente:
        return self._cliente

    @cliente.setter
    def cliente(self, novo_cliente: mod_cliente.Cliente) -> None:
        if not isinstance(novo_cliente, mod_cliente.Cliente):
            raise TypeError("O cliente deve ser uma instância da classe Cliente.")
        self._cliente = novo_cliente

    @property
    def data_hora_inicio(self) -> datetime:
        return self._data_hora_inicio #type: ignore[return-value]

    @data_hora_inicio.setter
    def data_hora_inicio(self, dh_inicio_str: str) -> None:
        try:
            self._data_hora_inicio = pessoa.Pessoa._parse_data(dh_inicio_str, is_datetime=True)
        except ValueError as e:
            raise ValueError(f"Data/hora de início inválida: {e}")

    @property
    def data_hora_fim(self) -> datetime:
        return self._data_hora_fim #type: ignore[return-value]

    @data_hora_fim.setter
    def data_hora_fim(self, dh_fim_str: str) -> None:
        try:
            dh_fim_obj = pessoa.Pessoa._parse_data(dh_fim_str, is_datetime=True)
        except ValueError as e:
            raise ValueError(f"Data/hora de fim inválida: {e}")

        if not hasattr(self, '_data_hora_inicio'):
            raise RuntimeError("Defina a data/hora de início antes da data/hora de fim.")

        if dh_fim_obj <= self._data_hora_inicio:
            raise ValueError("A data/hora de fim deve ser posterior à data/hora de início.")

        self._data_hora_fim = dh_fim_obj

    @property
    def itens_agendados(self) -> list[ItemAgendado]:
        return list(self._itens_agendados)

    @property
    def maquinas_agendadas(self) -> list[mod_maquina.Maquina]:
        return list(self._maquinas_agendadas)

    @maquinas_agendadas.setter
    def maquinas_agendadas(self, novas_maquinas: list[mod_maquina.Maquina]) -> None:
        if not isinstance(novas_maquinas, list):
            raise TypeError("A lista de máquinas agendadas deve ser uma lista de instâncias de Maquina.")
        for maq in novas_maquinas:
            if not isinstance(maq, mod_maquina.Maquina):
                raise TypeError("Todos os itens na lista 'maquinas_agendadas' devem ser instâncias de Maquina.")
            if maq.status != mod_maquina.StatusMaquina.OPERANDO:
                raise ValueError(f"Máquina '{maq.nome}' (Série: {maq.numero_serie}) não está em status 'Operando' e não pode ser agendada.")
        self._maquinas_agendadas = list(novas_maquinas)

    @property
    def suprimentos_utilizados(self) -> list[SuprimentoAgendado]:
        return list(self._suprimentos_utilizados)

    @suprimentos_utilizados.setter
    def suprimentos_utilizados(self, novos_suprimentos: list[SuprimentoAgendado]) -> None:
        if not isinstance(novos_suprimentos, list):
            raise TypeError("A lista de suprimentos utilizados deve ser uma lista de instâncias de SuprimentoAgendado.")
        for sup_ag in novos_suprimentos:
            if not isinstance(sup_ag, SuprimentoAgendado):
                raise TypeError("Todos os itens na lista 'suprimentos_utilizados' devem ser instâncias de SuprimentoAgendado.")

            if self._status != AgendaStatus.REALIZADO and sup_ag.suprimento.estoque < sup_ag.quantidade:
                raise ValueError(f"Estoque insuficiente para o suprimento '{sup_ag.suprimento.nome}'. Disponível: {sup_ag.suprimento.estoque}, Necessário: {sup_ag.quantidade}.")
        self._suprimentos_utilizados = list(novos_suprimentos)

    @property
    def status(self) -> AgendaStatus:
        return self._status

    @status.setter
    def status(self, novo_status: Union[str, AgendaStatus]) -> None:
        if isinstance(novo_status, str):
            self._status = AgendaStatus.de_string(novo_status)
        elif isinstance(novo_status, AgendaStatus):
            self._status = novo_status
        else:
            raise TypeError("O status deve ser um membro de AgendaStatus ou uma string válida.")

    @property
    def valor_total(self) -> float:
        return self._valor_total

    @property
    def comentario(self) -> Optional[str]:
        return self._comentario

    @comentario.setter
    def comentario(self, novo_comentario: Optional[str]) -> None:
        self._comentario = novo_comentario.strip() if novo_comentario else None

    def _recalcular_valor_total(self) -> None:
        self._valor_total = sum(item.subtotal for item in self._itens_agendados)

    def adicionar_itens(self, novos_itens: list[ItemAgendado]) -> None:
        if not isinstance(novos_itens, list):
            raise TypeError("Os novos itens devem ser fornecidos como uma lista de ItemAgendado.")
        for item in novos_itens:
            if not isinstance(item, ItemAgendado):
                raise TypeError("Cada item na lista deve ser uma instância de ItemAgendado.")
            self._itens_agendados.append(item)
        self._recalcular_valor_total()

    def remover_item(self, indice_item: int) -> None:
        if not isinstance(indice_item, int) or indice_item < 0 or indice_item >= len(self._itens_agendados):
            raise IndexError("Índice de item inválido.")
        del self._itens_agendados[indice_item]
        self._recalcular_valor_total()

    def _deduzir_estoque_realizacao(self) -> None:
        # Tenta deduzir o estoque de suprimentos e produtos.
        for sup_ag in self._suprimentos_utilizados:
            if sup_ag.suprimento.estoque < sup_ag.quantidade:
                raise ValueError(f"Estoque insuficiente. Suprimento '{sup_ag.suprimento.nome}' (ID: {sup_ag.suprimento.id}). Disponível: {sup_ag.suprimento.estoque}, Necessário: {sup_ag.quantidade}.")

        for item_ag in self._itens_agendados:
            if isinstance(item_ag.item, produto.Produto):
                if item_ag.item.estoque < item_ag.quantidade:
                    raise ValueError(f"Estoque insuficiente. Produto '{item_ag.item.nome}' (ID: {item_ag.item.id}). Disponível: {item_ag.item.estoque}, Necessário: {item_ag.quantidade}.")

        for sup_ag in self._suprimentos_utilizados:
            sup_ag.suprimento.estoque -= sup_ag.quantidade

        for item_ag in self._itens_agendados:
            if isinstance(item_ag.item, produto.Produto):
                item_ag.item.estoque -= item_ag.quantidade

    def marcar_como_realizado(self) -> None:
        # Marca a agenda como REALIZADO e deduz os estoques.
        if self._status == AgendaStatus.REALIZADO:
            return

        try:
            self._deduzir_estoque_realizacao()
        except ValueError as e:
            raise ValueError(f"Não foi possível marcar o agendamento ID {self.id} como REALIZADO: {e}")

        self._status = AgendaStatus.REALIZADO

    def marcar_como_nao_realizado(self) -> None:
        # Marca a agenda como NÃO REALIZADO e reverte os estoques se necessário.
        if self._status == AgendaStatus.NAO_REALIZADO:
            return

        if self._status == AgendaStatus.REALIZADO:
            for sup_ag in self._suprimentos_utilizados:
                sup_ag.suprimento.estoque += sup_ag.quantidade

            for item_ag in self._itens_agendados:
                if isinstance(item_ag.item, produto.Produto):
                    item_ag.item.estoque += item_ag.quantidade

        self._status = AgendaStatus.NAO_REALIZADO

    @staticmethod
    def _inicializar_proximo_id() -> None:
        if Agenda._agendas_por_id:
            Agenda._proximo_id_disponivel = max(Agenda._agendas_por_id.keys()) + 1
        else:
            Agenda._proximo_id_disponivel = 1

    @staticmethod
    def _verificar_conflito(func: mod_funcionario.Funcionario, cli: mod_cliente.Cliente, 
                           maquinas_propostas: Optional[list[mod_maquina.Maquina]],
                           inicio: datetime, fim: datetime, agenda_id_atual: Optional[int] = None) -> bool:
        # Verifica se há conflito de horário para um funcionário, cliente ou máquinas.
        for agenda_existente in Agenda._agendas_por_id.values():
            if agenda_id_atual is not None and agenda_existente.id == agenda_id_atual:
                continue

            if (agenda_existente.funcionario.cpf == func.cpf or agenda_existente.cliente.cpf == cli.cpf):
                if (inicio < agenda_existente.data_hora_fim) and (fim > agenda_existente.data_hora_inicio):
                    return True

            if maquinas_propostas:
                for maq_prop in maquinas_propostas:
                    for maq_agendada_existente in agenda_existente.maquinas_agendadas:
                        if maq_prop.id == maq_agendada_existente.id:
                            if (inicio < agenda_existente.data_hora_fim) and (fim > agenda_existente.data_hora_inicio):
                                return True
        return False

    @staticmethod
    def buscar_agenda(id_agenda: int) -> Optional['Agenda']:
        return Agenda._agendas_por_id.get(id_agenda, None)

    @staticmethod
    def listar_agendas() -> list['Agenda']:
        return list(Agenda._agendas_por_id.values())

    @staticmethod
    def criar_agenda(funcionario_obj: mod_funcionario.Funcionario, 
                     cliente_obj: mod_cliente.Cliente, data_hora_inicio: str, data_hora_fim: str, 
                     itens_agendados: list[ItemAgendado], comentario: Optional[str] = None,
                     maquinas_agendadas: Optional[list[mod_maquina.Maquina]] = None,
                     suprimentos_utilizados: Optional[list[SuprimentoAgendado]] = None,
                     status: Union[str, AgendaStatus] = AgendaStatus.AGENDADO
                     ) -> 'Agenda':
        nova_agenda = Agenda(None, funcionario_obj, cliente_obj, data_hora_inicio, data_hora_fim, 
                             itens_agendados, comentario, maquinas_agendadas, suprimentos_utilizados, status)
        return nova_agenda

    @staticmethod
    def atualizar_dados_agenda(id_agenda: int, **kwargs: Any) -> None:
        agenda_existente: Optional['Agenda'] = Agenda.buscar_agenda(id_agenda)
        if not agenda_existente:
            raise ValueError(f"Agenda com ID {id_agenda} não encontrada para atualização.")

        proposto_func: mod_funcionario.Funcionario = kwargs.get('funcionario', agenda_existente.funcionario)
        proposto_cli: mod_cliente.Cliente = kwargs.get('cliente', agenda_existente.cliente)
        proposto_maquinas: list[mod_maquina.Maquina] = kwargs.get('maquinas_agendadas', list(agenda_existente.maquinas_agendadas))
        proposto_suprimentos: list[SuprimentoAgendado] = kwargs.get('suprimentos_utilizados', list(agenda_existente.suprimentos_utilizados))

        proposto_inicio_dt: datetime = agenda_existente.data_hora_inicio 
        proposto_fim_dt: datetime = agenda_existente.data_hora_fim      

        proposto_status: AgendaStatus = agenda_existente.status
        if 'status' in kwargs:
            if isinstance(kwargs['status'], str):
                proposto_status = AgendaStatus.de_string(kwargs['status'])
            elif isinstance(kwargs['status'], AgendaStatus):
                proposto_status = kwargs['status']
            else:
                raise TypeError("O status deve ser um membro de AgendaStatus ou uma string válida.")

        if 'data_hora_inicio' in kwargs:
            proposto_inicio_dt = pessoa.Pessoa._parse_data(str(kwargs['data_hora_inicio']), is_datetime=True) #type: ignore[return-value]

        if 'data_hora_fim' in kwargs:
            proposto_fim_dt = pessoa.Pessoa._parse_data(str(kwargs['data_hora_fim']), is_datetime=True) #type: ignore[return-value]

        if proposto_fim_dt <= proposto_inicio_dt:
            raise ValueError("A data/hora de fim proposta deve ser posterior à data/hora de início proposta.")

        if Agenda._verificar_conflito(proposto_func, proposto_cli, proposto_maquinas,
                                      proposto_inicio_dt, proposto_fim_dt, agenda_existente.id):
            raise ValueError(f"Conflito de horário detectado para a Agenda ID {id_agenda}.")

        status_original = agenda_existente.status

        for chave, valor in kwargs.items():
            if chave in ['id', 'itens_agendados', 'valor_total', 'status']:
                continue

            if hasattr(agenda_existente, chave):
                setattr(agenda_existente, chave, valor)

        if 'status' in kwargs:
            if status_original == AgendaStatus.AGENDADO and proposto_status == AgendaStatus.REALIZADO:
                agenda_existente.marcar_como_realizado()
            elif status_original == AgendaStatus.REALIZADO and proposto_status in [AgendaStatus.AGENDADO, AgendaStatus.NAO_REALIZADO]:
                agenda_existente.marcar_como_nao_realizado()
                agenda_existente.status = proposto_status # Define o status final após a reversão.
            elif status_original != proposto_status:
                agenda_existente.status = proposto_status

    @staticmethod
    def deletar_agenda(id_agenda: int) -> None:
        if id_agenda in Agenda._agendas_por_id:
            agenda_a_deletar = Agenda._agendas_por_id[id_agenda]

            if agenda_a_deletar.status == AgendaStatus.REALIZADO:
                for sup_ag in agenda_a_deletar.suprimentos_utilizados:
                    sup_ag.suprimento.estoque += sup_ag.quantidade
                for item_ag in agenda_a_deletar.itens_agendados:
                    if isinstance(item_ag.item, produto.Produto):
                        item_ag.item.estoque += item_ag.quantidade

            del Agenda._agendas_por_id[id_agenda]
        else:
            raise ValueError(f"Agenda com ID {id_agenda} não encontrada para exclusão.")

    @staticmethod
    def filtrar_agendas(data_inicio_str: str, data_fim_str: str, 
                        funcionario_obj: Optional[mod_funcionario.Funcionario] = None,
                        cliente_obj: Optional[mod_cliente.Cliente] = None,
                        status_agenda: Optional[Union[str, AgendaStatus]] = None
                        ) -> list['Agenda']:
        # Busca agendas dentro de um período, com filtros opcionais.
        try:
            data_inicio = pessoa.Pessoa._parse_data(data_inicio_str, is_datetime=False)
            data_fim = pessoa.Pessoa._parse_data(data_fim_str, is_datetime=False)
        except ValueError as e:
            raise ValueError(f"Formato de data inválido para filtro: {e}")

        if data_inicio > data_fim:
            raise ValueError("Data de início não pode ser posterior à data de fim.")

        status_alvo: Optional[AgendaStatus] = None
        if status_agenda:
            if isinstance(status_agenda, str):
                status_alvo = AgendaStatus.de_string(status_agenda)
            elif isinstance(status_agenda, AgendaStatus):
                status_alvo = status_agenda
            else:
                raise TypeError("O status de filtro deve ser uma string ou membro de AgendaStatus.")

        resultados = []
        for agenda in Agenda._agendas_por_id.values():
            data_agenda = agenda.data_hora_inicio.date()
            if not (data_inicio <= data_agenda <= data_fim):
                continue

            if funcionario_obj is not None and agenda.funcionario is not funcionario_obj:
                continue

            if cliente_obj is not None and agenda.cliente is not cliente_obj:
                continue

            if status_alvo is not None and agenda.status is not status_alvo:
                continue

            resultados.append(agenda)
        return resultados

    @staticmethod
    def _formatar_agendas_para_tabela(agendas: list['Agenda']) -> str:
        if not agendas:
            return "Nenhum agendamento para exibir."

        cabecalhos = ["ID", "Início", "Fim", "Funcionário", "Cliente", "Status", "Valor Total"]
        dados_tabela = []

        for agenda in agendas:
            inicio_str = agenda.data_hora_inicio.strftime('%d/%m/%Y %H:%M')
            fim_str = agenda.data_hora_fim.strftime('%d/%m/%Y %H:%M')
            funcionario_info = f"{agenda.funcionario.nome} (ID: {agenda.funcionario.id})"
            cliente_info = f"{agenda.cliente.nome} (ID: {agenda.cliente.id})"
            status_str = agenda.status.value
            valor_total_str = f"R${agenda.valor_total:.2f}"

            dados_tabela.append([
                agenda.id,
                inicio_str,
                fim_str,
                funcionario_info,
                cliente_info,
                status_str,
                valor_total_str
            ])

        return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
