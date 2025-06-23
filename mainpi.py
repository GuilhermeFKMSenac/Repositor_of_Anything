#modulos python
import sys
import os
from datetime import datetime
from typing import Optional, Any, Union, Callable, List
import re
#modulos projeto
import pessoa
import info as mod_info
import funcionario as mod_funcionario
import cliente as mod_cliente
import produto
import servico
import agenda as mod_agenda
import venda as mod_venda
import fornecedor as mod_fornecedor
import despesa as mod_despesa
import suprimento as mod_suprimento
import maquina as mod_maquina

def limpar_tela():
   # Limpa o console para melhor visualização do menu.
   os.system('cls' if os.name == 'nt' else 'clear')

def esperar_enter():
   # Pausa a execução e aguarda o usuário pressionar Enter.
   input("\nPressione Enter para continuar...")

def solicitar_string(prompt: str, min_len: int = 1, max_len: Optional[int] = None,
                    pattern: Optional[str] = None, description: Optional[str] = None,
                    allow_cancel: bool = True) -> Optional[str]:
   # Solicita uma string com validação e opção de cancelar.
   cancel_msg = " (Digite 'c' para cancelar)" if allow_cancel else ""
   while True:
       entrada = input(f"{prompt}{cancel_msg}: ").strip()
       if allow_cancel and entrada.lower() == 'c':
           return None
       if len(entrada) < min_len:
           print(f"Erro: A entrada deve ter pelo menos {min_len} caracteres.")
           continue
       if max_len is not None and len(entrada) > max_len:
           print(f"Erro: A entrada deve ter no máximo {max_len} caracteres.")
           continue
       if pattern is not None and not re.fullmatch(pattern, entrada):
           print(f"Erro: Formato inválido. {description if description else ''}")
           continue
       return entrada

def solicitar_float(prompt: str, min_val: float = 0.0, description: Optional[str] = None,
                    allow_cancel: bool = True) -> Optional[float]:
   # Solicita um número float com validação e opção de cancelar.
   cancel_msg = " (Digite 'c' para cancelar)" if allow_cancel else ""
   while True:
       entrada_str = input(f"{prompt}{cancel_msg}: ").strip().replace(',', '.')
       if allow_cancel and entrada_str.lower() == 'c':
           return None
       try:
           valor = float(entrada_str)
           if valor < min_val:
               print(f"Erro: O valor deve ser maior ou igual a {min_val}.")
           else:
               return valor
       except ValueError:
           print(f"Erro: Entrada inválida. Por favor, digite um número válido. {description if description else ''}")

def solicitar_int(prompt: str, min_val: int = 0, description: Optional[str] = None,
                  allow_cancel: bool = True) -> Optional[int]:
   # Solicita um número inteiro com validação e opção de cancelar.
   cancel_msg = " (Digite 'c' para cancelar)" if allow_cancel else ""
   while True:
       entrada_str = input(f"{prompt}{cancel_msg}: ").strip()
       if allow_cancel and entrada_str.lower() == 'c':
           return None
       try:
           valor = int(entrada_str)
           if valor < min_val:
               print(f"Erro: O valor deve ser maior ou igual a {min_val}.")
           else:
               return valor
       except ValueError:
           print(f"Erro: Entrada inválida. Por favor, digite um número inteiro válido. {description if description else ''}")

def solicitar_data(prompt: str, description: str = "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)",
                   allow_cancel: bool = True) -> Optional[str]:
   # Solicita uma data em formato flexível, valida e retorna a string.
   cancel_msg = " (Digite 'c' para cancelar)" if allow_cancel else ""
   while True:
       entrada_str = input(f"{prompt} (Formatos aceitos: {description}){cancel_msg}: ").strip()
       if allow_cancel and entrada_str.lower() == 'c':
           return None
       if not entrada_str:
           print("Erro: A data não pode ser vazia.")
           continue
       try:
           pessoa.Pessoa._parse_data(entrada_str, is_datetime=False)
           return entrada_str
       except ValueError as e:
           print(f"Erro: {e} Por favor, digite novamente.")

def solicitar_data_hora(prompt: str, description: str = "DD/MM/YYYY HH:MM, DD-MM-YYYY HH:MM, DDMMYYYY HH:MM, DD MM YY(YY) HH:MM",
                        allow_cancel: bool = True) -> Optional[str]:
   # Solicita uma data e hora em formato flexível, valida e retorna a string.
   cancel_msg = " (Digite 'c' para cancelar)" if allow_cancel else ""
   while True:
       entrada_str = input(f"{prompt} (Formatos aceitos: {description}){cancel_msg}: ").strip()
       if allow_cancel and entrada_str.lower() == 'c':
           return None
       if not entrada_str:
           print("Erro: A data/hora não pode ser vazia.")
           continue
       try:
           pessoa.Pessoa._parse_data(entrada_str, is_datetime=True)
           return entrada_str
       except ValueError as e:
           print(f"Erro: {e} Por favor, digite novamente.")

def solicitar_sim_nao(prompt: str, allow_cancel: bool = True) -> Optional[bool]:
   # Solicita uma resposta Sim/Não.
   cancel_msg = ", Digite 'c' para cancelar" if allow_cancel else ""
   while True:
       resp = input(f"{prompt} (s/n{cancel_msg}): ").strip().lower()
       if resp == 's':
           return True
       elif resp == 'n':
           return False
       elif allow_cancel and resp == 'c':
           return None
       else:
           print("Resposta inválida. Digite 's' para sim, 'n' para não ou 'c' para cancelar.")

def solicitar_objeto(tipo_objeto_str: str, buscar_funcao: Callable, identificador_prompt: str,
                      identificador_description: str) -> Optional[Any]:
   # Função auxiliar para buscar um objeto existente por um identificador primário exato.
   while True:
       identificador = solicitar_string(f"Digite o {identificador_prompt} do {tipo_objeto_str}",
                                        description=identificador_description)
       if identificador is None:
           return None
       if identificador_prompt.lower() == 'id':
           try:
               identificador = int(identificador)
           except ValueError:
               print(f"Erro: ID deve ser um número inteiro. {identificador_description}")
               continue
       elif identificador_prompt.lower() in ('nome', 'cnpj', 'cpf', 'numero de serie', 'numero_serie'):
           identificador = identificador.strip()

       objeto_encontrado = buscar_funcao(identificador)
       if objeto_encontrado:
           display_name = ""
           if hasattr(objeto_encontrado, 'nome'):
               display_name = objeto_encontrado.nome
           elif hasattr(objeto_encontrado, 'id'):
               display_name = f"ID: {objeto_encontrado.id}"

           print(f"--> {tipo_objeto_str} encontrado: {display_name}")
           return objeto_encontrado
       else:
           print(f"Erro: {tipo_objeto_str} com {identificador_prompt} '{identificador}' não encontrado.")
           if not solicitar_sim_nao(f"Deseja tentar novamente buscar o {tipo_objeto_str}?"):
               return None

# Funções de filtro (utilizadas por múltiplos menus)
def solicitar_funcionario_para_filtro() -> Optional[mod_funcionario.Funcionario]:
   while True:
       print("\n--- Buscar Funcionário para Filtro ---")
       opcao_busca_str = solicitar_string("Buscar funcionário por (CPF, ID, Nome Completo): ",
                                      pattern=r"^(cpf|id|nome completo)$",
                                      description="CPF, ID ou Nome Completo", min_len=2)
       if opcao_busca_str is None: return None

       func_encontrado = None
       if opcao_busca_str.lower() == 'cpf':
           cpf_busca = solicitar_string("CPF do Funcionário", pattern=r"^(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})$", description="Formato: '999.999.999-99' ou '99999999999'")
           if cpf_busca is None: return None
           func_encontrado = mod_funcionario.Funcionario.buscar_funcionario_por_cpf(cpf_busca)
       elif opcao_busca_str.lower() == 'id':
           id_busca = solicitar_int("ID do Funcionário", min_val=1)
           if id_busca is None: return None
           func_encontrado = mod_funcionario.Funcionario.buscar_funcionario_por_id(id_busca)
       elif opcao_busca_str.lower() == 'nome completo':
           nome_busca = solicitar_string("Nome Completo do Funcionário")
           if nome_busca is None: return None
           func_encontrado = mod_funcionario.Funcionario.buscar_funcionario_por_nome_exato(nome_busca)

       if func_encontrado:
           print(f"--> Funcionário selecionado: {func_encontrado.nome} (CPF: {func_encontrado.cpf})")
           return func_encontrado
       else:
           print("Funcionário não encontrado com os critérios fornecidos.")
           if not solicitar_sim_nao("Deseja tentar novamente buscar o funcionário?"):
               return None

def solicitar_cliente_para_filtro() -> Optional[mod_cliente.Cliente]:
   while True:
       print("\n--- Buscar Cliente para Filtro ---")
       opcao_busca_str = solicitar_string("Buscar cliente por (CPF, ID, Nome): ",
                                      pattern=r"^(cpf|id|nome)$",
                                      description="CPF, ID ou Nome", min_len=2)
       if opcao_busca_str is None: return None

       cli_encontrado = None
       if opcao_busca_str.lower() == 'cpf':
           cpf_busca = solicitar_string("CPF do Cliente", pattern=r"^(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})$", description="Formato: '999.999.999-99' ou '99999999999'")
           if cpf_busca is None: return None
           cli_encontrado = mod_cliente.Cliente.buscar_cliente(cpf_busca)
       elif opcao_busca_str.lower() == 'id':
           id_busca = solicitar_int("ID do Cliente", min_val=1)
           if id_busca is None: return None
           cli_encontrado = mod_cliente.Cliente.buscar_cliente_id(id_busca)
       elif opcao_busca_str.lower() == 'nome':
           nome_busca = solicitar_string("Nome (completo ou parcial) do Cliente")
           if nome_busca is None: return None

           cli_encontrado = mod_cliente.Cliente.buscar_cliente_por_nome_exato(nome_busca)
           if cli_encontrado:
               print(f"--> Cliente selecionado: {cli_encontrado.nome} (CPF: {cli_encontrado.cpf})")
               return cli_encontrado

           print("Nome exato não encontrado. Buscando por correspondência parcial...")
           clientes_parciais = mod_cliente.Cliente.buscar_clientes_por_nome_parcial(nome_busca)

           if not clientes_parciais:
               print(f"Nenhum cliente encontrado com '{nome_busca}' no nome.")
           else:
               print("\nClientes Encontrados (selecione um número):")
               for i, cli in enumerate(clientes_parciais):
                   print(f"{i+1}. {cli.nome} (CPF: {cli.cpf})")

               escolha_num = solicitar_int("Digite o número do cliente desejado", min_val=1, description=f"Número entre 1 e {len(clientes_parciais)}")
               if escolha_num is None: return None

               if 1 <= escolha_num <= len(clientes_parciais):
                   cli_encontrado = clientes_parciais[escolha_num - 1]
                   print(f"--> Cliente selecionado: {cli_encontrado.nome} (CPF: {cli_encontrado.cpf})")
                   return cli_encontrado
               else:
                   print("Número inválido.")
                   continue

       if cli_encontrado:
           return cli_encontrado
       else:
           print("Cliente não encontrado com os critérios fornecidos.")
           if not solicitar_sim_nao("Deseja tentar novamente buscar o cliente?"):
               return None

def solicitar_fornecedor_para_filtro() -> Optional[mod_fornecedor.Fornecedor]:
   while True:
       print("\n--- Buscar Fornecedor para Filtro ---")
       opcao_busca_str = solicitar_string("Buscar fornecedor por (CNPJ, ID, Nome): ",
                                      pattern=r"^(cnpj|id|nome)$",
                                      description="CNPJ, ID ou Nome", min_len=2)
       if opcao_busca_str is None: return None

       forn_encontrado = None
       if opcao_busca_str.lower() == 'cnpj':
           cnpj_busca = solicitar_string("CNPJ do Fornecedor", pattern=r"^(?:\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14})$", description="Formato: 'XX.XXX.XXX/XXXX-XX' ou 'XXXXXXXXXXXXXX'")
           if cnpj_busca is None: return None
           forn_encontrado = mod_fornecedor.Fornecedor.buscar_fornecedor(cnpj_busca)
       elif opcao_busca_str.lower() == 'id':
           id_busca = solicitar_int("ID do Fornecedor", min_val=1)
           if id_busca is None: return None
           forn_encontrado = mod_fornecedor.Fornecedor.buscar_fornecedor_id(id_busca)
       elif opcao_busca_str.lower() == 'nome':
           nome_busca = solicitar_string("Nome (completo ou parcial) do Fornecedor")
           if nome_busca is None: return None

           forn_encontrado = mod_fornecedor.Fornecedor.buscar_fornecedor_por_nome_exato(nome_busca)
           if forn_encontrado:
               print(f"--> Fornecedor selecionado: {forn_encontrado.nome} (CNPJ: {forn_encontrado.cnpj})")
               return forn_encontrado

           print("Nome exato não encontrado. Buscando por correspondência parcial...")
           fornecedores_parciais = mod_fornecedor.Fornecedor.buscar_fornecedores_por_nome_parcial(nome_busca)

           if not fornecedores_parciais:
               print(f"Nenhum fornecedor encontrado com '{nome_busca}' no nome.")
           else:
               print("\nFornecedores Encontrados (selecione um número):")
               for i, forn in enumerate(fornecedores_parciais):
                   print(f"{i+1}. {forn.nome} (CNPJ: {forn.cnpj})")

               escolha_num = solicitar_int("Digite o número do fornecedor desejado", min_val=1, description=f"Número entre 1 e {len(fornecedores_parciais)}")
               if escolha_num is None: return None

               if 1 <= escolha_num <= len(fornecedores_parciais):
                   forn_encontrado = fornecedores_parciais[escolha_num - 1]
                   print(f"--> Fornecedor selecionado: {forn_encontrado.nome} (CNPJ: {forn_encontrado.cnpj})")
                   return forn_encontrado
               else:
                   print("Número inválido.")
                   continue

       if forn_encontrado:
           return forn_encontrado
       else:
           print("Fornecedor não encontrado com os critérios fornecidos.")
           if not solicitar_sim_nao("Deseja tentar novamente buscar o fornecedor?"):
               return None

def solicitar_produto_ou_servico(tipo_str: str, buscar_por_id: bool = False) -> Optional[Union[produto.Produto, servico.Servico]]:
   # tipo_str esperado: "produto" ou "servico" (em minúsculas, sem acento)
   while True:
       if buscar_por_id:
           identificador_prompt = "ID"
           identificador_description = "Número inteiro"
           busca_val_id = solicitar_int(f"ID do {tipo_str}", min_val=1)
           if busca_val_id is None: return None
           busca_val: Union[int, str] = busca_val_id
       else:
           identificador_prompt = "Nome"
           identificador_description = f"Nome do {tipo_str}"
           busca_val_nome = solicitar_string(f"Nome do {tipo_str} (ex: 'Notebook Gamer X')", min_len=3)
           if busca_val_nome is None: return None
           busca_val = busca_val_nome

       obj_encontrado = None
       if tipo_str.lower() == 'produto':
           if buscar_por_id:
               obj_encontrado = produto.Produto.buscar_produto_id(busca_val) #type: ignore
           else:
               obj_encontrado = produto.Produto.buscar_produto(busca_val) #type: ignore
       elif tipo_str.lower() == 'servico':
           if buscar_por_id:
               obj_encontrado = servico.Servico.buscar_servico_id(busca_val) #type: ignore
           else:
               obj_encontrado = servico.Servico.buscar_servico(busca_val) #type: ignore
       else:
           return None

       if obj_encontrado:
           print(f"--> {tipo_str} encontrado: {obj_encontrado.nome}")
           return obj_encontrado
       else:
           print(f"Erro: {tipo_str} com {identificador_prompt} '{busca_val}' não encontrado.")
           if not solicitar_sim_nao(f"Deseja tentar novamente buscar o {tipo_str}?"):
               return None

def solicitar_item_compra() -> Optional[Union[produto.Produto, mod_suprimento.Suprimento, mod_maquina.Maquina, str]]:
   while True:
       print("\n--- Selecione o Tipo de Item de Compra ---")
       print("1. Produto")
       print("2. Suprimento")
       print("3. Máquina")
       print("4. Outro (descrição manual)")
       print("0. Cancelar")
       tipo_escolha = solicitar_string("Escolha o tipo de item", pattern=r"^[0-4]$", description="Número de 0 a 4")
       if tipo_escolha is None or tipo_escolha == '0':
           return None

       if tipo_escolha == '1':
           item_obj = solicitar_produto_ou_servico("produto", buscar_por_id=True)
           if item_obj is None: continue
           return item_obj  #type: ignore

       elif tipo_escolha == '2':
           id_suprimento = solicitar_int("ID do Suprimento", min_val=1)
           if id_suprimento is None: continue
           suprimento_obj = mod_suprimento.Suprimento.buscar_suprimento_id(id_suprimento)
           if suprimento_obj:
               print(f"--> Suprimento encontrado: {suprimento_obj.nome} (ID: {suprimento_obj.id})")
               return suprimento_obj
           else:
               print(f"Suprimento com ID '{id_suprimento}' não encontrado.")
               if not solicitar_sim_nao("Deseja tentar novamente buscar o Suprimento?"):
                   continue

       elif tipo_escolha == '3':
           id_maquina = solicitar_int("ID da Máquina", min_val=1)
           if id_maquina is None: continue
           maquina_obj = mod_maquina.Maquina.buscar_maquina_id(id_maquina)
           if maquina_obj:
               print(f"--> Máquina encontrada: {maquina_obj.nome} (ID: {maquina_obj.id})")
               return maquina_obj
           else:
               print(f"Máquina com ID '{id_maquina}' não encontrada.")
               if not solicitar_sim_nao("Deseja tentar novamente buscar a Máquina?"):
                   continue

       elif tipo_escolha == '4':
           descricao_item = solicitar_string("Descrição do item (ex: 'Licença de Software', 'Serviço de Limpeza')", min_len=3)
           if descricao_item is None: continue
           return descricao_item

       print("Falha na seleção do item de compra. Por favor, tente novamente.")

