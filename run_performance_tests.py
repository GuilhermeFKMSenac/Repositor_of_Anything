import os
import time
from typing import Optional

# Import the new data generation module
import data_generator

# Basic helper functions for user interaction
def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_enter():
    """Pauses execution until the user presses Enter."""
    input("\nPressione Enter para continuar...")

def solicit_int(prompt: str, min_val: int = 0) -> Optional[int]:
    """
    Prompts the user for an integer, with validation and an option to cancel.
    """
    while True:
        value_str = input(f"{prompt} (Digite 'c' para cancelar): ").strip()
        if value_str.lower() == 'c':
            return None
        try:
            int_val = int(value_str)
            if int_val >= min_val:
                return int_val
            else:
                print(f"Erro: O valor deve ser maior ou igual a {min_val}.")
        except ValueError:
            print("Erro: Entrada inválida. Por favor, digite um número inteiro válido.")

def main_performance_runner():
    clear_screen()
    print("--- Performance Test Runner ---")
    print("Esta ferramenta gerará um grande número de objetos para testar o desempenho do sistema.")
    print("Atenção: Gerar milhões de objetos pode consumir muita RAM e levar bastante tempo.")
    print("Para 10^7 instâncias, o consumo de RAM pode ser de gigabytes e o tempo de execução de horas,")
    print("podendo levar a travamentos em sistemas com recursos limitados.")

    scales = [10**4, 10**5, 10**6] # Default scales to run automatically
    
    # Option to manually enter a scale
    manual_input = solicit_int("\nDeseja rodar os testes nas escalas padrão (10^4, 10^5, 10^6)? (1 para Sim, 0 para Não/Inserir Manualmente)", min_val=0)
    if manual_input is None:
        print("Operação cancelada.")
        return

    if manual_input == 0:
        custom_scale = solicit_int("Digite o número de instâncias por classe (ex: 10000, 100000, 1000000, 10000000):", min_val=1)
        if custom_scale is None:
            print("Operação cancelada.")
            return
        scales = [custom_scale]

    total_test_start_time = time.time()

    for scale in scales:
        print(f"\n--- Running test for {scale:,} instances per class ---")
        current_scale_start_time = time.time()
        
        # Call the generator function from the separate module
        results = data_generator.generate_performance_data(scale)
        
        current_scale_end_time = time.time()
        print(f"\nResults for {scale:,} instances:")
        for obj_type, duration in results.items():
            print(f"  {obj_type}: {duration:.4f} seconds")
        print(f"Total time for {scale:,} instances: {current_scale_end_time - current_scale_start_time:.4f} seconds.")
        wait_for_enter()

    total_test_end_time = time.time()
    print(f"\n--- ALL PERFORMANCE TESTS CONCLUDED ---")
    print(f"Total duration for all selected tests: {total_test_end_time - total_test_start_time:.4f} seconds.")
    print("Remember that data is stored in memory. For large tests, system resources are critical.")

if __name__ == "__main__":
    main_performance_runner()