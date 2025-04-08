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
        resultado_label.config(text=f"Error: {str(e)}", fg="red")

# Crear la ventana principal
root = tk.Tk()
root.title("Jupama Actuarial Software")
root.geometry("600x700")  # Tamaño de la ventana
root.configure(bg="#f0f4f8")  # Fondo gris claro

# Estilo para los widgets
style = ttk.Style()
style.configure("TLabel", background="#f0f4f8", font=("Helvetica", 11))
style.configure("TEntry", font=("Helvetica", 11))
style.configure("TCombobox", font=("Helvetica", 11))
style.configure("TButton", font=("Helvetica", 12, "bold"))

# Encabezado
header_frame = tk.Frame(root, bg="#2c3e50", pady=20)
header_frame.pack(fill="x")

# Título del programa
header_label = tk.Label(
    header_frame,
    text="Jupama Actuarial Software",
    font=("Helvetica", 20, "bold"),
    fg="white",
    bg="#2c3e50"
)
header_label.pack()

# Subtítulo
subtitle_label = tk.Label(
    header_frame,
    text="Cálculo de Rentas Actuariales",
    font=("Helvetica", 12, "italic"),
    fg="#dcdcdc",
    bg="#2c3e50"
)
subtitle_label.pack()

# Frame principal para las entradas
main_frame = tk.Frame(root, bg="#f0f4f8", padx=20, pady=20)
main_frame.pack(fill="both", expand=True)

# Frame para las entradas (sección de datos)
input_frame = tk.LabelFrame(
    main_frame,
    text="Datos de Entrada",
    font=("Helvetica", 14, "bold"),
    bg="#f0f4f8",
    fg="#2c3e50",
    padx=15,
    pady=15
)
input_frame.pack(fill="x", pady=10)

# Año de nacimiento
tk.Label(input_frame, text="Año de nacimiento:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_anio_nacimiento = ttk.Entry(input_frame)
entry_anio_nacimiento.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Tabla de mortalidad
tk.Label(input_frame, text="Tabla de mortalidad:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
combo_tabla = ttk.Combobox(
    input_frame,
    values=['PERM2000C', 'PERF2000C', 'PERM2000P', 'PERF2000P',
            'PERM_2020_Indiv_2Orden', 'PERM_2020_Indiv_1Orden',
            'PERF_2020_Indiv_2Orden', 'PERF_2020_Indiv_1Orden',
            'PERM_2020_Colectivos_2Orden', 'PERM_2020_Colectivos_1Orden',
            'PERF_2020_Colectivos_2Orden', 'PERF_2020_Colectivos_1Orden'],
    state="readonly"
)
combo_tabla.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Tasa de interés
tk.Label(input_frame, text="Tasa de interés (%):", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_interes = ttk.Entry(input_frame)
entry_interes.grid(row=2, column=1, padx=5, pady=5, sticky="w")

# Tipo de renta
tk.Label(input_frame, text="Tipo de renta:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=3, column=0, padx=5, pady=5, sticky="e")
combo_tipo_renta = ttk.Combobox(input_frame, values=["prepagable", "pospagable"], state="readonly")
combo_tipo_renta.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Edad al momento de contratación
tk.Label(input_frame, text="Edad al momento de contratación:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=4, column=0, padx=5, pady=5, sticky="e")
entry_edad_renta = ttk.Entry(input_frame)
entry_edad_renta.grid(row=4, column=1, padx=5, pady=5, sticky="w")

# Capital a asegurar
tk.Label(input_frame, text="Capital a asegurar:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=5, column=0, padx=5, pady=5, sticky="e")
entry_capital = ttk.Entry(input_frame)
entry_capital.grid(row=5, column=1, padx=5, pady=5, sticky="w")

# Temporalidad (vitalicia o temporal)
tk.Label(input_frame, text="Temporalidad:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=6, column=0, padx=5, pady=5, sticky="e")
combo_temporalidad = ttk.Combobox(input_frame, values=["Vitalicia", "Temporal"], state="readonly")
combo_temporalidad.grid(row=6, column=1, padx=5, pady=5, sticky="w")

# Duración (si es temporal)
tk.Label(input_frame, text="Duración (si temporal):", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=7, column=0, padx=5, pady=5, sticky="e")
entry_duracion = ttk.Entry(input_frame)
entry_duracion.grid(row=7, column=1, padx=5, pady=5, sticky="w")

# Diferimiento
tk.Label(input_frame, text="Diferimiento en años (dejar vacío si no hay):", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=8, column=0, padx=5, pady=5, sticky="e")
entry_diferimiento = ttk.Entry(input_frame)
entry_diferimiento.grid(row=8, column=1, padx=5, pady=5, sticky="w")

# Frame para el botón de cálculo
button_frame = tk.Frame(main_frame, bg="#f0f4f8")
button_frame.pack(pady=10)

# Botón para calcular
calcular_button = ttk.Button(button_frame, text="Calcular", command=calcular, style="Accent.TButton")
style.configure("Accent.TButton", background="#3498db", foreground="white", font=("Helvetica", 12, "bold"))
calcular_button.pack()

# Frame para los resultados
result_frame = tk.LabelFrame(
    main_frame,
    text="Resultados",
    font=("Helvetica", 14, "bold"),
    bg="#f0f4f8",
    fg="#2c3e50",
    padx=15,
    pady=15
)
result_frame.pack(fill="x", pady=10)

# Etiqueta para mostrar el resultado
resultado_label = tk.Label(
    result_frame,
    text="",
    font=("Helvetica", 12),
    bg="#f0f4f8",
    fg="#2c3e50",
    justify="left"
)
resultado_label.pack()

# Footer
footer_frame = tk.Frame(root, bg="#2c3e50", pady=10)
footer_frame.pack(fill="x", side="bottom")

footer_label = tk.Label(
    footer_frame,
    text="© 2025 Jupama Actuarial Software. Todos los derechos reservados.",
    font=("Helvetica", 10),
    fg="#dcdcdc",
    bg="#2c3e50"
)
footer_label.pack()

# Iniciar la aplicación
root.mainloop()