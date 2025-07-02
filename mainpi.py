
from sqlalchemy.orm import Session
import sys, os
from datetime import datetime, date
from typing import Optional, Any, Callable, Union
import tabulate

import database
from pessoa import analisar_data_flexivel, formatar_validar_nome_completo
import pessoa as mod_pessoa
import info as mod_info
import funcionario as crud_funcionario
import cliente as crud_cliente
import produto as crud_produto
import servico as crud_servico
import agenda as crud_agenda
import venda as crud_venda
import fornecedor as crud_fornecedor
import suprimento as crud_suprimento
import maquina as crud_maquina
from maquina import StatusMaquina
import despesa as crud_despesa

# --- Funções Auxiliares de UI e Sistema ---
def limpar_tela(): os.system('cls' if os.name == 'nt' else 'clear')
def esperar_enter(): input("\nPressione Enter para continuar...")

class InterrompidoPeloUsuario(Exception):
    pass

def _exportar_relatorio(nome_base_arquivo: str, filtros_usados: dict, conteudo_relatorio: str):
    timestamp = datetime.now().strftime('%d%m%Y%H%M%S')
    nome_arquivo = f"{nome_base_arquivo}-{timestamp}.txt"

    cabecalho_filtro = ["Relatório Gerado em: " + datetime.now().strftime('%d/%m/%Y %H:%M:%S')]
    cabecalho_filtro.append("Filtros Aplicados:")
    if not filtros_usados:
        cabecalho_filtro.append("  - Nenhum")
    else:
        for chave, valor in filtros_usados.items():
            cabecalho_filtro.append(f"  - {chave}: {valor}")
    
    cabecalho_texto = "\n".join(cabecalho_filtro)
    
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(cabecalho_texto)
            f.write("\n" + "="*50 + "\n\n")
            f.write(conteudo_relatorio)
        print(f"\nRelatório exportado com sucesso para o arquivo: {nome_arquivo}")
    except IOError as e:
        print(f"\nErro ao exportar relatório: {e}")

def _tratar_saida_relatorio(db: Session, nome_modulo: str, dados_relatorio: list[Any], funcao_formatacao: Callable, filtros_usados: dict):
    if not dados_relatorio:
        print("\nNenhum registro encontrado para os filtros selecionados.")
        return

    conteudo = funcao_formatacao(db, dados_relatorio)

    while True:
        escolha = solicitar_string("Como deseja ver o relatório? (1. Tela, 2. Exportar para .txt)")
        if escolha == '1':
            print(conteudo)
            break
        elif escolha == '2':
            nome_base = nome_modulo.lower()
            if nome_modulo == 'Despesas' and filtros_usados.get('Tipos'):
                tipos_str = '-'.join(sorted(filtros_usados['Tipos']))
                nome_base = tipos_str
            
            _exportar_relatorio(nome_base, filtros_usados, conteudo)
            break
        else:
            print("Opção inválida. Tente novamente.")

def solicitar_string(prompt: str, min_len: int = 1) -> str:
    while True:
        entrada = input(f"{prompt} (ou 'c' para cancelar): ").strip()
        if entrada.lower() == 'c': raise InterrompidoPeloUsuario()
        if len(entrada) >= min_len: return entrada
        print(f"Erro: A entrada deve ter pelo menos {min_len} caracteres. Tente novamente.")

def solicitar_float(prompt: str, min_val: float = 0.0, max_val: Optional[float] = None) -> float:
    while True:
        entrada_str = input(f"{prompt} (ou 'c' para cancelar): ").strip().replace(',', '.')
        if entrada_str.lower() == 'c': raise InterrompidoPeloUsuario()
        try:
            valor = float(entrada_str)
            if valor < min_val: 
                print(f"Erro: O valor deve ser no mínimo {min_val}. Tente novamente.")
            elif max_val is not None and valor > max_val: 
                print(f"Erro: O valor deve ser no máximo {max_val}. Tente novamente.")
            else: 
                return valor
        except ValueError: 
            print("Erro: Entrada inválida. Por favor, insira um número. Tente novamente.")

def solicitar_sim_nao(prompt: str) -> bool:
    while True:
        resp = input(f"{prompt} (s/n, ou 'c' para cancelar): ").strip().lower()
        if resp == 'c': raise InterrompidoPeloUsuario()
        if resp in ['s', 'n']: return resp == 's'
        print("Resposta inválida. Use 's' para sim ou 'n' para não.")

