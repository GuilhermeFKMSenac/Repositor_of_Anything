from datetime import datetime, date
from typing import Optional, Any, Union
import funcionario as mod_funcionario
import produto
import suprimento as mod_suprimento
import maquina as mod_maquina
import fornecedor as mod_fornecedor
import pessoa
from tabulate import tabulate

class Despesa:
    # Classe base para todos os tipos de despesas.
    _despesas_por_id: dict[int, 'Despesa'] = {}
    _proximo_id_disponivel: int = 1

    def __init__(self, id_despesa: Optional[int], valor_total: float,
                 data_despesa_str: Optional[str] = None, comentario: Optional[str] = None) -> None:
        if id_despesa is None:
            self._id = Despesa._proximo_id_disponivel
        else:
            if not isinstance(id_despesa, int) or id_despesa <= 0:
                raise ValueError("O ID da despesa deve ser um número inteiro positivo.")
            self._id = id_despesa

        if Despesa.buscar_despesa(self.id) is not None:
            raise ValueError(f"Já existe uma despesa com o ID {self.id}.")

        if not isinstance(valor_total, (int, float)) or valor_total <= 0:
            raise ValueError("O valor total da despesa deve ser um número positivo.")
        self._valor_total = float(valor_total)

        self.data_despesa = data_despesa_str if data_despesa_str else datetime.now().strftime("%d/%m/%Y")

        self._comentario = comentario.strip() if comentario else None

        Despesa._despesas_por_id[self.id] = self

        if id_despesa is None:
            Despesa._proximo_id_disponivel += 1
        elif self.id >= Despesa._proximo_id_disponivel:
            Despesa._proximo_id_disponivel = self.id + 1

    def __str__(self) -> str:
        comentario_str = f"\n  Comentário: {self._comentario}" if self._comentario else ""
        return (f"ID: {self._id}, Data: {self._data_despesa.strftime('%d/%m/%Y')}, "
                f"Valor: R${self._valor_total:.2f}{comentario_str}")

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(id_despesa={self._id!r}, valor_total={self._valor_total!r}, "
                f"data_despesa_str={self._data_despesa.strftime('%d/%m/%Y')!r}, comentario={self.comentario!r})")

    @property
    def id(self) -> int:
        return self._id

    @property
    def data_despesa(self) -> date:
        return self._data_despesa

    @data_despesa.setter
    def data_despesa(self, data_str: str) -> None:
        try:
            data_parseada = pessoa.Pessoa._parse_data(data_str, is_datetime=False)
        except ValueError as e:
            raise ValueError(f"Data de despesa inválida: {e}")

        if data_parseada > datetime.now().date():
            raise ValueError("A data da despesa não pode ser no futuro.")

        self._data_despesa = data_parseada

    @property
    def valor_total(self) -> float:
        return self._valor_total

    @valor_total.setter
    def valor_total(self, novo_valor: float) -> None:
        if not isinstance(novo_valor, (int, float)) or novo_valor <= 0:
            raise ValueError("O valor total deve ser um número positivo.")
        self._valor_total = float(novo_valor)

    @property
    def comentario(self) -> Optional[str]:
        return self._comentario

    @comentario.setter
    def comentario(self, novo_comentario: Optional[str]) -> None:
        self._comentario = novo_comentario.strip() if novo_comentario else None

    @staticmethod
    def _inicializar_proximo_id() -> None:
        if Despesa._despesas_por_id:
            Despesa._proximo_id_disponivel = max(Despesa._despesas_por_id.keys()) + 1
        else:
            Despesa._proximo_id_disponivel = 1

    @staticmethod
    def buscar_despesa(id_despesa: int) -> Optional['Despesa']:
        return Despesa._despesas_por_id.get(id_despesa, None)

    @staticmethod
    def listar_despesas() -> list['Despesa']:
        return list(Despesa._despesas_por_id.values())

    @staticmethod
    def atualizar_dados_despesa(id_despesa: int, **kwargs: Any) -> None:
        despesa_existente: Optional['Despesa'] = Despesa.buscar_despesa(id_despesa)
        if not despesa_existente:
            raise ValueError(f"Despesa com ID {id_despesa} não encontrada para atualização.")

        for chave, valor in kwargs.items():
            if chave == 'id':
                continue

            try:
                if hasattr(despesa_existente, chave):
                    setattr(despesa_existente, chave, valor)
            except (ValueError, TypeError) as e:
                raise type(e)(f"Erro ao validar '{chave}': {e}")

    @staticmethod
    def deletar_despesa(id_despesa: int) -> None:
        if id_despesa in Despesa._despesas_por_id:
            del Despesa._despesas_por_id[id_despesa]
        else:
            raise ValueError(f"Despesa com ID {id_despesa} não encontrada para exclusão.")

    @staticmethod
    def filtrar_despesas(
        data_inicio_str: str,
        data_fim_str: str,
        tipo_despesa_str: Optional[Union[str, list[str]]] = None,
        fornecedor_obj: Optional[mod_fornecedor.Fornecedor] = None,
        funcionario_obj: Optional[mod_funcionario.Funcionario] = None,
        item_compra_obj: Optional[Union[produto.Produto, mod_suprimento.Suprimento, mod_maquina.Maquina, str]] = None,
        comentario_parcial: Optional[str] = None
    ) -> list['Despesa']:
        try:
            data_inicio = pessoa.Pessoa._parse_data(data_inicio_str, is_datetime=False)
            data_fim = pessoa.Pessoa._parse_data(data_fim_str, is_datetime=False)
        except ValueError as e:
            raise ValueError(f"Formato de data inválido para filtro: {e}")

        if data_inicio > data_fim:
            raise ValueError("Data de início não pode ser posterior à data de fim.")

        tipos_esperados: Optional[list[str]] = None
        if tipo_despesa_str:
            if isinstance(tipo_despesa_str, str):
                tipo_normalizado = tipo_despesa_str.strip().upper().replace(" ", "").replace("_", "")
                tipos_esperados = [tipo_normalizado]
            elif isinstance(tipo_despesa_str, list):
                tipos_esperados = [t.strip().upper().replace(" ", "").replace("_", "") for t in tipo_despesa_str]

        resultados = []
        for despesa in Despesa._despesas_por_id.values():
            data_despesa = despesa.data_despesa
            if not (data_inicio <= data_despesa <= data_fim):
                continue

            tipo_despesa_normalizado = despesa.__class__.__name__.upper().replace(" ", "").replace("_", "")
            if tipos_esperados is not None and tipo_despesa_normalizado not in tipos_esperados:
                continue

            # Lógica de filtro para fornecedor. Se o filtro for aplicado, apenas despesas que podem ter um fornecedor são consideradas.
            if fornecedor_obj is not None:
                if hasattr(despesa, 'fornecedor_obj'):
                    if despesa.fornecedor_obj is not fornecedor_obj:
                        continue
                else:
                    continue

            # Lógica de filtro para funcionário.
            if funcionario_obj is not None:
                if hasattr(despesa, 'funcionario_obj'):
                    if despesa.funcionario_obj is not funcionario_obj:
                        continue
                else:
                    continue

            if item_compra_obj is not None:
                if isinstance(despesa, Compra):
                    if despesa.item_comprado is not item_compra_obj:
                        continue
                else:
                    continue

            if comentario_parcial is not None:
                if despesa.comentario is None or comentario_parcial.lower() not in despesa.comentario.lower():
                    continue

            resultados.append(despesa)
        return resultados

    @staticmethod
    def _formatar_despesas_para_tabela(despesas: list['Despesa']) -> str:
        if not despesas:
            return "Nenhuma despesa para exibir."

        cabecalhos = ["ID", "Tipo Despesa", "Data", "Valor Total", "Detalhes"]
        dados_tabela = []

        for despesa in despesas:
            tipo_despesa = despesa.__class__.__name__
            data_str = despesa.data_despesa.strftime('%d/%m/%Y')
            valor_total_str = f"R${despesa.valor_total:.2f}"

            detalhes = ""
            if isinstance(despesa, Compra):
                desc_item = ""
                if isinstance(despesa.item_comprado, produto.Produto):
                    desc_item = f"{despesa.item_comprado.nome} (ID: {despesa.item_comprado.id})"
                elif isinstance(despesa.item_comprado, mod_suprimento.Suprimento):
                    desc_item = f"{despesa.item_comprado.nome} (ID: {despesa.item_comprado.id})"
                elif isinstance(despesa.item_comprado, mod_maquina.Maquina):
                    desc_item = f"{despesa.item_comprado.nome} (ID: {despesa.item_comprado.id})"
                else:
                    desc_item = despesa.item_comprado
                detalhes = f"Item: {desc_item}, Qtd: {despesa.quantidade:.2f}, Forn: {despesa.fornecedor_obj.nome} (ID: {despesa.fornecedor_obj.id})"
            elif isinstance(despesa, FixoTerceiro):
                info_forn = f"{despesa.fornecedor_obj.nome} (ID: {despesa.fornecedor_obj.id})" if despesa.fornecedor_obj else "N/A"
                detalhes = f"Tipo: {despesa.tipo_despesa_str}, Forn: {info_forn}"
            elif isinstance(despesa, Salario):
                info_func = f"{despesa.funcionario_obj.nome} (ID: {despesa.funcionario_obj.id})"
                detalhes = f"Funcionário: {info_func}, Bruto: R${despesa.salario_bruto:.2f}, Desc: R${despesa.descontos:.2f}"
            elif isinstance(despesa, Comissao):
                info_func = f"{despesa.funcionario_obj.nome} (ID: {despesa.funcionario_obj.id})"
                detalhes = f"Funcionário: {info_func}, Svs: R${despesa.valor_soma_servicos:.2f} (Taxa: {despesa.taxa_servicos:.0%}), Prods: R${despesa.valor_soma_produtos:.2f} (Taxa: {despesa.taxa_produtos:.0%})"
            elif isinstance(despesa, Outros):
                detalhes = f"Tipo: {despesa.tipo_despesa_str}"

            if despesa.comentario:
                detalhes += f" (Comentário: {despesa.comentario})"

            dados_tabela.append([
                despesa.id,
                tipo_despesa,
                data_str,
                valor_total_str,
                detalhes
            ])

        return tabulate(dados_tabela, headers=cabecalhos, tablefmt="grid")

