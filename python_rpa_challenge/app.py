import json
from pathlib import Path
from tkinter import filedialog, ttk
import tkinter as tk

from rpa.portal_transparencia import collect_data, export_result, normalize_filters


class PortalApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Robô Portal da Transparência")
        self.geometry("620x360")
        self.resizable(False, False)

        tk.Label(self, text="Nome ou CPF", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        self.name_entry = tk.Entry(self, width=60)
        self.name_entry.pack(padx=16, fill="x")

        tk.Label(self, text="Filtros (um por linha)", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=16, pady=(12, 4))
        self.filters_text = tk.Text(self, height=8, width=60)
        self.filters_text.pack(padx=16, fill="x")
        self.filters_text.insert("1.0", "BENEFICIÁRIO DE PROGRAMA SOCIAL")

        self.status_var = tk.StringVar(value="Pronto")
        tk.Label(self, textvariable=self.status_var, fg="#0b5fff").pack(pady=(10, 0))

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=16)
        ttk.Button(button_frame, text="Executar", command=self.run_robot).grid(row=0, column=0, padx=8)
        ttk.Button(button_frame, text="Salvar JSON", command=self.save_json).grid(row=0, column=1, padx=8)

        self.last_result: dict | None = None

    def run_robot(self) -> None:
        name_or_cpf = self.name_entry.get().strip()
        filters = normalize_filters(self.filters_text.get("1.0", tk.END))
        if not name_or_cpf:
            self.status_var.set("Informe nome ou CPF")
            return

        self.status_var.set("Executando automação...")
        self.update_idletasks()
        self.last_result = collect_data(name_or_cpf, filters)
        self.status_var.set("Automação concluída")

    def save_json(self) -> None:
        if not self.last_result:
            self.status_var.set("Execute a automação antes de salvar")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if output_path:
            export_result(self.last_result, Path(output_path))
            self.status_var.set(f"JSON salvo em {Path(output_path).name}")


if __name__ == "__main__":
    app = PortalApp()
    app.mainloop()
