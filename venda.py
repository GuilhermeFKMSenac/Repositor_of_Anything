from typing import Optional, Any, Union
from datetime import datetime, date
import pessoa

import funcionario as mod_funcionario
import cliente as mod_cliente
import servico
import produto
import agenda as mod_agenda
from tabulate import tabulate

class ItemVenda:
    # Representa um item (serviço ou produto) dentro de uma venda.
    def __init__(self, item: Union[servico.Servico, produto.Produto], quantidade: float, preco_unitario_vendido: Optional[float] = None) -> None:
        if not isinstance(item, (servico.Servico, produto.Produto)):
            raise TypeError("O item de venda deve ser uma instância de Servico ou Produto.")
        
        if not isinstance(quantidade, (int, float)) or quantidade <= 0:
            raise ValueError("A quantidade do item de venda deve ser um número maior que zero.")

        self._item = item
        self._quantidade = float(quantidade)
        
        if preco_unitario_vendido is None:
            if isinstance(item, servico.Servico):
                self._preco_unitario_vendido = item.valor_venda
            elif isinstance(item, produto.Produto):
                self._preco_unitario_vendido = item.preco
        else:
            if not isinstance(preco_unitario_vendido, (int, float)) or preco_unitario_vendido <= 0:
                raise ValueError("O preço unitário vendido deve ser um número maior que zero.")
            self._preco_unitario_vendido = float(preco_unitario_vendido)

        self._subtotal = self._quantidade * self._preco_unitario_vendido

    def __str__(self) -> str:
        tipo_item = "Serviço" if isinstance(self._item, servico.Servico) else "Produto"
        return (f"{tipo_item}: {self._item.nome} (Qtd: {self._quantidade:.2f}, "
                f"Preço Unit.: R${self._preco_unitario_vendido:.2f}, Subtotal: R${self._subtotal:.2f})")

    def __repr__(self) -> str:
        return (f"ItemVenda(item={self._item.nome!r}, quantidade={self._quantidade!r}, "
                f"preco_unitario_vendido={self._preco_unitario_vendido!r})")

    @property
    def item(self) -> Union[servico.Servico, produto.Produto]:
        return self._item

    @property
    def quantidade(self) -> float:
        return self._quantidade

    @property
    def preco_unitario_vendido(self) -> float:
        return self._preco_unitario_vendido

    @property
    def subtotal(self) -> float:
        return self._subtotal