class Compra(Despesa):
    def __init__(self, id_despesa: Optional[int], fornecedor_obj: mod_fornecedor.Fornecedor,
                 item_comprado: Union[produto.Produto, mod_suprimento.Suprimento, mod_maquina.Maquina, str],
                 quantidade: float, valor_unitario: float,
                 data_despesa_str: Optional[str] = None, comentario: Optional[str] = None) -> None:

        if not isinstance(fornecedor_obj, mod_fornecedor.Fornecedor):
            raise TypeError("O fornecedor deve ser uma instância de Fornecedor.")

        if not isinstance(item_comprado, (produto.Produto, mod_suprimento.Suprimento, mod_maquina.Maquina, str)):
            raise TypeError("O item comprado deve ser uma instância de Produto, Suprimento, Máquina ou uma string (descrição).")

        if not isinstance(quantidade, (int, float)) or quantidade <= 0:
            raise ValueError("A quantidade deve ser um número positivo.")
        if not isinstance(valor_unitario, (int, float)) or valor_unitario <= 0:
            raise ValueError("O valor unitário deve ser um número positivo.")

        valor_total = quantidade * valor_unitario
        super().__init__(id_despesa, valor_total, data_despesa_str, comentario)

        self._fornecedor_obj = fornecedor_obj
        self._item_comprado = item_comprado
        self._quantidade = float(quantidade)
        self._valor_unitario = float(valor_unitario)

        data_compra: datetime
        if data_despesa_str:
            data_obj = pessoa.Pessoa._parse_data(data_despesa_str, is_datetime=False)
            data_compra = datetime.combine(data_obj, datetime.min.time())
        else:
            data_compra = datetime.now()

        if isinstance(self._item_comprado, produto.Produto):
            self._item_comprado.estoque += self._quantidade
            self._item_comprado.custo_compra = self._valor_unitario
            self._item_comprado._historico_custo_compra.append((
                data_compra,
                self._quantidade,
                self._valor_unitario
            ))
        elif isinstance(self._item_comprado, mod_suprimento.Suprimento):
            self._item_comprado.estoque += self._quantidade
            self._item_comprado.custo_unitario = self._valor_unitario
            self._item_comprado._historico_custo_compra.append((
                data_compra,
                self._quantidade,
                self._valor_unitario
            ))

    def __str__(self) -> str:
        base_str = super().__str__()
        if isinstance(self._item_comprado, (produto.Produto, mod_suprimento.Suprimento)):
            desc_item = self._item_comprado.nome
        elif isinstance(self._item_comprado, mod_maquina.Maquina):
            desc_item = f"{self._item_comprado.nome} (Série: {self._item_comprado.numero_serie})"
        else:
            desc_item = self._item_comprado

        return (f"[COMPRA] {base_str}\n"
                f"  Fornecedor: {self._fornecedor_obj.nome} (ID: {self._fornecedor_obj.id}) | Item: {desc_item} "
                f"(Qtd: {self._quantidade:.2f}, Valor Unit.: R${self._valor_unitario:.2f})")

    def __repr__(self) -> str:
        id_item_repr = None
        if isinstance(self._item_comprado, (produto.Produto, mod_suprimento.Suprimento, mod_maquina.Maquina)):
            id_item_repr = self._item_comprado.id
        elif isinstance(self._item_comprado, str):
            id_item_repr = self._item_comprado

        return (f"Compra(id_despesa={self.id!r}, fornecedor_obj={self.fornecedor_obj.cnpj!r}, "
                f"item_comprado_ref={id_item_repr!r}, "
                f"quantidade={self.quantidade!r}, valor_unitario={self.valor_unitario!r}, "
                f"data_despesa_str={self.data_despesa.strftime('%d/%m/%Y')!r}, comentario={self.comentario!r})")

    @property
    def fornecedor_obj(self) -> mod_fornecedor.Fornecedor:
        return self._fornecedor_obj

    @property
    def item_comprado(self) -> Union[produto.Produto, mod_suprimento.Suprimento, mod_maquina.Maquina, str]:
        return self._item_comprado

    @property
    def quantidade(self) -> float:
        return self._quantidade

    @property
    def valor_unitario(self) -> float:
        return self._valor_unitario

