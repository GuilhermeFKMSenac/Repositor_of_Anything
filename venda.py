from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import Session, relationship
from datetime import date
from typing import Optional, Union, List, Any
import tabulate

from database import Base, venda_itens_tabela, agenda_itens_tabela
import funcionario as mod_funcionario
import cliente as mod_cliente
import servico as mod_servico
import produto as mod_produto
import agenda as mod_agenda
import suprimento as mod_suprimento

class ItemVenda:
    def __init__(self, item: Union[mod_servico.Servico, mod_produto.Produto], quantidade: float, preco_unitario_vendido: Optional[float] = None):
        self.item = item
        self.quantidade = float(quantidade)
        self.preco_unitario_vendido = float(preco_unitario_vendido or (item.valor_venda if isinstance(item, mod_servico.Servico) else item.preco))
        self.subtotal = self.quantidade * self.preco_unitario_vendido

class Venda(Base):
    __tablename__ = 'vendas'

    id = Column(Integer, primary_key=True, index=True)
    data_venda = Column(Date, nullable=False)
    comentario = Column(String(500), nullable=True)
    valor_total = Column(Float, nullable=False)

    funcionario_id = Column(Integer, ForeignKey('pessoas.id'), nullable=False)
    cliente_id = Column(Integer, ForeignKey('pessoas.id'), nullable=False)
    agenda_id = Column(Integer, ForeignKey('agendas.id'), nullable=True)

    funcionario = relationship("Funcionario", foreign_keys=[funcionario_id])
    cliente = relationship("Cliente", foreign_keys=[cliente_id])
    agenda = relationship("Agenda", foreign_keys=[agenda_id])

    def __init__(self, funcionario_obj: mod_funcionario.Funcionario, cliente_obj: mod_cliente.Cliente,
                 data_venda: date, agenda_obj: Optional[mod_agenda.Agenda] = None, comentario: Optional[str] = None):
        self.funcionario_id = funcionario_obj.id
        self.cliente_id = cliente_obj.id
        self.data_venda = data_venda
        self.agenda_id = agenda_obj.id if agenda_obj else None
        self.comentario = comentario
        self.valor_total = 0.0

# Funções de CRUD e Lógica de Negócio para Venda

def criar_venda(db: Session, funcionario_obj: mod_funcionario.Funcionario, cliente_obj: mod_cliente.Cliente,
                data_venda_obj: date, itens_venda: List[ItemVenda],
                agenda_obj: Optional[mod_agenda.Agenda] = None, comentario: Optional[str] = None) -> Venda:

    for item_v in itens_venda:
        if isinstance(item_v.item, mod_produto.Produto):
            if item_v.item.estoque < item_v.quantidade:
                raise ValueError(f"Estoque insuficiente para o produto '{item_v.item.nome}'.")

    nova_venda = Venda(
        funcionario_obj=funcionario_obj, cliente_obj=cliente_obj,
        data_venda=data_venda_obj, agenda_obj=agenda_obj, comentario=comentario
    )
    db.add(nova_venda)
    db.commit()
    db.refresh(nova_venda)

    total_venda = 0
    for item_v in itens_venda:
        db.execute(venda_itens_tabela.insert().values(
            venda_id=nova_venda.id,
            item_tipo=item_v.item.__class__.__name__,
            item_id=item_v.item.id,
            quantidade=item_v.quantidade,
            preco_unitario_vendido=item_v.preco_unitario_vendido
        ))
        total_venda += item_v.subtotal

        if isinstance(item_v.item, mod_produto.Produto):
            item_v.item.estoque -= item_v.quantidade
            db.add(item_v.item)

    if agenda_obj:
        total_venda += agenda_obj.valor_total
        agenda_obj.status = mod_agenda.AgendaStatus.REALIZADO
        db.add(agenda_obj)

        suprimentos_da_agenda = db.execute(
            mod_agenda.agenda_suprimentos_tabela.select().where(mod_agenda.agenda_suprimentos_tabela.c.agenda_id == agenda_obj.id)
        ).fetchall()

        for sup_agendado in suprimentos_da_agenda:
            suprimento_db = mod_suprimento.buscar_suprimento_id(db, sup_agendado.suprimento_id)
            if suprimento_db:
                suprimento_db.estoque -= sup_agendado.quantidade
                if suprimento_db.estoque < 0:
                    suprimento_db.estoque = 0
                db.add(suprimento_db)

    nova_venda.valor_total = total_venda
    db.commit()
    db.refresh(nova_venda)
    return nova_venda


def buscar_venda(db: Session, id_venda: int) -> Optional[Venda]:
    return db.query(Venda).filter(Venda.id == id_venda).first()

