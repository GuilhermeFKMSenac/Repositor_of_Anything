from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import Session, relationship
import tabulate
from typing import Optional, Union, List, Any
from datetime import date

from database import Base
import produto as mod_produto
import suprimento as mod_suprimento
import maquina as mod_maquina
import fornecedor as mod_fornecedor
import funcionario as mod_funcionario

# --- Classes ORM para Despesas ---

class Despesa(Base):
    __tablename__ = 'despesas'
    id = Column(Integer, primary_key=True, index=True)
    valor_total = Column(Float, nullable=False)
    data_despesa = Column(Date, nullable=False)
    comentario = Column(String(500))
    tipo = Column(String(50))

    __mapper_args__ = {'polymorphic_on': tipo, 'polymorphic_identity': 'despesa'}

class Compra(Despesa):
    __tablename__ = 'compras'
    id = Column(Integer, ForeignKey('despesas.id'), primary_key=True)
    quantidade = Column(Float, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    item_tipo = Column(String(50), nullable=False)
    item_id = Column(Integer, nullable=True)
    item_descricao = Column(String(255), nullable=True)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'), nullable=False)
    fornecedor_obj = relationship("Fornecedor")
    __mapper_args__ = {'polymorphic_identity': 'compra'}

class FixoTerceiro(Despesa):
    __tablename__ = 'fixo_terceiros'
    id = Column(Integer, ForeignKey('despesas.id'), primary_key=True)
    tipo_despesa_str = Column(String(255), nullable=False)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'), nullable=True)
    fornecedor_obj = relationship("Fornecedor")
    __mapper_args__ = {'polymorphic_identity': 'fixo_terceiro'}

class Salario(Despesa):
    __tablename__ = 'salarios'
    id = Column(Integer, ForeignKey('despesas.id'), primary_key=True)
    salario_bruto = Column(Float, nullable=False)
    descontos = Column(Float, nullable=False)
    funcionario_id = Column(Integer, ForeignKey('pessoas.id'), nullable=False)
    funcionario_obj = relationship("Funcionario")
    __mapper_args__ = {'polymorphic_identity': 'salario'}

class Comissao(Despesa):
    __tablename__ = 'comissoes'
    id = Column(Integer, ForeignKey('despesas.id'), primary_key=True)
    valor_soma_servicos = Column(Float, nullable=False)
    valor_soma_produtos = Column(Float, nullable=False)
    taxa_servicos = Column(Float, nullable=False)
    taxa_produtos = Column(Float, nullable=False)
    funcionario_id = Column(Integer, ForeignKey('pessoas.id'), nullable=False)
    funcionario_obj = relationship("Funcionario")
    __mapper_args__ = {'polymorphic_identity': 'comissao'}

class Outros(Despesa):
    __tablename__ = 'outros_despesas'
    id = Column(Integer, ForeignKey('despesas.id'), primary_key=True)
    tipo_despesa_str = Column(String(255), nullable=False)
    __mapper_args__ = {'polymorphic_identity': 'outros'}

# --- Funções CRUD para Despesas ---

def criar_compra(db: Session, fornecedor_obj: mod_fornecedor.Fornecedor,
                 item_comprado: Union[mod_produto.Produto, mod_suprimento.Suprimento, mod_maquina.Maquina, str],
                 quantidade: float, valor_unitario: float, data_despesa_obj: date, comentario: Optional[str] = None):
    
    valor_total = quantidade * valor_unitario

    item_tipo_str = item_comprado.__class__.__name__ if not isinstance(item_comprado, str) else "DescricaoManual"
    item_id_num = item_comprado.id if hasattr(item_comprado, 'id') else None
    item_desc_str = item_comprado if isinstance(item_comprado, str) else None

    nova_compra = Compra(
        valor_total=valor_total, data_despesa=data_despesa_obj, comentario=comentario,
        fornecedor_id=fornecedor_obj.id, quantidade=quantidade, valor_unitario=valor_unitario,
        item_tipo=item_tipo_str, item_id=item_id_num, item_descricao=item_desc_str
    )
    db.add(nova_compra)

    if isinstance(item_comprado, (mod_produto.Produto, mod_suprimento.Suprimento)):
        item_comprado.estoque = float(getattr(item_comprado, 'estoque', 0) or 0) + quantidade
        
        if hasattr(item_comprado, 'custo_compra'):
            item_comprado.custo_compra = valor_unitario
        else:
            item_comprado.custo_unitario = valor_unitario
            
        historico_existente = item_comprado.historico_custo_compra or []
        novo_historico = list(historico_existente)
        
        novo_registro = {
            "data": data_despesa_obj.isoformat(),
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
            "fornecedor_id": fornecedor_obj.id,
            "fornecedor_nome": fornecedor_obj.nome
        }
        novo_historico.append(novo_registro)
        item_comprado.historico_custo_compra = novo_historico
        
        db.add(item_comprado)

    db.commit()

def criar_fixo_terceiro(db: Session, valor: float, tipo_despesa_str: str, data_despesa_obj: date,
                        fornecedor_obj: Optional[mod_fornecedor.Fornecedor] = None, comentario: Optional[str] = None):
    nova_despesa = FixoTerceiro(
        valor_total=valor, data_despesa=data_despesa_obj,
        tipo_despesa_str=tipo_despesa_str, fornecedor_id=fornecedor_obj.id if fornecedor_obj else None, comentario=comentario
    )
    db.add(nova_despesa)
    db.commit()

def criar_salario(db: Session, funcionario_obj: mod_funcionario.Funcionario, salario_bruto: float,
                  descontos: float, data_despesa_obj: date, comentario: Optional[str] = None):
    nova_despesa = Salario(
        valor_total=salario_bruto - descontos, data_despesa=data_despesa_obj,
        salario_bruto=salario_bruto, descontos=descontos, funcionario_id=funcionario_obj.id, comentario=comentario
    )
    db.add(nova_despesa)
    db.commit()

def criar_comissao(db: Session, funcionario_obj: mod_funcionario.Funcionario, valor_soma_servicos: float, valor_soma_produtos: float,
                   taxa_servicos: float, taxa_produtos: float, data_despesa_obj: date, comentario: Optional[str] = None):
    valor_final = (valor_soma_servicos * taxa_servicos) + (valor_soma_produtos * taxa_produtos)
    nova_despesa = Comissao(valor_total=valor_final, data_despesa=data_despesa_obj,
                            valor_soma_servicos=valor_soma_servicos, valor_soma_produtos=valor_soma_produtos,
                            taxa_servicos=taxa_servicos, taxa_produtos=taxa_produtos, funcionario_id=funcionario_obj.id, comentario=comentario)
    db.add(nova_despesa)
    db.commit()

def criar_outros(db: Session, valor: float, tipo_despesa_str: str, data_despesa_obj: date, comentario: Optional[str] = None):
    nova_despesa = Outros(valor_total=valor, data_despesa=data_despesa_obj,
                          tipo_despesa_str=tipo_despesa_str, comentario=comentario)
    db.add(nova_despesa)
    db.commit()

def deletar_despesa(db: Session, id_despesa: int):
    despesa = db.query(Despesa).get(id_despesa)
    if not despesa:
        raise ValueError(f"Despesa com ID {id_despesa} não encontrada.")
    db.delete(despesa)
    db.commit()

def _formatar_despesas_para_tabela(db: Session, despesas: List[Despesa]) -> str:
    if not despesas: return "Nenhuma despesa para exibir."
    
    cabecalhos = ["ID", "Data", "Tipo", "Valor", "Detalhes"]
    dados_tabela = []
    total_despesas = 0.0

    for d in despesas:
        detalhes = ""
        if isinstance(d, Compra):
            nome_item = ""
            if d.item_tipo == "Produto":
                item_obj = mod_produto.buscar_produto_id(db, d.item_id)
                if item_obj: nome_item = item_obj.nome
            elif d.item_tipo == "Suprimento":
                item_obj = mod_suprimento.buscar_suprimento_id(db, d.item_id)
                if item_obj: nome_item = item_obj.nome
            
            nome_item_final = nome_item or d.item_descricao or f"ID:{d.item_id} não encontrado"
            detalhes = f"Compra: {d.quantidade}x {nome_item_final} | Forn: {d.fornecedor_obj.nome}"
        elif isinstance(d, FixoTerceiro):
            forn_nome = f" | Forn: {d.fornecedor_obj.nome}" if d.fornecedor_obj else ""
            detalhes = f"{d.tipo_despesa_str}{forn_nome}"
        elif isinstance(d, Salario):
            detalhes = f"Salário: {d.funcionario_obj.nome} (Bruto: R${d.salario_bruto:.2f}, Desc: R${d.descontos:.2f})"
        elif isinstance(d, Comissao):
            detalhes = f"Comissão: {d.funcionario_obj.nome}"
        elif isinstance(d, Outros):
            detalhes = d.tipo_despesa_str
        
        tipo_str = d.__class__.__name__
        dados_tabela.append([d.id, d.data_despesa.strftime("%d/%m/%Y"), tipo_str, f"R${d.valor_total:.2f}", detalhes])
        total_despesas += d.valor_total

    tabela_formatada = tabulate.tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")
    sumario = f"\n--- RESUMO DO FILTRO ---\nValor Total das Despesas: R${total_despesas:.2f}"
    
    return f"{tabela_formatada}{sumario}"

def atualizar_dados_despesa(db: Session, id_despesa: int, **kwargs: Any) -> Despesa:
    despesa = db.query(Despesa).get(id_despesa)
    if not despesa:
        raise ValueError(f"Despesa com ID {id_despesa} não encontrada.")

    for chave, valor in kwargs.items():
        if hasattr(despesa, chave):
            setattr(despesa, chave, valor)

    if isinstance(despesa, Compra):
        setattr(despesa, "valor_total", despesa.quantidade * despesa.valor_unitario)
    elif isinstance(despesa, Salario):
        setattr(despesa, "valor_total", despesa.salario_bruto - despesa.descontos)
    elif isinstance(despesa, Comissao):
        valor_final = (despesa.valor_soma_servicos * despesa.taxa_servicos) + (despesa.valor_soma_produtos * despesa.taxa_produtos)
        setattr(despesa, "valor_total", valor_final)
    
    db.commit()
    db.refresh(despesa)
    return despesa

def listar_despesas(db: Session, data_inicio: Optional[date] = None, data_fim: Optional[date] = None, funcionario_id: Optional[int] = None, fornecedor_id: Optional[int] = None, tipos: Optional[List[str]] = None) -> list[Despesa]:
    query = db.query(Despesa)

    if data_inicio:
        query = query.filter(Despesa.data_despesa >= data_inicio)
    if data_fim:
        query = query.filter(Despesa.data_despesa <= data_fim)
    
    if tipos:
        query = query.filter(Despesa.tipo.in_(tipos))

    if funcionario_id:
        salario_ids = db.query(Salario.id).filter(Salario.funcionario_id == funcionario_id)
        comissao_ids = db.query(Comissao.id).filter(Comissao.funcionario_id == funcionario_id)
        query = query.filter(Despesa.id.in_(salario_ids.union(comissao_ids)))

    if fornecedor_id:
        compra_ids = db.query(Compra.id).filter(Compra.fornecedor_id == fornecedor_id)
        fixo_ids = db.query(FixoTerceiro.id).filter(FixoTerceiro.fornecedor_id == fornecedor_id)
        query = query.filter(Despesa.id.in_(compra_ids.union(fixo_ids)))

    return query.order_by(Despesa.data_despesa.asc()).all()