class FixoTerceiro(Despesa):
    def __init__(self, id_despesa: Optional[int], valor: float, tipo_despesa_str: str,
                 fornecedor_obj: Optional[mod_fornecedor.Fornecedor] = None,
                 data_despesa_str: Optional[str] = None, comentario: Optional[str] = None) -> None:

        if not isinstance(tipo_despesa_str, str) or not tipo_despesa_str.strip():
            raise ValueError("O tipo da despesa deve ser uma string não vazia.")
        if fornecedor_obj is not None and not isinstance(fornecedor_obj, mod_fornecedor.Fornecedor):
            raise TypeError("O fornecedor deve ser uma instância de Fornecedor ou None.")

        super().__init__(id_despesa, valor, data_despesa_str, comentario)

        self._tipo_despesa_str = tipo_despesa_str.strip()
        self._fornecedor_obj = fornecedor_obj

    def __str__(self) -> str:
        base_str = super().__str__()
        info_fornecedor = f" | Fornecedor: {self._fornecedor_obj.nome} (ID: {self._fornecedor_obj.id})" if self._fornecedor_obj else "N/A"
        return (f"[FIXO/TERCEIRO] {base_str}\n"
                f"  Tipo: {self._tipo_despesa_str}{info_fornecedor}")

    def __repr__(self) -> str:
        fornecedor_repr = self.fornecedor_obj.cnpj if self.fornecedor_obj else None
        return (f"FixoTerceiro(id_despesa={self.id!r}, valor={self.valor_total!r}, "
                f"tipo_despesa_str={self.tipo_despesa_str!r}, fornecedor_obj={fornecedor_repr!r}, "
                f"data_despesa_str={self.data_despesa.strftime('%d/%m/%Y')!r}, comentario={self.comentario!r})")

    @property
    def tipo_despesa_str(self) -> str:
        return self._tipo_despesa_str

    @property
    def fornecedor_obj(self) -> Optional[mod_fornecedor.Fornecedor]:
        return self._fornecedor_obj

