from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, and_
from sqlalchemy.orm import Session, relationship
from tabulate import tabulate
from typing import Optional, Union, List, Any
from datetime import datetime
from enum import Enum as PyEnum

from database import Base, agenda_maquinas_tabela, agenda_itens_tabela, agenda_suprimentos_tabela
import funcionario as mod_funcionario
import cliente as mod_cliente
import maquina as mod_maquina
import suprimento as mod_suprimento
import servico as mod_servico
import produto as mod_produto

class AgendaStatus(PyEnum):
    AGENDADO = "Agendado"
    REALIZADO = "Realizado"
    NAO_REALIZADO = "Não Realizado"

class ItemAgendado:
    def __init__(self, item: Union[mod_servico.Servico, mod_produto.Produto], quantidade: float, valor_negociado: Optional[float] = None):
        self.item = item
        self.quantidade = quantidade
        self.valor_negociado = valor_negociado or (item.valor_venda if isinstance(item, mod_servico.Servico) else item.preco)
        self.subtotal = self.quantidade * self.valor_negociado

class SuprimentoAgendado:
    def __init__(self, suprimento: mod_suprimento.Suprimento, quantidade: float):
        self.suprimento = suprimento
        self.quantidade = quantidade

class Agenda(Base):
    __tablename__ = 'agendas'

    id = Column(Integer, primary_key=True, index=True)
    data_hora_inicio = Column(DateTime, nullable=False)
    data_hora_fim = Column(DateTime, nullable=False)
    comentario = Column(String(500), nullable=True)
    status = Column(Enum(AgendaStatus), nullable=False, default=AgendaStatus.AGENDADO)
    valor_total = Column(Float, nullable=False, default=0.0)

    funcionario_id = Column(Integer, ForeignKey('pessoas.id'), nullable=False)
    cliente_id = Column(Integer, ForeignKey('pessoas.id'), nullable=False)

    funcionario = relationship("Funcionario", foreign_keys=[funcionario_id])
    cliente = relationship("Cliente", foreign_keys=[cliente_id])
    
    maquinas_agendadas = relationship("Maquina", secondary=agenda_maquinas_tabela)

    def __init__(self, funcionario_obj: mod_funcionario.Funcionario, cliente_obj: mod_cliente.Cliente,
                 data_hora_inicio: datetime, data_hora_fim: datetime, **kwargs):
        self.funcionario_id = funcionario_obj.id
        self.cliente_id = cliente_obj.id
        self.data_hora_inicio = data_hora_inicio
        self.data_hora_fim = data_hora_fim
        self.comentario = kwargs.get('comentario')
        self.status = kwargs.get('status', AgendaStatus.AGENDADO)
        self.valor_total = 0.0

# Funções de CRUD e Lógica de Negócio para Agenda

def _recalcular_valor_total(db: Session, agenda: Agenda) -> None:
    total = 0.0
    itens_db = db.execute(agenda_itens_tabela.select().where(agenda_itens_tabela.c.agenda_id == agenda.id)).fetchall()
    for item in itens_db:
        total += item.quantidade * item.valor_negociado
    agenda.valor_total = total
    db.commit()

def criar_agenda(db: Session, funcionario_obj: mod_funcionario.Funcionario, cliente_obj: mod_cliente.Cliente,
                 data_hora_inicio_obj: datetime, data_hora_fim_obj: datetime,
                 itens_agendados: List[ItemAgendado],
                 maquinas_agendadas: Optional[List[mod_maquina.Maquina]] = None,
                 suprimentos_utilizados: Optional[List[SuprimentoAgendado]] = None,
                 **kwargs) -> Agenda:
    
    if data_hora_fim_obj <= data_hora_inicio_obj:
        raise ValueError("A data/hora de fim deve ser posterior à de início.")

    nova_agenda = Agenda(
        funcionario_obj=funcionario_obj, cliente_obj=cliente_obj,
        data_hora_inicio=data_hora_inicio_obj, data_hora_fim=data_hora_fim_obj, **kwargs
    )

    if maquinas_agendadas:
        nova_agenda.maquinas_agendadas.extend(maquinas_agendadas)

    db.add(nova_agenda)
    db.commit()
    db.refresh(nova_agenda)

    total_valor = 0
    for item_ag in itens_agendados:
        db.execute(agenda_itens_tabela.insert().values(
            agenda_id=nova_agenda.id,
            item_tipo=item_ag.item.__class__.__name__, item_id=item_ag.item.id,
            quantidade=item_ag.quantidade, valor_negociado=item_ag.valor_negociado
        ))
        total_valor += item_ag.subtotal

    if suprimentos_utilizados:
        for sup_ag in suprimentos_utilizados:
            db.execute(agenda_suprimentos_tabela.insert().values(
                agenda_id=nova_agenda.id, suprimento_id=sup_ag.suprimento.id,
                quantidade=sup_ag.quantidade
            ))

    nova_agenda.valor_total = total_valor
    db.commit()
    db.refresh(nova_agenda)
    return nova_agenda

def buscar_agenda(db: Session, id_agenda: int) -> Optional[Agenda]:
    return db.query(Agenda).filter(Agenda.id == id_agenda).first()