def _executar_crud(funcao_crud, db: Session, **kwargs):
    try:
        funcao_crud(db, **kwargs)
        print("\nOperação realizada com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"\nErro na operação: {e}")

def solicitar_int(prompt: str, min_val: int = 0) -> int:
    while True:
        entrada_str = input(f"{prompt} (ou 'c' para cancelar): ").strip()
        if entrada_str.lower() == 'c': raise InterrompidoPeloUsuario()
        try:
            valor = int(entrada_str)
            if valor >= min_val: return valor
            print(f"Erro: O valor deve ser no mínimo {min_val}. Tente novamente.")
        except ValueError: 
            print("Erro: Entrada inválida. Por favor, insira um número inteiro. Tente novamente.")

def solicitar_data(prompt: str) -> date:
    while True:
        entrada_str = input(f"{prompt} (ex: 25/12/23 ou 25-12-2023): ").strip()
        if entrada_str.lower() == 'c': raise InterrompidoPeloUsuario()
        try:
            return analisar_data_flexivel(entrada_str, is_datetime=False)
        except ValueError as e:
            print(f"Erro: {e} Tente novamente.")

def solicitar_data_hora(prompt: str) -> datetime:
    while True:
        entrada_str = input(f"{prompt} (ex: 25/12/23 14:30): ").strip()
        if entrada_str.lower() == 'c': raise InterrompidoPeloUsuario()
        try:
            return analisar_data_flexivel(entrada_str, is_datetime=True)
        except ValueError as e:
            print(f"Erro: {e} Tente novamente.")

def solicitar_nome_completo_valido() -> str:
    while True:
        nome_str = solicitar_string("Nome Completo")
        try:
            return formatar_validar_nome_completo(nome_str)
        except (ValueError, InterrompidoPeloUsuario) as e:
            if isinstance(e, InterrompidoPeloUsuario): raise e
            print(f"Erro: {e} Tente novamente.")

def solicitar_cpf_valido(db: Session, prompt: str, id_atual: Optional[int] = None) -> str:
    while True:
        cpf_str = solicitar_string(prompt)
        try:
            cpf_limpo = "".join(filter(str.isdigit, cpf_str))
            if not mod_pessoa.Pessoa._eh_cpf_valido(cpf_limpo):
                raise ValueError("CPF inválido (formato ou dígito verificador incorreto).")

            cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

            conflito_cliente = crud_cliente.buscar_cliente_cpf(db, cpf_formatado)
            if conflito_cliente and conflito_cliente.id != id_atual:
                raise ValueError("CPF já cadastrado para um cliente.")
            
            conflito_func = crud_funcionario.buscar_funcionario_por_cpf(db, cpf_formatado)
            if conflito_func and conflito_func.id != id_atual:
                 raise ValueError("CPF já cadastrado para um funcionário.")

            return cpf_formatado
        except (ValueError, InterrompidoPeloUsuario) as e:
            if isinstance(e, InterrompidoPeloUsuario): raise e
            print(f"Erro: {e} Tente novamente.")

def solicitar_info_contato_valida() -> mod_info.Informacao:
    while True:
        telefone_str = solicitar_string("Telefone")
        try:
            mod_info.Informacao.validar_e_formatar_telefone(telefone_str)
            break
        except ValueError as e:
            print(f"Erro no telefone: {e}. Tente novamente.")
    while True:
        email_str = solicitar_string("Email")
        try:
            mod_info.Informacao(telefone=telefone_str, email=email_str, endereco="Rua Teste, 1", redes_sociais="")
            break
        except ValueError as e:
            print(f"Erro no e-mail: {e}. Tente novamente.")
    while True:
        endereco_str = solicitar_string("Endereço (Ex: Rua Alfa, 123, Bairro, Cidade, UF)")
        try:
            mod_info.Informacao(telefone=telefone_str, email=email_str, endereco=endereco_str, redes_sociais="")
            break
        except ValueError as e:
            print(f"Erro no endereço: {e}. Tente novamente.")

    redes_str = input("Redes Sociais (opcional, ou 'c' para cancelar): ").strip()
    if redes_str.lower() == 'c': raise InterrompidoPeloUsuario()
    
    return mod_info.Informacao(telefone=telefone_str, email=email_str, endereco=endereco_str, redes_sociais=redes_str)

def _selecionar_objeto_ui(db: Session, nome_entidade: str, funcao_busca_id: Callable) -> Any:
    while True:
        id_num = solicitar_int(f"ID do(a) {nome_entidade}")
        objeto = funcao_busca_id(db, id_num)
        if objeto:
            nome_exibicao = getattr(objeto, 'nome', f"ID {objeto.id}")
            print(f"--> {nome_entidade} selecionado(a): {nome_exibicao}")
            return objeto
        else:
            print(f"{nome_entidade} com ID {id_num} não encontrado.")
        if not solicitar_sim_nao("Tentar novamente?"):
             raise InterrompidoPeloUsuario()
        
def _selecionar_servico_ou_produto_ui(db: Session) -> Union[crud_produto.Produto, crud_servico.Servico]:
    while True:
        print("\nQual tipo de item deseja adicionar?")
        print("1. Serviço")
        print("2. Produto")
        print("0. Voltar/Cancelar")

        tipo_escolha = solicitar_string("Escolha o tipo")
        if tipo_escolha == '1':
            print("\n--- Lista de Serviços Disponíveis ---")
            _listar_servicos_ui(db)
            return _selecionar_objeto_ui(db, "Serviço", crud_servico.buscar_servico_id)
        elif tipo_escolha == '2':
            print("\n--- Lista de Produtos Disponíveis ---")
            _listar_produtos_ui(db)
            return _selecionar_objeto_ui(db, "Produto", crud_produto.buscar_produto_id)
        elif tipo_escolha == '0':
            raise InterrompidoPeloUsuario()
        else:
            print("Opção inválida. Tente novamente.")

def _selecionar_produto_ou_suprimento_ui(db: Session) -> Union[crud_produto.Produto, crud_suprimento.Suprimento]:
    while True:
        print("\nQual tipo de item foi comprado?")
        print("1. Produto (para revenda)")
        print("2. Suprimento (para uso interno)")
        print("0. Voltar/Cancelar")

        tipo_escolha = solicitar_string("Escolha o tipo")

        if tipo_escolha == '1':
            print("\n--- Lista de Produtos Cadastrados ---")
            _listar_produtos_ui(db)
            return _selecionar_objeto_ui(db, "Produto", crud_produto.buscar_produto_id)
        elif tipo_escolha == '2':
            print("\n--- Lista de Suprimentos Cadastrados ---")
            _listar_suprimentos_ui(db)
            return _selecionar_objeto_ui(db, "Suprimento", crud_suprimento.buscar_suprimento_id)
        elif tipo_escolha == '0':
            raise InterrompidoPeloUsuario()
        else:
            print("Opção inválida. Tente novamente.")

def _selecionar_entidade_ui(db: Session, nome_entidade: str, funcao_busca_id: Callable, funcao_busca_nome: Callable) -> Any:
    while True:
        metodo = solicitar_string(f"Buscar {nome_entidade} por (id/nome)?", min_len=2)
        if metodo.lower() not in ['id', 'nome']:
            print("Opção inválida. Digite 'id' ou 'nome'.")
            continue

        if metodo.lower() == 'id':
            return _selecionar_objeto_ui(db, nome_entidade, funcao_busca_id)

        elif metodo.lower() == 'nome':
            nome_busca = solicitar_string(f"Digite o nome (ou parte do nome) do(a) {nome_entidade}")
            resultados = funcao_busca_nome(db, nome_busca)

            if not resultados:
                print("Nenhuma correspondência encontrada.")
                continue

            exatas = [r for r in resultados if r.nome.lower() == nome_busca.lower()]
            if len(exatas) == 1:
                print(f"--> {nome_entidade} selecionado(a) por nome exato: {exatas[0].nome}")
                return exatas[0]

            if len(resultados) == 1:
                print(f"--> {nome_entidade} selecionado(a): {resultados[0].nome}")
                return resultados[0]
            
            print("\nMúltiplas correspondências encontradas:")
            for res in resultados:
                print(f"  ID: {res.id}, Nome: {res.nome}")
            
            id_num_escolha = solicitar_int("\nDigite o ID exato para selecionar")
            entidade_escolhida = next((res for res in resultados if res.id == id_num_escolha), None)

            if entidade_escolhida:
                print(f"--> {nome_entidade} selecionado(a): {entidade_escolhida.nome}")
                return entidade_escolhida
            print("Erro: ID inválido ou não corresponde aos resultados da busca.")

# --- Funções de UI ---
def _cadastrar_cliente_ui(db: Session):
    print("--- Cadastrar Cliente ---")
    try:
        nome = solicitar_nome_completo_valido()
        nascimento_obj = solicitar_data("Data de Nascimento")
        cpf = solicitar_cpf_valido(db, "CPF")
        info_contato = solicitar_info_contato_valida()
        _executar_crud(crud_cliente.criar_cliente, db, nome=nome, nascimento_obj=nascimento_obj, cpf=cpf, info_contato=info_contato)
    except InterrompidoPeloUsuario:
        print("\nCadastro cancelado.")

def _listar_clientes_ui(db: Session): _tratar_saida_relatorio(db, 'Clientes', crud_cliente.listar_clientes(db), crud_cliente._formatar_clientes_para_tabela, {})

def _atualizar_cliente_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Cliente", crud_cliente.buscar_cliente_id, crud_cliente.buscar_clientes_por_nome)
        alteracoes = {}
        if solicitar_sim_nao("Alterar nome?"):
            alteracoes['nome'] = solicitar_nome_completo_valido()
        if solicitar_sim_nao("Alterar data de nascimento?"):
            alteracoes['nascimento'] = solicitar_data(f"Nova Data (atual: {obj.nascimento.strftime('%d/%m/%Y')})")
        if solicitar_sim_nao("Alterar informações de contato?"):
            alteracoes['info_contato'] = solicitar_info_contato_valida()
        
        if alteracoes:
            _executar_crud(crud_cliente.atualizar_dados_cliente, db, id_cliente=obj.id, **alteracoes)
        else:
            print("\nNenhuma alteração realizada.")
    except InterrompidoPeloUsuario:
        print("\nAtualização cancelada.")

def _deletar_cliente_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Cliente", crud_cliente.buscar_cliente_id, crud_cliente.buscar_clientes_por_nome)
        if db.query(crud_agenda.Agenda).filter_by(cliente_id=obj.id).first() or db.query(crud_venda.Venda).filter_by(cliente_id=obj.id).first():
            print(f"\nErro: Cliente '{obj.nome}' não pode ser deletado pois está em uso."); return
        if solicitar_sim_nao(f"Deletar '{obj.nome}'?"):
            _executar_crud(crud_cliente.deletar_cliente, db, id_cliente=obj.id)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _cadastrar_funcionario_ui(db: Session):
    print("--- Cadastrar Funcionário ---")
    try:
        nome = solicitar_nome_completo_valido()
        nascimento_obj = solicitar_data("Data de Nascimento")
        cpf = solicitar_cpf_valido(db, "CPF")
        ctps = solicitar_string("CTPS")
        salario = solicitar_float("Salário", min_val=0.01)
        data_admissao_obj = solicitar_data("Data de Admissão")
        nis_str = input("NIS (11 dígitos, opcional, ou 'c' para cancelar): ").strip()
        if nis_str.lower() == 'c': raise InterrompidoPeloUsuario()
        info_contato = solicitar_info_contato_valida()
        dados = {
            'nome': nome, 'nascimento_obj': nascimento_obj, 'cpf': cpf, 'ctps': ctps,
            'salario': salario, 'data_admissao_obj': data_admissao_obj,
            'nis': nis_str if nis_str else None, 'informacao_contato': info_contato
        }
        _executar_crud(crud_funcionario.criar_funcionario, db, **dados)
    except InterrompidoPeloUsuario:
        print("\nCadastro cancelado.")

def _listar_funcionarios_ui(db: Session): _tratar_saida_relatorio(db, 'Funcionários', crud_funcionario.listar_funcionarios(db), crud_funcionario._formatar_funcionarios_para_tabela, {})

def _atualizar_funcionario_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Funcionário", crud_funcionario.buscar_funcionario_por_id, crud_funcionario.buscar_funcionarios_por_nome)
        alteracoes = {}
        if solicitar_sim_nao("Alterar nome?"):
            alteracoes['nome'] = solicitar_nome_completo_valido()
        if solicitar_sim_nao("Alterar salário?"):
            alteracoes['salario'] = solicitar_float("Novo Salário")
        if solicitar_sim_nao("Alterar data de demissão?"):
            demissao_atual = obj.data_demissao.strftime('%d/%m/%Y') if obj.data_demissao else "N/A"
            alteracoes['data_demissao'] = solicitar_data(f"Nova Data Demissão (atual: {demissao_atual})")
        if alteracoes: _executar_crud(crud_funcionario.atualizar_dados_funcionario, db, id_func=obj.id, **alteracoes)
    except InterrompidoPeloUsuario:
        print("\nAtualização cancelada.")

def _deletar_funcionario_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Funcionário", crud_funcionario.buscar_funcionario_por_id, crud_funcionario.buscar_funcionarios_por_nome)
        if db.query(crud_agenda.Agenda).filter_by(funcionario_id=obj.id).first() or db.query(crud_venda.Venda).filter_by(funcionario_id=obj.id).first() or db.query(crud_despesa.Salario).filter_by(funcionario_id=obj.id).first():
            print(f"\nErro: Funcionário '{obj.nome}' não pode ser deletado pois está em uso."); return
        if solicitar_sim_nao(f"Deletar '{obj.nome}'?"): _executar_crud(crud_funcionario.deletar_funcionario_por_id, db, id_func=obj.id)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _cadastrar_produto_ui(db: Session):
    print("--- Cadastrar Produto ---")
    try:
        while True:
            nome = solicitar_string("Nome do Produto")
            if not crud_produto.buscar_produto(db, nome): break
            print("Erro: Nome de produto já existe. Tente outro.")

        preco = solicitar_float("Preço", min_val=0.01)
        estoque = solicitar_float("Estoque")

        _executar_crud(crud_produto.criar_produto, db, nome=nome, preco=preco, estoque=estoque)
    except InterrompidoPeloUsuario:
        print("\nCadastro cancelado.")

def _listar_produtos_ui(db: Session): _tratar_saida_relatorio(db, 'Produtos', crud_produto.listar_produtos(db), crud_produto._formatar_produtos_para_tabela, {})

def _atualizar_produto_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Produto", crud_produto.buscar_produto_id, crud_produto.buscar_produto_id)
        alteracoes = {}
        if solicitar_sim_nao("Alterar nome?"):
            alteracoes['nome'] = solicitar_string(f"Novo Nome (atual: {obj.nome})")
        if solicitar_sim_nao("Alterar preço?"):
            alteracoes['preco'] = solicitar_float("Novo Preço", 0.01)
        if solicitar_sim_nao("Alterar estoque?"):
            alteracoes['estoque'] = solicitar_float("Novo Estoque")
        if alteracoes: _executar_crud(crud_produto.atualizar_dados_produto, db, id_produto=obj.id, **alteracoes)
    except InterrompidoPeloUsuario:
        print("\nAtualização cancelada.")

def _deletar_produto_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Produto", crud_produto.buscar_produto_id, crud_produto.buscar_produto_id)
        if db.query(database.agenda_itens_tabela).filter_by(item_tipo='Produto', item_id=obj.id).first() or db.query(database.venda_itens_tabela).filter_by(item_tipo='Produto', item_id=obj.id).first():
            print(f"\nErro: Produto '{obj.nome}' não pode ser deletado pois está em uso."); return
        if solicitar_sim_nao(f"Deletar '{obj.nome}'?"):
            _executar_crud(crud_produto.deletar_produto, db, id_produto=obj.id)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _ver_historico_compras_produto_ui(db: Session):
    print("--- Histórico de Compras de Produto ---")
    try:
        _listar_produtos_ui(db)
        produto_obj = _selecionar_objeto_ui(db, "Produto", crud_produto.buscar_produto_id)
        
        print(f"\nExibindo histórico para: {produto_obj.nome}")
        historico = produto_obj.historico_custo_compra
        tabela_historico = crud_produto._formatar_historico_para_tabela(historico)
        print(tabela_historico)

    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _cadastrar_suprimento_ui(db: Session):
    print("--- Cadastrar Suprimento ---")
    try:
        nome = solicitar_string("Nome")
        unidade = solicitar_string("Unidade de Medida")
        custo = solicitar_float("Custo Unitário", 0.01)
        estoque = solicitar_float("Estoque Inicial", 0.0)
        _executar_crud(crud_suprimento.criar_suprimento, db, nome=nome, unidade_medida=unidade, custo_unitario=custo, estoque=estoque)
    except InterrompidoPeloUsuario:
        print("\nCadastro cancelado.")

def _listar_suprimentos_ui(db: Session): _tratar_saida_relatorio(db, 'Suprimentos', crud_suprimento.listar_suprimentos(db), crud_suprimento._formatar_suprimentos_para_tabela, {})

def _atualizar_suprimento_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Suprimento", crud_suprimento.buscar_suprimento_id, crud_suprimento.buscar_suprimento_nome)
        alteracoes = {}
        if solicitar_sim_nao("Alterar nome?"):
            alteracoes['nome'] = solicitar_string(f"Novo Nome (atual: {obj.nome})")
        if solicitar_sim_nao("Alterar unidade de medida?"):
            alteracoes['unidade_medida'] = solicitar_string(f"Nova Unidade (atual: {obj.unidade_medida})")
        if solicitar_sim_nao("Alterar custo unitário?"):
            alteracoes['custo_unitario'] = solicitar_float("Novo Custo", 0.01)
        if solicitar_sim_nao("Alterar estoque?"):
            alteracoes['estoque'] = solicitar_float("Novo Estoque")
        if alteracoes: _executar_crud(crud_suprimento.atualizar_dados_suprimento, db, id_suprimento=obj.id, **alteracoes)
    except InterrompidoPeloUsuario:
        print("\nAtualização cancelada.")

def _deletar_suprimento_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Suprimento", crud_suprimento.buscar_suprimento_id, crud_suprimento.buscar_suprimento_nome)
        if db.query(database.agenda_suprimentos_tabela).filter_by(suprimento_id=obj.id).first():
            print(f"\nErro: Suprimento '{obj.nome}' não pode ser deletado pois está em uso em Agendas."); return
        if solicitar_sim_nao(f"Deletar '{obj.nome}'?"):
            _executar_crud(crud_suprimento.deletar_suprimento, db, id_suprimento=obj.id)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _ver_historico_compras_suprimento_ui(db: Session):
    print("--- Histórico de Compras de Suprimento ---")
    try:
        _listar_suprimentos_ui(db)
        suprimento_obj = _selecionar_objeto_ui(db, "Suprimento", crud_suprimento.buscar_suprimento_id)

        print(f"\nExibindo histórico para: {suprimento_obj.nome}")
        historico = suprimento_obj.historico_custo_compra
        tabela_historico = crud_suprimento._formatar_historico_para_tabela(historico)
        print(tabela_historico)

    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _cadastrar_servico_ui(db: Session):
    print("--- Cadastrar Serviço ---")
    try:
        while True:
            nome = solicitar_string("Nome do Serviço")
            if not crud_servico.buscar_servico(db, nome): break
            print("Erro: Nome de serviço já existe. Tente outro.")

        valor = solicitar_float("Valor", min_val=0.01)
        custo = solicitar_float("Custo", min_val=0.01)

        _executar_crud(crud_servico.criar_servico, db, nome=nome, valor_venda=valor, custo=custo)
    except InterrompidoPeloUsuario:
        print("\nCadastro cancelado.")

def _listar_servicos_ui(db: Session): _tratar_saida_relatorio(db, 'Serviços', crud_servico.listar_servicos(db), crud_servico._formatar_servicos_para_tabela, {})

def _atualizar_servico_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Serviço", crud_servico.buscar_servico_id, crud_servico.buscar_servico_id)
        alteracoes = {}
        if solicitar_sim_nao("Alterar nome?"):
            alteracoes['nome'] = solicitar_string(f"Novo Nome (atual: {obj.nome})")
        if solicitar_sim_nao("Alterar valor?"):
            alteracoes['valor_venda'] = solicitar_float("Novo Valor", 0.01)
        if solicitar_sim_nao("Alterar custo?"):
            alteracoes['custo'] = solicitar_float("Novo Custo", 0.01)
        if alteracoes: _executar_crud(crud_servico.atualizar_dados_servico, db, id_servico=obj.id, **alteracoes)
    except InterrompidoPeloUsuario:
        print("\nAtualização cancelada.")

def _deletar_servico_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Serviço", crud_servico.buscar_servico_id, crud_servico.buscar_servico_id)
        if db.query(database.agenda_itens_tabela).filter_by(item_tipo='Servico', item_id=obj.id).first() or db.query(database.venda_itens_tabela).filter_by(item_tipo='Servico', item_id=obj.id).first():
            print(f"\nErro: Serviço '{obj.nome}' não pode ser deletado pois está em uso."); return
        if solicitar_sim_nao(f"Deletar '{obj.nome}'?"):
            _executar_crud(crud_servico.deletar_servico, db, id_servico=obj.id)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _cadastrar_fornecedor_ui(db: Session):
    print("--- Cadastrar Fornecedor ---")
    try:
        nome = solicitar_string("Nome do Fornecedor (Razão Social)")
        while True:
            cnpj = solicitar_string("CNPJ")
            try:
                if crud_fornecedor.buscar_fornecedor(db, cnpj): raise ValueError("CNPJ já cadastrado.")
                break
            except ValueError as e: print(f"Erro: {e}. Tente novamente.")
        info_contato = solicitar_info_contato_valida()
        _executar_crud(crud_fornecedor.criar_fornecedor, db, nome=nome, cnpj=cnpj, info_contato=info_contato)
    except InterrompidoPeloUsuario:
        print("\nCadastro cancelado.")

def _listar_fornecedores_ui(db: Session): _tratar_saida_relatorio(db, 'Fornecedores', crud_fornecedor.listar_fornecedores(db), crud_fornecedor._formatar_fornecedores_para_tabela, {})

def _atualizar_fornecedor_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Fornecedor", crud_fornecedor.buscar_fornecedor_id, crud_fornecedor.buscar_fornecedores_por_nome)
        alteracoes = {}
        if solicitar_sim_nao("Alterar nome?"):
            alteracoes['nome'] = solicitar_string(f"Novo Nome (atual: {obj.nome})")
        if solicitar_sim_nao("Alterar CNPJ?"):
            alteracoes['cnpj'] = solicitar_string(f"Novo CNPJ (atual: {obj.cnpj})")
        if solicitar_sim_nao("Alterar contato?"):
            alteracoes['info_contato'] = solicitar_info_contato_valida()
        if alteracoes: _executar_crud(crud_fornecedor.atualizar_dados_fornecedor, db, id_fornecedor=obj.id, **alteracoes)
    except InterrompidoPeloUsuario:
        print("\nAtualização cancelada.")

def _deletar_fornecedor_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Fornecedor", crud_fornecedor.buscar_fornecedor_id, crud_fornecedor.buscar_fornecedores_por_nome)
        if db.query(crud_despesa.Compra).filter_by(fornecedor_id=obj.id).first() or db.query(crud_despesa.FixoTerceiro).filter_by(fornecedor_id=obj.id).first():
            print(f"\nErro: Fornecedor '{obj.nome}' não pode ser deletado pois está em uso em Despesas."); return
        if solicitar_sim_nao(f"Deletar '{obj.nome}'?"):
            _executar_crud(crud_fornecedor.deletar_fornecedor, db, id_fornecedor=obj.id)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _cadastrar_maquina_ui(db: Session):
    print("--- Cadastrar Máquina ---")
    try:
        nome = solicitar_string("Nome")
        serie = solicitar_string("Número de Série")
        custo = solicitar_float("Custo de Aquisição", 0.01)
        status_map = {"1": StatusMaquina.OPERANDO, "2": StatusMaquina.MANUTENCAO, "3": StatusMaquina.BAIXADO}
        while True:
            status_str = solicitar_string("Status (1: Operando, 2: Manutenção, 3: Baixado)")
            if status_str in status_map:
                status = status_map[status_str]
                break
            print("Opção de status inválida. Tente novamente.")
        _executar_crud(crud_maquina.criar_maquina, db, nome=nome, numero_serie=serie, custo_aquisicao=custo, status=status)
    except InterrompidoPeloUsuario:
        print("\nCadastro cancelado.")

def _listar_maquinas_ui(db: Session): _tratar_saida_relatorio(db, 'Máquinas', crud_maquina.listar_maquinas(db), crud_maquina._formatar_maquinas_para_tabela, {})

def _atualizar_maquina_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Máquina", crud_maquina.buscar_maquina_id, crud_maquina.buscar_maquina_id)
        alteracoes = {}
        if solicitar_sim_nao("Alterar nome?"):
            alteracoes['nome'] = solicitar_string(f"Novo Nome (atual: {obj.nome})")
        if solicitar_sim_nao("Alterar número de série?"):
            alteracoes['numero_serie'] = solicitar_string(f"Novo Nº Série (atual: {obj.numero_serie})")
        if solicitar_sim_nao("Alterar status?"):
            status_map = {"1": StatusMaquina.OPERANDO, "2": StatusMaquina.MANUTENCAO, "3": StatusMaquina.BAIXADO}
            while True:
                status_str = solicitar_string(f"Status atual: {obj.status.value}. Novo (1: Op, 2: Man, 3: Bx)")
                if status_str in status_map:
                    alteracoes['status'] = status_map[status_str]
                    break
                print("Opção de status inválida. Tente novamente.")
        if alteracoes: _executar_crud(crud_maquina.atualizar_dados_maquina, db, id_maquina=obj.id, **alteracoes)
    except InterrompidoPeloUsuario:
        print("\nAtualização cancelada.")

def _deletar_maquina_ui(db: Session):
    try:
        obj = _selecionar_entidade_ui(db, "Máquina", crud_maquina.buscar_maquina_id, crud_maquina.buscar_maquina_id)
        if db.query(database.agenda_maquinas_tabela).filter_by(maquina_id=obj.id).first():
            print(f"\nErro: Máquina '{obj.nome}' não pode ser deletada pois está em uso em Agendas."); return
        if solicitar_sim_nao(f"Deletar '{obj.nome}'?"):
            _executar_crud(crud_maquina.deletar_maquina, db, id_maquina=obj.id)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _cadastrar_agenda_ui(db: Session):
    print("--- Cadastrar Agenda ---")
    try:
        func = _selecionar_entidade_ui(db, "Funcionário", crud_funcionario.buscar_funcionario_por_id, crud_funcionario.buscar_funcionarios_por_nome)
        cli = _selecionar_entidade_ui(db, "Cliente", crud_cliente.buscar_cliente_id, crud_cliente.buscar_clientes_por_nome)
        
        while True:
            inicio_obj = solicitar_data_hora("Data/Hora de Início")
            fim_obj = solicitar_data_hora("Data/Hora de Fim")
            if fim_obj > inicio_obj: break
            print("Erro: A data/hora de fim deve ser posterior à de início.")

        itens_agendados, maquinas_agendadas, suprimentos_utilizados = [], [], []

        while solicitar_sim_nao("Adicionar serviço ou produto à agenda?"):
            item_sel = _selecionar_servico_ou_produto_ui(db)
            qtd = solicitar_float(f"Quantidade para '{item_sel.nome}'", min_val=0.01)
            valor_padrao = item_sel.valor_venda if isinstance(item_sel, crud_servico.Servico) else item_sel.preco
            valor_negociado = valor_padrao
            if solicitar_sim_nao(f"O valor padrão é R${valor_padrao:.2f}. Deseja alterar?"):
                valor_negociado = solicitar_float("Digite o novo valor", 0.01)
            itens_agendados.append(crud_agenda.ItemAgendado(item_sel, qtd, valor_negociado))

        while solicitar_sim_nao("Vincular máquina a esta agenda?"):
            print("\n--- Máquinas Disponíveis (Operando ou em Manutenção) ---")
            maquinas_disponiveis = [m for m in crud_maquina.listar_maquinas(db) if m.status != StatusMaquina.BAIXADO]
            print(crud_maquina._formatar_maquinas_para_tabela(db, maquinas_disponiveis))
            maquina_sel = _selecionar_objeto_ui(db, "Máquina", crud_maquina.buscar_maquina_id)
            if crud_agenda.verificar_conflito_maquina(db, maquina_sel.id, inicio_obj, fim_obj):
                print(f"Erro: A máquina '{maquina_sel.nome}' já está em uso no horário solicitado.")
            else:
                maquinas_agendadas.append(maquina_sel)
                print(f"Máquina '{maquina_sel.nome}' adicionada.")

        while solicitar_sim_nao("Vincular suprimento a esta agenda?"):
            print("\n--- Suprimentos Disponíveis ---")
            _listar_suprimentos_ui(db)
            suprimento_sel = _selecionar_objeto_ui(db, "Suprimento", crud_suprimento.buscar_suprimento_id)
            while True:
                qtd_sup = solicitar_float(f"Quantidade de '{suprimento_sel.nome}' necessária")
                if qtd_sup <= suprimento_sel.estoque:
                    suprimentos_utilizados.append(crud_agenda.SuprimentoAgendado(suprimento_sel, qtd_sup))
                    print(f"Suprimento '{suprimento_sel.nome}' adicionado.")
                    break
                print(f"Erro: Estoque insuficiente. Disponível: {suprimento_sel.estoque:.2f} {suprimento_sel.unidade_medida}.")

        if not itens_agendados:
            print("Uma agenda precisa de pelo menos um serviço ou produto. Operação cancelada.")
            return

        _executar_crud(crud_agenda.criar_agenda, db, funcionario_obj=func, cliente_obj=cli, 
                       data_hora_inicio_obj=inicio_obj, data_hora_fim_obj=fim_obj, 
                       itens_agendados=itens_agendados, maquinas_agendadas=maquinas_agendadas, 
                       suprimentos_utilizados=suprimentos_utilizados)

    except InterrompidoPeloUsuario:
        print("\nCadastro de agenda cancelado.")

def _listar_agendas_ui(db: Session):
    filtros = {}
    try:
        if solicitar_sim_nao("Deseja aplicar filtros à listagem?"):
            if solicitar_sim_nao("Filtrar por período?"):
                filtros['data_inicio'] = solicitar_data("Data de início")
                filtros['data_fim'] = solicitar_data("Data de fim")
            if solicitar_sim_nao("Filtrar por cliente?"):
                cliente = _selecionar_entidade_ui(db, "Cliente", crud_cliente.buscar_cliente_id, crud_cliente.buscar_clientes_por_nome)
                filtros['cliente_id'] = cliente.id
            if solicitar_sim_nao("Filtrar por funcionário?"):
                func = _selecionar_entidade_ui(db, "Funcionário", crud_funcionario.buscar_funcionario_por_id, crud_funcionario.buscar_funcionarios_por_nome)
                filtros['funcionario_id'] = func.id
    except InterrompidoPeloUsuario:
        print("\nFiltros cancelados. Listando todos os registros.")
        filtros = {}

    agendas = crud_agenda.listar_agendas(db, **filtros)
    _tratar_saida_relatorio(db, 'Agendas', agendas, crud_agenda._formatar_agendas_para_tabela, filtros)

def _atualizar_agenda_ui(db: Session):
    try:
        obj = _selecionar_objeto_ui(db, "Agenda", crud_agenda.buscar_agenda)
        alteracoes = {}
        itens_a_adicionar = []
        ids_a_remover = []
        mudancas_realizadas = False

        if solicitar_sim_nao("Alterar data/hora de início?"):
            inicio_atual = obj.data_hora_inicio.strftime('%d/%m/%Y %H:%M')
            alteracoes['data_hora_inicio'] = solicitar_data_hora(f"Novo Início (atual: {inicio_atual})")
            mudancas_realizadas = True
        if solicitar_sim_nao("Alterar data/hora de fim?"):
            fim_atual = obj.data_hora_fim.strftime('%d/%m/%Y %H:%M')
            alteracoes['data_hora_fim'] = solicitar_data_hora(f"Novo Fim (atual: {fim_atual})")
            mudancas_realizadas = True
        if solicitar_sim_nao("Modificar itens da agenda?"):
            mudancas_realizadas = True
            while True:
                limpar_tela()
                print("--- Itens Atuais na Agenda ---")
                itens_atuais = crud_agenda.get_itens_agendados_detalhes(db, obj.id)
                if not itens_atuais: print("Nenhum item na agenda.")
                else: print(tabulate.tabulate(itens_atuais, headers="keys", tablefmt="grid"))

                print("\nOpções de Itens:\n1. Adicionar item\n2. Remover item\n0. Concluir")
                
                try:
                    escolha = solicitar_string("Escolha uma opção")
                    if escolha == '1':
                        item_sel = _selecionar_servico_ou_produto_ui(db)
                        qtd = solicitar_float(f"Quantidade para '{item_sel.nome}'", min_val=0.01)
                        itens_a_adicionar.append(crud_agenda.ItemAgendado(item_sel, qtd))
                    elif escolha == '2':
                        if not itens_atuais:
                            print("Não há itens para remover."); esperar_enter()
                            continue
                        id_assoc_remover = solicitar_int("Digite o 'id_associacao' do item a ser removido")
                        if any(item['id_associacao'] == id_assoc_remover for item in itens_atuais):
                            ids_a_remover.append(id_assoc_remover)
                            print("Item marcado para remoção.")
                        else:
                            print("ID de associação inválido.")
                    elif escolha == '0':
                        break
                    else:
                        print("Opção inválida.")
                except InterrompidoPeloUsuario:
                    continue

        if alteracoes or mudancas_realizadas:
            _executar_crud(crud_agenda.atualizar_agenda, db, id_agenda=obj.id,
                           itens_a_adicionar=itens_a_adicionar,
                           ids_associacao_a_remover=ids_a_remover,
                           **alteracoes)
        else:
            print("\nNenhuma alteração realizada.")

    except InterrompidoPeloUsuario:
        print("\nAtualização cancelada.")


def _deletar_agenda_ui(db: Session):
    try:
        obj = _selecionar_objeto_ui(db, "Agenda", crud_agenda.buscar_agenda)
        if db.query(crud_venda.Venda).filter_by(agenda_id=obj.id).first():
            print(f"\nErro: Agenda ID {obj.id} não pode ser deletada pois está vinculada a uma Venda."); return
        if solicitar_sim_nao(f"Deletar Agenda ID {obj.id}?"):
            _executar_crud(crud_agenda.deletar_agenda, db, id_agenda=obj.id)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _cadastrar_venda_ui(db: Session):
    print("--- Cadastrar Venda ---")
    try:
        vincular_agenda = solicitar_sim_nao("Esta venda será baseada em uma agenda existente?")
        agenda_obj, func, cli = None, None, None

        if vincular_agenda:
            agenda_obj = _selecionar_objeto_ui(db, "Agenda", crud_agenda.buscar_agenda)
            if agenda_obj.status == crud_agenda.AgendaStatus.REALIZADO:
                print(f"Erro: A Agenda ID {agenda_obj.id} já foi realizada.")
                return
            func, cli = agenda_obj.funcionario, agenda_obj.cliente
            print(f"\nFuncionário selecionado da agenda: {func.nome}")
            print(f"Cliente selecionado da agenda: {cli.nome}\n")
        else:
            func = _selecionar_entidade_ui(db, "Funcionário", crud_funcionario.buscar_funcionario_por_id, crud_funcionario.buscar_funcionarios_por_nome)
            cli = _selecionar_entidade_ui(db, "Cliente", crud_cliente.buscar_cliente_id, crud_cliente.buscar_clientes_por_nome)

        data_obj = solicitar_data("Data da Venda")
        itens = []
        while solicitar_sim_nao("Adicionar item avulso à venda?"):
            item_sel = _selecionar_servico_ou_produto_ui(db)
            qtd = solicitar_float(f"Quantidade para '{item_sel.nome}'", min_val=0.01)
            valor_padrao = item_sel.valor_venda if isinstance(item_sel, crud_servico.Servico) else item_sel.preco
            valor_negociado = valor_padrao
            if solicitar_sim_nao(f"O valor padrão é R${valor_padrao:.2f}. Deseja alterar?"):
                valor_negociado = solicitar_float("Digite o novo valor", 0.01)
            itens.append(crud_venda.ItemVenda(item_sel, qtd, preco_unitario_vendido=valor_negociado))

        if not agenda_obj and not itens:
            print("\nErro: Uma venda sem agenda precisa ter pelo menos um item avulso. Operação cancelada.")
            return

        _executar_crud(crud_venda.criar_venda, db, funcionario_obj=func, cliente_obj=cli, data_venda_obj=data_obj, itens_venda=itens, agenda_obj=agenda_obj)

    except InterrompidoPeloUsuario:
        print("\nCadastro de venda cancelado.")

def _listar_vendas_ui(db: Session):
    filtros = {}
    kwargs_query = {}
    try:
        if solicitar_sim_nao("Deseja aplicar filtros à listagem?"):
            if solicitar_sim_nao("Filtrar por período?"):
                data_inicio = solicitar_data("Data de início")
                data_fim = solicitar_data("Data de fim")
                kwargs_query['data_inicio'] = data_inicio
                kwargs_query['data_fim'] = data_fim
                filtros['Período'] = f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
            if solicitar_sim_nao("Filtrar por cliente?"):
                cliente = _selecionar_entidade_ui(db, "Cliente", crud_cliente.buscar_cliente_id, crud_cliente.buscar_clientes_por_nome)
                kwargs_query['cliente_id'] = cliente.id
                filtros['Cliente'] = f"ID {cliente.id} - {cliente.nome}"
            if solicitar_sim_nao("Filtrar por funcionário?"):
                func = _selecionar_entidade_ui(db, "Funcionário", crud_funcionario.buscar_funcionario_por_id, crud_funcionario.buscar_funcionarios_por_nome)
                kwargs_query['funcionario_id'] = func.id
                filtros['Funcionário'] = f"ID {func.id} - {func.nome}"
    except InterrompidoPeloUsuario:
        print("\nFiltros cancelados. Listando todos os registros.")
        filtros = {}
    
    vendas = crud_venda.listar_vendas(db, **kwargs_query)
    _tratar_saida_relatorio(db, 'Vendas', vendas, crud_venda._formatar_vendas_para_tabela, filtros)


def _atualizar_venda_ui(db: Session):
    try:
        obj = _selecionar_objeto_ui(db, "Venda", crud_venda.buscar_venda)
        alteracoes = {}
        if solicitar_sim_nao("Alterar data da venda?"):
            data_atual_str = obj.data_venda.strftime('%d/%m/%Y')
            alteracoes['data_venda'] = solicitar_data(f"Nova Data (atual: {data_atual_str})")
        if solicitar_sim_nao("Alterar comentário?"):
            comentario_atual = obj.comentario or "Nenhum"
            alteracoes['comentario'] = solicitar_string(f"Novo Comentário (atual: {comentario_atual})", min_len=0)
        if alteracoes:
            _executar_crud(crud_venda.atualizar_dados_venda, db, id_venda=obj.id, **alteracoes)
        else:
            print("\nNenhuma alteração realizada.")
    except InterrompidoPeloUsuario:
        print("\nAtualização cancelada.")

def _deletar_venda_ui(db: Session):
    try:
        obj = _selecionar_objeto_ui(db, "Venda", crud_venda.buscar_venda)
        if solicitar_sim_nao(f"Deletar Venda ID {obj.id}? (Estoque será revertido)"):
            _executar_crud(crud_venda.deletar_venda, db, id_venda=obj.id)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _cadastrar_despesa_ui(db: Session):
    opcoes = {"1": "Compra", "2": "Fixa/Terceiro", "3": "Salário", "4": "Comissão", "5": "Outros"}
    try:
        print("--- Registrar Nova Despesa ---")
        for k, v in opcoes.items(): print(f"{k}. {v}")
        print("0. Voltar")
        while True:
            tipo = solicitar_string("Escolha o tipo")
            if tipo in opcoes: break
            if tipo == '0': raise InterrompidoPeloUsuario()
            print("Opção inválida.")

        if tipo == "1":
            forn = _selecionar_entidade_ui(db, "Fornecedor", crud_fornecedor.buscar_fornecedor_id, crud_fornecedor.buscar_fornecedores_por_nome)
            item_comprado = _selecionar_produto_ou_suprimento_ui(db)
            custo_padrao = getattr(item_comprado, 'custo_compra', getattr(item_comprado, 'custo_unitario', 0.0))
            valor_unitario = custo_padrao
            if not solicitar_sim_nao(f"O último custo registrado é R${custo_padrao:.2f}. Deseja usar este valor?"):
                valor_unitario = solicitar_float("Digite o valor unitário da compra", 0.01)
            qtd = solicitar_float("Quantidade", 0.01)
            data_obj = solicitar_data("Data")
            _executar_crud(crud_despesa.criar_compra, db, fornecedor_obj=forn, item_comprado=item_comprado, quantidade=qtd, valor_unitario=valor_unitario, data_despesa_obj=data_obj)
        
        elif tipo == "2":
            desc = solicitar_string("Descrição")
            vlr = solicitar_float("Valor", 0.01)
            data_obj = solicitar_data("Data")
            forn = None
            if solicitar_sim_nao("Associar a fornecedor?"):
                forn = _selecionar_entidade_ui(db, "Fornecedor", crud_fornecedor.buscar_fornecedor_id, crud_fornecedor.buscar_fornecedores_por_nome)
            _executar_crud(crud_despesa.criar_fixo_terceiro, db, valor=vlr, tipo_despesa_str=desc, data_despesa_obj=data_obj, fornecedor_obj=forn)
        elif tipo == "3":
            func = _selecionar_entidade_ui(db, "Funcionário", crud_funcionario.buscar_funcionario_por_id, crud_funcionario.buscar_funcionarios_por_nome)
            bruto = solicitar_float("Salário Bruto", 0.01)
            descontos = solicitar_float("Descontos")
            data_obj = solicitar_data("Data")
            _executar_crud(crud_despesa.criar_salario, db, funcionario_obj=func, salario_bruto=bruto, descontos=descontos, data_despesa_obj=data_obj)
        elif tipo == "4":
            func = _selecionar_entidade_ui(db, "Funcionário", crud_funcionario.buscar_funcionario_por_id, crud_funcionario.buscar_funcionarios_por_nome)
            servicos = solicitar_float("Soma Serviços")
            produtos = solicitar_float("Soma Produtos")
            taxa_s_perc = solicitar_float("Taxa de comissão de Serviços (%)", 0)
            taxa_p_perc = solicitar_float("Taxa de comissão de Produtos (%)", 0)
            taxa_s = taxa_s_perc / 100.0
            taxa_p = taxa_p_perc / 100.0
            data_obj = solicitar_data("Data")
            _executar_crud(crud_despesa.criar_comissao, db, funcionario_obj=func, valor_soma_servicos=servicos, valor_soma_produtos=produtos, taxa_servicos=taxa_s, taxa_produtos=taxa_p, data_despesa_obj=data_obj)
        elif tipo == "5":
            desc = solicitar_string("Descrição")
            vlr = solicitar_float("Valor", 0.01)
            data_obj = solicitar_data("Data")
            _executar_crud(crud_despesa.criar_outros, db, valor=vlr, tipo_despesa_str=desc, data_despesa_obj=data_obj)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def _listar_despesas_ui(db: Session):
    filtros = {}
    kwargs_query = {}
    try:
        if solicitar_sim_nao("Deseja aplicar filtros à listagem?"):
            if solicitar_sim_nao("Filtrar por período?"):
                data_inicio = solicitar_data("Data de início")
                data_fim = solicitar_data("Data de fim")
                kwargs_query['data_inicio'] = data_inicio
                kwargs_query['data_fim'] = data_fim
                filtros['Período'] = f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
            if solicitar_sim_nao("Filtrar por tipo de despesa?"):
                tipos_selecionados = []
                opcoes_tipo = {"1": "compra", "2": "fixo_terceiro", "3": "salario", "4": "comissao", "5": "outros"}
                while True:
                    print("\nSelecione os tipos de despesa (múltiplos permitidos):")
                    for k,v in opcoes_tipo.items():
                        print(f" {k}. {v.replace('_',' ').title()}")
                    print(" 0. Concluir seleção")
                    escolha = solicitar_string("Escolha um tipo ou 0 para continuar", min_len=1)
                    if escolha == '0': break
                    if escolha in opcoes_tipo and opcoes_tipo[escolha] not in tipos_selecionados:
                        tipos_selecionados.append(opcoes_tipo[escolha])
                        print(f"Adicionado: {opcoes_tipo[escolha]}. Selecionados: {', '.join(tipos_selecionados)}")
                    elif escolha in opcoes_tipo:
                        print("Tipo já selecionado.")
                    else:
                        print("Opção inválida.")
                if tipos_selecionados:
                    kwargs_query['tipos'] = tipos_selecionados
                    filtros['Tipos'] = tipos_selecionados
            if solicitar_sim_nao("Filtrar por fornecedor?"):
                forn = _selecionar_entidade_ui(db, "Fornecedor", crud_fornecedor.buscar_fornecedor_id, crud_fornecedor.buscar_fornecedores_por_nome)
                kwargs_query['fornecedor_id'] = forn.id
                filtros['Fornecedor'] = f"ID {forn.id} - {forn.nome}"
            if solicitar_sim_nao("Filtrar por funcionário (salários/comissões)?"):
                func = _selecionar_entidade_ui(db, "Funcionário", crud_funcionario.buscar_funcionario_por_id, crud_funcionario.buscar_funcionarios_por_nome)
                kwargs_query['funcionario_id'] = func.id
                filtros['Funcionário'] = f"ID {func.id} - {func.nome}"
    except InterrompidoPeloUsuario:
        print("\nFiltros cancelados. Listando todos os registros.")
        filtros = {}

    despesas = crud_despesa.listar_despesas(db, **kwargs_query)
    _tratar_saida_relatorio(db, 'Despesas', despesas, crud_despesa._formatar_despesas_para_tabela, filtros)


def _atualizar_despesa_ui(db: Session):
    try:
        id_despesa = solicitar_int("ID da Despesa para atualizar", 1)
        despesa = db.query(crud_despesa.Despesa).get(id_despesa)
        if not despesa:
            print(f"Despesa com ID {id_despesa} não encontrada.")
            return
        alteracoes = {}
        if solicitar_sim_nao("Alterar data da despesa?"):
            data_atual = despesa.data_despesa.strftime('%d/%m/%Y')
            alteracoes['data_despesa'] = solicitar_data(f"Nova Data (atual: {data_atual})")
        if isinstance(despesa, crud_despesa.Compra):
            if solicitar_sim_nao("Alterar quantidade?"):
                alteracoes['quantidade'] = solicitar_float(f"Nova Qtd (atual: {despesa.quantidade})", 0.01)
            if solicitar_sim_nao("Alterar valor unitário?"):
                alteracoes['valor_unitario'] = solicitar_float(f"Novo Vlr. Unit. (atual: {despesa.valor_unitario})", 0.01)
        elif isinstance(despesa, (crud_despesa.FixoTerceiro, crud_despesa.Outros)):
            if solicitar_sim_nao("Alterar valor total?"):
                alteracoes['valor_total'] = solicitar_float(f"Novo Valor (atual: {despesa.valor_total})", 0.01)
            if solicitar_sim_nao("Alterar descrição?"):
                alteracoes['tipo_despesa_str'] = solicitar_string(f"Nova Descrição (atual: {despesa.tipo_despesa_str})")
        elif isinstance(despesa, crud_despesa.Salario):
            if solicitar_sim_nao("Alterar salário bruto?"):
                alteracoes['salario_bruto'] = solicitar_float(f"Novo Bruto (atual: {despesa.salario_bruto})", 0.01)
            if solicitar_sim_nao("Alterar descontos?"):
                alteracoes['descontos'] = solicitar_float(f"Novos Descontos (atual: {despesa.descontos})")
        elif isinstance(despesa, crud_despesa.Comissao):
            if solicitar_sim_nao("Alterar soma de serviços?"):
                alteracoes['valor_soma_servicos'] = solicitar_float(f"Nova Soma Serviços (atual: {despesa.valor_soma_servicos})")
            if solicitar_sim_nao("Alterar taxa de serviços?"):
                taxa_s_perc = solicitar_float("Nova Taxa de comissão de Serviços (%)", 0)
                alteracoes['taxa_servicos'] = taxa_s_perc / 100.0
        
        if alteracoes:
            _executar_crud(crud_despesa.atualizar_dados_despesa, db, id_despesa=id_despesa, **alteracoes)
        else:
            print("\nNenhuma alteração realizada.")
    except InterrompidoPeloUsuario:
        print("\nAtualização cancelada.")

def _deletar_despesa_ui(db: Session):
    try:
        id_despesa = solicitar_int("ID da Despesa a ser deletada", 1)
        if solicitar_sim_nao(f"Tem certeza que deseja deletar a despesa ID {id_despesa}?"):
            _executar_crud(crud_despesa.deletar_despesa, db, id_despesa=id_despesa)
    except InterrompidoPeloUsuario:
        print("\nOperação cancelada.")

def main():
    database.criar_banco()
    menu_principal = {
        "1": "Agendas", "2": "Vendas", "3": "Despesas", "4": "Clientes",
        "5": "Produtos", "6": "Suprimentos", "7": "Fornecedores", "8": "Máquinas",
        "9": "Serviços", "10": "Funcionários"
    }
    opcoes_submenu_texto = {"1": "Cadastrar", "2": "Listar", "3": "Atualizar", "4": "Deletar", "5": "Ver Histórico de Compras"}
    submenus = {
        "1": {"1": _cadastrar_agenda_ui, "2": _listar_agendas_ui, "3": _atualizar_agenda_ui, "4": _deletar_agenda_ui},
        "2": {"1": _cadastrar_venda_ui, "2": _listar_vendas_ui, "3": _atualizar_venda_ui, "4": _deletar_venda_ui},
        "3": {"1": _cadastrar_despesa_ui, "2": _listar_despesas_ui, "3": _atualizar_despesa_ui, "4": _deletar_despesa_ui},
        "4": {"1": _cadastrar_cliente_ui, "2": _listar_clientes_ui, "3": _atualizar_cliente_ui, "4": _deletar_cliente_ui},
        "5": {"1": _cadastrar_produto_ui, "2": _listar_produtos_ui, "3": _atualizar_produto_ui, "4": _deletar_produto_ui, "5": _ver_historico_compras_produto_ui},
        "6": {"1": _cadastrar_suprimento_ui, "2": _listar_suprimentos_ui, "3": _atualizar_suprimento_ui, "4": _deletar_suprimento_ui, "5": _ver_historico_compras_suprimento_ui},
        "7": {"1": _cadastrar_fornecedor_ui, "2": _listar_fornecedores_ui, "3": _atualizar_fornecedor_ui, "4": _deletar_fornecedor_ui},
        "8": {"1": _cadastrar_maquina_ui, "2": _listar_maquinas_ui, "3": _atualizar_maquina_ui, "4": _deletar_maquina_ui},
        "9": {"1": _cadastrar_servico_ui, "2": _listar_servicos_ui, "3": _atualizar_servico_ui, "4": _deletar_servico_ui},
        "10": {"1": _cadastrar_funcionario_ui, "2": _listar_funcionarios_ui, "3": _atualizar_funcionario_ui, "4": _deletar_funcionario_ui},
    }

    while True:
        limpar_tela(); print("--- Sistema de Gestão ---")
        for k, v in menu_principal.items(): print(f"{k}. Gerenciar {v}")
        print("0. Sair")
        try:
            escolha_menu = solicitar_string("Escolha um módulo", min_len=1)
            if escolha_menu == '0': sys.exit("\nSaindo...")

            if escolha_menu in submenus:
                submenu_atual = submenus[escolha_menu]
                titulo_atual = menu_principal[escolha_menu]
                while True:
                    limpar_tela(); print(f"--- Gerenciar {titulo_atual} ---")
                    for k_sub, _ in submenu_atual.items():
                        nome_acao = opcoes_submenu_texto.get(k_sub, "Ação Desconhecida")
                        print(f"{k_sub}. {nome_acao}")
                    print("0. Voltar")
                    try:
                        escolha_sub = solicitar_string("Escolha uma opção", min_len=1)
                        if escolha_sub == '0': break
                        if escolha_sub in submenu_atual:
                            funcao_a_executar = submenu_atual[escolha_sub]
                            db = database.SessionLocal()
                            try:
                                limpar_tela()
                                funcao_a_executar(db)
                            except Exception as e:
                                db.rollback()
                                print(f"\nERRO INESPERADO: {e}\nOperação revertida.")
                            finally:
                                db.close()
                            esperar_enter()
                        else: print("Opção inválida."); esperar_enter()
                    except InterrompidoPeloUsuario:
                        break 
            else: print("Módulo inválido."); esperar_enter()
        except InterrompidoPeloUsuario:
            sys.exit("\nSaindo...")

if __name__ == "__main__":
    main()