class Salario(Despesa):
    def __init__(self, id_despesa: Optional[int], funcionario_obj: mod_funcionario.Funcionario,
                 salario_bruto: float, descontos: float,
                 data_despesa_str: Optional[str] = None, comentario: Optional[str] = None) -> None:

        if not isinstance(funcionario_obj, mod_funcionario.Funcionario):
            raise TypeError("O funcionário deve ser uma instância de Funcionario.")
        if not isinstance(salario_bruto, (int, float)) or salario_bruto <= 0:
            raise ValueError("O salário bruto deve ser um número positivo.")
        if not isinstance(descontos, (int, float)) or descontos < 0:
            raise ValueError("Os descontos devem ser um número não negativo.")
        if descontos > salario_bruto:
            raise ValueError("Os descontos não podem ser maiores que o salário bruto.")

        valor_final = salario_bruto - descontos
        super().__init__(id_despesa, valor_final, data_despesa_str, comentario)

        self._funcionario_obj = funcionario_obj
        self._salario_bruto = float(salario_bruto)
        self._descontos = float(descontos)

    def __str__(self) -> str:
        base_str = super().__str__()
        return (f"[SALÁRIO] {base_str}\n"
                f"  Funcionário: {self._funcionario_obj.nome} (ID: {self._funcionario_obj.id}) | Bruto: R${self._salario_bruto:.2f} | "
                f"Descontos: R${self._descontos:.2f}")

    def __repr__(self) -> str:
        return (f"Salario(id_despesa={self.id!r}, funcionario_obj_cpf={self.funcionario_obj.cpf!r}, "
                f"salario_bruto={self.salario_bruto!r}, descontos={self.descontos!r}, "
                f"data_despesa_str={self.data_despesa.strftime('%d/%m/%Y')!r}, comentario={self.comentario!r})")

    @property
    def funcionario_obj(self) -> mod_funcionario.Funcionario:
        return self._funcionario_obj

    @property
    def salario_bruto(self) -> float:
        return self._salario_bruto

    @property
    def descontos(self) -> float:
        return self._descontos

