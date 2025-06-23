# test_data_generator.py
import time
import random
from datetime import datetime, timedelta
from typing import Any, Union, List

# Import all necessary modules from the project
# Certifique-se de que esses módulos estão no mesmo diretório ou no PYTHONPATH
import pessoa
import info
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

# Global pools for dependent objects
# Estes pools serão usados para referenciar objetos existentes em classes que possuem dependências
_POOLS = {
    'funcs': [],
    'clients': [],
    'services': [],
    'products': [],
    'suppliers': [],
    'supplies': [],
    'machines': []
}

# Listas de palavras para gerar nomes válidos e variados
_SURNAMES = ["Silva", "Souza", "Santos", "Oliveira", "Pereira", "Almeida", "Costa", "Ferreira", "Rodrigues", "Gomes"]
_PRODUCT_ADJECTIVES = ["Básico", "Digital", "Premium", "Avançado", "Confiável", "Eficiente", "Rápido", "Completo"]

def int_to_alphastring(n):
    """Converts an integer to a unique alphabetical string (e.g., 1->A, 2->B, 27->AA)."""
    if n == 0:
        return 'A' # Handle case for i=0 or similar, though typically we use i+1
    s = ''
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        s = chr(65 + remainder) + s # 65 is ASCII for 'A'
    return s

def _clear_all_data():
    """Clears all class dictionaries to ensure a clean test environment for new generations."""
    mod_funcionario.Funcionario._funcionarios_por_cpf.clear()
    mod_funcionario.Funcionario._funcionarios_por_id.clear()
    mod_cliente.Cliente._clientes_por_cpf.clear()
    servico.Servico._servicos_por_nome.clear()
    produto.Produto._produtos_por_nome.clear()
    mod_agenda.Agenda._agendas_por_id.clear()
    mod_agenda.Agenda._proximo_id_disponivel = 1
    mod_venda.Venda._vendas_por_id.clear()
    mod_venda.Venda._proximo_id_disponivel = 1
    mod_fornecedor.Fornecedor._fornecedores_por_cnpj.clear()
    mod_despesa.Despesa._despesas_por_id.clear()
    mod_despesa.Despesa._proximo_id_disponivel = 1
    mod_suprimento.Suprimento._suprimentos_por_id.clear()
    mod_suprimento.Suprimento._suprimentos_por_nome.clear()
    mod_suprimento.Suprimento._proximo_id_disponivel = 1
    mod_maquina.Maquina._maquinas_por_id.clear()
    mod_maquina.Maquina._maquinas_por_serie.clear()
    mod_maquina.Maquina._proximo_id_disponivel = 1
    # print("All internal data structures reset.")