def _handle_report_output(report_data: list[Any], module_name: str, report_type_name: str, format_function: Callable[[list[Any]], str]) -> None:
   if not report_data:
       print(f"Nenhum(a) {report_type_name.lower()} para exibir ou salvar.")
       esperar_enter()
       return

   while True:
       opcao_saida = solicitar_string("Deseja exibir no (t)erminal ou salvar em (a)rquivo de texto?",
                                      pattern=r"^[ta]$", description="t ou a")
       if opcao_saida is None:
           print("Operação cancelada.")
           return

       if opcao_saida.lower() == 't':
           print("\n" + format_function(report_data))
           break
       elif opcao_saida.lower() == 'a':
           timestamp = datetime.now().strftime('%d%m%y%H%M%S')
           directory_name = f"{module_name.lower()}_relatorios"
           file_name = f"{module_name.upper()}_{report_type_name.upper().replace(' ', '_')}_{timestamp}.txt"
           full_path = os.path.join(directory_name, file_name)

           try:
               os.makedirs(directory_name, exist_ok=True)
               with open(full_path, 'w', encoding='utf-8') as f:
                   f.write(format_function(report_data))
               print(f"{report_type_name} salva em '{full_path}'.")
           except IOError as e:
               print(f"Erro ao salvar arquivo: {e}")
           break
       else:
           print("Opção inválida. Por favor, tente novamente.")

# Funções auxiliares de UI para Produtos
def _cadastrar_produto_ui():
   print("--- Cadastrar Novo Produto ---")
   nome = solicitar_string("Nome do Produto", min_len=3)
   if nome is None: return
   preco = solicitar_float("Preço de Venda (ex: 123.45)", min_val=0.01)
   if preco is None: return
   estoque = solicitar_float("Quantidade em Estoque (pode ser decimal, ex: 10.5)", min_val=0.0)
   if estoque is None: return

   try:
       produto.Produto.criar_produto(nome, preco, estoque)
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar produto: {e}")

def _listar_produtos_ui():
   print("--- Lista de Todos os Produtos ---")
   produtos_list = produto.Produto.listar_produtos()
   _handle_report_output(produtos_list, "PRODUTO", "Lista de Produtos", produto.Produto._formatar_produtos_para_tabela)

def _buscar_produto_ui():
   print("--- Buscar Produto ---")
   id_ou_nome = solicitar_string("Buscar produto por (ID, Nome): ", pattern=r"^(id|nome)$", description="ID ou Nome")
   if id_ou_nome is None: return

   prod = None
   if id_ou_nome.lower() == 'id':
       id_busca = solicitar_int("ID do Produto a buscar", min_val=1)
       if id_busca is None: return
       prod = produto.Produto.buscar_produto_id(id_busca)
   else: # nome
       nome_busca = solicitar_string("Nome do Produto a buscar")
       if nome_busca is None: return
       prod = produto.Produto.buscar_produto(nome_busca)

   if prod:
       print("\nProduto Encontrado:")
       print(prod)
   else:
       print(f"\nProduto não encontrado com o identificador fornecido.")

def _atualizar_produto_ui():
   print("--- Atualizar Dados do Produto ---")
   id_atualizar = solicitar_int("ID do Produto a atualizar", min_val=1)
   if id_atualizar is None: return

   prod_existente = produto.Produto.buscar_produto_id(id_atualizar)
   if not prod_existente:
       print(f"Produto com ID '{id_atualizar}' não encontrado.")
       esperar_enter()
       return

   updates = {}

   if solicitar_sim_nao("Deseja alterar o nome?") == True:
       novo_nome = solicitar_string("Novo Nome do Produto", min_len=3)
       if novo_nome is None: return
       updates['nome'] = novo_nome

   if solicitar_sim_nao("Deseja alterar o preço?") == True:
       novo_preco = solicitar_float("Novo Preço de Venda (ex: 123.45)", min_val=0.01)
       if novo_preco is None: return
       updates['preco'] = novo_preco

   if solicitar_sim_nao("Deseja alterar o estoque?") == True:
       novo_estoque = solicitar_float("Nova Quantidade em Estoque (pode ser decimal, ex: 10.5)", min_val=0.0)
       if novo_estoque is None: return
       updates['estoque'] = novo_estoque

   if updates:
       try:
           produto.Produto.atualizar_dados_produto(id_atualizar, **updates)
           print(f"\nProduto ID '{id_atualizar}' atualizado com sucesso!")
       except (ValueError, TypeError) as e:
           print(f"\nErro ao atualizar produto: {e}")
   else:
       print("\nNenhuma alteração solicitada.")

