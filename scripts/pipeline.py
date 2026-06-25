import os
import subprocess
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #busco el directorio base
ETL_DIR = os.path.join(BASE_DIR, "etl") #tomo ruta de directorio etl

parser = argparse.ArgumentParser()
parser.add_argument("--equities", nargs="+", required=True)
args = parser.parse_args()

print("Ejecutando ingesta...")
subprocess.run(["python3", os.path.join(ETL_DIR, "extract.py"), "--equities"] + args.equities, check=True)

print("Ejecutando limpieza y carga...")
subprocess.run(["python3", os.path.join(ETL_DIR, "transform_load.py")],check=True)

print("Pipeline finalizado")