def _setup_dependent_objects(num_base_objects=50):
    """
    Creates a small pool of base objects for classes that have dependencies
    (e.g., Funcionario, Cliente, Servico, Produto).
    These objects will be reused across many generated instances to avoid
    recreating them each time, which would inflate times and memory.
    """
    print(f"\nSetting up {num_base_objects} base objects for dependencies...")
    _clear_all_data() # Ensure clean state before setting up base objects

    # Clear previous pools before populating
    for pool_list in _POOLS.values():
        pool_list.clear()

    for i in range(num_base_objects):
        # Funcionarios
        # Garante CPF único para cada funcionário base
        unique_cpf_func = None
        while True:
            temp_cpf = pessoa.gerar_cpf_valido()
            if mod_funcionario.Funcionario.buscar_funcionario_cpf(temp_cpf) is None:
                unique_cpf_func = temp_cpf
                break
        func = mod_funcionario.Funcionario(
            id_funcionario=i + 1,
            nome=f"Funcionario {random.choice(_SURNAMES)}",
            nascimento="01/01/1990", cpf=unique_cpf_func,
            ctps=f"CTPS{i}", info=info.Informacao(f"119{i:08d}", f"func{i}@base.com", "Rua Base, 1", ""),
            salario=2500.00, admissao="01/01/2020", demissao=None
        )
        _POOLS['funcs'].append(func)

        # Clientes
        # Garante CPF único para cada cliente base
        unique_cpf_cli = None
        while True:
            temp_cpf = pessoa.gerar_cpf_valido()
            if mod_cliente.Cliente.buscar_cliente(temp_cpf) is None:
                unique_cpf_cli = temp_cpf
                break
        cli = mod_cliente.Cliente(
            nome=f"Cliente {random.choice(_SURNAMES)}",
            nascimento="01/01/1995", cpf=unique_cpf_cli,
            info_contato=info.Informacao(f"119{i:08d}", f"cli{i}@base.com", "Av Base, 2", "")
        )
        _POOLS['clients'].append(cli)

        # Serviços
        # Nome para serviços DEVE ser único e válido.
        # Usa int_to_alphastring para garantir unicidade e formato de nome válido
        serv = servico.Servico.criar_servico(f"Servico Base {int_to_alphastring(i+1)}", 100.00 + i, 30.00 + i)
        _POOLS['services'].append(serv)

        # Produtos
        # Nome para produtos DEVE ser único e válido.
        # Usa int_to_alphastring para garantir unicidade e formato de nome válido
        prod = produto.Produto.criar_produto(f"Produto Base {int_to_alphastring(i+1)}", 50.00 + i, 100 + i)
        _POOLS['products'].append(prod)

        # Fornecedores
        # Garante CNPJ único para cada fornecedor base
        unique_cnpj_forn = None
        while True:
            temp_cnpj = pessoa.gerar_cnpj_valido()
            if mod_fornecedor.Fornecedor.buscar_fornecedor(temp_cnpj) is None:
                unique_cnpj_forn = temp_cnpj
                break
        forn = mod_fornecedor.Fornecedor(
            nome=f"Fornecedor Generico {int_to_alphastring(i+1)}", # Garante nome válido
            cnpj=unique_cnpj_forn, # Usa o CNPJ único garantido
            info_contato=info.Informacao(f"119{i:08d}", f"forn{i}@base.com", "Praca Base, 3", "")
        )
        _POOLS['suppliers'].append(forn)

        # Suprimentos
        # Nome é único e válido.
        supr = mod_suprimento.Suprimento.criar_suprimento(
            f"Suprimento Comum {int_to_alphastring(i+1)}", # Garante nome válido e único
            "unidade", 5.00 + i, 50 + i
        )
        _POOLS['supplies'].append(supr)

        # Máquinas
        # Nome é válido, número de série é único pelo i.
        maq = mod_maquina.Maquina.criar_maquina(
            f"Maquina Padrao {int_to_alphastring(i+1)}", # Garante nome válido
            f"SERIE-BASE-{i}", 1000.00 + i * 100, mod_maquina.StatusMaquina.OPERANDO
        )
        _POOLS['machines'].append(maq)
    
    # Ensure ID counters are correctly initialized after base objects are created
    mod_agenda.Agenda._inicializar_proximo_id()
    mod_venda.Venda._inicializar_proximo_id()
    mod_despesa.Despesa._inicializar_proximo_id()
    mod_suprimento.Suprimento._inicializar_proximo_id()
    mod_maquina.Maquina._inicializar_proximo_id()
    print("Base objects configured.")


# --- NEW GENERATOR FUNCTIONS FOR MASS CREATION ---

def _generate_servicos(num_instances: int):
    """Generates a specified number of Servico instances, ensuring unique names."""
    servico.Servico._servicos_por_nome.clear() # Clear before generating for this test run
    start_time = time.time()
    for i in range(num_instances):
        try:
            # Nome para serviços DEVE ser único, pois é a chave do dicionário, e válido.
            # int_to_alphastring(i+1) garante unicidade aqui.
            name = f"Servico Gerado {int_to_alphastring(i+1)}"
            servico.Servico.criar_servico(name, 100.0 + i % 50, 30.0 + i % 20)
        except ValueError:
            pass # Suppress other ValueErrors (e.g., if somehow int_to_alphastring fails for extreme numbers, though unlikely)
    end_time = time.time()
    return end_time - start_time

def _generate_fornecedores(num_instances: int):
    """Generates a specified number of Fornecedor instances, ensuring unique CNPJ."""
    mod_fornecedor.Fornecedor._fornecedores_por_cnpj.clear() # Clear before generating for this test run
    start_time = time.time()
    for i in range(num_instances):
        try:
            unique_cnpj = None
            # Loop para garantir CNPJ único antes de criar o fornecedor
            while True:
                temp_cnpj = pessoa.gerar_cnpj_valido()
                if mod_fornecedor.Fornecedor.buscar_fornecedor(temp_cnpj) is None:
                    unique_cnpj = temp_cnpj
                    break
            
            # Nome é válido (duas palavras alfabéticas, a segunda sendo única)
            name = f"Fornecedor Gerado {int_to_alphastring(i+1)}"
            info_contact = info.Informacao(f"119{random.randint(10000000, 99999999)}", f"stress_forn_{i}@test.com", "Rua Forn, 1", "")
            mod_fornecedor.Fornecedor.criar_fornecedor(name, unique_cnpj, info_contact)
        except ValueError:
            # Captura outros ValueErrors que não sejam de duplicidade de CNPJ (se houver)
            pass
    end_time = time.time()
    return end_time - start_time

