import os
import threading
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from supabase import create_client, Client
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from turnos_modulo import TurnosModuloFrame
from historial_turnos_modal import HistorialTurnosModal

SUPABASE_URL = "https://ksymuaamkjzoehupdcdp.supabase.co"
SUPABASE_KEY = "sb_publishable_Mdq1uUvlrQikfraqcZ7vDw_dhGeeBW2"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class AdminDashboard(ctk.CTk):
    def __init__(self, nombre_usuario):
        super().__init__()
        self.title("PANE-SYS - Panel de Administración")
        self.geometry("1150x680")
        self.resizable(False, False)
        self.configure(fg_color="#FDFBF7")

        self.nombre_usuario = nombre_usuario
        self.ruta_imagen_seleccionada = None

        # --- MENÚ LATERAL (Sidebar) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#5C3A21")
        self.sidebar_frame.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🍞 PANE-SYS\n(Administrador)", 
            font=("Arial", 16, "bold"), 
            text_color="#FDFBF7"
        )
        self.logo_label.pack(pady=(25, 30))

        # Botones de navegación
        self.btn_inicio = ctk.CTkButton(self.sidebar_frame, text="📊 Tablero / Inicio", command=self.mostrar_inicio, fg_color="#8D5524", hover_color="#6F431B", height=38, font=("Arial", 13))
        self.btn_inicio.pack(fill="x", padx=15, pady=8)

        self.btn_productos = ctk.CTkButton(self.sidebar_frame, text="🥐 Registrar Producto", command=self.mostrar_nuevo_producto, fg_color="transparent", hover_color="#6F431B", height=38, font=("Arial", 13))
        self.btn_productos.pack(fill="x", padx=15, pady=8)

        self.btn_insumos = ctk.CTkButton(self.sidebar_frame, text="📦 Control de Insumos", command=self.mostrar_insumos, fg_color="transparent", hover_color="#6F431B", height=38, font=("Arial", 13), anchor="w")
        self.btn_insumos.pack(fill="x", padx=15, pady=8)

        self.btn_ventas = ctk.CTkButton(self.sidebar_frame, text="💰 Ventas y Reportes PDF", command=self.mostrar_ventas, fg_color="transparent", hover_color="#6F431B", height=38, font=("Arial", 13), anchor="w")
        self.btn_ventas.pack(fill="x", padx=15, pady=8)

        self.btn_mermas = ctk.CTkButton(self.sidebar_frame, text="📉 Control de Mermas", command=self.mostrar_mermas, fg_color="transparent", hover_color="#6F431B", height=38, font=("Arial", 13), anchor="w")
        self.btn_mermas.pack(fill="x", padx=15, pady=8)

        self.btn_compras = ctk.CTkButton(self.sidebar_frame, text="📦 Compra de Insumos", command=self.mostrar_compra_insumos, fg_color="transparent", hover_color="#6F431B", height=38, font=("Arial", 13), anchor="w")
        self.btn_compras.pack(fill="x", padx=15, pady=8)

        self.btn_turnos = ctk.CTkButton(self.sidebar_frame, text="🕒 Turnos y Stock", command=self.mostrar_turnos_stock, fg_color="transparent", hover_color="#6F431B", height=38, font=("Arial", 13), anchor="w")
        self.btn_turnos.pack(fill="x", padx=15, pady=8)

        self.btn_logout = ctk.CTkButton(self.sidebar_frame, text="🚪 Cerrar Sesión", command=self.cerrar_sesion, fg_color="#A93226", hover_color="#78281F", height=38, font=("Arial", 13), anchor="w")
        self.btn_logout.pack(side="bottom", fill="x", padx=15, pady=20)

        # --- ÁREA DE CONTENIDO PRINCIPAL ---
        self.main_content = ctk.CTkFrame(self, fg_color="#FDFBF7", corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True)

        self.mostrar_inicio()

    def limpiar_contenido(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def actualizar_botones_nav(self, activo):
        self.btn_inicio.configure(fg_color="#8D5524" if activo == "inicio" else "transparent")
        self.btn_productos.configure(fg_color="#8D5524" if activo == "productos" else "transparent")
        self.btn_insumos.configure(fg_color="#8D5524" if activo == "insumos" else "transparent")
        self.btn_ventas.configure(fg_color="#8D5524" if activo == "ventas" else "transparent")
        self.btn_mermas.configure(fg_color="#8D5524" if activo == "mermas" else "transparent")
        self.btn_compras.configure(fg_color="#8D5524" if activo == "compras" else "transparent")


    # ================= TABLERO / INICIO =================
    def mostrar_inicio(self):
        self.limpiar_contenido()
        self.actualizar_botones_nav("inicio")

        header = ctk.CTkLabel(self.main_content, text=f"Bienvenido, {self.nombre_usuario}", font=("Arial", 24, "bold"), text_color="#3E2723")
        header.pack(anchor="w", padx=30, pady=(20, 5))

        sub_header = ctk.CTkLabel(self.main_content, text="Tablero general de control y métricas en tiempo real", font=("Arial", 13), text_color="gray")
        sub_header.pack(anchor="w", padx=30, pady=(0, 15))

        # --- TARJETAS MÉTRICAS ---
        cards_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=5)

        self.card1 = ctk.CTkFrame(cards_frame, fg_color="#FFFFFF", corner_radius=15, border_width=2, border_color="#E6DCC3", width=280, height=115)
        self.card1.grid(row=0, column=0, padx=10, pady=5)
        self.card1.pack_propagate(False)
        ctk.CTkLabel(self.card1, text="💰 Ventas Totales", font=("Arial", 13, "bold"), text_color="#5C3A21").pack(pady=(15, 2))
        self.lbl_val_ventas = ctk.CTkLabel(self.card1, text="Cargando...", font=("Arial", 20, "bold"), text_color="#27AE60")
        self.lbl_val_ventas.pack(pady=5)

        self.card2 = ctk.CTkFrame(cards_frame, fg_color="#FFFFFF", corner_radius=15, border_width=2, border_color="#E6DCC3", width=280, height=115)
        self.card2.grid(row=0, column=1, padx=10, pady=5)
        self.card2.pack_propagate(False)
        ctk.CTkLabel(self.card2, text="📦 Materia Prima / Insumos", font=("Arial", 13, "bold"), text_color="#5C3A21").pack(pady=(15, 2))
        self.lbl_val_insumos = ctk.CTkLabel(self.card2, text="Cargando...", font=("Arial", 20, "bold"), text_color="#D35400")
        self.lbl_val_insumos.pack(pady=5)

        self.card3 = ctk.CTkFrame(cards_frame, fg_color="#FFFFFF", corner_radius=15, border_width=2, border_color="#E6DCC3", width=280, height=115)
        self.card3.grid(row=0, column=2, padx=10, pady=5)
        self.card3.pack_propagate(False)
        ctk.CTkLabel(self.card3, text="📉 Mermas Totales", font=("Arial", 13, "bold"), text_color="#7E5109").pack(pady=(15, 2))
        self.lbl_val_mermas = ctk.CTkLabel(self.card3, text="Cargando...", font=("Arial", 20, "bold"), text_color="#C0392B")
        self.lbl_val_mermas.pack(pady=5)

        # --- SECCIÓN DE GRÁFICA INFERIOR (UNIFICADA) ---
        grafica_frame = ctk.CTkFrame(self.main_content, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3")
        grafica_frame.pack(fill="both", expand=True, padx=30, pady=(15, 20))

        ctk.CTkLabel(grafica_frame, text="📈 Rendimiento y Salida de Productos", font=("Arial", 15, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(15, 2))
        ctk.CTkLabel(grafica_frame, text="Visualización gráfica del comportamiento real de venta diaria.", font=("Arial", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))

        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            res_productos = supabase.table("producto").select("*").execute()
            mapa_productos = {}
            conteo_ventas = {}

            if res_productos.data:
                for row in res_productos.data:
                    pid = row.get("idProducto") or row.get("idproducto") or row.get("id")
                    nombre = row.get("nombre", "Sin nombre")
                    mapa_productos[pid] = nombre
                    conteo_ventas[nombre] = 0 # Inicializamos todos los productos en 0 ventas

            res_detalles = supabase.table("detalleventa").select("*").execute()
            if res_detalles.data:
                for det in res_detalles.data:
                    pid = det.get("idProducto") or det.get("idproducto")
                    cant = int(det.get("cantidad", 0))
                    nombre_prod = mapa_productos.get(pid)
                    if nombre_prod:
                        conteo_ventas[nombre_prod] += cant

            if conteo_ventas:
                # Ordenamos de mayor a menor venta
                ordenados = sorted(conteo_ventas.items(), key=lambda x: x[1], reverse=True)
                productos = [item[0] for item in ordenados]
                cantidades = [item[1] for item in ordenados]
            else:
                productos = ['Sin productos']
                cantidades = [0]

            # Dibujar la gráfica de barras con estilo elegante
            fig, ax = plt.subplots(figsize=(9, 3.2), dpi=100)
            fig.patch.set_facecolor('#FFFFFF')
            ax.set_facecolor('#FDFBF7')

            barras = ax.bar(productos, cantidades, color='#8D5524', width=0.45, edgecolor='#5C3A21', linewidth=1)
            ax.set_ylabel("Unidades Vendidas", fontsize=10, color='#3E2723', fontweight='bold')
            ax.set_ylim(bottom=0, top=max(cantidades) * 1.2 if max(cantidades) > 0 else 5)
            ax.tick_params(axis='x', colors='#3E2723', labelsize=10)
            ax.tick_params(axis='y', colors='#3E2723', labelsize=10)
            
            for barra in barras:
                yval = barra.get_height()
                ax.text(barra.get_x() + barra.get_width()/2.0, yval + (max(cantidades)*0.03 if max(cantidades)>0 else 0.1), f"{int(yval)}", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#3E2723')

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#D7CCC8')
            ax.spines['bottom'].set_color('#D7CCC8')

            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=grafica_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 15))

        except Exception as e:
            print(f"Error gráfica: {e}")
            ctk.CTkLabel(grafica_frame, text="No se pudieron cargar los datos de la gráfica.", font=("Arial", 12), text_color="red").pack(pady=30)

        threading.Thread(target=self.cargar_metricas_async, daemon=True).start()

    def cargar_metricas_async(self):
        total_ventas = 0.0
        total_insumos = 0
        total_mermas = 0

        try:
            res_ventas = supabase.table("venta").select("total_vent").execute()
            if res_ventas.data:
                total_ventas = sum([item.get("total_vent", 0) for item in res_ventas.data])
        except Exception as e:
            print(f"Error ventas métricas: {e}")

        try:
            res_insumos = supabase.table("materia prima").select("*", count="exact").execute()
            total_insumos = res_insumos.count if res_insumos.count is not None else len(res_insumos.data)
        except Exception as e:
            print(f"Error insumos métricas: {e}")

        try:
            res_mermas = supabase.table("merma").select("*", count="exact").execute()
            total_mermas = res_mermas.count if res_mermas.count is not None else len(res_mermas.data)
        except Exception as e:
            print(f"Error mermas métricas: {e}")

        self.after(0, lambda: self.lbl_val_ventas.configure(text=f"${total_ventas:,.2f}"))
        self.after(0, lambda: self.lbl_val_insumos.configure(text=f"{total_insumos} Registrados"))
        self.after(0, lambda: self.lbl_val_mermas.configure(text=f"{total_mermas} Registradas"))

    # ================= REGISTRAR PRODUCTO =================
    def mostrar_nuevo_producto(self):
        self.limpiar_contenido()
        self.actualizar_botones_nav("productos")

        ctk.CTkLabel(self.main_content, text="Registro de Nuevo Producto o Pan", font=("Arial", 22, "bold"), text_color="#3E2723").pack(anchor="w", padx=30, pady=(20, 5))
        ctk.CTkLabel(self.main_content, text="Configura la información general del pan para el catálogo de la panadería.", font=("Arial", 13), text_color="gray").pack(anchor="w", padx=30, pady=(0, 15))

        main_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=5)

        # Columna Izquierda (Datos Generales - Sin Stock)
        left_frame = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        ctk.CTkLabel(left_frame, text="Datos generales del Pan", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(20, 15))

        self.entry_nom_prod = ctk.CTkEntry(left_frame, placeholder_text="Nombre del Pan (ej. Concha)", width=340, height=40, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_nom_prod.pack(anchor="w", padx=20, pady=10)

        self.entry_desc_prod = ctk.CTkEntry(left_frame, placeholder_text="Descripción (ej. Pan dulce con vainilla)", width=340, height=40, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_desc_prod.pack(anchor="w", padx=20, pady=10)

        self.entry_precio_prod = ctk.CTkEntry(left_frame, placeholder_text="Precio Venta al Público (ej. 15.00)", width=340, height=40, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_precio_prod.pack(anchor="w", padx=20, pady=10)

        self.entry_costo_prod = ctk.CTkEntry(left_frame, placeholder_text="Costo de Producción (ej. 8.50)", width=340, height=40, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_costo_prod.pack(anchor="w", padx=20, pady=10)

        # Columna Derecha (Imagen y Guardar)
        right_frame = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3", width=320)
        right_frame.pack(side="right", fill="y", padx=(10, 0), pady=5)
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame, text="Imagen del Producto", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(20, 10))

        self.lbl_preview_img = ctk.CTkLabel(right_frame, text="[Sin Imagen Seleccionada]", fg_color="#F9F6F0", corner_radius=10, width=260, height=160, text_color="gray")
        self.lbl_preview_img.pack(padx=20, pady=10)

        btn_cargar_img = ctk.CTkButton(right_frame, text="📁 Seleccionar Imagen", command=self.seleccionar_imagen, fg_color="#8D5524", hover_color="#6F431B", height=36, font=("Arial", 12, "bold"))
        btn_cargar_img.pack(padx=20, pady=10)

        btn_guardar_prod = ctk.CTkButton(right_frame, text="💾 Guardar Producto", command=self.guardar_producto, fg_color="#27AE60", hover_color="#1E8449", height=40, font=("Arial", 13, "bold"))
        btn_guardar_prod.pack(padx=20, pady=(20, 15))

    def seleccionar_imagen(self):
        archivo = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg")])
        if archivo:
            self.ruta_imagen_seleccionada = archivo
            nombre_corto = os.path.basename(archivo)
            self.lbl_preview_img.configure(text=f"Imagen:\n{nombre_corto}", text_color="#3E2723")

    def guardar_producto(self):
        nombre = self.entry_nom_prod.get().strip()
        desc = self.entry_desc_prod.get().strip()
        precio = self.entry_precio_prod.get().strip()
        costo = self.entry_costo_prod.get().strip()

        if not nombre or not precio:
            messagebox.showerror("Campos incompletos", "Por favor completa al menos el Nombre y el Precio de Venta.")
            return

        try:
            res_ult = supabase.table("producto").select("idProducto").order("idProducto", desc=True).limit(1).execute()
            nuevo_id = 1
            if res_ult.data:
                ultimo = res_ult.data[0].get("idProducto")
                if ultimo is not None:
                    nuevo_id = int(ultimo) + 1

            supabase.table("producto").insert({
                "idProducto": nuevo_id,
                "nombre": nombre,
                "descripcion": desc,
                "precio_vent": float(precio),
                "cost_produccion": float(costo) if costo else 0.0
            }).execute()

            messagebox.showinfo("¡Éxito!", f"El producto '{nombre}' se guardó correctamente en el catálogo.")
            self.entry_nom_prod.delete(0, 'end')
            self.entry_desc_prod.delete(0, 'end')
            self.entry_precio_prod.delete(0, 'end')
            self.entry_costo_prod.delete(0, 'end')
            self.ruta_imagen_seleccionada = None
            self.lbl_preview_img.configure(text="[Sin Imagen Seleccionada]", text_color="gray")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el producto:\n{e}")

    # ================= CONTROL DE INSUMOS =================
    def mostrar_insumos(self):
        self.limpiar_contenido()
        self.actualizar_botones_nav("insumos")

        ctk.CTkLabel(self.main_content, text="Gestión y Conteo de Insumos", font=("Arial", 22, "bold"), text_color="#3E2723").pack(anchor="w", padx=30, pady=(25, 5))
        ctk.CTkLabel(self.main_content, text="Supervisa, administra y elimina materia prima.", font=("Arial", 13), text_color="gray").pack(anchor="w", padx=30, pady=(0, 15))

        content_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)

        table_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3")
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=5)

        ctk.CTkLabel(table_frame, text="Inventario Actual de Materia Prima", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(15, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#3E2723", rowheight=28)
        style.configure("Treeview.Heading", background="#E6DCC3", foreground="#5C3A21", font=("Arial", 11, "bold"))

        columns = ("ID", "Nombre", "Stock", "Mínimo", "Unidad")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre Insumo")
        self.tree.heading("Stock", text="Stock Act.")
        self.tree.heading("Mínimo", text="Stock Mín.")
        self.tree.heading("Unidad", text="Unidad")

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Nombre", width=150, anchor="w")
        self.tree.column("Stock", width=80, anchor="center")
        self.tree.column("Mínimo", width=80, anchor="center")
        self.tree.column("Unidad", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        btn_eliminar = ctk.CTkButton(
            table_frame, 
            text="🗑️ Eliminar Insumo Seleccionado", 
            command=self.eliminar_insumo, 
            fg_color="#A93226", 
            hover_color="#78281F", 
            height=35, 
            font=("Arial", 12, "bold")
        )
        btn_eliminar.pack(anchor="w", padx=20, pady=(0, 15))

        threading.Thread(target=self.cargar_datos_insumos_async, daemon=True).start()

        form_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3", width=280)
        form_frame.pack(side="right", fill="y", padx=(15, 0), pady=5)
        form_frame.pack_propagate(False)

        ctk.CTkLabel(form_frame, text="Registrar Nuevo Insumo", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(15, 10))

        self.entry_id_insumo = ctk.CTkEntry(form_frame, placeholder_text="ID Manual (ej. 1)", width=240, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_id_insumo.pack(padx=20, pady=6)

        self.entry_nombre_insumo = ctk.CTkEntry(form_frame, placeholder_text="Nombre (ej. Harina)", width=240, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_nombre_insumo.pack(padx=20, pady=6)

        self.entry_stock_insumo = ctk.CTkEntry(form_frame, placeholder_text="Stock Actual (ej. 50)", width=240, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_stock_insumo.pack(padx=20, pady=6)

        self.entry_min_insumo = ctk.CTkEntry(form_frame, placeholder_text="Stock Mínimo (ej. 10)", width=240, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_min_insumo.pack(padx=20, pady=6)

        self.entry_unidad_insumo = ctk.CTkEntry(form_frame, placeholder_text="Unidad (ej. Kg, Litros)", width=240, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_unidad_insumo.pack(padx=20, pady=6)

        btn_guardar_insumo = ctk.CTkButton(form_frame, text="💾 Guardar Insumo", command=self.guardar_insumo, fg_color="#8D5524", hover_color="#6F431B", height=38, font=("Arial", 13, "bold"))
        btn_guardar_insumo.pack(padx=20, pady=(12, 10))

    def cargar_datos_insumos_async(self):
        try:
            res = supabase.table("materia prima").select("*").execute()
            
            def actualizar_tabla():
                for item in self.tree.get_children():
                    self.tree.delete(item)
                if res.data:
                    self.tree.tag_configure("alerta", background="#FADB08", foreground="#78281F")
                    self.tree.tag_configure("normal", background="#FFFFFF", foreground="#3E2723")

                    for row in res.data:
                        id_mat = row.get("id_Mat_Prim", "")
                        nombre = row.get("nom_pro", "")
                        stock = row.get("stock_act", 0)
                        stock_min = row.get("stock_min", 5)
                        costo = row.get("costo_unit", 0.0)
                        unidad = row.get("uni_med", "")

                        if float(stock) <= float(stock_min):
                            tag_alerta = ("alerta",)
                        else:
                            tag_alerta = ("normal",)

                        self.tree.insert("", "end", values=(
                            id_mat, nombre, stock, stock_min, f'${float(costo):,.2f}', unidad
                        ), tags=tag_alerta)
            self.after(0, actualizar_tabla)

        except Exception as e:
            print(f"Error al cargar insumos: {e}")

    def guardar_insumo(self):
        id_str = self.entry_id_insumo.get().strip()
        nombre = self.entry_nombre_insumo.get().strip()
        stock = self.entry_stock_insumo.get().strip()
        stock_min = self.entry_min_insumo.get().strip()
        unidad = self.entry_unidad_insumo.get().strip()

        if not id_str or not nombre or not stock or not stock_min or not unidad:
            messagebox.showerror("Campos incompletos", "Por favor completa todos los campos.")
            return

        try:
            supabase.table("materia prima").insert({
                "id_Mat_Prim": int(id_str),
                "nom_pro": nombre,
                "stock_act": float(stock),
                "stock_min": float(stock_min),
                "uni_med": unidad
            }).execute()

            messagebox.showinfo("¡Éxito!", "Insumo registrado correctamente.")
            self.entry_id_insumo.delete(0, 'end')
            self.entry_nombre_insumo.delete(0, 'end')
            self.entry_stock_insumo.delete(0, 'end')
            self.entry_min_insumo.delete(0, 'end')
            self.entry_unidad_insumo.delete(0, 'end')
            threading.Thread(target=self.cargar_datos_insumos_async, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el insumo:\n{e}")

    def eliminar_insumo(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selección requerida", "Por favor selecciona un insumo de la tabla para eliminar.")
            return

        item_data = self.tree.item(selected_item)
        id_mat = item_data['values'][0]
        nombre = item_data['values'][1]

        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás segura de eliminar '{nombre}'?"):
            try:
                supabase.table("materia prima").delete().eq("id_Mat_Prim", id_mat).execute()
                messagebox.showinfo("Eliminado", f"Insumo '{nombre}' eliminado con éxito.")
                threading.Thread(target=self.cargar_datos_insumos_async, daemon=True).start()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    # ================= VENTAS Y REPORTES PDF =================
    def mostrar_ventas(self):
        self.limpiar_contenido()
        self.actualizar_botones_nav("ventas")

        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(header_frame, text="Consultas y Reportes de Ventas", font=("Arial", 22, "bold"), text_color="#3E2723").pack(side="left")
        
        botones_header_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        botones_header_frame.pack(side="right")

        # Botón para abrir el Historial de Turnos y Ganancias
        btn_turnos = ctk.CTkButton(
            botones_header_frame, 
            text="📋 Historial de Turnos", 
            command=lambda: HistorialTurnosModal(self, supabase), 
            fg_color="#8D5524", 
            hover_color="#6F431B", 
            height=36, 
            font=("Arial", 13, "bold")
        )
        btn_turnos.pack(side="left", padx=10)

        btn_pdf = ctk.CTkButton(
            botones_header_frame, 
            text="🖨️ Imprimir / Exportar PDF", 
            command=self.exportar_pdf, 
            fg_color="#8D5524", 
            hover_color="#6F431B", 
            height=36, 
            font=("Arial", 13, "bold")
        )
        btn_pdf.pack(side="left")

        filter_frame = ctk.CTkFrame(self.main_content, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E6DCC3")
        filter_frame.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(filter_frame, text="📅 Filtrar periodo:", font=("Arial", 12, "bold"), text_color="#5C3A21").pack(side="left", padx=15, pady=10)
        
        self.combo_filtro = ctk.CTkComboBox(
            filter_frame, 
            values=["Todos", "Hoy", "Esta Semana"], 
            command=self.aplicar_filtro_ventas,
            width=160,
            fg_color="#F9F6F0",
            border_color="#D7CCC8"
        )
        self.combo_filtro.pack(side="left", padx=5, pady=10)
        self.combo_filtro.set("Todos")

        metrics_frame = ctk.CTkFrame(self.main_content, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E6DCC3")
        metrics_frame.pack(fill="x", padx=30, pady=5, ipady=2)

        m1 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        m1.pack(side="left", expand=True, padx=10, pady=8)
        ctk.CTkLabel(m1, text="Ventas Registradas", font=("Arial", 11), text_color="gray").pack()
        self.lbl_met_trans = ctk.CTkLabel(m1, text="0", font=("Arial", 16, "bold"), text_color="#5C3A21")
        self.lbl_met_trans.pack()

        m2 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        m2.pack(side="left", expand=True, padx=10, pady=8)
        ctk.CTkLabel(m2, text="Ingresos del Periodo", font=("Arial", 11), text_color="gray").pack()
        self.lbl_met_ingresos = ctk.CTkLabel(m2, text="$0.00", font=("Arial", 16, "bold"), text_color="#27AE60")
        self.lbl_met_ingresos.pack()

        m3 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        m3.pack(side="left", expand=True, padx=10, pady=8)
        ctk.CTkLabel(m3, text="Promedio por Venta", font=("Arial", 11), text_color="gray").pack()
        self.lbl_met_prom = ctk.CTkLabel(m3, text="$0.00", font=("Arial", 16, "bold"), text_color="#2980B9")
        self.lbl_met_prom.pack()

        table_frame = ctk.CTkFrame(self.main_content, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3")
        table_frame.pack(fill="both", expand=True, padx=30, pady=10)

        ctk.CTkLabel(table_frame, text="Historial de Ventas Filtrado", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(15, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#3E2723", rowheight=28)
        style.configure("Treeview.Heading", background="#E6DCC3", foreground="#5C3A21", font=("Arial", 11, "bold"))

        columns = ("ID Venta", "Fecha", "Usuario ID", "Total Venta")
        self.tree_ventas = ttk.Treeview(table_frame, columns=columns, show="headings", height=7)
        
        self.tree_ventas.heading("ID Venta", text="ID Venta")
        self.tree_ventas.heading("Fecha", text="Fecha / Hora")
        self.tree_ventas.heading("Usuario ID", text="ID Usuario")
        self.tree_ventas.heading("Total Venta", text="Total")

        self.tree_ventas.column("ID Venta", width=80, anchor="center")
        self.tree_ventas.column("Fecha", width=220, anchor="center")
        self.tree_ventas.column("Usuario ID", width=90, anchor="center")
        self.tree_ventas.column("Total Venta", width=120, anchor="center")

        self.tree_ventas.pack(fill="both", expand=True, padx=20, pady=10)

        threading.Thread(target=self.cargar_datos_ventas_filtradas_async, daemon=True).start()

    def aplicar_filtro_ventas(self, choice):
        threading.Thread(target=self.cargar_datos_ventas_filtradas_async, daemon=True).start()

    def obtener_ventas_filtradas_data(self):
        filtro = getattr(self, 'combo_filtro', None)
        tipo_filtro = filtro.get() if filtro else "Todos"
        
        try:
            res = supabase.table("venta").select("*").execute()
            if not res.data:
                return []

            ventas_filtradas = []
            ahora = datetime.now()

            for row in res.data:
                f_raw = row.get("fecha_vent", "")
                try:
                    dt = datetime.fromisoformat(f_raw.replace("Z", "+00:00"))
                    dt_naive = dt.replace(tzinfo=None)
                except Exception:
                    dt_naive = ahora

                if tipo_filtro == "Hoy":
                    if dt_naive.date() == ahora.date():
                        ventas_filtradas.append(row)
                elif tipo_filtro == "Esta Semana":
                    inicio_semana = ahora - timedelta(days=ahora.weekday())
                    if dt_naive.date() >= inicio_semana.date():
                        ventas_filtradas.append(row)
                else:
                    ventas_filtradas.append(row)

            return ventas_filtradas
        except Exception as e:
            print(f"Error al filtrar ventas: {e}")
            return []

    def cargar_datos_ventas_filtradas_async(self):
        ventas = self.obtener_ventas_filtradas_data()
        
        self.total_transacciones = len(ventas)
        self.monto_total = sum([float(item.get("total_vent", 0)) for item in ventas])
        promedio_venta = self.monto_total / self.total_transacciones if self.total_transacciones > 0 else 0.0

        def actualizar_ui():
            if hasattr(self, 'lbl_met_trans'):
                self.lbl_met_trans.configure(text=str(self.total_transacciones))
                self.lbl_met_ingresos.configure(text=f"${self.monto_total:,.2f}")
                self.lbl_met_prom.configure(text=f"${promedio_venta:,.2f}")

            for item in self.tree_ventas.get_children():
                self.tree_ventas.delete(item)

            for row in ventas:
                id_venta = row.get("idVenta", row.get("id", ""))
                fecha_raw = row.get("fecha_vent", "")
                try:
                    dt = datetime.fromisoformat(fecha_raw.replace("Z", "+00:00"))
                    fecha_formateada = dt.strftime("%d/%m/%Y %I:%M %p")
                except Exception:
                    fecha_formateada = fecha_raw

                usuario_id = row.get("idUsuario", "")
                total = row.get("total_vent", 0.0)
                
                self.tree_ventas.insert("", "end", values=(id_venta, fecha_formateada, usuario_id, f"${float(total):,.2f}"))

        self.after(0, actualizar_ui)

    def exportar_pdf(self):
        try:
            carpeta_reportes = "reportes"
            if not os.path.exists(carpeta_reportes):
                os.makedirs(carpeta_reportes)

            tipo_filtro = self.combo_filtro.get()
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nombre_archivo = os.path.join(carpeta_reportes, f"reporte_general_{tipo_filtro.lower().replace(' ', '_')}_{timestamp}.pdf")

            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            elementos = []
            styles = getSampleStyleSheet()
            
            estilo_sub = ParagraphStyle(
                'SubDerecha',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10,
                textColor=colors.HexColor('#7E5109'),
                alignment=2
            )

            logo_cell = ""
            if os.path.exists("logo.png"):
                try:
                    logo_cell = RLImage("logo.png", width=75, height=75)
                except Exception:
                    logo_cell = Paragraph("<b>PANE-SYS</b>", styles['Normal'])

            fecha_actual = datetime.now().strftime("%d/%m/%Y %I:%M %p")
            texto_derecha = Paragraph(
                "<b>PANE-SYS - PANADERÍA</b><br/>"
                f"<b>REPORTE GENERAL ({tipo_filtro.upper()})</b><br/>"
                f"<font size=9 color='gray'>Admin: {self.nombre_usuario}</font><br/>"
                f"<font size=9 color='gray'>Fecha: {fecha_actual}</font>",
                estilo_sub
            )

            header_table = Table([[logo_cell, texto_derecha]], colWidths=[100, 434])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15)
            ]))

            elementos.append(header_table)
            elementos.append(Spacer(1, 10))

            # --- SECCIÓN 1: VENTAS ---
            total_ingresos = getattr(self, 'monto_total', 0.0)
            resumen_texto = f"""
            <b>1. Resumen de Ventas ({tipo_filtro}):</b><br/>
            • Total de Transacciones: {getattr(self, 'total_transacciones', 0)}<br/>
            • Ingresos Totales: ${total_ingresos:,.2f}
            """
            elementos.append(Paragraph(resumen_texto, styles['Normal']))
            elementos.append(Spacer(1, 8))

            data = [["ID Venta", "Fecha / Hora", "ID Usuario", "Total Venta"]]
            ventas_filtradas = self.obtener_ventas_filtradas_data()
            for row in ventas_filtradas:
                id_v = str(row.get("idVenta", row.get("id", "")))
                f_raw = row.get("fecha_vent", "")
                try:
                    dt = datetime.fromisoformat(f_raw.replace("Z", "+00:00"))
                    f_fmt = dt.strftime("%d/%m/%Y %I:%M %p")
                except Exception:
                    f_fmt = f_raw
                u_id = str(row.get("idUsuario", ""))
                tot = f"${float(row.get('total_vent', 0.0)):,.2f}"
                data.append([id_v, f_fmt, u_id, tot])

            tabla_pdf = Table(data, colWidths=[80, 200, 90, 110])
            tabla_pdf.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5C3A21')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FDFBF7')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E6DCC3')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F6F0')])
            ]))

            elementos.append(tabla_pdf)
            elementos.append(Spacer(1, 15))

            # --- SECCIÓN 2: COMPRAS DE INSUMOS (CORREGIDO) ---
            elementos.append(Paragraph("<b>2. Historial de Compras de Insumos (Gastos)</b>", styles['Heading2']))
            elementos.append(Spacer(1, 8))

            data_compras = [["ID Compra", "Fecha", "Proveedor", "Insumo", "Cant.", "Subtotal"]]
            total_gastos_compras = 0.0

            try:
                insumos_map = {}
                res_mat = supabase.table("materia prima").select("id_Mat_Prim, nom_pro").execute()
                if res_mat.data:
                    for m in res_mat.data:
                        insumos_map[m.get("id_Mat_Prim")] = m.get("nom_pro", "Insumo")

                res_c = supabase.table("det_compra_insumo").select("idCompra, cant, subtot, id_Mat_Prim, comprainsumo(fecha_com, proveedor)").execute()
                if res_c.data:
                    for c in res_c.data:
                        id_c = str(c.get("idCompra", ""))
                        cant = str(c.get("cant", 0))
                        subtot = float(c.get("subtot", 0))
                        total_gastos_compras += subtot

                        id_mat = c.get("id_Mat_Prim")
                        insumo = insumos_map.get(id_mat, "Insumo")

                        compra_info = c.get("comprainsumo", {}) or {}
                        fecha_c = str(compra_info.get("fecha_com", ""))[:16].replace("T", " ")
                        prov = str(compra_info.get("proveedor", "General"))

                        data_compras.append([id_c, fecha_c, prov, insumo, cant, f"${subtot:,.2f}"])
            except Exception as e:
                print(f"Error consultando compras para PDF: {e}")

            if len(data_compras) > 1:
                t_compras = Table(data_compras, colWidths=[55, 115, 100, 100, 50, 84])
                t_compras.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#8D5524")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('TOPPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#FDFBF7")),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E6DCC3')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F6F0')])
                ]))
                elementos.append(t_compras)
                elementos.append(Spacer(1, 5))
                elementos.append(Paragraph(f"<b>Total Gastado en Compras:</b> ${total_gastos_compras:,.2f}", styles['Normal']))
            else:
                elementos.append(Paragraph("No hay registros de compras de insumos disponibles.", styles['Normal']))

            elementos.append(Spacer(1, 15))

            # --- SECCIÓN 3: BALANCE NETO ---
            balance_neto = total_ingresos - total_gastos_compras
            resumen_financiero = f"""
            <b>3. Balance Financiero General:</b><br/>
            • Total Ingresos (Ventas): <b>${total_ingresos:,.2f}</b><br/>
            • Total Egresos (Compras): <b>${total_gastos_compras:,.2f}</b><br/>
            • Balance Neto: <b>${balance_neto:,.2f}</b>
            """
            elementos.append(Paragraph(resumen_financiero, styles['Normal']))

            doc.build(elementos)

            messagebox.showinfo("¡PDF Generado con Éxito!", f"El reporte general se guardó correctamente en:\n📁 /{nombre_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")

    # ================= CONTROL DE MERMAS =================
    def mostrar_mermas(self):
        self.limpiar_contenido()
        self.actualizar_botones_nav("mermas")

        ctk.CTkLabel(self.main_content, text="Control de Merma", font=("Arial", 22, "bold"), text_color="#3E2723").pack(anchor="w", padx=30, pady=(25, 5))
        ctk.CTkLabel(self.main_content, text="Supervisión y registro de producto dañado, caducado o no vendido.", font=("Arial", 13), text_color="gray").pack(anchor="w", padx=30, pady=(0, 15))

        content_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)

        table_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3")
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=5)

        ctk.CTkLabel(table_frame, text="Historial de Mermas Registradas", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(15, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#3E2723", rowheight=28)
        style.configure("Treeview.Heading", background="#E6DCC3", foreground="#5C3A21", font=("Arial", 11, "bold"))

        columns = ("ID", "ID Prod", "Motivo", "Cantidad", "Costo Perdida", "Fecha")
        self.tree_mermas = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        self.tree_mermas.heading("ID", text="ID")
        self.tree_mermas.heading("ID Prod", text="ID Prod")
        self.tree_mermas.heading("Motivo", text="Motivo")
        self.tree_mermas.heading("Cantidad", text="Cant.")
        self.tree_mermas.heading("Costo Perdida", text="Costo Pérdida")
        self.tree_mermas.heading("Fecha", text="Fecha")

        self.tree_mermas.column("ID", width=45, anchor="center")
        self.tree_mermas.column("ID Prod", width=60, anchor="center")
        self.tree_mermas.column("Motivo", width=140, anchor="w")
        self.tree_mermas.column("Cantidad", width=55, anchor="center")
        self.tree_mermas.column("Costo Perdida", width=90, anchor="center")
        self.tree_mermas.column("Fecha", width=110, anchor="center")

        self.tree_mermas.pack(fill="both", expand=True, padx=20, pady=10)

        btn_eliminar_merma = ctk.CTkButton(
            table_frame, 
            text="🗑️ Eliminar Merma Seleccionada", 
            command=self.eliminar_merma, 
            fg_color="#A93226", 
            hover_color="#78281F", 
            height=35, 
            font=("Arial", 12, "bold")
        )
        btn_eliminar_merma.pack(anchor="w", padx=20, pady=(0, 15))

        threading.Thread(target=self.cargar_datos_mermas_async, daemon=True).start()

        form_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3", width=280)
        form_frame.pack(side="right", fill="y", padx=(15, 0), pady=5)
        form_frame.pack_propagate(False)

        ctk.CTkLabel(form_frame, text="Registrar Nueva Merma", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(15, 10))

        self.entry_id_merma = ctk.CTkEntry(form_frame, placeholder_text="ID Manual (ej. 1)", width=240, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_id_merma.pack(padx=20, pady=6)

        self.entry_idprod_merma = ctk.CTkEntry(form_frame, placeholder_text="ID Producto (ej. 1)", width=240, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_idprod_merma.pack(padx=20, pady=6)

        self.entry_motivo_merma = ctk.CTkEntry(form_frame, placeholder_text="Motivo (ej. Pan quemado)", width=240, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_motivo_merma.pack(padx=20, pady=6)

        self.entry_cant_merma = ctk.CTkEntry(form_frame, placeholder_text="Cantidad (ej. 5)", width=240, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_cant_merma.pack(padx=20, pady=6)

        self.entry_costo_merma = ctk.CTkEntry(form_frame, placeholder_text="Costo Pérdida (ej. 50.00)", width=240, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_costo_merma.pack(padx=20, pady=6)

        btn_guardar_merma = ctk.CTkButton(form_frame, text="💾 Guardar Merma", command=self.guardar_merma, fg_color="#8D5524", hover_color="#6F431B", height=38, font=("Arial", 13, "bold"))
        btn_guardar_merma.pack(padx=20, pady=(15, 10))

    def cargar_datos_mermas_async(self):
        try:
            res = supabase.table("merma").select("*").execute()
            def actualizar_ui():
                for item in self.tree_mermas.get_children():
                    self.tree_mermas.delete(item)
                if res.data:
                    for row in res.data:
                        id_m = row.get("idMerma", "")
                        id_prod = row.get("idProducto", "")
                        motivo = row.get("motivo", "")
                        cant = row.get("cantidad", 0)
                        costo = row.get("cost_perdida", 0.0)
                        fecha_raw = row.get("fecha_merma", "")
                        
                        try:
                            dt = datetime.fromisoformat(fecha_raw.replace("Z", "+00:00"))
                            fecha_fmt = dt.strftime("%d/%m/%Y")
                        except Exception:
                            fecha_fmt = fecha_raw
                        
                        self.tree_mermas.insert("", "end", values=(id_m, id_prod, motivo, cant, f"${float(costo):,.2f}", fecha_fmt))
            self.after(0, actualizar_ui)
        except Exception as e:
            print(f"❌ Error al cargar mermas async: {e}")

    def guardar_merma(self):
        id_str = self.entry_id_merma.get().strip()
        idprod_str = self.entry_idprod_merma.get().strip()
        motivo = self.entry_motivo_merma.get().strip()
        cant = self.entry_cant_merma.get().strip()
        costo = self.entry_costo_merma.get().strip()

        if not id_str or not idprod_str or not motivo or not cant or not costo:
            messagebox.showerror("Campos incompletos", "Por favor completa todos los campos de la merma.")
            return

        try:
            supabase.table("merma").insert({
                "idMerma": int(id_str),
                "idProducto": int(idprod_str),
                "motivo": motivo,
                "cantidad": int(cant),
                "cost_perdida": float(costo),
                "fecha_merma": datetime.now().isoformat()
            }).execute()

            messagebox.showinfo("¡Éxito!", "Merma registrada correctamente en Supabase.")
            self.entry_id_merma.delete(0, 'end')
            self.entry_idprod_merma.delete(0, 'end')
            self.entry_motivo_merma.delete(0, 'end')
            self.entry_cant_merma.delete(0, 'end')
            self.entry_costo_merma.delete(0, 'end')
            threading.Thread(target=self.cargar_datos_mermas_async, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la merma:\n{e}")

    def eliminar_merma(self):
        selected_item = self.tree_mermas.selection()
        if not selected_item:
            messagebox.showwarning("Selección requerida", "Por favor selecciona un registro de merma para eliminar.")
            return

        item_data = self.tree_mermas.item(selected_item)
        id_m = item_data['values'][0]

        if messagebox.askyesno("Confirmar Eliminación", "¿Estás segura de eliminar este registro de merma?"):
            try:
                supabase.table("merma").delete().eq("idMerma", id_m).execute()
                messagebox.showinfo("Eliminado", "Registro de merma eliminado con éxito.")
                threading.Thread(target=self.cargar_datos_mermas_async, daemon=True).start()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")
# ==================== COMPRA DE INSUMOS ====================
    def mostrar_compra_insumos(self):
        self.limpiar_contenido()
        self.actualizar_botones_nav("compras")

        # Título del módulo
        ctk.CTkLabel(self.main_content, text="🛒 Registro y Historial de Compras", font=("Arial", 22, "bold"), text_color="#3E2723").pack(anchor="w", padx=30, pady=(20, 5))
        ctk.CTkLabel(self.main_content, text="Registra reabastecimientos de proveedores y actualiza el stock automáticamente.", font=("Arial", 13), text_color="gray").pack(anchor="w", padx=30, pady=(0, 15))

        main_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=5)

        # --- COLUMNA IZQUIERDA: HISTORIAL DE COMPRAS (Tabla + Botones) ---
        left_frame = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        ctk.CTkLabel(left_frame, text="Historial de Reabastecimientos", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(15, 10))

        # Tabla (Treeview) para compras
        columns = ("id", "insumo", "proveedor", "cantidad", "costo_total", "fecha")
        self.tree_compras = ttk.Treeview(left_frame, columns=columns, show="headings", height=11)
        
        self.tree_compras.heading("id", text="ID")
        self.tree_compras.heading("insumo", text="Materia Prima")
        self.tree_compras.heading("proveedor", text="Proveedor")
        self.tree_compras.heading("cantidad", text="Cant. Comprada")
        self.tree_compras.heading("costo_total", text="Costo Total")
        self.tree_compras.heading("fecha", text="Fecha")

        self.tree_compras.column("id", width=35, anchor="center")
        self.tree_compras.column("insumo", width=110, anchor="w")
        self.tree_compras.column("proveedor", width=110, anchor="w")
        self.tree_compras.column("cantidad", width=80, anchor="center")
        self.tree_compras.column("costo_total", width=80, anchor="center")
        self.tree_compras.column("fecha", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree_compras.yview)
        self.tree_compras.configure(yscroll=scrollbar.set)
        
        self.tree_compras.pack(side="top", fill="both", expand=True, padx=15, pady=(0, 10))
        scrollbar.pack(side="right", fill="y")

        # Botones de Acción inferior (Eliminar y Editar)
        btn_acciones_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_acciones_frame.pack(fill="x", padx=15, pady=(0, 15))

        btn_eliminar_compra = ctk.CTkButton(
            btn_acciones_frame, 
            text="🗑️ Eliminar Compra", 
            command=self.eliminar_compra_insumo, 
            fg_color="#A93226", 
            hover_color="#78281F", 
            height=35, 
            font=("Arial", 12, "bold")
        )
        btn_eliminar_compra.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_cargar_editar = ctk.CTkButton(
            btn_acciones_frame, 
            text="✏️ Cargar para Editar", 
            command=self.cargar_compra_para_editar, 
            fg_color="#2980B9", 
            hover_color="#1F618D", 
            height=35, 
            font=("Arial", 12, "bold")
        )
        btn_cargar_editar.pack(side="right", expand=True, fill="x", padx=(5, 0))

        # --- COLUMNA DERECHA: FORMULARIO DE NUEVA / EDITAR COMPRA ---
        right_frame = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3", width=320)
        right_frame.pack(side="right", fill="y", padx=(10, 0), pady=5)
        right_frame.pack_propagate(False)

        self.lbl_titulo_form_compra = ctk.CTkLabel(right_frame, text="Registrar Nueva Compra", font=("Arial", 14, "bold"), text_color="#5C3A21")
        self.lbl_titulo_form_compra.pack(anchor="w", padx=20, pady=(15, 10))

        # ID Oculto para control de edición
        self.id_compra_editando = None

        self.insumos_dict = {}
        
        ctk.CTkLabel(right_frame, text="Seleccionar Insumo:", font=("Arial", 11, "bold"), text_color="#3E2723").pack(anchor="w", padx=20, pady=(5, 2))
        self.combo_insumo_compra = ctk.CTkComboBox(right_frame, values=["Cargando..."], width=280)
        self.combo_insumo_compra.pack(padx=20, pady=(0, 10))

        ctk.CTkLabel(right_frame, text="Proveedor / Empresa:", font=("Arial", 11, "bold"), text_color="#3E2723").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_proveedor = ctk.CTkEntry(right_frame, placeholder_text="ej. Distribuidora San José", width=280)
        self.entry_proveedor.pack(padx=20, pady=(0, 10))

        ctk.CTkLabel(right_frame, text="Cantidad Comprada:", font=("Arial", 11, "bold"), text_color="#3E2723").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_cant_compra = ctk.CTkEntry(right_frame, placeholder_text="ej. 25.0", width=280)
        self.entry_cant_compra.pack(padx=20, pady=(0, 10))

        ctk.CTkLabel(right_frame, text="Costo Total ($):", font=("Arial", 11, "bold"), text_color="#3E2723").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_costo_compra = ctk.CTkEntry(right_frame, placeholder_text="ej. 450.00", width=280)
        self.entry_costo_compra.pack(padx=20, pady=(0, 15))

        # Botón Guardar / Actualizar
        self.btn_guardar_compra_txt = ctk.CTkButton(
            right_frame, 
            text="💾 Guardar y Actualizar Stock", 
            fg_color="#8D5524", 
            hover_color="#5C3A21", 
            font=("Arial", 12, "bold"), 
            height=38,
            command=self.guardar_compra_insumo
        )
        self.btn_guardar_compra_txt.pack(padx=20, pady=5, fill="x")

        self.btn_cancelar_edit = ctk.CTkButton(
            right_frame, 
            text="❌ Cancelar Edición", 
            fg_color="#7F8C8D", 
            hover_color="#515A5A", 
            font=("Arial", 11, "bold"), 
            height=30,
            command=self.resetear_formulario_compra
        )

        threading.Thread(target=self.cargar_datos_compras_async, daemon=True).start()

    def cargar_datos_compras_async(self):
        nombres_insumos = []
        self.insumos_dict = {}
        compras_data = []

        try:
            res_mat = supabase.table("materia prima").select("id_Mat_Prim, nom_pro").execute()
            if res_mat.data:
                for row in res_mat.data:
                    nom = row.get("nom_pro", "")
                    id_m = row.get("id_Mat_Prim")
                    if nom:
                        nombres_insumos.append(nom)
                        self.insumos_dict[nom] = id_m
        except Exception as e:
            print(f"Error cargando materia prima: {e}")

        try:
            res_compras = supabase.table("det_compra_insumo").select("idCompra, cant, subtot, id_Mat_Prim, comprainsumo(fecha_com, proveedor)").execute()
            if res_compras.data:
                compras_data = res_compras.data
        except Exception as e:
            print(f"Error cargando detalle compras: {e}")

        def actualizar_gui():
            if nombres_insumos:
                self.combo_insumo_compra.configure(values=nombres_insumos)
                if not self.combo_insumo_compra.get() or self.combo_insumo_compra.get() == "Cargando...":
                    self.combo_insumo_compra.set(nombres_insumos[0])
            else:
                self.combo_insumo_compra.configure(values=["Sin insumos registrados"])
                self.combo_insumo_compra.set("Sin insumos registrados")

            for item in self.tree_compras.get_children():
                self.tree_compras.delete(item)

            for c in compras_data:
                id_c = c.get("idCompra", "")
                id_mat = c.get("id_Mat_Prim")
                
                nom_ins = "Insumo"
                for nombre, id_m in self.insumos_dict.items():
                    if id_m == id_mat:
                        nom_ins = nombre
                        break

                compra_info = c.get("comprainsumo")
                proveedor_val = "Proveedor General"
                fecha_raw = ""
                
                if isinstance(compra_info, dict):
                    proveedor_val = compra_info.get("proveedor") or "Proveedor General"
                    fecha_raw = compra_info.get("fecha_com", "")

                try:
                    dt = datetime.fromisoformat(fecha_raw.replace("Z", "+00:00"))
                    fecha = dt.strftime("%d/%m/%Y %I:%M %p")
                except Exception:
                    fecha = fecha_raw if fecha_raw else "Reciente"

                cant = c.get("cant", 0)
                subtot = c.get("subtot", 0.0)

                self.tree_compras.insert("", "end", values=(
                    id_c, nom_ins, proveedor_val, cant, f"${float(subtot):,.2f}", fecha
                ))

        self.after(0, actualizar_gui)

    def guardar_compra_insumo(self):
        insumo_nom = self.combo_insumo_compra.get()
        proveedor = self.entry_proveedor.get().strip()
        cant_str = self.entry_cant_compra.get().strip()
        costo_str = self.entry_costo_compra.get().strip()

        if not cant_str or not costo_str or insumo_nom == "Sin insumos registrados":
            messagebox.showwarning("Atención", "Por favor completa la cantidad y el costo total.")
            return

        try:
            cant_comprada = float(cant_str)
            costo_total = float(costo_str)
            costo_unitario = costo_total / cant_comprada if cant_comprada > 0 else 0.0
            id_insumo = self.insumos_dict.get(insumo_nom)
            proveedor_final = proveedor if proveedor else "Proveedor General"

            if self.id_compra_editando is None:
                # --- MODO CREAR NUEVA COMPRA ---
                res_cabecera = supabase.table("comprainsumo").insert({
                    "tot_compra": costo_total,
                    "proveedor": proveedor_final,
                    "fecha_com": datetime.now().isoformat()
                }).execute()

                if res_cabecera.data:
                    id_compra_creada = res_cabecera.data[0].get("idCompra")
                else:
                    res_ult = supabase.table("comprainsumo").select("idCompra").order("idCompra", desc=True).limit(1).execute()
                    id_compra_creada = res_ult.data[0].get("idCompra") if res_ult.data else 1

                supabase.table("det_compra_insumo").insert({
                    "idCompra": id_compra_creada,
                    "id_Mat_Prim": id_insumo,
                    "cant": cant_comprada,
                    "cost_unit": costo_unitario,
                    "subtot": costo_total
                }).execute()

                # Sumar al stock actual
                res_actual = supabase.table("materia prima").select("stock_act").eq("id_Mat_Prim", id_insumo).execute()
                if res_actual.data:
                    stock_previo = float(res_actual.data[0].get("stock_act", 0))
                    supabase.table("materia prima").update({"stock_act": stock_previo + cant_comprada}).eq("id_Mat_Prim", id_insumo).execute()

                messagebox.showinfo("Éxito", f"Compra registrada.\nSe sumaron {cant_comprada} al stock de {insumo_nom}.")

            else:
                # --- MODO EDITAR COMPRA EXISTENTE ---
                id_c = self.id_compra_editando

                res_det_ant = supabase.table("det_compra_insumo").select("cant, id_Mat_Prim").eq("idCompra", id_c).execute()
                if res_det_ant.data:
                    cant_anterior = float(res_det_ant.data[0].get("cant", 0))
                    id_mat_ant = res_det_ant.data[0].get("id_Mat_Prim")

                    res_st = supabase.table("materia prima").select("stock_act").eq("id_Mat_Prim", id_mat_ant).execute()
                    if res_st.data:
                        stock_actual_bd = float(res_st.data[0].get("stock_act", 0))
                        stock_corregido = (stock_actual_bd - cant_anterior) + cant_comprada
                        supabase.table("materia prima").update({"stock_act": stock_corregido}).eq("id_Mat_Prim", id_mat_ant).execute()

                supabase.table("comprainsumo").update({
                    "tot_compra": costo_total,
                    "proveedor": proveedor_final
                }).eq("idCompra", id_c).execute()

                supabase.table("det_compra_insumo").update({
                    "id_Mat_Prim": id_insumo,
                    "cant": cant_comprada,
                    "cost_unit": costo_unitario,
                    "subtot": costo_total
                }).eq("idCompra", id_c).execute()

                messagebox.showinfo("Éxito", "Compra actualizada correctamente.")
                self.resetear_formulario_compra()

            self.entry_proveedor.delete(0, "end")
            self.entry_cant_compra.delete(0, "end")
            self.entry_costo_compra.delete(0, "end")

            threading.Thread(target=self.cargar_datos_compras_async, daemon=True).start()

        except ValueError:
            messagebox.showerror("Error", "La cantidad y el costo deben ser valores numéricos válidos.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la compra:\n{e}")

    def cargar_compra_para_editar(self):
        selected_item = self.tree_compras.selection()
        if not selected_item:
            messagebox.showwarning("Selección requerida", "Por favor selecciona una compra del historial para editar.")
            return

        item_data = self.tree_compras.item(selected_item)
        valores = item_data['values']
        
        id_c = valores[0]
        insumo_nom = valores[1]
        proveedor = valores[2]
        cantidad = valores[3]
        costo_total = valores[4].replace("$", "").replace(",", "")

        self.id_compra_editando = id_c
        self.lbl_titulo_form_compra.configure(text=f"Editando Compra ID: {id_c}")
        self.btn_guardar_compra_txt.configure(text="💾 Actualizar Cambios", fg_color="#2980B9", hover_color="#1F618D")
        self.btn_cancelar_edit.pack(padx=20, pady=(0, 10), fill="x")

        self.combo_insumo_compra.set(insumo_nom)
        self.entry_proveedor.delete(0, "end")
        self.entry_proveedor.insert(0, proveedor if proveedor != "Proveedor General" else "")
        
        self.entry_cant_compra.delete(0, "end")
        self.entry_cant_compra.insert(0, str(cantidad))
        
        self.entry_costo_compra.delete(0, "end")
        self.entry_costo_compra.insert(0, str(costo_total))

    def resetear_formulario_compra(self):
        self.id_compra_editando = None
        self.lbl_titulo_form_compra.configure(text="Registrar Nueva Compra")
        self.btn_guardar_compra_txt.configure(text="💾 Guardar y Actualizar Stock", fg_color="#8D5524", hover_color="#5C3A21")
        self.btn_cancelar_edit.pack_forget()

        self.entry_proveedor.delete(0, "end")
        self.entry_cant_compra.delete(0, "end")
        self.entry_costo_compra.delete(0, "end")

    def eliminar_compra_insumo(self):
        selected_item = self.tree_compras.selection()
        if not selected_item:
            messagebox.showwarning("Selección requerida", "Por favor selecciona una compra del historial para eliminar.")
            return

        item_data = self.tree_compras.item(selected_item)
        id_c = item_data['values'][0]
        insumo_nom = item_data['values'][1]

        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de eliminar la compra ID {id_c} de {insumo_nom}?\n(Esto descontará la cantidad del stock actual)."):
            try:
                res_det = supabase.table("det_compra_insumo").select("cant, id_Mat_Prim").eq("idCompra", id_c).execute()
                if res_det.data:
                    cant_a_descontar = float(res_det.data[0].get("cant", 0))
                    id_mat = res_det.data[0].get("id_Mat_Prim")

                    res_st = supabase.table("materia prima").select("stock_act").eq("id_Mat_Prim", id_mat).execute()
                    if res_st.data:
                        stock_actual = float(res_st.data[0].get("stock_act", 0))
                        nuevo_stock = max(0.0, stock_actual - cant_a_descontar)
                        supabase.table("materia prima").update({"stock_act": nuevo_stock}).eq("id_Mat_Prim", id_mat).execute()

                supabase.table("det_compra_insumo").delete().eq("idCompra", id_c).execute()
                supabase.table("comprainsumo").delete().eq("idCompra", id_c).execute()

                messagebox.showinfo("Eliminado", "Compra eliminada y stock actualizado correctamente.")
                self.resetear_formulario_compra()
                threading.Thread(target=self.cargar_datos_compras_async, daemon=True).start()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la compra:\n{e}")

    def mostrar_turnos_stock(self):
        self.limpiar_contenido()
        self.actualizar_botones_nav("turnos")

        modulo_turnos = TurnosModuloFrame(self.main_content, supabase)
        modulo_turnos.pack(fill="both", expand=True)

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas salir del sistema?"):
            self.destroy()



if __name__ == "__main__":
    app = AdminDashboard("Dueño (Admin)")
    app.mainloop()