class Venda:
    # Representa uma transação de venda.
    _vendas_por_id: dict[int, 'Venda'] = {}
    _proximo_id_disponivel: int = 1

    def __init__(self, id_venda: Optional[int], funcionario_obj: mod_funcionario.Funcionario, 
                 cliente_obj: mod_cliente.Cliente, itens_venda: list[ItemVenda], 
                 data_venda_str: Optional[str] = None, 
                 agenda_obj: Optional[mod_agenda.Agenda] = None, 
                 comentario: Optional[str] = None) -> None:
        if id_venda is None:
            self._id = Venda._proximo_id_disponivel
        else:
            if not isinstance(id_venda, int) or id_venda <= 0:
                raise ValueError("O ID da venda deve ser um número inteiro positivo.")
            self._id = id_venda
        
        if Venda.buscar_venda(self.id) is not None:
            raise ValueError(f"Já existe uma venda com o ID {self.id}.")
        
        if not isinstance(funcionario_obj, mod_funcionario.Funcionario):
            raise TypeError("O funcionário da venda deve ser uma instância da classe Funcionario.")
        
        if not isinstance(cliente_obj, mod_cliente.Cliente):
            raise TypeError("O cliente da venda deve ser uma instância da classe Cliente.")
        
        if not isinstance(itens_venda, list):
            raise TypeError("Os itens da venda devem ser fornecidos como uma lista de ItemVenda.")
        
        if agenda_obj is None and not itens_venda:
            raise ValueError("A venda deve conter pelo menos um ItemVenda ou estar associada a uma Agenda.")
        
        if agenda_obj is not None and not isinstance(agenda_obj, mod_agenda.Agenda):
            raise TypeError("A agenda da venda deve ser uma instância da classe Agenda ou None.")

        self._funcionario = funcionario_obj
        self._cliente = cliente_obj
        self._comentario = comentario.strip() if comentario else None
        self._itens_venda = []
        
        self.data_venda = data_venda_str if data_venda_str else datetime.now().strftime("%d/%m/%Y")
        
        self._agenda = None
        self.agenda = agenda_obj

        if self.agenda and self.agenda.status != mod_agenda.AgendaStatus.REALIZADO:
            try:
                self.agenda.marcar_como_realizado()
            except ValueError as e:
                raise ValueError(f"Não foi possível criar a venda: Erro ao marcar agenda como REALIZADO: {e}")

        if itens_venda:
            self.adicionar_itens(itens_venda)
        else:
            self._recalcular_valor_total()

        for item_venda in itens_venda:
            if isinstance(item_venda.item, produto.Produto):
                if item_venda.item.estoque < item_venda.quantidade:
                    raise ValueError(f"Estoque insuficiente para o produto '{item_venda.item.nome}'. Disponível: {item_venda.item.estoque}, Necessário: {item_venda.quantidade}.")
                item_venda.item.estoque -= item_venda.quantidade
        
        Venda._vendas_por_id[self.id] = self
        
        if id_venda is None:
            Venda._proximo_id_disponivel += 1
        elif self.id >= Venda._proximo_id_disponivel:
            Venda._proximo_id_disponivel = self.id + 1

    def __str__(self) -> str:
        itens_str = "\n    ".join([str(item) for item in self._itens_venda])
        if self._agenda:
            itens_agenda_str = f"\n  --- Itens da Agenda ID {self._agenda.id} ---\n    " + \
                               "\n    ".join([str(item) for item in self._agenda.itens_agendados])
        else:
            itens_agenda_str = ""
        
        comentario_str = f"\n  Comentário: {self._comentario}" if self._comentario else ""
        
        valor_exibido = self.valor_total

        return (f"Venda ID: {self._id}, Data: {self._data_venda.strftime('%d/%m/%Y')}\n"
                f"  Funcionário: {self._funcionario.nome} (CPF: {self._funcionario.cpf}, ID: {self._funcionario.id})\n"
                f"  Cliente: {self._cliente.nome} (CPF: {self._cliente.cpf}, ID: {self._cliente.id}){comentario_str}\n"
                f"  --- Itens de Venda Avulsos ---\n    {itens_str}{itens_agenda_str}\n"
                f"  Valor Total: R${valor_exibido:.2f}")

    def __repr__(self) -> str:
        id_agenda = self._agenda.id if self._agenda else None
        return (f"Venda(id_venda={self._id!r}, funcionario_obj_cpf={self._funcionario.cpf!r}, "
                f"cliente_obj_cpf={self._cliente.cpf!r}, data_venda={self._data_venda!r}, "
                f"itens_venda_count={len(self._itens_venda)!r}, id_agenda={id_agenda!r}, "
                f"valor_total_calculado={self._valor_total!r}, comentario={self._comentario!r})")

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
    def data_venda(self) -> date:
        return self._data_venda

    @data_venda.setter
    def data_venda(self, data_str: str) -> None:
        try:
            data_parseada = pessoa.Pessoa._parse_data(data_str, is_datetime=False) 
        except ValueError as e:
            raise ValueError(f"Data de venda inválida: {e}")
        
        self._data_venda = data_parseada

    @property
    def itens_venda(self) -> list[ItemVenda]:
        return list(self._itens_venda) 

    @property
    def agenda(self) -> Optional[mod_agenda.Agenda]:
        return self._agenda

    @agenda.setter
    def agenda(self, nova_agenda: Optional[mod_agenda.Agenda]) -> None:
        if nova_agenda is not None and not isinstance(nova_agenda, mod_agenda.Agenda):
            raise TypeError("A agenda deve ser uma instância da classe Agenda ou None.")
        self._agenda = nova_agenda
        self._recalcular_valor_total()

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
        total_calculado = sum(item.subtotal for item in self._itens_venda)
        if self._agenda:
            total_calculado += self._agenda.valor_total
        self._valor_total = total_calculado

    def adicionar_itens(self, novos_itens: list[ItemVenda]) -> None:
        if not isinstance(novos_itens, list):
            raise TypeError("Os novos itens devem ser fornecidos como uma lista de ItemVenda.")
        for item in novos_itens:
            if not isinstance(item, ItemVenda):
                raise TypeError("Cada item na lista deve ser uma instância de ItemVenda.")
            self._itens_venda.append(item)
        self._recalcular_valor_total()

    def remover_item(self, indice_item: int) -> None:
        if not isinstance(indice_item, int) or indice_item < 0 or indice_item >= len(self._itens_venda):
            raise IndexError("Índice de item inválido.")
        del self._itens_venda[indice_item]
        self._recalcular_valor_total()

    @staticmethod
    def _inicializar_proximo_id() -> None:
        if Venda._vendas_por_id:
            Venda._proximo_id_disponivel = max(Venda._vendas_por_id.keys()) + 1
        else:
            Venda._proximo_id_disponivel = 1

    @staticmethod
    def buscar_venda(id_venda: int) -> Optional['Venda']:
        return Venda._vendas_por_id.get(id_venda, None)

    @staticmethod
    def listar_vendas() -> list['Venda']:
        return list(Venda._vendas_por_id.values())

    @staticmethod
    def atualizar_dados_venda(id_venda: int, **kwargs: Any) -> None:
        venda_existente: Optional['Venda'] = Venda.buscar_venda(id_venda)
        if not venda_existente:
            raise ValueError(f"Venda com ID {id_venda} não encontrada para atualização.")

        agenda_anterior = venda_existente.agenda
        nova_agenda = kwargs.get('agenda_obj', agenda_anterior)

        # Lógica para reverter status da agenda anterior se ela for removida ou substituída.
        if agenda_anterior and nova_agenda is not agenda_anterior:
            if agenda_anterior.status == mod_agenda.AgendaStatus.REALIZADO:
                agenda_anterior.marcar_como_nao_realizado()
                agenda_anterior.status = mod_agenda.AgendaStatus.AGENDADO

        # Lógica para atualizar a nova agenda.
        if nova_agenda and nova_agenda.status != mod_agenda.AgendaStatus.REALIZADO:
            try:
                nova_agenda.marcar_como_realizado()
            except ValueError as e:
                raise ValueError(f"Erro ao marcar nova agenda como REALIZADO: {e}")

        # Aplica as outras atualizações.
        for chave, valor in kwargs.items():
            if chave in ['id', 'itens_venda']:
                continue
            try:
                if chave == 'agenda_obj':
                    venda_existente.agenda = valor
                    if venda_existente.agenda:
                        venda_existente.funcionario = venda_existente.agenda.funcionario
                        venda_existente.cliente = venda_existente.agenda.cliente
                elif hasattr(venda_existente, chave):
                    setattr(venda_existente, chave, valor)
            except (ValueError, TypeError) as e:
                raise type(e)(f"Erro ao validar '{chave}': {e}")

    @staticmethod
    def deletar_venda(id_venda: int) -> None:
        if id_venda in Venda._vendas_por_id:
            venda_a_deletar = Venda._vendas_por_id[id_venda]
            for item_venda in venda_a_deletar.itens_venda:
                if isinstance(item_venda.item, produto.Produto):
                    item_venda.item.estoque += item_venda.quantidade
            
            del Venda._vendas_por_id[id_venda]
        else:
            raise ValueError(f"Venda com ID {id_venda} não encontrada para exclusão.")

    @staticmethod
    def criar_venda(funcionario_obj: mod_funcionario.Funcionario, 
                    cliente_obj: mod_cliente.Cliente, itens_venda: list[ItemVenda], 
                    data_venda_str: Optional[str] = None, 
                    agenda_obj: Optional[mod_agenda.Agenda] = None, 
                    comentario: Optional[str] = None) -> 'Venda':
        nova_venda = Venda(None, funcionario_obj, cliente_obj, itens_venda, 
                           data_venda_str, agenda_obj, comentario)
        return nova_venda

    @staticmethod
    def filtrar_vendas(data_inicio_str: str, data_fim_str: str, 
                       funcionario_obj: Optional[mod_funcionario.Funcionario] = None,
                       cliente_obj: Optional[mod_cliente.Cliente] = None) -> list['Venda']:
        try:
            data_inicio = pessoa.Pessoa._parse_data(data_inicio_str, is_datetime=False)
            data_fim = pessoa.Pessoa._parse_data(data_fim_str, is_datetime=False)
        except ValueError as e:
            raise ValueError(f"Formato de data inválido para filtro: {e}")

        if data_inicio > data_fim:
            raise ValueError("Data de início não pode ser posterior à data de fim.")

        resultados = []
        for venda in Venda._vendas_por_id.values():
            data_venda = venda.data_venda 
            if not (data_inicio <= data_venda <= data_fim):
                continue

            if funcionario_obj is not None and venda.funcionario is not funcionario_obj:
                continue

            if cliente_obj is not None and venda.cliente is not cliente_obj:
                continue
                
            resultados.append(venda)
        return resultados

    @staticmethod
    def _formatar_vendas_para_tabela(vendas: list['Venda']) -> str:
        if not vendas:
            return "Nenhuma venda para exibir."

        cabecalhos = ["ID", "Data", "Funcionário", "Cliente", "Itens Avulsos", "Itens Agenda", "Valor Total"]
        dados_tabela = []

        for venda in vendas:
            data_str = venda.data_venda.strftime('%d/%m/%Y')
            funcionario_info = f"{venda.funcionario.nome} (ID: {venda.funcionario.id})"
            cliente_info = f"{venda.cliente.nome} (ID: {venda.cliente.id})"
            
            itens_avulsos_detalhes = []
            for item_venda in venda.itens_venda:
                tipo_item_str = "Serviço" if isinstance(item_venda.item, servico.Servico) else "Produto"
                itens_avulsos_detalhes.append(f"{item_venda.quantidade:.0f}x {item_venda.item.nome} ({tipo_item_str} ID: {item_venda.item.id})")
            itens_avulsos_str = ", ".join(itens_avulsos_detalhes) if itens_avulsos_detalhes else "Nenhum"

            itens_agenda_detalhes = []
            if venda.agenda:
                for item_agendado in venda.agenda.itens_agendados:
                    tipo_item_str = "Serviço" if isinstance(item_agendado.item, servico.Servico) else "Produto"
                    itens_agenda_detalhes.append(f"{item_agendado.quantidade:.0f}x {item_agendado.item.nome} ({tipo_item_str} ID: {item_agendado.item.id})")
            itens_agenda_str = f"ID {venda.agenda.id}: " + (", ".join(itens_agenda_detalhes) if itens_agenda_detalhes else "Nenhum") if venda.agenda else "N/A"

            valor_total_str = f"R${venda.valor_total:.2f}"
            
            dados_tabela.append([
                venda.id,
                data_str,
                funcionario_info,
                cliente_info,
                itens_avulsos_str,
                itens_agenda_str,
                valor_total_str
            ])
        
        return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