# --- EXISTING GENERATOR FUNCTIONS (REPRODUCED FOR COMPLETENESS) ---

def _generate_clientes(num_instances: int):
    """Generates a specified number of Cliente instances, ensuring unique CPF."""
    mod_cliente.Cliente._clientes_por_cpf.clear() # Clear before generating for this test run
    start_time = time.time()
    for i in range(num_instances):
        try:
            unique_cpf = None
            # Loop para garantir CPF único antes de criar o cliente
            # Evita colisões e ValueErrors que seriam suprimidos
            while True:
                temp_cpf = pessoa.gerar_cpf_valido()
                if mod_cliente.Cliente.buscar_cliente(temp_cpf) is None:
                    unique_cpf = temp_cpf
                    break
            
            name = f"Cliente Gerado {int_to_alphastring(i+1)}"
            info_contact = info.Informacao(f"119{random.randint(10000000, 99999999)}", f"stress_cli_{i}@test.com", "Rua Teste, 1", "")
            mod_cliente.Cliente(name, "01/01/1990", unique_cpf, info_contact)
        except ValueError:
            # Captura outros ValueErrors que não sejam de duplicidade de CPF (se houver)
            pass
    end_time = time.time()
    return end_time - start_time

def _generate_produtos(num_instances: int):
    """Generates a specified number of Produto instances, ensuring unique names."""
    produto.Produto._produtos_por_nome.clear() # Clear before generating
    start_time = time.time()
    for i in range(num_instances):
        try:
            # Nome para produtos DEVE ser único, pois é a chave do dicionário, e válido.
            # int_to_alphastring(i+1) garante unicidade aqui.
            name = f"Produto Gerado {int_to_alphastring(i+1)}"
            produto.Produto.criar_produto(name, 10.0 + i % 10, 100 + i % 50)
        except ValueError:
            pass
    end_time = time.time()
    return end_time - start_time

def _generate_suprimentos(num_instances: int):
    """Generates a specified number of Suprimento instances, ensuring unique names."""
    mod_suprimento.Suprimento._suprimentos_por_id.clear()
    mod_suprimento.Suprimento._suprimentos_por_nome.clear()
    mod_suprimento.Suprimento._proximo_id_disponivel = 1 # Reset ID counter
    start_time = time.time()
    for i in range(num_instances):
        try:
            # Nome para suprimentos DEVE ser único, e válido.
            # int_to_alphastring(i+1) garante unicidade aqui.
            name = f"Suprimento Gerado {int_to_alphastring(i+1)}"
            mod_suprimento.Suprimento.criar_suprimento(
                name, "unidade", 1.0 + i % 5, 1000 + i % 100
            )
        except ValueError:
            pass
    end_time = time.time()
    return end_time - start_time

def _generate_maquinas(num_instances: int):
    """Generates a specified number of Maquina instances, ensuring unique serial numbers."""
    mod_maquina.Maquina._maquinas_por_id.clear()
    mod_maquina.Maquina._maquinas_por_serie.clear()
    mod_maquina.Maquina._proximo_id_disponivel = 1 # Reset ID counter
    start_time = time.time()
    for i in range(num_instances):
        try:
            unique_serial = None
            # Loop para garantir número de série único antes de criar a máquina
            while True:
                # Combina 'i' (único) com uma parte aleatória para maior dispersão
                temp_serial = f"SERIE-STRESS-{i}-{random.randint(0,999999)}"
                if mod_maquina.Maquina.buscar_maquina_serie(temp_serial) is None:
                    unique_serial = temp_serial
                    break

            name = f"Maquina Teste {int_to_alphastring(i+1)}"
            mod_maquina.Maquina.criar_maquina(
                name, unique_serial, # Usa o número de série único garantido
                1000.0 + i % 100, random.choice(list(mod_maquina.StatusMaquina))
            )
        except ValueError:
            # Captura outros ValueErrors que não sejam de duplicidade de série (se houver)
            pass
    end_time = time.time()
    return end_time - start_time