def deletar_venda(db: Session, id_venda: int) -> None:
    venda = buscar_venda(db, id_venda)
    if not venda:
        raise ValueError(f"Venda com ID {id_venda} não encontrada.")

    itens_vendidos = db.execute(venda_itens_tabela.select().where(venda_itens_tabela.c.venda_id == id_venda)).fetchall()
    for item_vendido in itens_vendidos:
        if item_vendido.item_tipo == 'Produto':
            produto_obj = db.query(mod_produto.Produto).get(item_vendido.item_id)
            if produto_obj:
                produto_obj.estoque += item_vendido.quantidade
                db.add(produto_obj)

    if venda.agenda and venda.agenda.status == mod_agenda.AgendaStatus.REALIZADO:
        venda.agenda.status = mod_agenda.AgendaStatus.AGENDADO
        db.add(venda.agenda)

    db.execute(venda_itens_tabela.delete().where(venda_itens_tabela.c.venda_id == id_venda))
    db.delete(venda)
    db.commit()

def _formatar_vendas_para_tabela(db: Session, vendas: list[Venda]) -> str:
    if not vendas:
        return "Nenhuma venda para exibir."

    cabecalhos = ["ID", "Data", "Funcionário", "Cliente", "Itens", "Valor Total"]
    dados_tabela = []
    total_geral = 0.0
    total_produtos = 0.0
    total_servicos = 0.0

    for venda in vendas:
        itens_str_list = []
        
        # Itens avulsos da venda
        itens_avulsos = db.execute(venda_itens_tabela.select().where(venda_itens_tabela.c.venda_id == venda.id)).fetchall()
        for item in itens_avulsos:
            nome_item = ""
            subtotal = item.quantidade * item.preco_unitario_vendido
            if item.item_tipo == 'Produto':
                prod = mod_produto.buscar_produto_id(db, item.item_id)
                if prod: nome_item = prod.nome
                total_produtos += subtotal
            elif item.item_tipo == 'Servico':
                serv = mod_servico.buscar_servico_id(db, item.item_id)
                if serv: nome_item = serv.nome
                total_servicos += subtotal
            itens_str_list.append(f"{item.quantidade}x {nome_item} (R${item.preco_unitario_vendido:.2f})")
        
        # Itens da agenda, se houver
        if venda.agenda:
            itens_da_agenda = db.execute(agenda_itens_tabela.select().where(agenda_itens_tabela.c.agenda_id == venda.agenda_id)).fetchall()
            agenda_str_list = []
            for item_agenda in itens_da_agenda:
                nome_item = ""
                subtotal = item_agenda.quantidade * item_agenda.valor_negociado
                if item_agenda.item_tipo == 'Produto':
                    prod = mod_produto.buscar_produto_id(db, item_agenda.item_id)
                    if prod: nome_item = prod.nome
                    total_produtos += subtotal
                elif item_agenda.item_tipo == 'Servico':
                    serv = mod_servico.buscar_servico_id(db, item_agenda.item_id)
                    if serv: nome_item = serv.nome
                    total_servicos += subtotal
                agenda_str_list.append(f"{item_agenda.quantidade}x {nome_item} (R${item_agenda.valor_negociado:.2f})")
            itens_str_list.append(f"[Agenda ID:{venda.agenda.id}: {', '.join(agenda_str_list)}]")

        itens_str = ", ".join(itens_str_list) or "N/A"
        total_geral += venda.valor_total
        
        dados_tabela.append([
            venda.id,
            venda.data_venda.strftime('%d/%m/%Y'),
            venda.funcionario.nome,
            venda.cliente.nome,
            itens_str,
            f"R${venda.valor_total:.2f}"
        ])

    tabela_formatada = tabulate.tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
    
    sumario = (
        f"\n--- RESUMO DO FILTRO ---\n"
        f"Total em Produtos: R${total_produtos:.2f}\n"
        f"Total em Serviços: R${total_servicos:.2f}\n"
        f"--------------------------\n"
        f"Valor Total Geral: R${total_geral:.2f}"
    )

    return f"{tabela_formatada}{sumario}"


def atualizar_dados_venda(db: Session, id_venda: int, **kwargs: Any) -> Venda:
    venda_existente = buscar_venda(db, id_venda)
    if not venda_existente:
        raise ValueError(f"Venda com ID {id_venda} não encontrada.")

    campos_permitidos = ['data_venda', 'comentario']

    for chave, valor in kwargs.items():
        if chave in campos_permitidos:
            setattr(venda_existente, chave, valor)

    db.commit()
    db.refresh(venda_existente)
    return venda_existente

def listar_vendas(db: Session, data_inicio: Optional[date] = None, data_fim: Optional[date] = None, cliente_id: Optional[int] = None, funcionario_id: Optional[int] = None) -> list[Venda]:
    query = db.query(Venda)
    if data_inicio:
        query = query.filter(Venda.data_venda >= data_inicio)
    if data_fim:
        query = query.filter(Venda.data_venda <= data_fim)
    if cliente_id:
        query = query.filter(Venda.cliente_id == cliente_id)
    if funcionario_id:  
        query = query.filter(Venda.funcionario_id == funcionario_id)

    return query.order_by(Venda.data_venda.asc()).all()