def _deletar_produto_ui():
   print("--- Deletar Produto ---")
   id_deletar = solicitar_int("ID do Produto a deletar", min_val=1)
   if id_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar o produto ID '{id_deletar}'?") == True:
       try:
           produto.Produto.deletar_produto(id_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar produto: {e}")
   else:
       print("\nDeleção cancelada.")

# Funções auxiliares de UI para Serviços
def _cadastrar_servico_ui():
   print("--- Cadastrar Novo Serviço ---")
   nome = solicitar_string("Nome do Serviço", min_len=3)
   if nome is None: return
   valor_venda = solicitar_float("Valor de Venda (ex: 123.45)", min_val=0.01)
   if valor_venda is None: return
   custo = solicitar_float("Custo do Serviço (ex: 123.45)", min_val=0.01)
   if custo is None: return

   try:
       servico.Servico.criar_servico(nome, valor_venda, custo)
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar serviço: {e}")

def _listar_servicos_ui():
   print("--- Lista de Todos os Serviços ---")
   servicos_list = servico.Servico.listar_servicos()
   _handle_report_output(servicos_list, "SERVICO", "Lista de Servicos", servico.Servico._formatar_servicos_para_tabela)

def _buscar_servico_ui():
   print("--- Buscar Serviço ---")
   id_ou_nome = solicitar_string("Buscar serviço por (ID, Nome): ", pattern=r"^(id|nome)$", description="ID ou Nome")
   if id_ou_nome is None: return

   serv = None
   if id_ou_nome.lower() == 'id':
       id_busca = solicitar_int("ID do Serviço a buscar", min_val=1)
       if id_busca is None: return
       serv = servico.Servico.buscar_servico_id(id_busca)
   else: # nome
       nome_busca = solicitar_string("Nome do Serviço a buscar")
       if nome_busca is None: return
       serv = servico.Servico.buscar_servico(nome_busca)

   if serv:
       print("\nServiço Encontrado:")
       print(serv)
   else:
       print(f"\nServiço '{nome_busca}' não encontrado.")

def _atualizar_servico_ui():
   print("--- Atualizar Dados do Serviço ---")
   id_atualizar = solicitar_int("ID do Serviço a atualizar", min_val=1)
   if id_atualizar is None: return

   serv_existente = servico.Servico.buscar_servico_id(id_atualizar)
   if not serv_existente:
       print(f"Serviço com ID '{id_atualizar}' não encontrado.")
       esperar_enter()
       return

   updates = {}

   if solicitar_sim_nao("Deseja alterar o nome?") == True:
       novo_nome = solicitar_string("Novo Nome do Serviço", min_len=3)
       if novo_nome is None: return
       updates['nome'] = novo_nome

   if solicitar_sim_nao("Deseja alterar o valor de venda?") == True:
       novo_valor_venda = solicitar_float("Novo Valor de Venda (ex: 123.45)", min_val=0.01)
       if novo_valor_venda is None: return
       updates['valor_venda'] = novo_valor_venda

   if solicitar_sim_nao("Deseja alterar o custo?") == True:
       novo_custo = solicitar_float("Novo Custo do Serviço (ex: 123.45)", min_val=0.01)
       if novo_custo is None: return
       updates['custo'] = novo_custo

   if updates:
       try:
           servico.Servico.atualizar_dados_servico(id_atualizar, **updates)
           print(f"\nServiço ID '{id_atualizar}' atualizado com sucesso!")
       except (ValueError, TypeError) as e:
           print(f"\nErro ao atualizar serviço: {e}")
   else:
       print("\nNenhuma alteração solicitada.")

def _deletar_servico_ui():
   print("--- Deletar Serviço ---")
   id_deletar = solicitar_int("ID do Serviço a deletar", min_val=1)
   if id_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar o serviço ID '{id_deletar}'?") == True:
       try:
           servico.Servico.deletar_servico(id_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar serviço: {e}")
   else:
       print("\nDeleção cancelada.")

# Funções auxiliares de UI para Clientes
def _cadastrar_cliente_ui():
   print("--- Cadastrar Novo Cliente ---")
   nome = solicitar_string("Nome Completo do Cliente (pelo menos dois nomes/palavras, ex: 'João Silva')", min_len=5, description="Ex: 'João Silva'")
   if nome is None: return
   nascimento = solicitar_data("Data de Nascimento", description="DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if nascimento is None: return
   cpf = solicitar_string("CPF (apenas números ou 999.999.999-99)", pattern=r"^(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})$", description="Formato: '999.999.999-99' ou '99999999999'")
   if cpf is None: return

   print("\n--- Informações de Contato ---")
   temp_telefone = solicitar_string("Telefone (Ex: +55 (11) 98765-4321 ou 11987654321)", min_len=8)
   temp_email = solicitar_string("Email (Ex: exemplo@dominio.com)", pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
   temp_endereco = solicitar_string("Endereço (Ex: Rua Nome, 123, Bairro, Cidade, UF ou Rua Nome, 123)", min_len=10)
   temp_redes_sociais = solicitar_string("Redes Sociais (opcional)", min_len=0)

   if any(item is None for item in [temp_telefone, temp_email, temp_endereco]):
       print("Cadastro de cliente cancelado devido a informações de contato incompletas.")
       return

   try:
       informacao_contato = mod_info.Informacao(temp_telefone, temp_email, temp_endereco, temp_redes_sociais if temp_redes_sociais is not None else "") #type: ignore
       mod_cliente.Cliente.criar_cliente(nome, nascimento, cpf, informacao_contato)
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar cliente: {e}")

def _listar_clientes_ui():
   print("--- Lista de Todos os Clientes ---")
   clientes_list = mod_cliente.Cliente.listar_clientes()
   _handle_report_output(clientes_list, "CLIENTE", "Lista de Clientes", mod_cliente.Cliente._formatar_clientes_para_tabela)

def _buscar_cliente_por_cpf_ui():
   print("--- Buscar Cliente por CPF ---")
   cpf_busca = solicitar_string("CPF do Cliente (apenas números ou 999.999.999-99)")
   if cpf_busca is None: return

   cli = mod_cliente.Cliente.buscar_cliente(cpf_busca)
   if cli:
       print("\nCliente Encontrado:")
       print(cli)
   else:
       print(f"\nCliente com CPF '{cpf_busca}' não encontrado.")

def _buscar_cliente_por_id_ui():
   print("--- Buscar Cliente por ID ---")
   id_busca = solicitar_int("ID do Cliente", min_val=1)
   if id_busca is None: return

   cli = mod_cliente.Cliente.buscar_cliente_id(id_busca)
   if cli:
       print("\nCliente Encontrado:")
       print(cli)
   else:
       print(f"\nCliente com ID '{id_busca}' não encontrado.")

def _buscar_cliente_por_nome_exato_ui():
   print("--- Buscar Cliente por Nome (Exato) ---")
   nome_busca = solicitar_string("Nome Exato do Cliente a buscar")
   if nome_busca is None: return

   cli = mod_cliente.Cliente.buscar_cliente_por_nome_exato(nome_busca)
   if cli:
       print("\nCliente Encontrado:")
       print(cli)
   else:
       print(f"\nCliente com nome '{nome_busca}' não encontrado.")

def _buscar_clientes_por_nome_parcial_ui():
   print("--- Buscar Clientes por Nome (Parcial) ---")
   nome_parcial = solicitar_string("Parte do Nome do Cliente a buscar")
   if nome_parcial is None: return

   clientes_encontrados = mod_cliente.Cliente.buscar_clientes_por_nome_parcial(nome_parcial)
   _handle_report_output(clientes_encontrados, "CLIENTE", "Clientes por Nome Parcial", mod_cliente.Cliente._formatar_clientes_para_tabela)

def _atualizar_dados_cliente_ui():
   print("--- Atualizar Dados do Cliente ---")
   id_atualizar = solicitar_int("ID do Cliente a atualizar", min_val=1)
   if id_atualizar is None: return

   cli_existente = mod_cliente.Cliente.buscar_cliente_id(id_atualizar)
   if not cli_existente:
       print(f"Cliente com ID '{id_atualizar}' não encontrado.")
       esperar_enter()
       return

   updates = {}

   if solicitar_sim_nao("Deseja alterar o nome?") == True:
       novo_nome = solicitar_string("Novo Nome Completo (pelo menos dois nomes/palavras, ex: 'João Silva')", min_len=5, description="Ex: 'João Silva'")
       if novo_nome is None: return
       updates['nome'] = novo_nome

   if solicitar_sim_nao("Deseja alterar a data de nascimento?") == True:
       nova_nascimento = solicitar_data("Nova Data de Nascimento", description="DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
       if nova_nascimento is None: return
       updates['nascimento'] = nova_nascimento

   if solicitar_sim_nao("Deseja alterar informações de contato?") == True:
       print("\n--- Novas Informações de Contato ---")

       temp_telefone = solicitar_string("Telefone (Ex: +55 (11) 98765-4321 ou 11987654321)", min_len=8)
       temp_email = solicitar_string("Email (Ex: exemplo@dominio.com)", pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
       temp_endereco = solicitar_string("Endereço (Ex: Rua Nome, 123, Bairro, Cidade, UF ou Rua Nome, 123)", min_len=10)
       temp_redes_sociais = solicitar_string("Redes Sociais (opcional)", min_len=0)

       if any(item is None for item in [temp_telefone, temp_email, temp_endereco]):
           print("Atualização de informações de contato cancelada devido a entrada incompleta.")
       else:
           try:
               updates['info_contato'] = mod_info.Informacao(temp_telefone, temp_email, temp_endereco, temp_redes_sociais if temp_redes_sociais is not None else "") #type: ignore
           except (ValueError, TypeError) as e:
               print(f"Erro ao criar novas informações de contato: {e}")
               esperar_enter()

   if updates:
       try:
           mod_cliente.Cliente.atualizar_dados_cliente(id_atualizar, **updates)
           print(f"\nCliente com ID '{id_atualizar}' atualizado com sucesso!")
       except (ValueError, TypeError) as e:
           print(f"\nErro ao atualizar cliente: {e}")
   else:
       print("\nNenhuma alteração solicitada.")

def _atualizar_cpf_cliente_ui():
   print("--- Atualizar CPF do Cliente ---")
   id_cliente_para_cpf = solicitar_int("ID do Cliente cujo CPF será atualizado", min_val=1)
   if id_cliente_para_cpf is None: return

   cli_existente = mod_cliente.Cliente.buscar_cliente_id(id_cliente_para_cpf)
   if not cli_existente:
       print(f"Cliente com ID '{id_cliente_para_cpf}' não encontrado.")
       esperar_enter()
       return

   novo_cpf = solicitar_string("Novo CPF do Cliente (apenas números ou 999.999.999-99)", pattern=r"^(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})$", description="Formato: '999.999.999-99' ou '99999999999'")
   if novo_cpf is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja alterar o CPF do cliente ID '{id_cliente_para_cpf}' de '{cli_existente.cpf}' para '{novo_cpf}'?") == True:
       try:
           mod_cliente.Cliente.atualizar_cpf_cliente(id_cliente_para_cpf, novo_cpf)
           print(f"\nCPF do cliente ID '{id_cliente_para_cpf}' atualizado com sucesso!")
       except ValueError as e:
           print(f"\nErro ao atualizar CPF: {e}")
   else:
       print("\nAtualização de CPF cancelada.")

def _deletar_cliente_ui():
   print("--- Deletar Cliente ---")
   id_deletar = solicitar_int("ID do Cliente a deletar", min_val=1)
   if id_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar o cliente com ID '{id_deletar}'?") == True:
       try:
           mod_cliente.Cliente.deletar_cliente(id_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar cliente: {e}")
   else:
       print("\nDeleção cancelada.")

# Funções auxiliares de UI para Funcionários
def _cadastrar_funcionario_ui():
   print("--- Cadastrar Novo Funcionário ---")

   id_func_for_display = mod_funcionario.Funcionario._proximo_id_disponivel
   print(f"O ID para o novo funcionário será: {id_func_for_display} (auto-gerado)")

   nome = solicitar_string("Nome Completo do Funcionário (pelo menos dois nomes/palavras, ex: 'João Silva')", min_len=5, description="Ex: 'João Silva'")
   if nome is None: return
   nascimento = solicitar_data("Data de Nascimento", description="DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if nascimento is None: return
   cpf = solicitar_string("CPF (apenas números ou 999.999.999-99)", pattern=r"^(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})$", description="Formato: '999.999.999-99' ou '99999999999'")
   if cpf is None: return
   ctps = solicitar_string("CTPS (Carteira de Trabalho e Previdência Social)", min_len=5)
   if ctps is None: return
   salario = solicitar_float("Salário (ex: 3000.00)", min_val=0.0)
   if salario is None: return
   data_admissao = solicitar_data("Data de Admissão", description="DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_admissao is None: return
   demissao_resp = solicitar_sim_nao("Funcionário já foi demitido?")
   if demissao_resp is None: return
   data_demissao = solicitar_data("Data de Demissão", description="DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)") if demissao_resp else None
   if data_demissao is None and demissao_resp: return
   nis = solicitar_string("NIS (Número de Identificação Social - 11 dígitos, opcional)", pattern=r"^\d{11}$", description="11 dígitos numéricos", allow_cancel=True)
   if nis is None: nis = None # Garante que NIS é None se cancelado ou vazio

   print("\n--- Informações de Contato ---")

   temp_telefone = solicitar_string("Telefone (Ex: +55 (11) 98765-4321 ou 11987654321)", min_len=8)
   temp_email = solicitar_string("Email (Ex: exemplo@dominio.com)", pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
   temp_endereco = solicitar_string("Endereço (Ex: Rua Nome, 123, Bairro, Cidade, UF ou Rua Nome, 123)", min_len=10)
   temp_redes_sociais = solicitar_string("Redes Sociais (opcional)", min_len=0)

   if any(item is None for item in [temp_telefone, temp_email, temp_endereco]):
       print("Cadastro de funcionário cancelado devido a informações de contato incompletas.")
       return

   try:
       informacao_contato = mod_info.Informacao(temp_telefone, temp_email, temp_endereco, temp_redes_sociais if temp_redes_sociais is not None else "") #type: ignore
       mod_funcionario.Funcionario(None, nome, nascimento, cpf, ctps, informacao_contato, salario, data_admissao, data_demissao, nis)
       print(f"\nFuncionário '{nome}' (ID: {id_func_for_display}) cadastrado com sucesso!")
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar funcionário: {e}")

def _listar_funcionarios_ui():
   print("--- Lista de Todos os Funcionários ---")
   funcionarios_list = mod_funcionario.Funcionario.listar_funcionarios()
   _handle_report_output(funcionarios_list, "FUNCIONARIO", "Lista de Funcionarios", mod_funcionario.Funcionario._formatar_funcionarios_para_tabela)

def _buscar_funcionario_cpf_ui():
   print("--- Buscar Funcionário por CPF ---")
   cpf_busca = solicitar_string("CPF do Funcionário (apenas números ou 999.999.999-99)")
   if cpf_busca is None: return

   func = mod_funcionario.Funcionario.buscar_funcionario_por_cpf(cpf_busca)
   if func:
       print("\nFuncionário Encontrado:")
       print(func)
   else:
       print(f"\nFuncionário com CPF '{cpf_busca}' não encontrado.")

def _buscar_funcionario_id_ui():
   print("--- Buscar Funcionário por ID ---")
   id_busca = solicitar_int("ID do Funcionário", min_val=1)
   if id_busca is None: return

   func = mod_funcionario.Funcionario.buscar_funcionario_por_id(id_busca)
   if func:
       print("\nFuncionário Encontrado:")
       print(func)
   else:
       print(f"\nFuncionário com ID '{id_busca}' não encontrado.")

   func = mod_funcionario.Funcionario.buscar_funcionario_por_id(id_busca)
   if func:
       print("\nFuncionário Encontrado:")
       print(func)
   else:
       print(f"\nFuncionário com ID '{id_busca}' não encontrado.")

def _atualizar_dados_funcionario_ui():
   print("--- Atualizar Dados do Funcionário ---")
   id_atualizar = solicitar_int("ID do Funcionário a atualizar", min_val=1)
   if id_atualizar is None: return

   func_existente = mod_funcionario.Funcionario.buscar_funcionario_por_id(id_atualizar)
   if not func_existente:
       print(f"Funcionário com ID '{id_atualizar}' não encontrado.")
       esperar_enter()
       return

   updates = {}

   if solicitar_sim_nao("Deseja alterar o nome?") == True:
       novo_nome = solicitar_string("Novo Nome Completo (pelo menos dois nomes/palavras, ex: 'João Silva')", min_len=5, description="Ex: 'João Silva'")
       if novo_nome is None: return
       updates['nome'] = novo_nome

   if solicitar_sim_nao("Deseja alterar a data de nascimento?") == True:
       nova_nascimento = solicitar_data("Nova Data de Nascimento", description="DD/MM/YY(YY), DD-MM-YY(YY), DDMMYY(YY), DD MM YY(YY)")
       if nova_nascimento is None: return
       updates['nascimento'] = nova_nascimento

   if solicitar_sim_nao("Deseja alterar a CTPS?") == True:
       nova_ctps = solicitar_string("Nova CTPS", min_len=5)
       if nova_ctps is None: return
       updates['ctps'] = nova_ctps

   if solicitar_sim_nao("Deseja alterar o salário?") == True:
       novo_salario = solicitar_float("Novo Salário", min_val=0.0)
       if novo_salario is None: return
       updates['salario'] = novo_salario

   if solicitar_sim_nao("Deseja alterar a data de admissão?") == True:
       nova_admissao = solicitar_data("Nova Data de Admissão", description="DD/MM/YY(YY), DD-MM-YY(YY), DDMMYY(YY), DD MM YY(YY)")
       if nova_admissao is None: return
       updates['data_admissao'] = nova_admissao

   if solicitar_sim_nao("Deseja alterar a data de demissão?") == True:
       demissao_resp = solicitar_sim_nao("Marcar como demitido (s) ou Ativo (n)?")
       if demissao_resp is None: return
       if demissao_resp:
           nova_demissao = solicitar_data("Nova Data de Demissão", description="DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
           if nova_demissao is None: return
           updates['data_demissao'] = nova_demissao
       else:
           updates['data_demissao'] = None

   if solicitar_sim_nao("Deseja alterar o NIS?") == True:
       novo_nis = solicitar_string("Novo NIS (Número de Identificação Social - 11 dígitos, opcional)", pattern=r"^\d{11}$", description="11 dígitos numéricos", allow_cancel=True)
       if novo_nis is None: novo_nis = None
       updates['nis'] = novo_nis

   if solicitar_sim_nao("Deseja alterar informações de contato?") == True:
       print("\n--- Novas Informações de Contato ---")

       temp_telefone = solicitar_string("Telefone (Ex: +55 (11) 98765-4321 ou 11987654321)", min_len=8)
       temp_email = solicitar_string("Email (Ex: exemplo@dominio.com)", pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
       temp_endereco = solicitar_string("Endereço (Ex: Rua Nome, 123, Bairro, Cidade, UF ou Rua Nome, 123)", min_len=10)
       temp_redes_sociais = solicitar_string("Redes Sociais (opcional)", min_len=0)

       if any(item is None for item in [temp_telefone, temp_email, temp_endereco]):
           print("Atualização de informações de contato cancelada devido a entrada incompleta.")
       else:
           try:
               updates['informacao_contato'] = mod_info.Informacao(temp_telefone, temp_email, temp_endereco, temp_redes_sociais if temp_redes_sociais is not None else "")  #type: ignore
           except (ValueError, TypeError) as e:
               print(f"Erro ao criar novas informações de contato: {e}")
               esperar_enter()

   if updates:
       try:
           for chave, valor in updates.items():
               if chave == 'nome': mod_funcionario.Funcionario.atualizar_nome_por_id(id_atualizar, valor)
               elif chave == 'nascimento': mod_funcionario.Funcionario.atualizar_data_nascimento_por_id(id_atualizar, valor)
               elif chave == 'ctps': mod_funcionario.Funcionario.atualizar_ctps_por_id(id_atualizar, valor)
               elif chave == 'salario': func_existente.salario = valor
               elif chave == 'data_admissao': func_existente.data_admissao = valor
               elif chave == 'data_demissao': func_existente.data_demissao = valor
               elif chave == 'nis': mod_funcionario.Funcionario.atualizar_nis_por_id(id_atualizar, valor)
               elif chave == 'informacao_contato': func_existente.informacao_contato = valor
           print(f"\nFuncionário com ID '{id_atualizar}' atualizado com sucesso!")
       except (ValueError, TypeError) as e:
           print(f"\nErro ao atualizar funcionário: {e}")
   else:
       print("\nNenhuma alteração solicitada.")

def _atualizar_cpf_funcionario_ui():
   print("--- Atualizar CPF do Funcionário ---")
   id_func_para_cpf = solicitar_int("ID do Funcionário cujo CPF será atualizado", min_val=1)
   if id_func_para_cpf is None: return

   func_existente = mod_funcionario.Funcionario.buscar_funcionario_por_id(id_func_para_cpf)
   if not func_existente:
       print(f"Funcionário com ID '{id_func_para_cpf}' não encontrado.")
       esperar_enter()
       return

   novo_cpf = solicitar_string("Novo CPF do Funcionário (apenas números ou 999.999.999-99)", pattern=r"^(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})$", description="Formato: '999.999.999-99' ou '99999999999'")
   if novo_cpf is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja alterar o CPF do funcionário ID '{id_func_para_cpf}' de '{func_existente.cpf}' para '{novo_cpf}'?") == True:
       try:
           mod_funcionario.Funcionario.atualizar_cpf(func_existente.cpf, novo_cpf) #type: ignore
           print(f"\nCPF do funcionário ID '{id_func_para_cpf}' atualizado com sucesso!")
       except ValueError as e:
           print(f"\nErro ao atualizar CPF: {e}")
   else:
       print("\nAtualização de CPF cancelada.")

def _deletar_funcionario_cpf_ui():
   print("--- Deletar Funcionário por CPF ---")
   cpf_deletar = solicitar_string("CPF do Funcionário a deletar")
   if cpf_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar o funcionário com CPF '{cpf_deletar}'?") == True:
       try:
           mod_funcionario.Funcionario.deletar_funcionario_por_cpf(cpf_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar funcionário: {e}")
   else:
       print("\nDeleção cancelada.")

def _deletar_funcionario_id_ui():
   print("--- Deletar Funcionário por ID ---")
   id_deletar = solicitar_int("ID do Funcionário a deletar")
   if id_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar o funcionário com ID '{id_deletar}'?") == True:
       try:
           mod_funcionario.Funcionario.deletar_funcionario_por_id(id_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar funcionário: {e}")
   else:
       print("\nDeleção cancelada.")

# Funções auxiliares de UI para Agendas
def _cadastrar_agendamento_ui():
   print("--- Cadastrar Novo Agendamento ---")

   func_obj = solicitar_funcionario_para_filtro()
   if func_obj is None: return

   cli_obj = solicitar_cliente_para_filtro()
   if cli_obj is None: return

   # Solicitar e validar data e hora de início
   while True:
       data_inicio_str = solicitar_data("Data de Início (DD/MM/YYYY)", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
       if data_inicio_str is None: return
       hora_inicio_str = solicitar_string("Hora de Início (HH:MM)", pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$", description="HH:MM")
       if hora_inicio_str is None: return
       data_hora_inicio_str_combined = f"{data_inicio_str} {hora_inicio_str}"
       try:
           data_hora_inicio_dt = pessoa.Pessoa._parse_data(data_hora_inicio_str_combined, is_datetime=True)
           break
       except ValueError as e:
           print(f"Erro na data/hora de início: {e}. Por favor, digite novamente.")

   # Solicitar e validar hora de fim (usando a mesma data de início)
   while True:
       hora_fim_str = solicitar_string("Hora de Fim (HH:MM, no mesmo dia da data de início)", pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$", description="HH:MM")
       if hora_fim_str is None: return
       data_hora_fim_str_combined = f"{data_inicio_str} {hora_fim_str}" # Usa a data de início para a data de fim
       try:
           data_hora_fim_dt = pessoa.Pessoa._parse_data(data_hora_fim_str_combined, is_datetime=True)
           if data_hora_fim_dt <= data_hora_inicio_dt:
               print("Erro: A hora de fim deve ser posterior à hora de início.")
               continue
           break
       except ValueError as e:
           print(f"Erro na data/hora de fim: {e}. Por favor, digite novamente.")

   itens_agendados = []
   while True:
       print("\n--- Adicionar Itens Agendados (Serviços/Produtos) ---")
       # Corrigido o tipo_item para ser passado em minúsculas e sem acento
       tipo_item = solicitar_string("Tipo de Item (s para servico, p para produto)", pattern=r"^[sp]$", description="s ou p")
       if tipo_item is None: break

       if tipo_item.lower() == 's':
           item_base_obj = solicitar_produto_ou_servico("servico", buscar_por_id=True)
       else:
           item_base_obj = solicitar_produto_ou_servico("produto", buscar_por_id=True)

       if item_base_obj is None: continue

       while True:
           quantidade = solicitar_float("Quantidade (para serviço, pode ser horas; para produto, unidades)", min_val=0.01)
           if quantidade is None: break

           if isinstance(item_base_obj, produto.Produto):
               # A validação de estoque para AGENDADO é feita no __init__ da Agenda.
               # Este feedback antecipado é para UX, mas a validação rigorosa é da classe.
               if item_base_obj.estoque < quantidade:
                   print(f"Aviso: Estoque atual para o produto '{item_base_obj.nome}' é {item_base_obj.estoque:.2f}.")
                   print("Agendar uma quantidade maior pode resultar em erro na marcação como 'Realizado'.")
                   if not solicitar_sim_nao("Deseja informar uma quantidade menor ou continuar mesmo assim?") == True:
                       quantidade = None # Indica que o usuário não quer continuar com este item
                       break # Sai do loop de quantidade para escolher outro item ou cancelar
                   else:
                       continue # Pede para re-informar a quantidade
           break # Sai do loop de quantidade se tudo estiver ok

       if quantidade is None: continue # Se o usuário cancelou ou não inseriu quantidade válida

       valor_negociado_resp = solicitar_sim_nao("Deseja informar um valor negociado para este item?")
       if valor_negociado_resp is None: continue
       valor_negociado = solicitar_float("Valor Negociado Unitário", min_val=0.01) if valor_negociado_resp else None
       if valor_negociado is None and valor_negociado_resp: continue

       try:
           item_ag = mod_agenda.ItemAgendado(item_base_obj, quantidade, valor_negociado)
           itens_agendados.append(item_ag)
           print("Item adicionado ao agendamento.")
       except (ValueError, TypeError) as e:
           print(f"Erro ao adicionar item: {e}")

       if not solicitar_sim_nao("Deseja adicionar outro item?"):
           break

   if not itens_agendados:
       print("Erro: Nenhum item foi adicionado ao agendamento. Operação cancelada.")
       esperar_enter()
       return

   maquinas_agendadas = []
   if solicitar_sim_nao("Deseja associar máquinas a este agendamento?") == True:
       while True:
           maq_obj = solicitar_objeto("Máquina", mod_maquina.Maquina.buscar_maquina_id, "ID", "Número inteiro")
           if maq_obj is None: break
           if not isinstance(maq_obj, mod_maquina.Maquina):
               print("Erro: O objeto selecionado não é uma Máquina válida.")
               continue
           if maq_obj.status != mod_maquina.StatusMaquina.OPERANDO:
               print(f"Erro: Máquina '{maq_obj.nome}' (Série: {maq_obj.numero_serie}) não está 'Operando' e não pode ser agendada.")
               continue
           maquinas_agendadas.append(maq_obj)
           if not solicitar_sim_nao("Deseja adicionar outra máquina?"):
               break

   suprimentos_utilizados = []
   if solicitar_sim_nao("Deseja associar suprimentos a este agendamento?") == True:
       while True:
           sup_obj = solicitar_objeto("Suprimento", mod_suprimento.Suprimento.buscar_suprimento_id, "ID", "Número inteiro")
           if sup_obj is None: break
           if not isinstance(sup_obj, mod_suprimento.Suprimento):
               print("Erro: O objeto selecionado não é um Suprimento válido.")
               continue

           # Verificar se o suprimento já está na lista temporária e editar em vez de duplicar
           found_existing_sup = False
           for existing_sup_ag in suprimentos_utilizados:
               if existing_sup_ag.suprimento.id == sup_obj.id:
                   print(f"Suprimento '{sup_obj.nome}' já existe na lista. Por favor, use a opção (e)ditar para alterar a quantidade.")
                   found_existing_sup = True
                   break
           if found_existing_sup:
               continue

           while True:
               quantidade_sup = solicitar_float(f"Quantidade de {sup_obj.nome} ({sup_obj.unidade_medida}) a utilizar", min_val=0.01)
               if quantidade_sup is None: break

               # A validação de estoque para AGENDADO é feita no __init__ da Agenda.
               # Este feedback antecipado é para UX, mas a validação rigorosa é da classe.
               if sup_obj.estoque < quantidade_sup:
                   print(f"Aviso: Estoque atual para o suprimento '{sup_obj.nome}' é {sup_obj.estoque:.2f}.")
                   print("Agendar uma quantidade maior pode resultar em erro na marcação como 'Realizado'.")
                   if not solicitar_sim_nao("Deseja informar uma quantidade menor ou continuar mesmo assim?") == True:
                       quantidade_sup = None # Indica que o usuário não quer continuar com este suprimento
                       break # Sai do loop de quantidade para escolher outro suprimento ou cancelar
                   else:
                       continue # Pede para re-informar a quantidade
               break # Sai do loop de quantidade se tudo estiver ok

           if quantidade_sup is None: continue # Se o usuário cancelou ou não inseriu quantidade válida

           try:
               sup_ag = mod_agenda.SuprimentoAgendado(sup_obj, quantidade_sup)
               suprimentos_utilizados.append(sup_ag)
               print("Suprimento adicionado ao agendamento.")
           except (ValueError, TypeError) as e:
               print(f"Erro ao adicionar suprimento: {e}")

           if not solicitar_sim_nao("Deseja adicionar outro suprimento?"):
               break

   comentario = solicitar_string("Comentário (opcional)", min_len=0)
   if comentario is None: return

   try:
       mod_agenda.Agenda.criar_agenda(
           func_obj, cli_obj, data_hora_inicio_str_combined, data_hora_fim_str_combined,
           itens_agendados, comentario, maquinas_agendadas, suprimentos_utilizados,
           mod_agenda.AgendaStatus.AGENDADO
       )
       print(f"\nAgendamento com ID {((mod_agenda.Agenda._proximo_id_disponivel)-1)} cadastrado com sucesso!")
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar agendamento: {e}")

def _listar_agendamentos_ui():
   print("--- Lista de Todos os Agendamentos ---")
   agendas_list = mod_agenda.Agenda.listar_agendas()
   _handle_report_output(agendas_list, "AGENDA", "Lista de Agendamentos", mod_agenda.Agenda._formatar_agendas_para_tabela)

def _buscar_agendamento_ui():
   print("--- Buscar Agendamento por ID ---")
   id_busca = solicitar_int("ID do Agendamento", min_val=1)
   if id_busca is None: return

   agenda = mod_agenda.Agenda.buscar_agenda(id_busca)
   if agenda:
       print("\nAgendamento Encontrado:")
       print(agenda)
   else:
       print(f"\nAgendamento com ID '{id_busca}' não encontrado.")

def _atualizar_agendamento_ui():
   print("--- Atualizar Dados do Agendamento ---")
   id_atualizar = solicitar_int("ID do Agendamento a atualizar", min_val=1)
   if id_atualizar is None: return

   agenda_existente = mod_agenda.Agenda.buscar_agenda(id_atualizar)
   if not agenda_existente:
       print(f"Agendamento com ID '{id_atualizar}' não encontrado.")
       esperar_enter()
       return

   updates = {}

   if solicitar_sim_nao("Deseja alterar o Funcionário?") == True:
       novo_func_obj = solicitar_funcionario_para_filtro()
       if novo_func_obj is None: return
       updates['funcionario'] = novo_func_obj

   if solicitar_sim_nao("Deseja alterar o Cliente?") == True:
       novo_cli_obj = solicitar_cliente_para_filtro()
       if novo_cli_obj is None: return
       updates['cliente'] = novo_cli_obj

   if solicitar_sim_nao("Deseja alterar a Data e Hora de Início?") == True:
       nova_data_hora_inicio = solicitar_data_hora("Nova Data e Hora de Início", "DD/MM/YYYY HH:MM, DD-MM-YYYY HH:MM, DDMMYYYY HH:MM, DD MM YY(YY) HH:MM")
       if nova_data_hora_inicio is None: return
       updates['data_hora_inicio'] = nova_data_hora_inicio

   if solicitar_sim_nao("Deseja alterar a Data e Hora de Fim?") == True:
       nova_data_hora_fim = solicitar_data_hora("Nova Data e Hora de Fim", "DD/MM/YYYY HH:MM, DD-MM-YYYY HH:MM, DDMMYYYY HH:MM, DD MM YY(YY) HH:MM")
       if nova_data_hora_fim is None: return
       updates['data_hora_fim'] = nova_data_hora_fim

   if solicitar_sim_nao("Deseja alterar as Máquinas agendadas?") == True:
       maquinas_novas_temp = []
       print("\n--- Máquinas Atuais: ---")
       if agenda_existente.maquinas_agendadas:
           for i, maq in enumerate(agenda_existente.maquinas_agendadas):
               print(f"{i+1}. {maq.nome} (Série: {maq.numero_serie})")
           maquinas_novas_temp.extend(agenda_existente.maquinas_agendadas)
       else:
           print("Nenhuma máquina associada atualmente.")

       while True:
           op_maquina = solicitar_string("Deseja (a)dicionar, (r)emover ou (c)ancelar a edição de máquinas?", pattern=r"^[arc", description="a, r ou c")
           if op_maquina is None or op_maquina == 'c':
               break

           if op_maquina == 'a':
               maq_add = solicitar_objeto("Máquina", mod_maquina.Maquina.buscar_maquina_id, "ID", "Número inteiro")
               if maq_add:
                   if not isinstance(maq_add, mod_maquina.Maquina):
                       print("Erro: O objeto selecionado não é uma Máquina válida.")
                       continue
                   if maq_add.status != mod_maquina.StatusMaquina.OPERANDO:
                       print(f"Erro: Máquina '{maq_add.nome}' (Série: {maq_add.numero_serie}) não está 'Operando' e não pode ser agendada.")
                   elif maq_add in maquinas_novas_temp:
                       print(f"Máquina '{maq_add.nome}' já está na lista.")
                   else:
                       maquinas_novas_temp.append(maq_add)
                       print(f"Máquina '{maq_add.nome}' adicionada temporariamente para esta atualização.")
           elif op_maquina == 'r':
               if not maquinas_novas_temp:
                   print("Não há máquinas para remover.")
                   continue

               print("\nLista de Máquinas (escolha o número para remover):")
               for i, maq in enumerate(maquinas_novas_temp):
                   print(f"{i+1}. {maq.nome} (Série: {maq.numero_serie})")

               idx_remover = solicitar_int("Número da máquina para remover", min_val=1, description=f"Número entre 1 e {len(maquinas_novas_temp)}")
               if idx_remover is None: continue
               if 1 <= idx_remover <= len(maquinas_novas_temp):
                   maq_removida = maquinas_novas_temp.pop(idx_remover - 1)
                   print(f"Máquina '{maq_removida.nome}' removida temporariamente.")
               else:
                   print("Número inválido.")
           else:
               break
       updates['maquinas_agendadas'] = maquinas_novas_temp

   if solicitar_sim_nao("Deseja alterar os Suprimentos utilizados?") == True:
       suprimentos_novos_temp = list(agenda_existente.suprimentos_utilizados) # Copia a lista atual
       print("\n--- Suprimentos Atuais: ---")
       if suprimentos_novos_temp:
           for i, sup_ag in enumerate(suprimentos_novos_temp):
               print(f"{i+1}. {sup_ag.suprimento.nome} (Qtd: {sup_ag.quantidade} {sup_ag.suprimento.unidade_medida})")
       else:
           print("Nenhum suprimento associado atualmente.")

       while True:
           op_suprimento = solicitar_string("Deseja (a)dicionar, (r)emover, (e)ditar quantidade ou (c)ancelar a edição de suprimentos?", pattern=r"^[arec]$", description="a, r, e ou c")
           if op_suprimento is None or op_suprimento == 'c':
               break

           if op_suprimento == 'a':
               sup_add = solicitar_objeto("Suprimento", mod_suprimento.Suprimento.buscar_suprimento_id, "ID", "Número inteiro")
               if sup_add:
                   if not isinstance(sup_add, mod_suprimento.Suprimento):
                       print("Erro: O objeto selecionado não é um Suprimento válido.")
                       continue

                   # Verifica se já está na lista temporária e atualiza a quantidade
                   found_existing = False
                   for existing_sup_ag in suprimentos_novos_temp:
                       if existing_sup_ag.suprimento.id == sup_add.id:
                           print(f"Suprimento '{sup_add.nome}' já existe na lista. Por favor, use a opção (e)ditar para alterar a quantidade.")
                           found_existing = True
                           break
                   if found_existing:
                       continue

                   quantidade_sup_add = solicitar_float(f"Quantidade de {sup_add.nome} ({sup_add.unidade_medida}) a utilizar", min_val=0.01)
                   if quantidade_sup_add is None: continue

                   try:
                       sup_ag_add = mod_agenda.SuprimentoAgendado(sup_add, quantidade_sup_add)
                       suprimentos_novos_temp.append(sup_ag_add)
                       print("Suprimento adicionado temporariamente para esta atualização.")
                   except (ValueError, TypeError) as e:
                       print(f"Erro ao adicionar suprimento: {e}")

           elif op_suprimento == 'r':
               if not suprimentos_novos_temp:
                   print("Não há suprimentos para remover.")
                   continue

               print("\nLista de Suprimentos (escolha o número para remover):")
               for i, sup_ag in enumerate(suprimentos_novos_temp):
                   print(f"{i+1}. {sup_ag.suprimento.nome} (Qtd: {sup_ag.quantidade})")

               idx_remover = solicitar_int("Número do suprimento para remover", min_val=1, description=f"Número entre 1 e {len(suprimentos_novos_temp)}")
               if idx_remover is None: continue
               if 1 <= idx_remover <= len(suprimentos_novos_temp):
                   sup_ag_removido = suprimentos_novos_temp.pop(idx_remover - 1)
                   print(f"Suprimento '{sup_ag_removido.suprimento.nome}' removido temporariamente.")
               else:
                   print("Número inválido.")

           elif op_suprimento == 'e':
               if not suprimentos_novos_temp:
                   print("Não há suprimentos para editar.")
                   continue

               print("\nLista de Suprimentos (escolha o número para editar):")
               for i, sup_ag in enumerate(suprimentos_novos_temp):
                   print(f"{i+1}. {sup_ag.suprimento.nome} (Qtd: {sup_ag.quantidade})")

               idx_editar = solicitar_int("Número do suprimento para editar a quantidade", min_val=1, description=f"Número entre 1 e {len(suprimentos_novos_temp)}")
               if idx_editar is None: continue
               if 1 <= idx_editar <= len(suprimentos_novos_temp):
                   sup_ag_editar = suprimentos_novos_temp[idx_editar - 1]
                   nova_quantidade_sup = solicitar_float(f"Nova quantidade para {sup_ag_editar.suprimento.nome} ({sup_ag_editar.suprimento.unidade_medida})", min_val=0.01)
                   if nova_quantidade_sup is None: continue
                   try:
                       sup_ag_editar.atualizar_quantidade(nova_quantidade_sup)
                       print("Quantidade do suprimento atualizada temporariamente.")
                   except (ValueError, TypeError) as e:
                       print(f"Erro ao atualizar quantidade do suprimento: {e}")
               else:
                   print("Número inválido.")

       updates['suprimentos_utilizados'] = suprimentos_novos_temp

   if solicitar_sim_nao("Deseja alterar o Status do Agendamento?") == True:
       print("Status disponíveis: Agendado, Realizado, Não Realizado")
       novo_status_str = solicitar_string("Novo Status (ex: 'Agendado', 'Realizado', 'Nao Realizado')",
                                              pattern=r"^(agendado|realizado|nao realizado)$",
                                              description="Agendado, Realizado ou Não Realizado")
       if novo_status_str is None: return
       updates['status'] = novo_status_str

   if solicitar_sim_nao("Deseja alterar o Comentário?") == True:
       novo_comentario = solicitar_string("Novo Comentário (opcional)", min_len=0)
       if novo_comentario is None: return
       updates['comentario'] = novo_comentario

   if updates:
       try:
           mod_agenda.Agenda.atualizar_dados_agenda(id_atualizar, **updates)
           print(f"\nAgendamento ID '{id_atualizar}' atualizado com sucesso!")
       except (ValueError, TypeError) as e:
           print(f"\nErro ao atualizar agendamento: {e}")
   else:
       print("\nNenhuma alteração solicitada.")

def _deletar_agendamento_ui():
   print("--- Deletar Agendamento ---")
   id_deletar = solicitar_int("ID do Agendamento a deletar", min_val=1)
   if id_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar o agendamento ID '{id_deletar}'?") == True:
       try:
           mod_agenda.Agenda.deletar_agenda(id_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar agendamento: {e}")
   else:
       print("\nDeleção cancelada.")

def _filtrar_agendamentos_ui():
   print("--- Filtrar Agendamentos por Período e Critérios ---")
   data_inicio = solicitar_data("Data de Início do Período", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_inicio is None: return
   data_fim = solicitar_data("Data de Fim do Período", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_fim is None: return

   func_filtro = None
   if solicitar_sim_nao("Deseja filtrar por Funcionário?") == True:
       func_filtro = solicitar_funcionario_para_filtro()
       if func_filtro is None:
           return

   cli_filtro = None
   if solicitar_sim_nao("Deseja filtrar por Cliente?") == True:
       cli_filtro = solicitar_cliente_para_filtro()
       if cli_filtro is None:
           return

   status_filtro = None
   if solicitar_sim_nao("Deseja filtrar por Status da Agenda?") == True:
       print("Status disponíveis: Agendado, Realizado, Não Realizado")
       status_str = solicitar_string("Digite o Status para filtro", pattern=r"^(agendado|realizado|nao realizado)$", description="Agendado, Realizado ou Não Realizado")
       if status_str is None:
           return
       else:
           try:
               status_filtro = mod_agenda.AgendaStatus[status_str.upper().replace(" ", "_")]
           except ValueError as e:
               print(f"Erro: {e}")
               return

   try:
       agendas_filtradas = mod_agenda.Agenda.filtrar_agendas(
           data_inicio, data_fim,
           funcionario_obj=func_filtro,
           cliente_obj=cli_filtro,
           status_agenda=status_filtro
       )
       _handle_report_output(agendas_filtradas, "AGENDA", "Agendamentos Filtrados", mod_agenda.Agenda._formatar_agendas_para_tabela)

   except ValueError as e:
       print(f"\nErro ao filtrar agendamentos: {e}")

def _marcar_agendamento_realizado_ui():
   print("--- Marcar Agendamento como Realizado ---")
   id_agenda = solicitar_int("ID do Agendamento a marcar como Realizado", min_val=1)
   if id_agenda is None: return

   agenda = mod_agenda.Agenda.buscar_agenda(id_agenda)
   if not agenda:
       print(f"Agendamento com ID '{id_agenda}' não encontrado.")
       esperar_enter()
       return

   print(f"\nDetalhes do Agendamento ID {id_agenda}:\n{agenda}")

   if agenda.status == mod_agenda.AgendaStatus.REALIZADO:
       print("Agendamento já está REALIZADO. Nenhuma ação necessária.")
       esperar_enter()
       return

   if agenda.data_hora_fim > datetime.now():
       print("Aviso: A data/hora de término do agendamento ainda não passou. Ao marcar como REALIZADO agora, os estoques serão deduzidos.")
       confirm = solicitar_sim_nao("Deseja continuar e marcar como REALIZADO mesmo assim?")
       if confirm is None or not confirm:
           print("Operação cancelada.")
           return

   if solicitar_sim_nao(f"Tem certeza que deseja marcar o agendamento ID '{id_agenda}' como REALIZADO? Isso afetará o estoque de suprimentos e produtos.") == True:
       try:
           agenda.marcar_como_realizado()
       except (ValueError, TypeError) as e:
           print(f"\nErro ao marcar agendamento como Realizado: {e}")
   else:
       print("\nOperação cancelada.")

def _marcar_agendamento_nao_realizado_ui():
   print("--- Marcar Agendamento como Não Realizado ---")
   id_agenda = solicitar_int("ID do Agendamento a marcar como Não Realizado", min_val=1)
   if id_agenda is None: return

   agenda = mod_agenda.Agenda.buscar_agenda(id_agenda)
   if not agenda:
       print(f"Agendamento com ID '{id_agenda}' não encontrado.")
       esperar_enter()
       return

   print(f"\nDetalhes do Agendamento ID {id_agenda}:\n{agenda}")

   if agenda.status == mod_agenda.AgendaStatus.NAO_REALIZADO:
       print("Agendamento já está NÃO REALIZADO. Nenhuma ação necessária.")
       esperar_enter()
       return

   if solicitar_sim_nao(f"Tem certeza que deseja marcar o agendamento ID '{id_agenda}' como NÃO REALIZADO? Isso reverterá o estoque de suprimentos e produtos se ele já foi deduzido.") == True:
       try:
           agenda.marcar_como_nao_realizado()
       except (ValueError, TypeError) as e:
           print(f"\nErro ao marcar agendamento como Não Realizado: {e}")
   else:
       print("\nOperação cancelada.")

# Funções auxiliares de UI para Vendas
def _cadastrar_venda_ui():
   print("--- Cadastrar Nova Venda ---")

   agenda_obj = None
   func_obj = None
   cli_obj = None
   # Flag para saber se uma agenda foi associada no início do processo
   # e se ela precisará ser revertida em caso de cancelamento/erro.
   agenda_linked_during_process = False

   agenda_resp = solicitar_sim_nao("Deseja associar esta venda a um agendamento existente?")
   if agenda_resp is None:
       return  # Usuário cancelou a operação inicial

   if agenda_resp:
       while True:
           agenda_id_input = solicitar_int("ID do Agendamento a associar", min_val=1)
           if agenda_id_input is None:
               return  # Usuário cancelou a seleção do ID da agenda

           temp_agenda_obj = mod_agenda.Agenda.buscar_agenda(agenda_id_input)
           if temp_agenda_obj:
               if temp_agenda_obj.status == mod_agenda.AgendaStatus.REALIZADO:
                   print(f"Erro: Agendamento ID {temp_agenda_obj.id} já está REALIZADO. Não pode ser usado em uma nova venda.")
                   if not solicitar_sim_nao("Deseja tentar outro agendamento ou cancelar a venda?"):
                       return
                   continue
               # Armazenar o objeto da agenda temporariamente
               agenda_obj = temp_agenda_obj
               func_obj = agenda_obj.funcionario
               cli_obj = agenda_obj.cliente
               print(f"--> Agendamento ID {agenda_obj.id} selecionado.")
               print(f"--> Funcionário automaticamente definido como: {func_obj.nome} (CPF: {func_obj.cpf})")
               print(f"--> Cliente automaticamente definido como: {cli_obj.nome} (CPF: {cli_obj.cpf})")
               agenda_linked_during_process = True # Marca que uma agenda foi selecionada
               break  # Agendamento válido selecionado, prosseguir
           else:
               print(f"Agendamento com ID '{agenda_id_input}' não encontrado.")
               if not solicitar_sim_nao("Deseja tentar novamente buscar o agendamento?"):
                   return
   else:  # Usuário não quer associar a uma agenda, solicita func e cli manualmente
       func_obj = solicitar_funcionario_para_filtro()
       if func_obj is None: return
       cli_obj = solicitar_cliente_para_filtro()
       if cli_obj is None: return

   # Se func_obj ou cli_obj ainda são None (significa que o usuário cancelou a seleção do func/cli manual ou da agenda)
   if func_obj is None or cli_obj is None:
       print("Operação de venda cancelada devido à seleção incompleta de funcionário/cliente/agenda.")
       return

   # Coletar os detalhes restantes da venda
   data_venda = solicitar_data("Data da Venda", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_venda is None:
       print("Venda cancelada.")
       return

   itens_venda = []
   if solicitar_sim_nao("Deseja adicionar itens avulsos a esta venda?") == True:
       print("\n--- Adicionar Itens de Venda Avulsos ---")
       while True:
           print("\n--- Adicionar Item (Servico/Produto) ---")
           tipo_item = solicitar_string("Tipo de Item (s para servico, p para produto)", pattern=r"^[sp]$", description="s ou p")
           if tipo_item is None: break

           if tipo_item.lower() == 's':
               item_base_obj = solicitar_produto_ou_servico("servico", buscar_por_id=True)
           else:
               item_base_obj = solicitar_produto_ou_servico("produto", buscar_por_id=True)

           if item_base_obj is None: continue

           while True:
               quantidade = solicitar_float("Quantidade", min_val=0.01)
               if quantidade is None: break

               if isinstance(item_base_obj, produto.Produto):
                   if item_base_obj.estoque < quantidade:
                       print(f"Erro: Estoque insuficiente para o produto '{item_base_obj.nome}'.")
                       print(f"Estoque disponível: {item_base_obj.estoque:.2f}.")
                       if not solicitar_sim_nao("Deseja informar uma quantidade menor ou cancelar a adição deste item?") == True:
                           quantidade = None
                           break
                       else:
                           continue
               break

           if quantidade is None: continue

           preco_unitario_resp = solicitar_sim_nao("Deseja informar um preço unitário especial para este item?")
           if preco_unitario_resp is None: continue
           preco_unitario = solicitar_float("Preço Unitário Especial", min_val=0.01) if preco_unitario_resp else None
           if preco_unitario is None and preco_unitario_resp: continue

           try:
               item_v = mod_venda.ItemVenda(item_base_obj, quantidade, preco_unitario)
               itens_venda.append(item_v)
               print("Item avulso adicionado à venda.")
           except (ValueError, TypeError) as e:
               print(f"Erro ao adicionar item: {e}")

           if not solicitar_sim_nao("Deseja adicionar outro item avulso?"):
               break

   if not itens_venda and agenda_obj is None:
       print("Erro: Venda sem itens avulsos e sem agendamento associado. Operação cancelada.")
       esperar_enter()
       return

   comentario = solicitar_string("Comentário (opcional)", min_len=0)
   if comentario is None:
       print("Venda cancelada.")
       return

   # Tenta criar a venda. Se for bem-sucedido, a agenda (se houver) é marcada como REALIZADO
   # e os estoques são ajustados. Se falhar em qualquer ponto, a agenda é revertida.
   try:
       mod_venda.Venda.criar_venda(func_obj, cli_obj, itens_venda, data_venda, agenda_obj, comentario)
       print(f"\nVenda ID {((mod_venda.Venda._proximo_id_disponivel)-1)} cadastrada com sucesso!")

   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar venda: {e}")
       # Se um erro ocorreu na criação da venda (ou na marcação da agenda), e uma agenda estava associada, reverter o status da agenda.
       if agenda_linked_during_process and agenda_obj:
           print("Erro na criação da venda. Revertendo status do agendamento...")
           try:
               agenda_obj.marcar_como_nao_realizado()
               agenda_obj.status = mod_agenda.AgendaStatus.AGENDADO # Reverte para AGENDADO para que possa ser reutilizada
               print(f"Agendamento ID {agenda_obj.id} revertido para AGENDADO e estoque restaurado.")
           except Exception as revert_e:
               print(f"Erro adicional ao tentar reverter agendamento ID {agenda_obj.id}: {revert_e}")
   except Exception as e: # Captura qualquer outro erro inesperado
       print(f"\nOcorreu um erro inesperado durante o cadastro da venda: {e}")
       if agenda_linked_during_process and agenda_obj:
           print("Erro inesperado. Revertendo status do agendamento...")
           try:
               agenda_obj.marcar_como_nao_realizado()
               agenda_obj.status = mod_agenda.AgendaStatus.AGENDADO # Reverte para AGENDADO
               print(f"Agendamento ID {agenda_obj.id} revertido para AGENDADO e estoque restaurado.")
           except Exception as revert_e:
                print(f"Erro adicional ao tentar reverter agendamento ID {agenda_obj.id}: {revert_e}")

def _listar_vendas_ui():
   print("--- Lista de Todas as Vendas ---")
   vendas_list = mod_venda.Venda.listar_vendas()
   _handle_report_output(vendas_list, "VENDA", "Lista de Vendas", mod_venda.Venda._formatar_vendas_para_tabela)

def _buscar_venda_ui():
   print("--- Buscar Venda por ID ---")
   id_busca = solicitar_int("ID da Venda", min_val=1)
   if id_busca is None: return

   venda = mod_venda.Venda.buscar_venda(id_busca)
   if venda:
       print("\nVenda Encontrada:")
       print(venda)
   else:
       print(f"\nVenda com ID '{id_busca}' não encontrada.")

def _atualizar_venda_ui():
   print("--- Atualizar Dados da Venda ---")
   id_atualizar = solicitar_int("ID da Venda a atualizar", min_val=1)
   if id_atualizar is None: return

   venda_existente = mod_venda.Venda.buscar_venda(id_atualizar)
   if not venda_existente:
       print(f"Venda com ID '{id_atualizar}' não encontrada.")
       esperar_enter()
       return

   updates = {}

   # Apenas permite alterar func/cli se NÃO estiver associado a uma agenda,
   # ou se a agenda associada foi removida na mesma operação de atualização.
   # A lógica aqui pode ser complexa dependendo das regras de negócio.
   # Por simplicidade, vou permitir mudar se não há agenda ou se a agenda *atual* não é REALIZADO.
   # Se a agenda estiver REALIZADO, a venda não deveria ser atualizada para não desvirtualizar a baixa de estoque.
   # Ou, se permite, a atualização de func/cli da venda não altera a agenda.

   if venda_existente.agenda and venda_existente.agenda.status == mod_agenda.AgendaStatus.REALIZADO:
       print("Aviso: Esta venda está associada a um agendamento REALIZADO.")
       print("Alterar funcionário ou cliente diretamente nesta venda pode causar inconsistência de dados.")
       if not solicitar_sim_nao("Deseja prosseguir com as alterações, mesmo assim?"):
           return

   if solicitar_sim_nao("Deseja alterar o Funcionário?") == True:
       novo_func_obj = solicitar_funcionario_para_filtro()
       if novo_func_obj is None: return
       updates['funcionario'] = novo_func_obj

   if solicitar_sim_nao("Deseja alterar o Cliente?") == True:
       novo_cli_obj = solicitar_cliente_para_filtro()
       if novo_cli_obj is None: return
       updates['cliente'] = novo_cli_obj

   if solicitar_sim_nao("Deseja alterar a Data da Venda?") == True:
       nova_data_venda = solicitar_data("Nova Data da Venda", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
       if nova_data_venda is None: return
       updates['data_venda'] = nova_data_venda

   if solicitar_sim_nao("Deseja alterar a Agenda associada?") == True:
       agenda_resp_att = solicitar_sim_nao("Deseja associar uma nova agenda (s) ou remover a existente (n)?")
       if agenda_resp_att is None: return
       if agenda_resp_att:
           nova_agenda_obj = solicitar_objeto("Agendamento", mod_agenda.Agenda.buscar_agenda,
                                              "ID", "Número inteiro")
           if nova_agenda_obj is None: return
           # Tenta marcar a nova agenda como realizada
           try:
               # A dedução de estoque para itens da nova agenda acontecerá dentro de marcar_como_realizado()
               nova_agenda_obj.marcar_como_realizado()
               updates['agenda_obj'] = nova_agenda_obj
               # Se a agenda mudou, garantir que func/cli da venda correspondam à nova agenda
               updates['funcionario'] = nova_agenda_obj.funcionario
               updates['cliente'] = nova_agenda_obj.cliente
               print(f"--> Agendamento ID {nova_agenda_obj.id} marcado como REALIZADO e associado à venda.")
               print(f"--> Funcionário e Cliente da venda atualizados para corresponder à nova agenda.")
           except (ValueError, TypeError) as e:
               print(f"Erro ao associar nova agenda: {e}. Alteração de agenda cancelada.")
               return
       else:
           # Se a agenda existente for removida, reverter o estoque dela se estava REALIZADO
           if venda_existente.agenda and venda_existente.agenda.status == mod_agenda.AgendaStatus.REALIZADO:
               if solicitar_sim_nao("Ao remover a agenda associada, deseja reverter o status da agenda para AGENDADO e reverter os estoques?") == True:
                   try:
                       venda_existente.agenda.marcar_como_nao_realizado()
                       venda_existente.agenda.status = mod_agenda.AgendaStatus.AGENDADO # Garante que o status é AGENDADO após reversão
                       print(f"Agenda ID {venda_existente.agenda.id} revertida para AGENDADO e estoque restaurado.")
                   except (ValueError, TypeError) as e:
                       print(f"Erro ao reverter status da agenda: {e}. Remoção da agenda cancelada.")
                       return
               else:
                   print("Remoção da agenda cancelada para evitar inconsistências.")
                   return
           updates['agenda_obj'] = None # Remove a agenda

   if solicitar_sim_nao("Deseja alterar o Comentário?") == True:
       novo_comentario = solicitar_string("Novo Comentário (opcional)", min_len=0)
       if novo_comentario is None: return
       updates['comentario'] = novo_comentario

   if updates:
       try:
           mod_venda.Venda.atualizar_dados_venda(id_atualizar, **updates)
           print(f"\nVenda ID '{id_atualizar}' atualizada com sucesso!")
       except (ValueError, TypeError) as e:
           print(f"\nErro ao atualizar venda: {e}")
   else:
       print("\nNenhuma alteração solicitada.")

def _deletar_venda_ui():
   print("--- Deletar Venda ---")
   id_deletar = solicitar_int("ID da Venda a deletar", min_val=1)
   if id_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar a venda ID '{id_deletar}'?") == True:
       try:
           mod_venda.Venda.deletar_venda(id_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar venda: {e}")
   else:
       print("\nDeleção cancelada.")

def _filtrar_vendas_ui():
   print("--- Filtrar Vendas por Período e Critérios ---")
   data_inicio = solicitar_data("Data de Início do Período", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_inicio is None: return
   data_fim = solicitar_data("Data de Fim do Período", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_fim is None: return

   func_filtro = None
   if solicitar_sim_nao("Deseja filtrar por Funcionário?") == True:
       func_filtro = solicitar_funcionario_para_filtro()
       if func_filtro is None:
           return

   cli_filtro = None
   if solicitar_sim_nao("Deseja filtrar por Cliente?") == True:
       cli_filtro = solicitar_cliente_para_filtro()
       if cli_filtro is None:
           return

   try:
       vendas_filtradas = mod_venda.Venda.filtrar_vendas(
           data_inicio, data_fim, funcionario_obj=func_filtro, cliente_obj=cli_filtro
       )
       _handle_report_output(vendas_filtradas, "VENDA", "Vendas Filtradas", mod_venda.Venda._formatar_vendas_para_tabela)
   except ValueError as e:
       print(f"\nErro ao filtrar vendas: {e}")

# Funções auxiliares de UI para Fornecedores
def _cadastrar_fornecedor_ui():
   print("--- Cadastrar Novo Fornecedor ---")
   nome = solicitar_string("Nome (Razão Social) do Fornecedor", min_len=3)
   if nome is None: return
   cnpj = solicitar_string("CNPJ (apenas números ou XX.XXX.XXX/XXXX-XX)", pattern=r"^(?:\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14})$", description="Formato: 'XX.XXX.XXX/XXXX-XX' ou 'XXXXXXXXXXXXXX'")
   if cnpj is None: return

   print("\n--- Informações de Contato ---")
   temp_telefone = solicitar_string("Telefone (Ex: +55 (11) 98765-4321 ou 11987654321)", min_len=8)
   temp_email = solicitar_string("Email (Ex: exemplo@dominio.com)", pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
   temp_endereco = solicitar_string("Endereço (Ex: Rua Nome, 123, Bairro, Cidade, UF ou Rua Nome, 123)", min_len=10)
   temp_redes_sociais = solicitar_string("Redes Sociais (opcional)", min_len=0)

   if any(item is None for item in [temp_telefone, temp_email, temp_endereco]):
       print("Cadastro de fornecedor cancelado devido a informações de contato incompletas.")
       return

   try:
       informacao_contato = mod_info.Informacao(temp_telefone, temp_email, temp_endereco, temp_redes_sociais if temp_redes_sociais is not None else "")  #type: ignore
       mod_fornecedor.Fornecedor.criar_fornecedor(nome, cnpj, informacao_contato)
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar fornecedor: {e}")

def _listar_fornecedores_ui():
   print("--- Lista de Todos os Fornecedores ---")
   fornecedores_list = mod_fornecedor.Fornecedor.listar_fornecedores()
   _handle_report_output(fornecedores_list, "FORNECEDOR", "Lista de Fornecedores", mod_fornecedor.Fornecedor._formatar_fornecedores_para_tabela)

def _buscar_fornecedor_cnpj_ui():
   print("--- Buscar Fornecedor por CNPJ ---")
   cnpj_busca = solicitar_string("CNPJ do Fornecedor (apenas números ou XX.XXX.XXX/XXXX-XX)")
   if cnpj_busca is None: return

   forn = mod_fornecedor.Fornecedor.buscar_fornecedor(cnpj_busca)
   if forn:
       print("\nFornecedor Encontrado:")
       print(forn)
   else:
       print(f"\nFornecedor com CNPJ '{cnpj_busca}' não encontrado.")

def _buscar_fornecedor_id_ui():
   print("--- Buscar Fornecedor por ID ---")
   id_busca = solicitar_int("ID do Fornecedor", min_val=1)
   if id_busca is None: return

   forn = mod_fornecedor.Fornecedor.buscar_fornecedor_id(id_busca)
   if forn:
       print("\nFornecedor Encontrado:")
       print(forn)
   else:
       print(f"\nFornecedor com ID '{id_busca}' não encontrado.")

def _buscar_fornecedor_por_nome_exato_ui():
   print("--- Buscar Fornecedor por Nome (Exato) ---")
   nome_busca = solicitar_string("Nome Exato do Fornecedor a buscar")
   if nome_busca is None: return

   forn = mod_fornecedor.Fornecedor.buscar_fornecedor_por_nome_exato(nome_busca)
   if forn:
       print("\nFornecedor Encontrado:")
       print(forn)
   else:
       print(f"\nFornecedor com nome '{nome_busca}' não encontrado.")

def _buscar_fornecedores_por_nome_parcial_ui():
   print("--- Buscar Fornecedores por Nome (Parcial) ---")
   nome_parcial = solicitar_string("Parte do Nome do Fornecedor a buscar")
   if nome_parcial is None: return

   fornecedores_encontrados = mod_fornecedor.Fornecedor.buscar_fornecedores_por_nome_parcial(nome_parcial)
   _handle_report_output(fornecedores_encontrados, "FORNECEDOR", "Fornecedores por Nome Parcial", mod_fornecedor.Fornecedor._formatar_fornecedores_para_tabela)

def _atualizar_dados_fornecedor_ui():
   print("--- Atualizar Dados do Fornecedor ---")
   id_atualizar = solicitar_int("ID do Fornecedor a atualizar", min_val=1)
   if id_atualizar is None: return

   forn_existente = mod_fornecedor.Fornecedor.buscar_fornecedor_id(id_atualizar)
   if not forn_existente:
       print(f"Fornecedor com ID '{id_atualizar}' não encontrado.")
       esperar_enter()
       return

   updates = {}

   if solicitar_sim_nao("Deseja alterar o nome?") == True:
       novo_nome = solicitar_string("Novo Nome (Razão Social)", min_len=3)
       if novo_nome is None: return
       updates['nome'] = novo_nome

   if solicitar_sim_nao("Deseja alterar informações de contato?") == True:
       print("\n--- Novas Informações de Contato ---")

       temp_telefone = solicitar_string("Telefone (Ex: +55 (11) 98765-4321 ou 11987654321)", min_len=8)
       temp_email = solicitar_string("Email (Ex: exemplo@dominio.com)", pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
       temp_endereco = solicitar_string("Endereço (Ex: Rua Nome, 123, Bairro, Cidade, UF ou Rua Nome, 123)", min_len=10)
       temp_redes_sociais = solicitar_string("Redes Sociais (opcional)", min_len=0)

       if any(item is None for item in [temp_telefone, temp_email, temp_endereco]):
           print("Atualização de informações de contato cancelada devido a entrada incompleta.")
       else:
           try:
               updates['informacao_contato'] = mod_info.Informacao(temp_telefone, temp_email, temp_endereco, temp_redes_sociais if temp_redes_sociais is not None else "")  #type: ignore
           except (ValueError, TypeError) as e:
               print(f"Erro ao criar novas informações de contato: {e}")
               esperar_enter()

   if updates:
       try:
           mod_fornecedor.Fornecedor.atualizar_dados_fornecedor(id_atualizar, **updates)
           print(f"\nFornecedor com ID '{id_atualizar}' atualizado com sucesso!")
       except (ValueError, TypeError) as e:
           print(f"\nErro ao atualizar fornecedor: {e}")
   else:
       print("\nNenhuma alteração solicitada.")

def _atualizar_cnpj_fornecedor_ui():
   print("--- Atualizar CNPJ do Fornecedor ---")
   id_forn_para_cnpj = solicitar_int("ID do Fornecedor cujo CNPJ será atualizado", min_val=1)
   if id_forn_para_cnpj is None: return

   forn_existente = mod_fornecedor.Fornecedor.buscar_fornecedor_id(id_forn_para_cnpj)
   if not forn_existente:
       print(f"Fornecedor com ID '{id_forn_para_cnpj}' não encontrado.")
       esperar_enter()
       return

   novo_cnpj = solicitar_string("Novo CNPJ do Fornecedor (apenas números ou XX.XXX.XXX/XXXX-XX)", pattern=r"^(?:\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14})$", description="Formato: 'XX.XXX.XXX/XXXX-XX' ou 'XXXXXXXXXXXXXX'")
   if novo_cnpj is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja alterar o CNPJ do fornecedor ID '{id_forn_para_cnpj}' de '{forn_existente.cnpj}' para '{novo_cnpj}'?") == True:
       try:
           mod_fornecedor.Fornecedor.atualizar_cnpj_fornecedor(forn_existente.cnpj, novo_cnpj)  #type: ignore
           print(f"\nCNPJ do fornecedor ID '{id_forn_para_cnpj}' atualizado com sucesso!")
       except ValueError as e:
           print(f"\nErro ao atualizar CNPJ: {e}")
   else:
       print("\nAtualização de CNPJ cancelada.")

def _deletar_fornecedor_ui():
   print("--- Deletar Fornecedor ---")
   id_deletar = solicitar_int("ID do Fornecedor a deletar", min_val=1)
   if id_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar o fornecedor ID '{id_deletar}'?") == True:
       try:
           mod_fornecedor.Fornecedor.deletar_fornecedor(id_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar fornecedor: {e}")
   else:
       print("\nDeleção cancelada.")

# Funções auxiliares de UI para Suprimentos
def _cadastrar_suprimento_ui():
   print("--- Cadastrar Novo Suprimento ---")
   nome = solicitar_string("Nome do Suprimento", min_len=3)
   if nome is None: return
   unidade = solicitar_string("Unidade de Medida (ex: 'unidade', 'litro', 'rolo')", min_len=1)
   if unidade is None: return
   custo = solicitar_float("Custo Unitário (ex: 5.50)", min_val=0.01)
   if custo is None: return
   estoque = solicitar_float("Quantidade em Estoque (pode ser decimal, ex: 10.5)", min_val=0.0)
   if estoque is None: return

   try:
       mod_suprimento.Suprimento.criar_suprimento(nome, unidade, custo, estoque)
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar suprimento: {e}")

def _listar_suprimentos_ui():
   print("--- Lista de Todos os Suprimentos ---")
   suprimentos_list = mod_suprimento.Suprimento.listar_suprimentos()
   _handle_report_output(suprimentos_list, "SUPRIMENTO", "Lista de Suprimentos", mod_suprimento.Suprimento._formatar_suprimentos_para_tabela)

def _buscar_suprimento_id_ui():
   print("--- Buscar Suprimento por ID ---")
   id_busca = solicitar_int("ID do Suprimento", min_val=1)
   if id_busca is None: return

   supr = mod_suprimento.Suprimento.buscar_suprimento_id(id_busca)
   if supr:
       print("\nSuprimento Encontrado:")
       print(supr)
   else:
       print(f"\nSuprimento com ID '{id_busca}' não encontrado.")

def _buscar_suprimento_nome_ui():
   print("--- Buscar Suprimento por Nome ---")
   nome_busca = solicitar_string("Nome do Suprimento a buscar")
   if nome_busca is None: return

   supr = mod_suprimento.Suprimento.buscar_suprimento_nome(nome_busca)
   if supr:
       print("\nSuprimento Encontrado:")
       print(supr)
   else:
       print(f"\nSuprimento '{nome_busca}' não encontrado.")

def _atualizar_suprimento_ui():
   print("--- Atualizar Dados do Suprimento ---")
   id_atualizar = solicitar_int("ID do Suprimento a atualizar", min_val=1)
   if id_atualizar is None: return

   supr_existente = mod_suprimento.Suprimento.buscar_suprimento_id(id_atualizar)
   if not supr_existente:
       print(f"Suprimento com ID '{id_atualizar}' não encontrado.")
       esperar_enter()
       return

   updates = {}

   if solicitar_sim_nao("Deseja alterar o nome?") == True:
       novo_nome = solicitar_string("Novo Nome do Suprimento", min_len=3)
       if novo_nome is None: return
       updates['nome'] = novo_nome

   if solicitar_sim_nao("Deseja alterar a unidade de medida?") == True:
       nova_unidade = solicitar_string("Nova Unidade de Medida", min_len=1)
       if nova_unidade is None: return
       updates['unidade_medida'] = nova_unidade

   if solicitar_sim_nao("Deseja alterar o custo unitário?") == True:
       novo_custo = solicitar_float("Novo Custo Unitário (ex: 7.00)", min_val=0.01)
       if novo_custo is None: return
       updates['custo_unitario'] = novo_custo

   if solicitar_sim_nao("Deseja alterar o estoque?") == True:
       novo_estoque = solicitar_float("Nova Quantidade em Estoque (pode ser decimal, ex: 10.5)", min_val=0.0)
       if novo_estoque is None: return
       updates['estoque'] = novo_estoque

   if updates:
       try:
           mod_suprimento.Suprimento.atualizar_dados_suprimento(id_atualizar, **updates)
           print(f"\nSuprimento ID '{id_atualizar}' atualizado com sucesso!")
       except (ValueError, TypeError) as e:
           print(f"\nErro ao atualizar suprimento: {e}")
   else:
       print("\nNenhuma alteração solicitada.")

def _deletar_suprimento_ui():
   print("--- Deletar Suprimento ---")
   id_deletar = solicitar_int("ID do Suprimento a deletar", min_val=1)
   if id_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar o suprimento ID '{id_deletar}'?") == True:
       try:
           mod_suprimento.Suprimento.deletar_suprimento(id_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar suprimento: {e}")
   else:
       print("\nDeleção cancelada.")

# Funções auxiliares de UI para Máquinas
def _cadastrar_maquina_ui():
   print("--- Cadastrar Nova Máquina ---")
   nome = solicitar_string("Nome da Máquina", min_len=3)
   if nome is None: return
   numero_serie = solicitar_string("Número de Série", min_len=5)
   if numero_serie is None: return
   custo = solicitar_float("Custo de Aquisição (ex: 15000.00)", min_val=0.01)
   if custo is None: return

   print("Status disponíveis: Operando, Em Manutenção, Baixado")
   status_str = solicitar_string("Status da Máquina (ex: 'Operando', 'Manutencao', 'Baixado')",
                                           pattern=r"^(operando|manutencao|baixado)$",
                                           description="Operando, Manutencao ou Baixado")
   if status_str is None: return

   try:
       status_enum = mod_maquina.StatusMaquina[status_str.upper()]
       mod_maquina.Maquina.criar_maquina(nome, numero_serie, custo, status_enum)
   except (ValueError, TypeError, KeyError) as e:
       print(f"\nErro ao cadastrar máquina: {e}")

def _listar_maquinas_ui():
   print("--- Lista de Todas as Máquinas ---")
   maquinas_list = mod_maquina.Maquina.listar_maquinas()
   _handle_report_output(maquinas_list, "MAQUINA", "Lista de Maquinas", mod_maquina.Maquina._formatar_maquinas_para_tabela)

def _buscar_maquina_id_ui():
   print("--- Buscar Máquina por ID ---")
   id_busca = solicitar_int("ID da Máquina", min_val=1)
   if id_busca is None: return

   maq = mod_maquina.Maquina.buscar_maquina_id(id_busca)
   if maq:
       print("\nMáquina Encontrada:")
       print(maq)
   else:
       print(f"\nMáquina com ID '{id_busca}' não encontrada.")

def _buscar_maquina_serie_ui():
   print("--- Buscar Máquina por Número de Série ---")
   serie_busca = solicitar_string("Número de Série da Máquina a buscar")
   if serie_busca is None: return

   maq = mod_maquina.Maquina.buscar_maquina_serie(serie_busca)
   if maq:
       print("\nMáquina Encontrada:")
       print(maq)
   else:
       print(f"\nMáquina com número de série '{serie_busca}' não encontrada.")

def _atualizar_maquina_ui():
   print("--- Atualizar Dados da Máquina ---")
   id_atualizar = solicitar_int("ID da Máquina a atualizar", min_val=1)
   if id_atualizar is None: return

   maq_existente = mod_maquina.Maquina.buscar_maquina_id(id_atualizar)
   if not maq_existente:
       print(f"Máquina com ID '{id_atualizar}' não encontrada.")
       esperar_enter()
       return

   updates = {}

   if solicitar_sim_nao("Deseja alterar o nome?") == True:
       novo_nome = solicitar_string("Novo Nome da Máquina", min_len=3)
       if novo_nome is None: return
       updates['nome'] = novo_nome

   if solicitar_sim_nao("Deseja alterar o número de série?") == True:
       nova_serie = solicitar_string("Novo Número de Série", min_len=5)
       if nova_serie is None: return
       updates['numero_serie'] = nova_serie

   if solicitar_sim_nao("Deseja alterar o custo de aquisição?") == True:
       novo_custo = solicitar_float("Novo Custo de Aquisição (ex: 15000.00)", min_val=0.01)
       if novo_custo is None: return
       updates['custo_aquisicao'] = novo_custo

   if solicitar_sim_nao("Deseja alterar o status?") == True:
       print("Status disponíveis: Operando, Em Manutenção, Baixado")
       novo_status_str = solicitar_string("Novo Status (ex: 'Operando', 'Manutencao', 'Baixado')",
                                              pattern=r"^(operando|manutencao|baixado)$",
                                              description="Operando, Manutencao ou Baixado")
       if novo_status_str is None: return
       try:
           updates['status'] = mod_maquina.StatusMaquina[novo_status_str.upper()]
       except KeyError:
           print(f"Erro: Status '{novo_status_str}' inválido. Por favor, digite um status válido.")
           return

   if updates:
       try:
           mod_maquina.Maquina.atualizar_dados_maquina(id_atualizar, **updates)
           print(f"\nMáquina ID '{id_atualizar}' atualizada com sucesso!")
       except (ValueError, TypeError) as e:
           print(f"\nErro ao atualizar máquina: {e}")
   else:
       print("\nNenhuma alteração solicitada.")

def _deletar_maquina_ui():
   print("--- Deletar Máquina ---")
   id_deletar = solicitar_int("ID da Máquina a deletar", min_val=1)
   if id_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar a máquina ID '{id_deletar}'?") == True:
       try:
           mod_maquina.Maquina.deletar_maquina(id_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar máquina: {e}")
   else:
       print("\nDeleção cancelada.")

# Funções auxiliares de UI para Despesas
def _cadastrar_compra_ui():
   print("--- Cadastrar Despesa de Compra ---")
   fornecedor_obj = solicitar_fornecedor_para_filtro()
   if fornecedor_obj is None: return

   item_comprado = solicitar_item_compra()
   if item_comprado is None: return

   quantidade = solicitar_float("Quantidade (ex: 2.5)", min_val=0.01)
   if quantidade is None: return
   valor_unitario = solicitar_float("Valor Unitário (ex: 150.75)", min_val=0.01)
   if valor_unitario is None: return
   data_despesa_str = solicitar_data("Data da Despesa", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_despesa_str is None: return
   comentario = solicitar_string("Comentário (opcional)", min_len=0)
   if comentario is None: return

   try:
       # A Compra.__init__ agora gerencia o ajuste de estoque e a atualização de custos para Produto/Suprimento
       mod_despesa.Compra(
           None, fornecedor_obj, item_comprado, quantidade, valor_unitario, data_despesa_str, comentario
       )
       print("\nDespesa de Compra cadastrada com sucesso!")
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar despesa de compra: {e}")

def _cadastrar_fixo_terceiro_ui():
   print("--- Cadastrar Despesa Fixa ou de Terceiro ---")
   valor = solicitar_float("Valor da Despesa (ex: 2500.00)", min_val=0.01)
   if valor is None: return
   tipo_despesa = solicitar_string("Tipo de Despesa (ex: 'Aluguel', 'Contabilidade')", min_len=3)
   if tipo_despesa is None: return

   fornecedor_resp = solicitar_sim_nao("Deseja associar um Fornecedor a esta despesa?")
   if fornecedor_resp is None: return
   fornecedor_obj = solicitar_fornecedor_para_filtro() if fornecedor_resp else None
   if fornecedor_obj is None and fornecedor_resp: # Se o usuário disse 's' mas não encontrou fornecedor
       print("Fornecedor não selecionado. Operação cancelada.")
       return

   data_despesa_str = solicitar_data("Data da Despesa", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_despesa_str is None: return
   comentario = solicitar_string("Comentário (opcional)", min_len=0)
   if comentario is None: return

   try:
       mod_despesa.FixoTerceiro(
           None, valor, tipo_despesa, fornecedor_obj, data_despesa_str, comentario
       )
       print("\nDespesa Fixa/Terceiro cadastrada com sucesso!")
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar despesa fixa/terceiro: {e}")

def _cadastrar_salario_ui():
   print("--- Cadastrar Despesa de Salário ---")
   funcionario_obj = solicitar_funcionario_para_filtro()
   if funcionario_obj is None: return
   salario_bruto = solicitar_float("Salário Bruto (ex: 3000.00)", min_val=0.01)
   if salario_bruto is None: return
   descontos = solicitar_float("Total de Descontos (ex: 250.00)", min_val=0.0)
   if descontos is None: return

   if descontos > salario_bruto:
       print("Erro: Descontos não podem ser maiores que o salário bruto.")
       return

   data_despesa_str = solicitar_data("Data da Despesa", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_despesa_str is None: return
   comentario = solicitar_string("Comentário (opcional)", min_len=0)
   if comentario is None: return

   try:
       mod_despesa.Salario(
           None, funcionario_obj, salario_bruto, descontos, data_despesa_str, comentario
       )
       print("\nDespesa de Salário cadastrada com sucesso!")
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar despesa de salário: {e}")

def _cadastrar_comissao_ui():
   print("--- Cadastrar Despesa de Comissão ---")
   funcionario_obj = solicitar_funcionario_para_filtro()
   if funcionario_obj is None: return

   valor_servicos = solicitar_float("Valor Total de Serviços Vendidos (base para comissão)", min_val=0.0)
   if valor_servicos is None: return
   taxa_servicos = solicitar_float("Taxa de Comissão sobre Serviços (ex: 0.05 para 5%)", min_val=0.0, description="Entre 0 e 1")
   if taxa_servicos is None: return

   valor_produtos = solicitar_float("Valor Total de Produtos Vendidos (base para comissão)", min_val=0.0)
   if valor_produtos is None: return
   taxa_produtos = solicitar_float("Taxa de Comissão sobre Produtos (ex: 0.02 para 2%)", min_val=0.0, description="Entre 0 e 1")
   if taxa_produtos is None: return

   if not (0 <= taxa_servicos <= 1) or not (0 <= taxa_produtos <= 1):
        print("Erro: Taxas de comissão devem estar entre 0 e 1 (0% a 100%).")
        return

   data_despesa_str = solicitar_data("Data da Despesa", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_despesa_str is None: return
   comentario = solicitar_string("Comentário (opcional)", min_len=0)
   if comentario is None: return

   try:
       mod_despesa.Comissao(
           None, funcionario_obj, valor_servicos, valor_produtos, taxa_servicos, taxa_produtos, data_despesa_str, comentario
       )
       print("\nDespesa de Comissão cadastrada com sucesso!")
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar despesa de comissão: {e}")

def _cadastrar_outros_ui():
   print("--- Cadastrar Outras Despesas ---")
   valor = solicitar_float("Valor da Despesa (ex: 150.00)", min_val=0.01)
   if valor is None: return
   tipo_despesa = solicitar_string("Tipo de Despesa (ex: 'Imposto', 'Marketing', 'Reparos')", min_len=3)
   if tipo_despesa is None: return
   data_despesa_str = solicitar_data("Data da Despesa", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_despesa_str is None: return
   comentario = solicitar_string("Comentário (opcional)", min_len=0)
   if comentario is None: return

   try:
       mod_despesa.Outros(
           None, valor, tipo_despesa, data_despesa_str, comentario
       )
       print("\nOutra Despesa cadastrada com sucesso!")
   except (ValueError, TypeError) as e:
       print(f"\nErro ao cadastrar outra despesa: {e}")

def _listar_despesas_ui():
   print("--- Lista de Todas as Despesas ---")
   despesas_list = mod_despesa.Despesa.listar_despesas()
   _handle_report_output(despesas_list, "DESPESA", "Lista de Despesas", mod_despesa.Despesa._formatar_despesas_para_tabela)

def _buscar_despesa_ui():
   print("--- Buscar Despesa por ID ---")
   id_busca = solicitar_int("ID da Despesa", min_val=1)
   if id_busca is None: return

   despesa = mod_despesa.Despesa.buscar_despesa(id_busca)
   if despesa:
       print("\nDespesa Encontrada:")
       print(despesa)
   else:
       print(f"\nDespesa com ID '{id_busca}' não encontrada.")

def _atualizar_dados_despesa_ui():
   print("--- Atualizar Dados do Despesa ---")
   id_atualizar = solicitar_int("ID do Despesa a atualizar", min_val=1)
   if id_atualizar is None: return

   despesa_existente = mod_despesa.Despesa.buscar_despesa(id_atualizar)
   if not despesa_existente:
       print(f"Despesa com ID '{id_atualizar}' não encontrada.")
       esperar_enter()
       return

   updates = {}

   if solicitar_sim_nao("Deseja alterar a Data da Despesa?") == True:
       nova_data = solicitar_data("Nova Data da Despesa", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
       if nova_data is None: return
       updates['data_despesa'] = nova_data

   if solicitar_sim_nao("Deseja alterar o Valor Total da Despesa?") == True:
       novo_valor = solicitar_float("Novo Valor Total da Despesa", min_val=0.01)
       if novo_valor is None: return
       updates['valor_total'] = novo_valor

   if solicitar_sim_nao("Deseja alterar o Comentário?") == True:
       novo_comentario = solicitar_string("Novo Comentário (opcional)", min_len=0)
       if novo_comentario is None: return
       updates['comentario'] = novo_comentario

   if updates:
       try:
           mod_despesa.Despesa.atualizar_dados_despesa(id_atualizar, **updates)
           print(f"\nDespesa ID '{id_atualizar}' atualizada com sucesso!")
       except (ValueError, TypeError) as e:
           print(f"\nErro ao atualizar despesa: {e}")
   else:
       print("\nNenhuma alteração solicitada.")

def _deletar_despesa_ui():
   print("--- Deletar Despesa ---")
   id_deletar = solicitar_int("ID do Despesa a deletar", min_val=1)
   if id_deletar is None: return

   if solicitar_sim_nao(f"Tem certeza que deseja deletar a despesa ID '{id_deletar}'?") == True:
       try:
           mod_despesa.Despesa.deletar_despesa(id_deletar)
       except ValueError as e:
           print(f"\nErro ao deletar despesa: {e}")
   else:
       print("\nDeleção cancelada.")

def _filtrar_despesas_ui():
   print("--- Filtrar Despesas por Período e Critérios ---")
   data_inicio = solicitar_data("Data de Início do Período", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_inicio is None: return
   data_fim = solicitar_data("Data de Fim do Período", "DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD MM YY(YY)")
   if data_fim is None: return

   tipos_filtrar: Optional[List[str]] = None
   tipo_despesa_resp = solicitar_sim_nao("Deseja filtrar por Tipo de Despesa?")
   if tipo_despesa_resp is None:
       return # Usuário cancelou o filtro completo
   elif tipo_despesa_resp == True:
       print("Tipos disponíveis: COMPRA, FIXO_TERCEIRO, SALARIO, COMISSAO, OUTROS")
       tipos_str = solicitar_string("Digite os tipos separados por vírgula (ex: 'COMPRA, SALARIO')", min_len=1)
       if tipos_str is None:
           return # Usuário cancelou o filtro completo
       else:
           tipos_filtrar = [t.strip() for t in tipos_str.split(',')]
           valid_types_normalized = {"COMPRA", "FIXOTERCEIRO", "SALARIO", "COMISSAO", "OUTROS"}
           if not all(t.upper().replace(" ", "").replace("_", "") in valid_types_normalized for t in tipos_filtrar):
               print("Erro: Tipo de despesa inválido digitado.")
               return

   func_filtro = None
   func_filtro_resp = solicitar_sim_nao("Deseja filtrar por Funcionário (aplicável a Salário e Comissão)?")
   if func_filtro_resp is None:
       return # Usuário cancelou o filtro completo
   elif func_filtro_resp == True:
       func_filtro = solicitar_funcionario_para_filtro()
       if func_filtro is None:
           return # Usuário cancelou a seleção, retorna do filtro completo

   forn_filtro = None
   forn_filtro_resp = solicitar_sim_nao("Deseja filtrar por Fornecedor (aplicável a Compra e Fixo/Terceiro)?")
   if forn_filtro_resp is None:
       return # Usuário cancelou o filtro completo
   elif forn_filtro_resp == True:
       forn_filtro = solicitar_fornecedor_para_filtro()
       if forn_filtro is None:
           return # Usuário cancelou a seleção, retorna do filtro completo

   item_filtro = None # Armazenará o objeto do item específico ou permanecerá None para "todos os itens de uma categoria"
   item_filtro_resp = solicitar_sim_nao("Deseja filtrar por Produto/Suprimento/Máquina (aplicável a Compra)?")
   if item_filtro_resp is None:
       return # Usuário cancelou o processo de filtro de itens
   elif item_filtro_resp == True:
       while True: # Loop para permitir a resseleção do tipo de item se inválido
           print("\n--- Filtrar por Item de Compra ---")
           print("1. Produto")
           print("2. Suprimento")
           print("3. Máquina")
           print("0. Cancelar")
           item_tipo_filtro_str = solicitar_string("Escolha o tipo de item para filtro", pattern=r"^[0-3]$", description="Número de 0 a 3")
           if item_tipo_filtro_str is None or item_tipo_filtro_str == '0':
               item_filtro = None # Define explicitamente como None se cancelado aqui.
               break # Sai do loop de seleção do tipo de item

           filtrar_especifico_escolha = solicitar_sim_nao(f"Deseja filtrar por um item ESPECÍFICO (s) ou por TODOS os itens desta categoria (n)?")
           if filtrar_especifico_escolha is None: # Usuário cancelou neste ponto
               item_filtro = None
               break

           if filtrar_especifico_escolha: # Usuário escolheu 's' para item específico
               if item_tipo_filtro_str == '1': # Produto
                   item_obj_filtro = solicitar_produto_ou_servico("produto", buscar_por_id=True)
                   if item_obj_filtro is None: continue # Repete o loop se o produto específico não foi encontrado ou cancelado
                   if not isinstance(item_obj_filtro, produto.Produto):
                       print("Erro: Selecionado tipo Produto, mas o objeto retornado não é um Produto.")
                       continue # Repete o loop
                   item_filtro = item_obj_filtro
                   break # Sai do loop de seleção do tipo de item
               elif item_tipo_filtro_str == '2': # Suprimento
                   id_suprimento_filtro = solicitar_int("ID do Suprimento para filtro", min_val=1)
                   if id_suprimento_filtro is None: continue # Repete o loop
                   suprimento_obj_filtro = mod_suprimento.Suprimento.buscar_suprimento_id(id_suprimento_filtro)
                   if suprimento_obj_filtro is None:
                       print(f"Suprimento com ID '{id_suprimento_filtro}' não encontrado.")
                       continue # Repete o loop
                   item_filtro = suprimento_obj_filtro
                   break # Sai do loop de seleção do tipo de item
               elif item_tipo_filtro_str == '3': # Máquina
                   id_maquina_filtro = solicitar_int("ID da Máquina para filtro", min_val=1)
                   if id_maquina_filtro is None: continue # Repete o loop
                   maquina_obj_filtro = mod_maquina.Maquina.buscar_maquina_id(id_maquina_filtro)
                   if maquina_obj_filtro is None:
                       print(f"Máquina com ID '{id_maquina_filtro}' não encontrada.")
                       continue # Repete o loop
                   item_filtro = maquina_obj_filtro
                   break # Sai do loop de seleção do tipo de item
           else: # Usuário escolheu 'n' para todos os itens desta categoria
               # item_filtro permanece None, o que significa filtrar implicitamente por tipo de categoria
               # O `tipo_despesa_str` deve ser 'COMPRA' para que este sub-filtro funcione
               if tipos_filtrar is None: # Se o usuário ainda não especificou 'COMPRA'
                   if solicitar_sim_nao("Para filtrar por TODOS os itens desta categoria, o filtro de Tipo de Despesa será definido como 'COMPRA'. Deseja continuar?") == True:
                       tipos_filtrar = ['COMPRA'] # Força este filtro de tipo
                       break # Sai do loop de seleção do tipo de item
                   else:
                       item_filtro = None # Usuário cancelou esta parte
                       break # Sai do loop de seleção do tipo de item
               elif 'COMPRA' not in [t.upper().replace(" ", "").replace("_", "") for t in tipos_filtrar]:
                   print("Aviso: Para filtrar por todos os itens desta categoria, o filtro de Tipo de Despesa deve incluir 'COMPRA'.")
                   if solicitar_sim_nao("Deseja adicionar 'COMPRA' aos tipos de despesa filtrados?") == True:
                       if tipos_filtrar is None: # Garante que é uma lista se era None
                           tipos_filtrar = ['COMPRA']
                       else:
                           tipos_filtrar.append('COMPRA')
                       break # Sai do loop de seleção do tipo de item
                   else:
                       item_filtro = None # Usuário cancelou esta parte
                       break # Sai do loop de seleção do tipo de item
               else: # 'COMPRA' já está em tipos_filtrar
                   break # Sai do loop de seleção do tipo de item, item_filtro é None

   comentario_parcial_filtro = None
   comentario_filtro_resp = solicitar_sim_nao("Deseja filtrar por parte do Comentário?")
   if comentario_filtro_resp is None:
       return # Usuário cancelou o filtro completo
   elif comentario_filtro_resp == True:
       comentario_parcial_filtro = solicitar_string("Parte do Comentário", min_len=1)
       if comentario_parcial_filtro is None:
           return # Usuário cancelou a entrada, retorna do filtro completo

   try:
       despesas_filtradas = mod_despesa.Despesa.filtrar_despesas(
           data_inicio, data_fim,
           tipo_despesa_str=tipos_filtrar,
           fornecedor_obj=forn_filtro,
           funcionario_obj=func_filtro,
           item_compra_obj=item_filtro,
           comentario_parcial=comentario_parcial_filtro
       )
       _handle_report_output(despesas_filtradas, "DESPESA", "Despesas Filtradas", mod_despesa.Despesa._formatar_despesas_para_tabela)
   except ValueError as e:
       print(f"\nErro ao filtrar despesas: {e}")

# Funções do Menu Principal (Chamando as funções de Menu da UI) ---
def menu_produtos():
   while True:
       limpar_tela()
       print("--- Gerenciar Produtos ---")
       print("1. Cadastrar Produto")
       print("2. Listar Todos os Produtos")
       print("3. Buscar Produto por ID ou Nome")
       print("4. Atualizar Dados do Produto")
       print("5. Deletar Produto")
       print("0. Voltar ao Menu Principal")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^[0-5]$", description="Número de 0 a 5")
       if escolha is None: return # Permite cancelar e voltar ao menu anterior

       limpar_tela()
       try:
           if escolha == '1': _cadastrar_produto_ui()
           elif escolha == '2': _listar_produtos_ui()
           elif escolha == '3': _buscar_produto_ui()
           elif escolha == '4': _atualizar_produto_ui()
           elif escolha == '5': _deletar_produto_ui()
           elif escolha == '0': return

       except Exception as e:
           print(f"\nOcorreu um erro inesperado: {e}")

       esperar_enter()

def menu_servicos():
   while True:
       limpar_tela()
       print("--- Gerenciar Serviços ---")
       print("1. Cadastrar Serviço")
       print("2. Listar Todos os Serviços")
       print("3. Buscar Serviço por ID ou Nome")
       print("4. Atualizar Dados do Serviço")
       print("5. Deletar Serviço")
       print("0. Voltar ao Menu Principal")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^[0-5]$", description="Número de 0 a 5")
       if escolha is None: return # Permite cancelar e voltar ao menu anterior

       limpar_tela()
       try:
           if escolha == '1': _cadastrar_servico_ui()
           elif escolha == '2': _listar_servicos_ui()
           elif escolha == '3': _buscar_servico_ui()
           elif escolha == '4': _atualizar_servico_ui()
           elif escolha == '5': _deletar_servico_ui()
           elif escolha == '0': return

       except Exception as e:
           print(f"\nOcorreu um erro inesperado: {e}")

       esperar_enter()

def menu_clientes():
   while True:
       limpar_tela()
       print("--- Gerenciar Clientes ---")
       print("1. Cadastrar Cliente")
       print("2. Listar Todos os Clientes")
       print("3. Buscar Cliente por CPF")
       print("4. Buscar Cliente por ID")
       print("5. Buscar Cliente por Nome (Exato)")
       print("6. Buscar Clientes por Nome (Parcial)")
       print("7. Atualizar Dados do Cliente (por ID)")
       print("8. Atualizar CPF do Cliente (por ID)")
       print("9. Deletar Cliente (por ID)")
       print("0. Voltar ao Menu Principal")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^(?:[0-9])$", description="Número de 0 a 9")
       if escolha is None: return # Permite cancelar e voltar ao menu anterior

       limpar_tela()
       try:
           if escolha == '1': _cadastrar_cliente_ui()
           elif escolha == '2': _listar_clientes_ui()
           elif escolha == '3': _buscar_cliente_por_cpf_ui()
           elif escolha == '4': _buscar_cliente_por_id_ui()
           elif escolha == '5': _buscar_cliente_por_nome_exato_ui()
           elif escolha == '6': _buscar_clientes_por_nome_parcial_ui()
           elif escolha == '7': _atualizar_dados_cliente_ui()
           elif escolha == '8': _atualizar_cpf_cliente_ui()
           elif escolha == '9': _deletar_cliente_ui()
           elif escolha == '0': return

       except Exception as e:
           print(f"\nOcorreu um erro inesperado: {e}")

       esperar_enter()

def menu_funcionarios():
   while True:
       limpar_tela()
       print("--- Gerenciar Funcionários ---")
       print("1. Cadastrar Funcionário")
       print("2. Listar Todos os Funcionários")
       print("3. Buscar Funcionário por CPF")
       print("4. Buscar Funcionário por ID")
       print("5. Atualizar Dados do Funcionário (por ID)")
       print("6. Atualizar CPF do Funcionário (por ID)")
       print("7. Deletar Funcionário por CPF")
       print("8. Deletar Funcionário por ID")
       print("0. Voltar ao Menu Principal")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^[0-8]$", description="Número de 0 a 8")
       if escolha is None: return # Permite cancelar e voltar ao menu anterior

       limpar_tela()
       try:
           if escolha == '1': _cadastrar_funcionario_ui()
           elif escolha == '2': _listar_funcionarios_ui()
           elif escolha == '3': _buscar_funcionario_cpf_ui()
           elif escolha == '4': _buscar_funcionario_id_ui()
           elif escolha == '5': _atualizar_dados_funcionario_ui()
           elif escolha == '6': _atualizar_cpf_funcionario_ui()
           elif escolha == '7': _deletar_funcionario_cpf_ui()
           elif escolha == '8': _deletar_funcionario_id_ui()
           elif escolha == '0': return

       except Exception as e:
           print(f"\nOcorreu um erro inesperado: {e}")

       esperar_enter()

def menu_agendas():
   while True:
       limpar_tela()
       print("--- Gerenciar Agendas ---")
       print("1. Cadastrar Agendamento")
       print("2. Listar Todos os Agendamentos")
       print("3. Buscar Agendamento por ID")
       print("4. Atualizar Dados do Agendamento")
       print("5. Deletar Agendamento")
       print("6. Filtrar Agendamentos por Período e Critérios")
       print("7. Marcar Agendamento como Realizado")
       print("8. Marcar Agendamento como Não Realizado")
       print("0. Voltar ao Menu Principal")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^[0-8]$", description="Número de 0 a 8")
       if escolha is None: return # Permite cancelar e voltar ao menu anterior

       limpar_tela()
       try:
           if escolha == '1': _cadastrar_agendamento_ui()
           elif escolha == '2': _listar_agendamentos_ui()
           elif escolha == '3': _buscar_agendamento_ui()
           elif escolha == '4': _atualizar_agendamento_ui()
           elif escolha == '5': _deletar_agendamento_ui()
           elif escolha == '6': _filtrar_agendamentos_ui()
           elif escolha == '7': _marcar_agendamento_realizado_ui()
           elif escolha == '8': _marcar_agendamento_nao_realizado_ui()
           elif escolha == '0': return

       except Exception as e:
           print(f"\nOcorreu um erro inesperado: {e}")

       esperar_enter()

def menu_vendas():
   while True:
       limpar_tela()
       print("--- Gerenciar Vendas ---")
       print("1. Cadastrar Venda")
       print("2. Listar Todas as Vendas")
       print("3. Buscar Venda por ID")
       print("4. Atualizar Dados da Venda")
       print("5. Deletar Venda")
       print("6. Filtrar Vendas por Período e Critérios")
       print("0. Voltar ao Menu Principal")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^[0-6]$", description="Número de 0 a 6")
       if escolha is None: return # Permite cancelar e voltar ao menu anterior

       limpar_tela()
       try:
           if escolha == '1': _cadastrar_venda_ui()
           elif escolha == '2': _listar_vendas_ui()
           elif escolha == '3': _buscar_venda_ui()
           elif escolha == '4': _atualizar_venda_ui()
           elif escolha == '5': _deletar_venda_ui()
           elif escolha == '6': _filtrar_vendas_ui()
           elif escolha == '0': return

       except Exception as e:
           print(f"\nOcorreu um erro inesperado: {e}")

       esperar_enter()

def menu_fornecedores():
   while True:
       limpar_tela()
       print("--- Gerenciar Fornecedores ---")
       print("1. Cadastrar Fornecedor")
       print("2. Listar Todos os Fornecedores")
       print("3. Buscar Fornecedor por CNPJ")
       print("4. Buscar Fornecedor por ID")
       print("5. Buscar Fornecedor por Nome (Exato)")
       print("6. Buscar Fornecedores por Nome (Parcial)")
       print("7. Atualizar Dados do Fornecedor (por ID)")
       print("8. Atualizar CNPJ do Fornecedor (por ID)")
       print("9. Deletar Fornecedor (por ID)")
       print("0. Voltar ao Menu Principal")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^(?:[0-9])$", description="Número de 0 a 9")
       if escolha is None: return # Permite cancelar e voltar ao menu anterior

       limpar_tela()
       try:
           if escolha == '1': _cadastrar_fornecedor_ui()
           elif escolha == '2': _listar_fornecedores_ui()
           elif escolha == '3': _buscar_fornecedor_cnpj_ui()
           elif escolha == '4': _buscar_fornecedor_id_ui()
           elif escolha == '5': _buscar_fornecedor_por_nome_exato_ui()
           elif escolha == '6': _buscar_fornecedores_por_nome_parcial_ui()
           elif escolha == '7': _atualizar_dados_fornecedor_ui()
           elif escolha == '8': _atualizar_cnpj_fornecedor_ui()
           elif escolha == '9': _deletar_fornecedor_ui()
           elif escolha == '0': return

       except Exception as e:
           print(f"\nOcorreu um erro inesperado: {e}")

       esperar_enter()

def menu_suprimentos():
   while True:
       limpar_tela()
       print("--- Gerenciar Suprimentos ---")
       print("1. Cadastrar Suprimento")
       print("2. Listar Todos os Suprimentos")
       print("3. Buscar Suprimento por ID")
       print("4. Buscar Suprimento por Nome")
       print("5. Atualizar Dados do Suprimento")
       print("6. Deletar Suprimento")
       print("0. Voltar ao Menu Principal")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^[0-6]$", description="Número de 0 a 6")
       if escolha is None: return # Permite cancelar e voltar ao menu anterior

       limpar_tela()
       try:
           if escolha == '1': _cadastrar_suprimento_ui()
           elif escolha == '2': _listar_suprimentos_ui()
           elif escolha == '3': _buscar_suprimento_id_ui()
           elif escolha == '4': _buscar_suprimento_nome_ui()
           elif escolha == '5': _atualizar_suprimento_ui()
           elif escolha == '6': _deletar_suprimento_ui()
           elif escolha == '0': return

       except Exception as e:
           print(f"\nOcorreu um erro inesperado: {e}")

       esperar_enter()

def menu_maquinas():
   while True:
       limpar_tela()
       print("--- Gerenciar Máquinas ---")
       print("1. Cadastrar Máquina")
       print("2. Listar Todas as Máquinas")
       print("3. Buscar Máquina por ID")
       print("4. Buscar Máquina por Número de Série")
       print("5. Atualizar Dados da Máquina")
       print("6. Deletar Máquina")
       print("0. Voltar ao Menu Principal")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^[0-6]$", description="Número de 0 a 6")
       if escolha is None: return # Permite cancelar e voltar ao menu anterior

       limpar_tela()
       try:
           if escolha == '1': _cadastrar_maquina_ui()
           elif escolha == '2': _listar_maquinas_ui()
           elif escolha == '3': _buscar_maquina_id_ui()
           elif escolha == '4': _buscar_maquina_serie_ui()
           elif escolha == '5': _atualizar_maquina_ui()
           elif escolha == '6': _deletar_maquina_ui()
           elif escolha == '0': return

       except Exception as e:
           print(f"\nOcorreu um erro inesperado: {e}")

       esperar_enter()

def menu_despesas():
   while True:
       limpar_tela()
       print("--- Gerenciar Despesas ---")
       print("1. Cadastrar Nova Despesa")
       print("2. Listar Todas as Despesas")
       print("3. Buscar Despesa por ID")
       print("4. Atualizar Dados da Despesa")
       print("5. Deletar Despesa")
       print("6. Filtrar Despesas por Período e Critérios")
       print("0. Voltar ao Menu Principal")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^[0-6]$", description="Número de 0 a 6")
       if escolha is None: return # Permite cancelar e voltar ao menu anterior

       limpar_tela()
       try:
           if escolha == '1':
               while True:
                   print("\n--- Selecione o Tipo de Despesa ---")
                   print("1. Compra")
                   print("2. Fixo ou Terceiro")
                   print("3. Salário")
                   print("4. Comissão")
                   print("5. Outros")
                   print("0. Cancelar")
                   tipo_escolha = solicitar_string("Escolha o tipo de despesa", pattern=r"^[0-5]$", description="Número de 0 a 5")
                   if tipo_escolha is None or tipo_escolha == '0':
                       break

                   limpar_tela()
                   if tipo_escolha == '1': _cadastrar_compra_ui()
                   elif tipo_escolha == '2': _cadastrar_fixo_terceiro_ui()
                   elif tipo_escolha == '3': _cadastrar_salario_ui()
                   elif tipo_escolha == '4': _cadastrar_comissao_ui()
                   elif tipo_escolha == '5': _cadastrar_outros_ui()
                   break

           elif escolha == '2': _listar_despesas_ui()
           elif escolha == '3': _buscar_despesa_ui()
           elif escolha == '4': _atualizar_dados_despesa_ui()
           elif escolha == '5': _deletar_despesa_ui()
           elif escolha == '6': _filtrar_despesas_ui()
           elif escolha == '0': return

       except Exception as e:
           print(f"\nOcorreu um erro inesperado: {e}")

       esperar_enter()

# Funções de Criação de Dados Iniciais (Simula carga do BD) ---

def inicializar_dados_testes():
   # Popula os dicionários de classe com dados de teste e inicializa IDs.
   print("Inicializando dados de teste...")

   # Limpar todos os dicionários de classe antes de iniciar
   mod_funcionario.Funcionario._funcionarios_por_cpf.clear()
   mod_funcionario.Funcionario._funcionarios_por_id.clear()
   mod_cliente.Cliente._clientes_por_cpf.clear()
   mod_cliente.Cliente._clientes_por_id.clear()
   servico.Servico._servicos_por_nome.clear()
   servico.Servico._servicos_por_id.clear()
   produto.Produto._produtos_por_nome.clear()
   produto.Produto._produtos_por_id.clear()
   mod_agenda.Agenda._agendas_por_id.clear()
   mod_agenda.Agenda._proximo_id_disponivel = 1
   mod_venda.Venda._vendas_por_id.clear()
   mod_venda.Venda._proximo_id_disponivel = 1
   mod_fornecedor.Fornecedor._fornecedores_por_cnpj.clear()
   mod_fornecedor.Fornecedor._fornecedores_por_id.clear()
   mod_despesa.Despesa._despesas_por_id.clear()
   mod_despesa.Despesa._proximo_id_disponivel = 1
   mod_suprimento.Suprimento._suprimentos_por_id.clear()
   mod_suprimento.Suprimento._suprimentos_por_nome.clear()
   mod_suprimento.Suprimento._proximo_id_disponivel = 1
   mod_maquina.Maquina._maquinas_por_id.clear()
   mod_maquina.Maquina._maquinas_por_serie.clear()
   mod_maquina.Maquina._proximo_id_disponivel = 1

   # Inicializar o próximo ID de todas as classes com auto-incremento
   mod_cliente.Cliente._inicializar_proximo_id()
   servico.Servico._inicializar_proximo_id()
   produto.Produto._inicializar_proximo_id()
   mod_fornecedor.Fornecedor._inicializar_proximo_id()
   mod_agenda.Agenda._inicializar_proximo_id()
   mod_venda.Venda._inicializar_proximo_id()
   mod_despesa.Despesa._inicializar_proximo_id()
   mod_suprimento.Suprimento._inicializar_proximo_id()
   mod_maquina.Maquina._inicializar_proximo_id()
   mod_funcionario.Funcionario._inicializar_proximo_id()

   # Criar Funcionários (usando IDs fixos para os dados de teste, eles não auto-incrementam)
   global func_joao, func_maria, func_atendente
   func_joao = mod_funcionario.Funcionario(
       id_funcionario=1, nome="João Silva", nascimento="01/01/1980", cpf=pessoa.gerar_cpf_valido(),
       ctps="1234567-89", informacao_contato=mod_info.Informacao("11987654321", "joao@email.com", "Rua A, 10, Centro, SP, SP", "linkedin.com/joao"),
       salario=3000.00, data_admissao="01/01/2010", data_demissao=None,
       nis="12345678901"
   )
   func_maria = mod_funcionario.Funcionario(
       id_funcionario=2, nome="Maria Souza", nascimento="10/05/1992", cpf=pessoa.gerar_cpf_valido(),
       ctps="9876543-21", informacao_contato=mod_info.Informacao("21998765432", "maria@empresa.com", "Av B, 20, Copacabana, RJ, RJ", ""),
       salario=3500.00, data_admissao="15/03/2015", data_demissao=None,
       nis="10987654321"
   )
   func_atendente = mod_funcionario.Funcionario(
       id_funcionario=3, nome="Ana Atendente", nascimento="01/02/1991", cpf=pessoa.gerar_cpf_valido(),
       ctps="1122334-45", informacao_contato=mod_info.Informacao("11911112222", "ana@empresa.com", "Rua X, 50, Bairro, SP, SP", ""),
       salario=2500.00, data_admissao="01/01/2020", data_demissao=None,
       nis=None
   )

   # Criar Clientes (id_cliente=None para auto-incremento)
   global cli_ana, cli_pedro, cli_fernanda
   cli_ana = mod_cliente.Cliente.criar_cliente(
       nome="Ana Costa", nascimento="20/03/1995", cpf=pessoa.gerar_cpf_valido(),
       info_contato=mod_info.Informacao("11912345678", "ana@cliente.com", "Rua C, 30, Jardins, SP, SP", "")
   )
   cli_pedro = mod_cliente.Cliente.criar_cliente(
       nome="Pedro Dantas", nascimento="15/11/1988", cpf=pessoa.gerar_cpf_valido(),
       info_contato=mod_info.Informacao("21987651234", "pedro@cliente.com", "Rua D, 40, Tijuca, RJ, RJ", "")
   )
   cli_fernanda = mod_cliente.Cliente.criar_cliente(
       nome="Fernanda Compradora", nascimento="12/12/1993", cpf=pessoa.gerar_cpf_valido(),
       info_contato=mod_info.Informacao("31933334444", "fernanda@cliente.com", "Av Z, 100, Cidade, MG, MG", "")
   )

   # Criar Serviços (id_servico=None para auto-incremento)
   global serv_limpeza, serv_conserto
   serv_limpeza = servico.Servico.criar_servico("Limpeza Detalhada", 200.00, 50.00)
   serv_conserto = servico.Servico.criar_servico("Conserto Hardware", 450.00, 100.00)

   # Criar Produtos (id_produto=None para auto-incremento)
   global prod_software, prod_peca, prod_tinta, prod_escova
   prod_software = produto.Produto.criar_produto("Software Licença", 1200.00, 100)
   prod_peca = produto.Produto.criar_produto("Peca Eletronica", 150.00, 20)
   prod_tinta = produto.Produto.criar_produto("Tinta Premium", 50.00, 100)
   prod_escova = produto.Produto.criar_produto("Escova de Limpeza", 10.00, 200)

   # Criar Suprimentos
   global supr_papel, supr_caneta, supr_cabo, supr_alcool
   supr_papel = mod_suprimento.Suprimento.criar_suprimento("Papel A4", "resma", 20.00, 50)
   supr_caneta = mod_suprimento.Suprimento.criar_suprimento("Caneta Esferográfica", "unidade", 1.50, 200)
   supr_cabo = mod_suprimento.Suprimento.criar_suprimento("Cabo HDMI", "unidade", 30.00, 15)
   supr_alcool = mod_suprimento.Suprimento.criar_suprimento("Álcool Isopropílico", "litro", 25.00, 10)

   # Criar Máquinas
   global maq_impressora, maq_servidor, maq_projetor
   maq_impressora = mod_maquina.Maquina.criar_maquina("Impressora Laser", "IMPL-XYZ-001", 1200.00, mod_maquina.StatusMaquina.OPERANDO)
   maq_servidor = mod_maquina.Maquina.criar_maquina("Servidor Web", "SRV-WEB-ABC", 5000.00, mod_maquina.StatusMaquina.EM_MANUTENCAO)
   maq_projetor = mod_maquina.Maquina.criar_maquina("Projetor", "PROJ-LUM-222", 800.00, mod_maquina.StatusMaquina.OPERANDO)

   # Criar Fornecedores para Despesas (id_fornecedor=None para auto-incremento)
   global forn_materiais, forn_servicos, forn_marketing
   forn_materiais = mod_fornecedor.Fornecedor.criar_fornecedor(
       nome="ABC Materiais Ltda", cnpj=pessoa.gerar_cnpj_valido(),
       info_contato=mod_info.Informacao("1133334444", "contato@abcmateriais.com", "Rua Alfa, 100, Centro, SP, SP", "")
   )
   forn_servicos = mod_fornecedor.Fornecedor.criar_fornecedor(
       nome="XYZ Consultoria", cnpj=pessoa.gerar_cnpj_valido(),
       info_contato=mod_info.Informacao("2155556666", "contato@xyzconsultoria.com", "Av. Beta, 200, Gloria, RJ, RJ", "")
   )
   forn_marketing = mod_fornecedor.Fornecedor.criar_fornecedor(
       nome="Agencia Criativa MKT", cnpj=pessoa.gerar_cnpj_valido(),
       info_contato=mod_info.Informacao("31977778888", "contato@agenciamkt.com", "Rua da Publicidade, 50, Savassi, BH, MG", "")
   )

   # Criar algumas Agendas
   # Agendas de Junho de 2024
   mod_agenda.Agenda.criar_agenda(
       funcionario_obj=func_joao, cliente_obj=cli_ana,
       data_hora_inicio="01/06/2024 10:00", data_hora_fim="01/06/2024 11:00",
       itens_agendados=[mod_agenda.ItemAgendado(serv_limpeza, 1)], comentario="Agenda de Junho (João/Ana)"
   )
   mod_agenda.Agenda.criar_agenda(
       funcionario_obj=func_maria, cliente_obj=cli_pedro,
       data_hora_inicio="05/06/2024 14:00", data_hora_fim="05/06/2024 16:00",
       itens_agendados=[mod_agenda.ItemAgendado(serv_conserto, 1.5), mod_agenda.ItemAgendado(prod_peca, 1)],
       maquinas_agendadas=[maq_impressora],
       suprimentos_utilizados=[mod_agenda.SuprimentoAgendado(supr_alcool, 0.5)],
       comentario="Agenda de Junho (Maria/Pedro), com máquina e suprimento"
   )
   mod_agenda.Agenda.criar_agenda(
       funcionario_obj=func_joao, cliente_obj=cli_pedro,
       data_hora_inicio="10/06/2024 09:00", data_hora_fim="10/06/2024 10:30",
       itens_agendados=[mod_agenda.ItemAgendado(serv_limpeza, 1)], comentario="Agenda de Junho (João/Pedro)"
   )
   mod_agenda.Agenda.criar_agenda(
       funcionario_obj=func_atendente, cliente_obj=cli_fernanda,
       data_hora_inicio="15/06/2024 11:00", data_hora_fim="15/06/2024 12:00",
       itens_agendados=[mod_agenda.ItemAgendado(serv_conserto, 0.5)], comentario="Agenda de Junho (Ana/Fernanda)",
       status=mod_agenda.AgendaStatus.REALIZADO
   )
   # Agendas de Julho de 2024
   mod_agenda.Agenda.criar_agenda(
       funcionario_obj=func_joao, cliente_obj=cli_ana,
       data_hora_inicio="01/07/2024 10:00", data_hora_fim="01/07/2024 11:00",
       itens_agendados=[mod_agenda.ItemAgendado(serv_limpeza, 1)], comentario="Agenda de Julho (João/Ana)"
   )
   mod_agenda.Agenda.criar_agenda(
       funcionario_obj=func_maria, cliente_obj=cli_fernanda,
       data_hora_inicio="05/07/2024 14:00", data_hora_fim="05/07/2024 16:00",
       itens_agendados=[mod_agenda.ItemAgendado(prod_software, 1)], comentario="Agenda de Julho (Maria/Fernanda)",
       suprimentos_utilizados=[mod_agenda.SuprimentoAgendado(supr_cabo, 2)],
       status=mod_agenda.AgendaStatus.NAO_REALIZADO
   )


   # Criar algumas Vendas
   # Vendas de Maio de 2024
   mod_venda.Venda.criar_venda(
       funcionario_obj=func_joao, cliente_obj=cli_ana,
       itens_venda=[mod_venda.ItemVenda(prod_software, 1)],
       data_venda_str="10/05/2024", comentario="Venda Software (Maio)"
   )
   mod_venda.Venda.criar_venda(
       funcionario_obj=func_maria, cliente_obj=cli_pedro,
       itens_venda=[mod_venda.ItemVenda(serv_limpeza, 1)],
       data_venda_str="15/05/2024", comentario="Venda Limpeza (Maio)"
   )
   mod_venda.Venda.criar_venda(
       funcionario_obj=func_atendente, cliente_obj=cli_fernanda,
       itens_venda=[mod_venda.ItemVenda(prod_peca, 5)],
       data_venda_str="20/05/2024", comentario="Venda Peças (Maio)"
   )
   # Vendas de Junho de 2024
   mod_venda.Venda.criar_venda(
       funcionario_obj=func_joao, cliente_obj=cli_pedro,
       itens_venda=[mod_venda.ItemVenda(serv_conserto, 1)],
       data_venda_str="01/06/2024", comentario="Venda Conserto (Junho)"
   )
   mod_venda.Venda.criar_venda(
       funcionario_obj=func_maria, cliente_obj=cli_ana,
       itens_venda=[mod_venda.ItemVenda(prod_software, 0.5)],
       data_venda_str="05/06/2024", comentario="Venda Software Parcial (Junho)"
   )
   mod_venda.Venda.criar_venda(
       funcionario_obj=func_atendente, cliente_obj=cli_pedro,
       itens_venda=[], agenda_obj=mod_agenda.Agenda.buscar_agenda(3), # Agenda ID 3 (João/Pedro/Junho)
       data_venda_str="10/06/2024", comentario="Venda de Agenda (Junho)"
   )

   # Criar algumas Despesas
   # Despesas de Junho de 2024
   mod_despesa.Compra( # Compra de produto (Tinta Premium)
       id_despesa=None, fornecedor_obj=forn_materiais, item_comprado=prod_tinta,
       quantidade=10, valor_unitario=45.00, data_despesa_str="10/06/2024",
       comentario="Compra de tintas para nova sala."
   )
   mod_despesa.Compra( # Compra de suprimento (Papel A4)
       id_despesa=None, fornecedor_obj=forn_materiais, item_comprado=supr_papel,
       quantidade=5, valor_unitario=18.00, data_despesa_str="11/06/2024",
       comentario="Compra de resmas de papel."
   )
   mod_despesa.Compra( # Compra de máquina
       id_despesa=None, fornecedor_obj=forn_servicos, item_comprado=maq_impressora,
       quantidade=1, valor_unitario=1100.00, data_despesa_str="12/06/2024",
       comentario="Aquisição de nova impressora."
   )
   mod_despesa.FixoTerceiro(
       id_despesa=None, valor=1200.00, tipo_despesa_str="Aluguel Mensal",
       fornecedor_obj=forn_servicos, data_despesa_str="01/06/2024"
   )
   mod_despesa.Salario(
       id_despesa=None, funcionario_obj=func_joao, salario_bruto=3000.00,
       descontos=300.00, data_despesa_str="05/06/2024", comentario="Salário de João Silva."
   )
   mod_despesa.Comissao(
       id_despesa=None, funcionario_obj=func_maria, valor_soma_servicos=10000.00,
       valor_soma_produtos=5000.00, taxa_servicos=0.05, taxa_produtos=0.02,
       data_despesa_str="07/06/2024", comentario="Comissão referente a vendas de Junho."
   )
   mod_despesa.Outros(
       id_despesa=None, valor=250.00, tipo_despesa_str="Manutenção Predial",
       data_despesa_str="12/06/2024", comentario="Pequenos reparos no escritório."
   )
   mod_despesa.Compra( # Compra de um item genérico (string)
       id_despesa=None, fornecedor_obj=forn_materiais, item_comprado="Cabo de Rede Cat6",
       quantidade=50, valor_unitario=3.00, data_despesa_str="15/06/2024",
       comentario="Cabo de rede para nova instalação."
   )
   mod_despesa.FixoTerceiro( # Despesa sem fornecedor associado
       id_despesa=None, valor=500.00, tipo_despesa_str="Conta de Luz",
       fornecedor_obj=None, data_despesa_str="25/06/2024", comentario="Pagamento da conta de energia."
   )
   mod_despesa.Outros( # Despesa de julho para filtro
       id_despesa=None, valor=300.00, tipo_despesa_str="Marketing Digital",
       data_despesa_str="01/07/2024", comentario="Campanha de Facebook Ads."
   )
   print("\nDados de teste inicializados.")
   esperar_enter()

# Funções do Menu Principal (Chamando as funções de Menu da UI) ---
def exibir_menu_principal():
   while True:
       limpar_tela()
       print("--- Menu Principal do Sistema de Gerenciamento ---")
       print("1. Gerenciar Agendas")
       print("2. Gerenciar Vendas")
       print("3. Gerenciar Despesas")
       print("4. Gerenciar Clientes")
       print("5. Gerenciar Produtos")
       print("6. Gerenciar Suprimentos")
       print("7. Gerenciar Máquinas")
       print("8. Gerenciar Fornecedores")
       print("9. Gerenciar Funcionários")
       print("10. Gerenciar Serviços")
       print("0. Sair do Sistema")

       escolha = solicitar_string("Escolha uma opção", pattern=r"^(?:[0-9]|10)$", description="Número de 0 a 10")
       if escolha is None:
           print("\nSaindo do sistema. Até mais!")
           sys.exit()
       elif escolha == '0':
           print("\nSaindo do sistema. Até mais!")
           sys.exit()

       if escolha == '1':
           menu_agendas()
       elif escolha == '2':
           menu_vendas()
       elif escolha == '3':
           menu_despesas()
       elif escolha == '4':
           menu_clientes()
       elif escolha == '5':
           menu_produtos()
       elif escolha == '6':
           menu_suprimentos()
       elif escolha == '7':
           menu_maquinas()
       elif escolha == '8':
           menu_fornecedores()
       elif escolha == '9':
           menu_funcionarios()
       elif escolha == '10':
           menu_servicos()
       else:
           print("Opção inválida. Por favor, tente novamente.")
           esperar_enter()

if __name__ == "__main__":
   inicializar_dados_testes()
   exibir_menu_principal()