def _generate_funcionarios(num_instances: int):
    """Generates a specified number of Funcionario instances, ensuring unique CPF."""
    mod_funcionario.Funcionario._funcionarios_por_cpf.clear()
    mod_funcionario.Funcionario._funcionarios_por_id.clear()
    start_time = time.time()
    for i in range(num_instances):
        try:
            unique_cpf = None
            # Loop para garantir CPF único antes de criar o funcionário
            while True:
                temp_cpf = pessoa.gerar_cpf_valido()
                if mod_funcionario.Funcionario.buscar_funcionario_cpf(temp_cpf) is None:
                    unique_cpf = temp_cpf
                    break
            
            name = f"Funcionario Teste {int_to_alphastring(i+1)}"
            mod_funcionario.Funcionario(
                id_funcionario=i + 1, nome=name, # ID é único por i
                nascimento="01/01/1985", cpf=unique_cpf, # Usa o CPF único garantido
                ctps=f"CTPSSTRESS{i}", info=info.Informacao(f"119{random.randint(10000000, 99999999)}", f"stress_func_{i}@test.com", "Rua Func, 1", ""),
                salario=3000.00 + i % 100, admissao="01/01/2015", demissao=None
            )
        except ValueError:
            # Captura outros ValueErrors que não sejam de duplicidade de CPF/ID (se houver)
            pass
    end_time = time.time()
    return end_time - start_time

def _generate_agendas(num_instances: int):
    """Generates a specified number of Agenda instances."""
    mod_agenda.Agenda._agendas_por_id.clear()
    mod_agenda.Agenda._proximo_id_disponivel = 1 # Reset ID counter
    start_time = time.time()
    if not _POOLS['funcs'] or not _POOLS['clients'] or not _POOLS['services']:
        print("Warning: Dependent pools for Agendas are empty. Skipping Agenda generation.")
        return 0.0 # Return 0 if prerequisites are not met

    for i in range(num_instances):
        try:
            func = random.choice(_POOLS['funcs'])
            cli = random.choice(_POOLS['clients'])
            service = random.choice(_POOLS['services'])
            
            # Use random date within a range to avoid all same dates
            start_dt = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364), minutes=random.randint(0, 1439))
            end_dt = start_dt + timedelta(hours=random.randint(1, 3)) # Random duration between 1-3 hours

            item_ag = mod_agenda.ItemAgendado(service, random.uniform(0.5, 2.0))
            mod_agenda.Agenda.criar_agenda(
                funcionario_obj=func, cliente_obj=cli,
                data_hora_inicio=start_dt.strftime("%d/%m/%Y %H:%M"),
                data_hora_fim=end_dt.strftime("%d/%m/%Y %H:%M"),
                itens_agendados=[item_ag], comentario=f"Stress Agenda {i}"
            )
        except ValueError:
            # ValueErrors aqui são provavelmente devido a conflitos de horário.
            # Para testes de performance de geração em massa, estamos suprimindo.
            pass
    end_time = time.time()
    return end_time - start_time

def _generate_vendas(num_instances: int):
    """Generates a specified number of Venda instances."""
    mod_venda.Venda._vendas_por_id.clear()
    mod_venda.Venda._proximo_id_disponivel = 1 # Reset ID counter
    start_time = time.time()
    if not _POOLS['funcs'] or not _POOLS['clients'] or (not _POOLS['products'] and not _POOLS['services']):
        print("Warning: Dependent pools for Vendas are empty. Skipping Venda generation.")
        return 0.0

    for i in range(num_instances):
        try:
            func = random.choice(_POOLS['funcs'])
            cli = random.choice(_POOLS['clients'])
            item_base = random.choice(_POOLS['products'] + _POOLS['services'])
            item_v = mod_venda.ItemVenda(item_base, random.uniform(0.1, 5.0))
            
            data_venda = (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364))).strftime("%d/%m/%Y")

            mod_venda.Venda.criar_venda(
                funcionario_obj=func, cliente_obj=cli, itens_venda=[item_v],
                data_venda_str=data_venda, comentario=f"Stress Venda {i}"
            )
        except ValueError:
            pass
    end_time = time.time()
    return end_time - start_time

