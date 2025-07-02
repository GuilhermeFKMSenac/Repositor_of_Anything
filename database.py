from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, create_engine

# A string de conexão agora segue o padrão do MySQL.
# Formato: "mysql+mysqlconnector://<usuario>:<senha>@<host>/<nome_do_banco>"
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:root@localhost/pi5"

# O 'engine' é o ponto de entrada para o banco de dados.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# Cada instância de SessionLocal será uma sessão de banco de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A classe Base será herdada por nossas classes de modelo (ORM).
Base = declarative_base()

# Função para criar as tabelas no banco de dados
def criar_banco():
    # Este comando irá criar a tabela 'servicos' no seu banco MySQL
    # se ela ainda não existir.
    Base.metadata.create_all(bind=engine)

agenda_maquinas_tabela = Table('agenda_maquinas', Base.metadata,
    Column('agenda_id', Integer, ForeignKey('agendas.id'), primary_key=True),
    Column('maquina_id', Integer, ForeignKey('maquinas.id'), primary_key=True)
)

agenda_itens_tabela = Table('agenda_itens', Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('agenda_id', Integer, ForeignKey('agendas.id')),
    # Não podemos ter uma FK para duas tabelas (servicos, produtos),
    # então usaremos um campo para tipo e outro para o ID.
    Column('item_tipo', String(50)),
    Column('item_id', Integer),
    Column('quantidade', Float),
    Column('valor_negociado', Float)
)

agenda_suprimentos_tabela = Table('agenda_suprimentos', Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('agenda_id', Integer, ForeignKey('agendas.id')),
    Column('suprimento_id', Integer, ForeignKey('suprimentos.id')),
    Column('quantidade', Float)
)

venda_itens_tabela = Table('venda_itens', Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('venda_id', Integer, ForeignKey('vendas.id')),
    # Estratégia igual à da agenda para lidar com produtos e serviços
    Column('item_tipo', String(50), nullable=False),
    Column('item_id', Integer, nullable=False),
    Column('quantidade', Float, nullable=False),
    Column('preco_unitario_vendido', Float, nullable=False)
)
