# realestate_scraper/exporter.py
import pandas as pd
import json
import os
import datetime
import logging

class DataExporter:
    def __init__(self, folder="data"):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        logging.basicConfig(level=logging.INFO)
        # Generar una marca de tiempo única por instancia
        self.run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_csv(self, data, name):
        if not data:
            return
        df = pd.DataFrame(data)
        # Usar el run_id único en lugar de timestamp()
        path = os.path.join(self.folder, f"{name}_{self.run_id}.csv")
        df.to_csv(path, index=False, encoding="utf-8-sig")
        logging.info(f"Guardado {len(df)} registros en {path}")

    def save_json(self, data, name):
        path = os.path.join(self.folder, f"{name}_{self.run_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Guardado JSON en {path}")

    def save_all(self, sales, rentals):
        self.save_csv(sales, "sales")
        self.save_csv(rentals, "rentals")
        self.save_json(sales + rentals, "all")