def _generate_despesas(num_instances: int):
    """Generates a specified number of Despesa instances of various types."""
    mod_despesa.Despesa._despesas_por_id.clear()
    mod_despesa.Despesa._proximo_id_disponivel = 1 # Reset ID counter
    start_time = time.time()

    despesa_types = ['compra', 'fixo_terceiro', 'salario', 'comissao', 'outros']

    # Check if necessary pools are populated
    if not _POOLS['funcs'] or not _POOLS['suppliers'] or (not _POOLS['products'] and not _POOLS['supplies'] and not _POOLS['machines']):
        print("Warning: Dependent pools for Despesas are empty. Skipping Despesa generation.")
        return 0.0

    for i in range(num_instances):
        try:
            chosen_type = random.choice(despesa_types)
            data_despesa = (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364))).strftime("%d/%m/%Y")

            if chosen_type == 'compra':
                forn = random.choice(_POOLS['suppliers'])
                item_comprado_pool = _POOLS['products'] + _POOLS['supplies'] + _POOLS['machines']
                item_comprado = random.choice(item_comprado_pool)
                mod_despesa.Compra(
                    None, forn, item_comprado, random.uniform(1, 10), 50.0 + random.randint(0, 100), data_despesa, f"Stress Compra {i}"
                )
            elif chosen_type == 'fixo_terceiro':
                forn = random.choice(_POOLS['suppliers'])
                mod_despesa.FixoTerceiro(
                    None, 100.0 + random.randint(0, 200), f"Tipo Fixo {random.randint(0, 5)}", forn, data_despesa, f"Stress Fixo {i}"
                )
            elif chosen_type == 'salario':
                func = random.choice(_POOLS['funcs'])
                mod_despesa.Salario(
                    None, func, 2000.0 + random.randint(0, 500), 200.0 + random.randint(0, 100), data_despesa, f"Stress Salario {i}"
                )
            elif chosen_type == 'comissao':
                func = random.choice(_POOLS['funcs'])
                mod_despesa.Comissao(
                    None, func, 1000.0 + random.randint(0, 1000), 500.0 + random.randint(0, 500), 0.05, 0.02, data_despesa, f"Stress Comissao {i}"
                )
            elif chosen_type == 'outros':
                mod_despesa.Outros(
                    None, 50.0 + random.randint(0, 50), f"Tipo Outro {random.randint(0, 3)}", data_despesa, f"Stress Outros {i}"
                )
        except ValueError:
            pass
    end_time = time.time()
    return end_time - start_time

def generate_performance_data(num_instances: int):
    """
    Generates a specified number of instances for various data models and
    measures the time taken for each.

    Args:
        num_instances (int): The number of instances to generate for each class.
    """
    print(f"\n--- STARTING DATA GENERATION FOR {num_instances:,} INSTANCES PER CLASS ---")
    
    num_base_objects = min(num_instances // 100 if num_instances >= 100 else 10, 50)
    _setup_dependent_objects(num_base_objects=num_base_objects)

    results = {}
    print("\nGeneration time for each class (in seconds):")

    # Call each generator function and record time
    results['Clientes'] = _generate_clientes(num_instances)
    print(f"  - Clientes: {results['Clientes']:.4f}")

    results['Produtos'] = _generate_produtos(num_instances)
    print(f"  - Produtos: {results['Produtos']:.4f}")

    # NOW INCLUDING THE MISSING ONES!
    results['Servicos'] = _generate_servicos(num_instances)
    print(f"  - Serviços: {results['Servicos']:.4f}")

    results['Fornecedores'] = _generate_fornecedores(num_instances)
    print(f"  - Fornecedores: {results['Fornecedores']:.4f}")
    # END OF NEW INCLUSIONS

    results['Suprimentos'] = _generate_suprimentos(num_instances)
    print(f"  - Suprimentos: {results['Suprimentos']:.4f}")
    
    results['Maquinas'] = _generate_maquinas(num_instances)
    print(f"  - Máquinas: {results['Maquinas']:.4f}")

    results['Funcionarios'] = _generate_funcionarios(num_instances)
    print(f"  - Funcionários: {results['Funcionarios']:.4f}")

    results['Agendas'] = _generate_agendas(num_instances)
    print(f"  - Agendas: {results['Agendas']:.4f}")

    results['Vendas'] = _generate_vendas(num_instances)
    print(f"  - Vendas: {results['Vendas']:.4f}")

    results['Despesas'] = _generate_despesas(num_instances)
    print(f"  - Despesas: {results['Despesas']:.4f}")

    print(f"\n--- DATA GENERATION FOR {num_instances:,} INSTANCES CONCLUDED ---")
    
    # You can uncomment this block if you have psutil installed to check memory usage
    # import os
    # import psutil
    # process = psutil.Process(os.getpid())
    # mem_info = process.memory_info()
    # print(f"  Approximate Memory Usage (RSS): {mem_info.rss / (1024 * 1024):.2f} MB") # RSS - Resident Set Size
    
    return results

if __name__ == "__main__":
    print("This module is intended to be imported. Running a small test here.")
    # Example small test run
    generate_performance_data(100)
    # Clean up after the test
    _clear_all_data()
    print("Small test finished. Data cleared.")