# frontend.py
import tkinter as tk
from tkinter import ttk
from backend import tabla_gen, renta

# Función principal de cálculo
def calcular():
    try:
        # Obtener los valores de los campos
        g = int(entry_anio_nacimiento.get())
        nombre_tabla = combo_tabla.get()
        if not nombre_tabla:
            raise ValueError("Debe seleccionar una tabla de mortalidad.")
        
        interes = float(entry_interes.get()) / 100
        tipo_renta = combo_tipo_renta.get()
        if not tipo_renta:
            raise ValueError("Debe seleccionar un tipo de renta (prepagable/pospagable).")
        
        edad_renta = int(entry_edad_renta.get())
        capital = float(entry_capital.get())
        
        # Temporalidad
        temporalidad = combo_temporalidad.get()
        if temporalidad == "Vitalicia":
            temporalidad = None
        elif temporalidad == "Temporal":
            temporalidad = int(entry_duracion.get())
        else:
            raise ValueError("Debe seleccionar si la renta es vitalicia o temporal.")
        
        # Diferimiento
        diferimiento = entry_diferimiento.get()
        if diferimiento == "":
            diferimiento = None
        else:
            diferimiento = int(diferimiento)

        # Generar la tabla generacional
        tabla_generacion = tabla_gen(g, nombre_tabla)

        # Calcular la renta
        sumatorio, valor_renta = renta(tipo_renta, edad_renta, capital, temporalidad, diferimiento, interes, tabla_generacion)
        resultado_label.config(text=f"Valor actual actuarial: {sumatorio:.2f}\nValor de la renta actuarial: {valor_renta:.2f}")
    except Exception as e:
        resultado_label.config(text=f"Error: {str(e)}")

# Interfaz gráfica
root = tk.Tk()
root.title("Calculadora de Renta Actuarial")

# Año de nacimiento
tk.Label(root, text="Año de nacimiento:").grid(row=0, column=0, padx=5, pady=5)
entry_anio_nacimiento = tk.Entry(root)
entry_anio_nacimiento.grid(row=0, column=1)

# Tabla de mortalidad
tk.Label(root, text="Tabla de mortalidad:").grid(row=1, column=0, padx=5, pady=5)
combo_tabla = ttk.Combobox(root, values=['PERM2000C', 'PERF2000C', 'PERM2000P', 'PERF2000P',
                                         'PERM_2020_Indiv_2Orden', 'PERM_2020_Indiv_1Orden',
                                         'PERF_2020_Indiv_2Orden', 'PERF_2020_Indiv_1Orden',
                                         'PERM_2020_Colectivos_2Orden', 'PERM_2020_Colectivos_1Orden',
                                         'PERF_2020_Colectivos_2Orden', 'PERF_2020_Colectivos_1Orden'])
combo_tabla.grid(row=1, column=1)

# Tasa de interés
tk.Label(root, text="Tasa de interés (%):").grid(row=2, column=0, padx=5, pady=5)
entry_interes = tk.Entry(root)
entry_interes.grid(row=2, column=1)

# Tipo de renta
tk.Label(root, text="Tipo de renta:").grid(row=3, column=0, padx=5, pady=5)
combo_tipo_renta = ttk.Combobox(root, values=["prepagable", "pospagable"])
combo_tipo_renta.grid(row=3, column=1)

# Edad al momento de contratación
tk.Label(root, text="Edad al momento de contratación:").grid(row=4, column=0, padx=5, pady=5)
entry_edad_renta = tk.Entry(root)
entry_edad_renta.grid(row=4, column=1)

# Capital a asegurar
tk.Label(root, text="Capital a asegurar:").grid(row=5, column=0, padx=5, pady=5)
entry_capital = tk.Entry(root)
entry_capital.grid(row=5, column=1)

# Temporalidad (vitalicia o temporal)
tk.Label(root, text="Temporalidad:").grid(row=6, column=0, padx=5, pady=5)
combo_temporalidad = ttk.Combobox(root, values=["Vitalicia", "Temporal"])
combo_temporalidad.grid(row=6, column=1)

# Duración (si es temporal)
tk.Label(root, text="Duración (si temporal):").grid(row=7, column=0, padx=5, pady=5)
entry_duracion = tk.Entry(root)
entry_duracion.grid(row=7, column=1)

# Diferimiento
tk.Label(root, text="Diferimiento en años (dejar vacío si no hay):").grid(row=8, column=0, padx=5, pady=5)
entry_diferimiento = tk.Entry(root)
entry_diferimiento.grid(row=8, column=1)

# Botón para calcular
ttk.Button(root, text="Calcular", command=calcular).grid(row=9, column=0, columnspan=2, pady=10)

# Etiqueta para mostrar el resultado
resultado_label = tk.Label(root, text="")
resultado_label.grid(row=10, column=0, columnspan=2)

root.mainloop()