class Comissao(Despesa):
    def __init__(self, id_despesa: Optional[int], funcionario_obj: mod_funcionario.Funcionario,
                 valor_soma_servicos: float, valor_soma_produtos: float,
                 taxa_servicos: float, taxa_produtos: float,
                 data_despesa_str: Optional[str] = None, comentario: Optional[str] = None) -> None:

        if not isinstance(funcionario_obj, mod_funcionario.Funcionario):
            raise TypeError("O funcionário deve ser uma instância de Funcionario.")
        if not isinstance(valor_soma_servicos, (int, float)) or valor_soma_servicos < 0:
            raise ValueError("O valor de soma de serviços deve ser um número não negativo.")
        if not isinstance(valor_soma_produtos, (int, float)) or valor_soma_produtos < 0:
            raise ValueError("O valor de soma de produtos deve ser um número não negativo.")
        if not isinstance(taxa_servicos, (int, float)) or not (0 <= taxa_servicos <= 1):
            raise ValueError("A taxa de serviços deve ser um número entre 0 e 1 (0% a 100%).")
        if not isinstance(taxa_produtos, (int, float)) or not (0 <= taxa_produtos <= 1):
            raise ValueError("A taxa de produtos deve ser um número entre 0 e 1 (0% a 100%).")

        valor_final_comissao = (valor_soma_servicos * taxa_servicos) + (valor_soma_produtos * taxa_produtos)
        super().__init__(id_despesa, valor_final_comissao, data_despesa_str, comentario)

        self._funcionario_obj = funcionario_obj
        self._valor_soma_servicos = float(valor_soma_servicos)
        self._valor_soma_produtos = float(valor_soma_produtos)
        self._taxa_servicos = float(taxa_servicos)
        self._taxa_produtos = float(taxa_produtos)

    def __str__(self) -> str:
        base_str = super().__str__()
        return (f"[COMISSÃO] {base_str}\n"
                f"  Funcionário: {self._funcionario_obj.nome} (ID: {self._funcionario_obj.id}) | Soma Serviços: R${self._valor_soma_servicos:.2f} (Taxa: {self._taxa_servicos:.2%}) | "
                f"Soma Produtos: R${self._valor_soma_produtos:.2f} (Taxa: {self._taxa_produtos:.2%})")

    def __repr__(self) -> str:
        return (f"Comissao(id_despesa={self.id!r}, funcionario_obj_cpf={self.funcionario_obj.cpf!r}, "
                f"valor_soma_servicos={self.valor_soma_servicos!r}, valor_soma_produtos={self.valor_soma_produtos!r}, "
                f"taxa_servicos={self.taxa_servicos!r}, taxa_produtos={self.taxa_produtos!r}, "
                f"data_despesa_str={self.data_despesa.strftime('%d/%m/%Y')!r}, comentario={self.comentario!r})")

    @property
    def funcionario_obj(self) -> mod_funcionario.Funcionario:
        return self._funcionario_obj

    @property
    def valor_soma_servicos(self) -> float:
        return self._valor_soma_servicos

    @property
    def valor_soma_produtos(self) -> float:
        return self._valor_soma_produtos

    @property
    def taxa_servicos(self) -> float:
        return self._taxa_servicos

    @property
    def taxa_produtos(self) -> float:
        return self._taxa_produtos

class Outros(Despesa):
    def __init__(self, id_despesa: Optional[int], valor: float, tipo_despesa_str: str,
                 data_despesa_str: Optional[str] = None, comentario: Optional[str] = None) -> None:

        if not isinstance(tipo_despesa_str, str) or not tipo_despesa_str.strip():
            raise ValueError("O tipo da despesa deve ser uma string não vazia.")

        super().__init__(id_despesa, valor, data_despesa_str, comentario)

        self._tipo_despesa_str = tipo_despesa_str.strip()

    def __str__(self) -> str:
        base_str = super().__str__()
        return (f"[OUTROS] {base_str}\n"
                f"  Tipo: {self._tipo_despesa_str}")

    def __repr__(self) -> str:
        return (f"Outros(id_despesa={self.id!r}, valor={self.valor_total!r}, "
                f"tipo_despesa_str={self.tipo_despesa_str!r}, "
                f"data_despesa_str={self.data_despesa.strftime('%d/%m/%Y')!r}, comentario={self.comentario!r})")

    @property
    def tipo_despesa_str(self) -> str:
        return self._tipo_despesa_str
