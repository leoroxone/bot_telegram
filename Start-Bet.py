import subprocess
import time

scripts = [
    "bilhetes/main-Bilhetes.py",
    "cantos/main-cantos.py",
    "elite/main-elite.py",
    "punter/main-punter.py",
    "tips/main-tips.py"
]

while True:
    for script in scripts:
        try:
            print(f"Executando script: {script}")
            subprocess.run(["python", script], check=True)
            print(f"Script {script} concluído.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar {script}: {e}")

    intervalo_espera = 5 
    print(f"Aguardando {intervalo_espera} segundos antes da próxima execução...")
    time.sleep(intervalo_espera)
