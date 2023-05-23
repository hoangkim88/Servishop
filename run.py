import os
import multiprocessing

def run_app(folder_name, port):
    os.chdir(folder_name)
    os.system('flask run --port={}'.format(port))

def run_apps_from_config_file():
    app_config = {
        
        'account-server': 5001,
        'product-server': 5002,
        'cart-server': 5003,
        'order-server': 5004,
        'search-server': 5005
    }

    processes = []

    for folder_name, port in app_config.items():
        print(f'Starting {folder_name} on port {port}...')
        process = multiprocessing.Process(target=run_app, args=(folder_name, port))
        processes.append(process)
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()

if __name__ == '__main__':
    run_apps_from_config_file()