def deletar_agenda(db: Session, id_agenda: int) -> None:
    agenda = buscar_agenda(db, id_agenda)
    if not agenda:
        raise ValueError(f"Agenda com ID {id_agenda} não encontrada.")

    db.execute(agenda_itens_tabela.delete().where(agenda_itens_tabela.c.agenda_id == id_agenda))
    db.execute(agenda_suprimentos_tabela.delete().where(agenda_suprimentos_tabela.c.agenda_id == id_agenda))
    
    db.delete(agenda)
    db.commit()

def _formatar_agendas_para_tabela(db: Session, agendas: list[Agenda]) -> str:
    if not agendas:
        return "Nenhum agendamento para exibir."

    cabecalhos = ["ID", "Início", "Fim", "Funcionário", "Cliente", "Itens", "Status", "Valor"]
    dados_tabela = []

    for agenda in agendas:
        itens_str_list = []
        itens_agendados = db.execute(agenda_itens_tabela.select().where(agenda_itens_tabela.c.agenda_id == agenda.id)).fetchall()
        for item in itens_agendados:
            nome_item = f"({item.item_tipo} ID:{item.item_id} não encontrado)"
            if item.item_tipo == 'Produto':
                prod = mod_produto.buscar_produto_id(db, item.item_id)
                if prod: nome_item = prod.nome
            elif item.item_tipo == 'Servico':
                serv = mod_servico.buscar_servico_id(db, item.item_id)
                if serv: nome_item = serv.nome
            itens_str_list.append(f"{item.quantidade}x {nome_item}")
        
        itens_str = ", ".join(itens_str_list) if itens_str_list else "Nenhum"

        dados_tabela.append([
            agenda.id,
            agenda.data_hora_inicio.strftime('%d/%m/%y %H:%M'),
            agenda.data_hora_fim.strftime('%d/%m/%y %H:%M'),
            agenda.funcionario.nome,
            agenda.cliente.nome,
            itens_str,
            agenda.status.value,
            f"R${agenda.valor_total:.2f}"
        ])
    
    return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")

def get_itens_agendados_detalhes(db: Session, id_agenda: int) -> List[dict]:
    itens_db = db.execute(
        agenda_itens_tabela.select().where(agenda_itens_tabela.c.agenda_id == id_agenda)
    ).fetchall()
    detalhes = []
    for item in itens_db:
        nome_item = f"({item.item_tipo} ID:{item.item_id} não encontrado)"
        if item.item_tipo == 'Produto':
            prod = mod_produto.buscar_produto_id(db, item.item_id)
            if prod: nome_item = prod.nome
        elif item.item_tipo == 'Servico':
            serv = mod_servico.buscar_servico_id(db, item.item_id)
            if serv: nome_item = serv.nome
        detalhes.append({
            "id_associacao": item.id,
            "nome": nome_item,
            "quantidade": item.quantidade,
            "valor_negociado": item.valor_negociado
        })
    return detalhes

def atualizar_agenda(db: Session, id_agenda: int,
                     itens_a_adicionar: Optional[List[ItemAgendado]] = None,
                     ids_associacao_a_remover: Optional[List[int]] = None,
                     **kwargs: Any) -> Agenda:
    agenda = buscar_agenda(db, id_agenda)
    if not agenda:
        raise ValueError(f"Agenda com ID {id_agenda} não encontrada.")

    for chave, valor in kwargs.items():
        if hasattr(agenda, chave):
            setattr(agenda, chave, valor)

    if ids_associacao_a_remover:
        for id_assoc in ids_associacao_a_remover:
            db.execute(agenda_itens_tabela.delete().where(agenda_itens_tabela.c.id == id_assoc))

    if itens_a_adicionar:
        for item_ag in itens_a_adicionar:
            db.execute(agenda_itens_tabela.insert().values(
                agenda_id=agenda.id,
                item_tipo=item_ag.item.__class__.__name__,
                item_id=item_ag.item.id,
                quantidade=item_ag.quantidade,
                valor_negociado=item_ag.valor_negociado
            ))
    _recalcular_valor_total(db, agenda)
    db.commit()
    db.refresh(agenda)
    return agenda

def verificar_conflito_maquina(db: Session, maquina_id: int, inicio: datetime, fim: datetime, agenda_id_a_ignorar: Optional[int] = None) -> bool:
    query = db.query(Agenda).join(agenda_maquinas_tabela).filter(
        agenda_maquinas_tabela.c.maquina_id == maquina_id,
        and_(
            Agenda.data_hora_inicio < fim, #type: ignore
            Agenda.data_hora_fim > inicio #type: ignore
        )
    )

    if agenda_id_a_ignorar:
        query = query.filter(Agenda.id != agenda_id_a_ignorar)

    return db.query(query.exists()).scalar()

def listar_agendas(db: Session, data_inicio: Optional[datetime] = None, data_fim: Optional[datetime] = None, cliente_id: Optional[int] = None, funcionario_id: Optional[int] = None) -> list[Agenda]:
    query = db.query(Agenda)
    if data_inicio:
        query = query.filter(Agenda.data_hora_inicio >= data_inicio) #type: ignore
    if data_fim:
        from datetime import timedelta
        query = query.filter(Agenda.data_hora_inicio <= data_fim) #type: ignore
    if cliente_id:
        query = query.filter(Agenda.cliente_id == cliente_id)
    if funcionario_id:
        query = query.filter(Agenda.funcionario_id == funcionario_id)
    
    return query.order_by(Agenda.data_hora_inicio.desc()).all() #type: ignore
 