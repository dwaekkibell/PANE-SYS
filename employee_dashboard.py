import os
import customtkinter as ctk
import uuid
from tkinter import messagebox, ttk
from supabase import create_client, Client
from datetime import datetime, timedelta
from PIL import Image

from turno_modal import VentanaTurnoModal
from cobro_modal import VentanaCobroModal
from cierre_turno_modal import CierreTurnoModal
from empleado_panel_widget import EmpleadoPanelWidget
from cancelar_venta_modal import VentanaAutorizacionAdmin

SUPABASE_URL = "https://ksymuaamkjzoehupdcdp.supabase.co"
SUPABASE_KEY = "sb_publishable_Mdq1uUvlrQikfraqcZ7vDw_dhGeeBW2"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class EmployeeDashboard(ctk.CTk):
    def __init__(self, nombre_usuario, id_usuario=2):
        super().__init__()
        self.supabase = supabase
        self.title("PANE-SYS - Panel de Empleado (Punto de Venta)")
        self.geometry("1200x740")
        self.resizable(False, False)
        self.configure(fg_color="#FDFBF7")

        self.nombre_usuario = nombre_usuario
        self.id_usuario = id_usuario
        self.id_turno_actual = None
        self.nombre_turno_actual = "Sin Turno Activo"
        self.carrito = []
        self.imagenes_referencias = []

        # --- MENÚ LATERAL (Sidebar) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#5C3A21")
        self.sidebar_frame.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text=f"🍞 PANE-SYS\n({nombre_usuario})", 
            font=("Arial", 15, "bold"), 
            text_color="#FDFBF7"
        )
        self.logo_label.pack(pady=(30, 20))

        self.btn_pos = ctk.CTkButton(self.sidebar_frame, text="🛒 Punto de Venta (POS)", command=self.mostrar_pos, fg_color="#8D5524", hover_color="#6F431B", height=40, font=("Arial", 13))
        self.btn_pos.pack(fill="x", padx=15, pady=10)

        self.btn_historial = ctk.CTkButton(self.sidebar_frame, text="📋 Mis Ventas del Turno", command=self.mostrar_historial, fg_color="transparent", hover_color="#6F431B", height=40, font=("Arial", 13))
        self.btn_historial.pack(fill="x", padx=15, pady=10)

        self.btn_cerrar_turno = ctk.CTkButton(self.sidebar_frame, text="🛑 Cerrar Turno Actual", command=self.cerrar_turno_actual, fg_color="#C0392B", hover_color="#922B21", height=35, font=("Arial", 12))
        self.btn_cerrar_turno.pack(fill="x", padx=15, pady=5)

        self.btn_logout = ctk.CTkButton(self.sidebar_frame, text="🚪 Cerrar Sesión", command=self.cerrar_sesion, fg_color="#A93226", hover_color="#78281F", height=40, font=("Arial", 13))
        self.btn_logout.pack(side="bottom", fill="x", padx=15, pady=20)

        # --- ÁREA DE CONTENIDO PRINCIPAL ---
        self.main_content = ctk.CTkFrame(self, fg_color="#FDFBF7", corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True)

        self.after(100, self.verificar_o_crear_turno)

    def verificar_o_crear_turno(self):
        try:
            res = supabase.table("turno").select("*").eq("idusuario", self.id_usuario).order("idturno", desc=True).limit(1).execute()
            
            if res.data:
                ultimo_turno = res.data[0]
                h_inicio_str = ultimo_turno.get("hora_inicio")
                h_fin_str = ultimo_turno.get("hora_fin")
                
                dt_inicio = datetime.fromisoformat(h_inicio_str.replace("Z", "+00:00")).replace(tzinfo=None)
                dt_fin = datetime.fromisoformat(h_fin_str.replace("Z", "+00:00")).replace(tzinfo=None)
                ahora = datetime.now()

                if ahora < dt_fin:
                    self.id_turno_actual = ultimo_turno.get("idturno") or ultimo_turno.get("id")
                    tipo = ultimo_turno.get("nombre_turno", "Turno")
                    self.nombre_turno_actual = f"{tipo} ({dt_inicio.strftime('%I:%M %p')} - {dt_fin.strftime('%I:%M %p')})"
                    self.mostrar_pos()
                    return

            self.abrir_modal_turno()
        except Exception as e:
            print(f"Error al verificar turno: {e}")
            self.abrir_modal_turno()

    def abrir_modal_turno(self):
        VentanaTurnoModal(self, supabase, self.id_usuario, self.on_turno_iniciado)

    def on_turno_iniciado(self, id_turno, nombre_formateado):
        self.id_turno_actual = id_turno
        self.nombre_turno_actual = nombre_formateado
        messagebox.showinfo("¡Turno Iniciado!", f"Turno configurado con éxito:\n{nombre_formateado}")
        self.mostrar_pos()

    def cerrar_turno_actual(self):
        if not hasattr(self, 'id_turno_actual') or not self.id_turno_actual:
            messagebox.showwarning("Aviso", "No tienes ningún turno activo en este momento.")
            return

        CierreTurnoModal(
            parent=self,
            id_turno_actual=self.id_turno_actual,
            id_usuario=self.id_usuario,
            supabase_client=supabase,
            callback_cierre_exito=self.despues_de_cerrar_turno
        )

    def despues_de_cerrar_turno(self):
        self.id_turno_actual = None
        self.nombre_turno_actual = None
        self.destroy()

    def limpiar_contenido(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def actualizar_botones_nav(self, activo):
        self.btn_pos.configure(fg_color="#8D5524" if activo == "pos" else "transparent")
        self.btn_historial.configure(fg_color="#8D5524" if activo == "historial" else "transparent")

    # ================= 1. PUNTO DE VENTA (POS) =================
    def mostrar_pos(self):
        if not self.id_turno_actual:
            return

        self.limpiar_contenido()
        self.actualizar_botones_nav("pos")
        self.carrito = []
        self.imagenes_referencias = []

        self.panel_empleado = EmpleadoPanelWidget(self.main_content, supabase, id_turno_actual=self.id_turno_actual)
        self.panel_empleado.pack(fill="x", padx=25, pady=(20, 10))

        pos_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        pos_container.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        left_panel = ctk.CTkFrame(pos_container, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))

        # Título y Buscador Rápido
        top_left_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        top_left_frame.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(top_left_frame, text="Catálogo de Productos", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(side="left")

        # Campo de Búsqueda en tiempo real
        self.entry_buscar_pos = ctk.CTkEntry(
            top_left_frame, 
            placeholder_text="🔍 Buscar producto...", 
            width=180, 
            height=30,
            fg_color="#F9F6F0",
            border_color="#D7CCC8"
        )
        self.entry_buscar_pos.pack(side="right")
        self.entry_buscar_pos.bind("<KeyRelease>", lambda event: self.cargar_tarjetas_productos(self.entry_buscar_pos.get()))

        self.scroll_productos = ctk.CTkScrollableFrame(left_panel, fg_color="transparent", width=550, height=450)
        self.scroll_productos.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_tarjetas_productos()

        right_panel = ctk.CTkFrame(pos_container, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3", width=340)
        right_panel.pack(side="right", fill="y", padx=(0, 0))
        right_panel.pack_propagate(False)

        ctk.CTkLabel(right_panel, text="🛒 Ticket de Venta", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(15, 10))

        self.scroll_ticket = ctk.CTkScrollableFrame(right_panel, fg_color="#F9F6F0", corner_radius=10, width=300, height=340)
        self.scroll_ticket.pack(padx=20, pady=10)

        total_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        total_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(total_frame, text="TOTAL:", font=("Arial", 16, "bold"), text_color="#3E2723").pack(side="left")
        self.lbl_total_ticket = ctk.CTkLabel(total_frame, text="$0.00", font=("Arial", 20, "bold"), text_color="#27AE60")
        self.lbl_total_ticket.pack(side="right")

        btn_pagar = ctk.CTkButton(
            right_panel, 
            text="✅ Confirmar y Cobrar Venta", 
            command=self.confirmar_venta_pos, 
            fg_color="#27AE60", 
            hover_color="#1E8449", 
            height=45, 
            font=("Arial", 14, "bold")
        )
        btn_pagar.pack(fill="x", padx=20, pady=(10, 20))

    def cargar_tarjetas_productos(self, filtro=""):
        for widget in self.scroll_productos.winfo_children():
            widget.destroy()

        try:
            stock_turno_dict = {}
            if hasattr(self, 'id_turno_actual') and self.id_turno_actual:
                res_det = supabase.table("detalle_turno").select("idproducto, cantidad").eq("idturno", self.id_turno_actual).execute()
                if res_det.data:
                    for d in res_det.data:
                        stock_turno_dict[d.get("idproducto")] = d.get("cantidad", 0)

            res = supabase.table("producto").select("*").execute()
            if res.data:
                row_idx = 0
                col_idx = 0
                filtro_lower = filtro.strip().lower()

                for prod in res.data:
                    nombre = prod.get("nombre", "Sin nombre")
                    descripcion = prod.get("descripcion", "")
                    
                    if filtro_lower and filtro_lower not in nombre.lower() and filtro_lower not in descripcion.lower():
                        continue

                    precio = prod.get("precio_vent", 0.0)
                    
                    pid = prod.get("idProducto") or prod.get("idproducto") or prod.get("id")
                    
                    stock = stock_turno_dict.get(pid, 0)

                    datos_producto = prod.copy()
                    datos_producto["stock"] = stock

                    card = ctk.CTkFrame(self.scroll_productos, fg_color="#FDFBF7", corner_radius=12, border_width=1, border_color="#D7CCC8", width=175, height=235)
                    card.grid(row=row_idx, column=col_idx, padx=8, pady=8)
                    card.pack_propagate(False)

                    img_widget = None
                    nombre_img = f"{nombre.lower().replace(' ', '_')}.png"
                    ruta_img = os.path.join("images", nombre_img)

                    if os.path.exists(ruta_img):
                        try:
                            pil_img = Image.open(ruta_img).resize((65, 65))
                            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(65, 65))
                            self.imagenes_referencias.append(ctk_img)
                            img_widget = ctk.CTkLabel(card, image=ctk_img, text="")
                        except Exception:
                            pass

                    if img_widget is None:
                        img_widget = ctk.CTkLabel(card, text="🥐", font=("Arial", 26))

                    img_widget.pack(pady=(6, 2))

                    ctk.CTkLabel(card, text=nombre, font=("Arial", 12, "bold"), text_color="#3E2723").pack()
                    ctk.CTkLabel(card, text=descripcion, font=("Arial", 10), text_color="gray", wraplength=160).pack()
                    ctk.CTkLabel(card, text=f"${float(precio):,.2f}", font=("Arial", 12, "bold"), text_color="#27AE60").pack(pady=1)
                    ctk.CTkLabel(card, text=f"Stock: {stock}", font=("Arial", 10), text_color="#7E5109").pack(pady=(0, 4))

                    btn_add = ctk.CTkButton(
                    card, 
                    text="+ Agregar", 
                    command=lambda p=datos_producto: self.agregar_al_carrito(p),
                    fg_color="#8D5524", 
                    hover_color="#6F431B", 
                    height=26, 
                    font=("Arial", 11, "bold")
                    )
                    btn_add.pack(pady=(0, 6))

                    col_idx += 1
                    if col_idx > 2:
                        col_idx = 0
                        row_idx += 1
        except Exception as e:
            print(f"Error al cargar tarjetas de productos: {e}")

    def agregar_al_carrito(self, producto):
        item_carrito = producto.copy()
        item_carrito["cart_item_id"] = str(uuid.uuid4())
        
        precio_val = float(item_carrito.get("precio_vent") or item_carrito.get("precio", 0.0))
        item_carrito["precio"] = precio_val
        item_carrito["precio_vent"] = precio_val

        stock_disponible = int(item_carrito.get("stock", 0))
        if stock_disponible <= 0:
            messagebox.showwarning("Sin Stock", f"Lo sentimos, ya no hay piezas disponibles de este producto para este turno.", parent=self)
            return  

        id_actual = item_carrito.get("idProducto") or item_carrito.get("idproducto") or item_carrito.get("id")
        
        piezas_en_carrito = 0
        for item in self.carrito:
            id_item_en_carrito = item.get("idProducto") or item.get("idproducto") or item.get("id")
            if id_item_en_carrito == id_actual:
                piezas_en_carrito += 1

        if piezas_en_carrito >= stock_disponible:
            messagebox.showwarning("Stock Insufficiente", f"Has alcanzado el límite de stock disponible ({stock_disponible} pzas) para este producto en este turno.", parent=self)
            return

        self.carrito.append(item_carrito)
        self.actualizar_vista_ticket()

    def quitar_del_carrito(self, cart_item_id):
        # Filtramos la lista para remover únicamente el ítem con ese identificador único
        self.carrito = [item for item in self.carrito if item["cart_item_id"] != cart_item_id]
        self.actualizar_vista_ticket()

    def actualizar_vista_ticket(self):
        for widget in self.scroll_ticket.winfo_children():
            widget.destroy()

        total = 0.0
        for item in self.carrito:
            precio = float(item.get("precio_vent", 0.0))
            total += precio
            item_frame = ctk.CTkFrame(self.scroll_ticket, fg_color="transparent")
            item_frame.pack(fill="x", padx=5, pady=4)

            # Nombre y Precio del producto
            ctk.CTkLabel(item_frame, text=item["nombre"], font=("Arial", 12), text_color="#3E2723").pack(side="left")
            
            # Botón para eliminar este ítem específico
            btn_quitar = ctk.CTkButton(
                item_frame, 
                text="❌", 
                width=24, 
                height=24, 
                fg_color="transparent", 
                hover_color="#FADBD8", 
                text_color="#C0392B",
                font=("Arial", 10, "bold"),
                command=lambda cid=item["cart_item_id"]: self.quitar_del_carrito(cid)
            )
            btn_quitar.pack(side="right", padx=(5, 0))

            ctk.CTkLabel(item_frame, text=f"${precio:,.2f}", font=("Arial", 12, "bold"), text_color="#5C3A21").pack(side="right")

        self.lbl_total_ticket.configure(text=f"${total:,.2f}")

    def confirmar_venta_pos(self):
     if not self.carrito:
         messagebox.showwarning("Ticket Vacío", "Por favor selecciona al menos un producto para realizar la venta.")
         return

     total_venta = sum([item["precio"] for item in self.carrito])
     VentanaCobroModal(
         parent=self, 
         total_venta=total_venta, 
         id_usuario=self.id_usuario, 
         id_turno_actual=self.id_turno_actual, 
         supabase=supabase, 
         carrito=self.carrito, 
         on_cobro_exito=self.al_completar_cobro
     )

    def al_completar_cobro(self):
     self.carrito = []
     self.actualizar_vista_ticket()
     self.cargar_tarjetas_productos()

    # ================= 2. MIS VENTAS DEL TURNO =================
    def mostrar_historial(self):
        if not self.id_turno_actual:
            messagebox.showwarning("Turno Requerido", "Debes configurar tu turno actual para ver las ventas asociadas.")
            self.abrir_modal_turno()
            return

        self.limpiar_contenido()
        self.actualizar_botones_nav("historial")

        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 5))
        ctk.CTkLabel(header_frame, text="Historial de Ventas del Turno", font=("Arial", 22, "bold"), text_color="#3E2723").pack(side="left")

        filter_frame = ctk.CTkFrame(self.main_content, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E6DCC3")
        filter_frame.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(filter_frame, text="📅 Filtrar periodo:", font=("Arial", 12, "bold"), text_color="#5C3A21").pack(side="left", padx=15, pady=10)
        
        self.combo_filtro_historial = ctk.CTkComboBox(
            filter_frame, 
            values=["Todos", "Hoy", "Esta Semana"], 
            command=self.aplicar_filtro_historial,
            width=160,
            fg_color="#F9F6F0",
            border_color="#D7CCC8"
        )
        self.combo_filtro_historial.pack(side="left", padx=5, pady=10)
        self.combo_filtro_historial.set("Todos")

        table_frame = ctk.CTkFrame(self.main_content, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3")
        table_frame.pack(fill="both", expand=True, padx=30, pady=10)

        btn_cancelar_venta = ctk.CTkButton(
            table_frame, 
            text="❌ Cancelar Venta Seleccionada", 
            command=self.pedir_cancelacion_venta,
            fg_color="#C0392B", 
            hover_color="#962D22", 
            height=38, 
            font=("Arial", 12, "bold")
        )
        btn_cancelar_venta.pack(side="bottom", fill="x", padx=20, pady=15)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#3E2723", rowheight=28)
        style.configure("Treeview.Heading", background="#E6DCC3", foreground="#5C3A21", font=("Arial", 11, "bold"))

        columns = ("ID Venta", "Fecha y Hora", "Turno", "Total")
        self.tree_mis_ventas = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        self.tree_mis_ventas.heading("ID Venta", text="ID Venta")
        self.tree_mis_ventas.heading("Fecha y Hora", text="Fecha / Hora")
        self.tree_mis_ventas.heading("Turno", text="Turno Registrado")
        self.tree_mis_ventas.heading("Total", text="Total Venta")

        self.tree_mis_ventas.column("ID Venta", width=80, anchor="center")
        self.tree_mis_ventas.column("Fecha y Hora", width=220, anchor="center")
        self.tree_mis_ventas.column("Turno", width=180, anchor="center")
        self.tree_mis_ventas.column("Total", width=110, anchor="center")

        self.tree_mis_ventas.pack(side="top", fill="both", expand=True, padx=20, pady=(15, 0))

        try:
            res = self.supabase.table("venta").select("*").eq("idturno", self.id_turno_actual).execute()
            if res.data:
                for venta in res.data:
                    id_v = venta.get("idVenta") or venta.get("idventa") or venta.get("id")
                    fecha = venta.get("fecha_vent", "")
                    total = float(venta.get("total_vent", 0.0))
                    self.tree_mis_ventas.insert("", "end", values=(id_v, fecha, "Turno Actual", f"${total:,.2f}"))
        except Exception as e:
            print(f"Error al cargar historial: {e}")

    def pedir_cancelacion_venta(self):
            seleccion = self.tree_mis_ventas.selection()
            if not seleccion:
                messagebox.showwarning("Selección Requerida", "Por favor seleccione una venta de la lista para cancelar.")
                return
        
            item_data = self.tree_mis_ventas.item(seleccion)
            valores = item_data.get("values")
                
            if valores:
                id_venta_a_cancelar = valores[0] # El ID Venta es la primera columna
        
                from cancelar_venta_modal import VentanaAutorizacionAdmin
                VentanaAutorizacionAdmin(
                    parent=self,
                    supabase=self.supabase,
                    id_venta_a_cancelar=id_venta_a_cancelar,
                    on_exito=self.cargar_mis_ventas 
                    )

        # --- BOTÓN PARA CANCELAR VENTA SELECCIONADA ---
            btn_cancelar_venta = ctk.CTkButton(
                    table_frame, 
                    text="❌ Cancelar Venta Seleccionada", 
                    command=self.pedir_cancelacion_venta,
                    fg_color="#C0392B", 
                    hover_color="#962D22", 
                    height=38, 
                    font=("Arial", 12, "bold")
                    )
            btn_cancelar_venta.pack(pady=(0, 15), padx=20, anchor="e")

    def aplicar_filtro_historial(self, choice):
        self.cargar_mis_ventas()

    def cargar_mis_ventas(self):
        if not hasattr(self, "tree_mis_ventas") or self.tree_mis_ventas is None:
            return

        for item in self.tree_mis_ventas.get_children():
            self.tree_mis_ventas.delete(item)

        try:
            from datetime import datetime, timedelta

            filtro = "Todos"
            if hasattr(self, "combo_filtro_historial") and self.combo_filtro_historial:
                filtro = self.combo_filtro_historial.get()

            res = self.supabase.table("venta").select("*").order("fecha_vent", desc=True).execute()
            
            res_turnos = self.supabase.table("turno").select("*").execute()
            mapa_turnos = {}
            if res_turnos.data:
                for t in res_turnos.data:
                    tid = t.get("idturno") or t.get("idTurno") or t.get("id")
                    nombre_real = t.get("nombre_turno") or f"Turno {tid}"
                    mapa_turnos[tid] = nombre_real

            if res.data:
                hoy = datetime.now().date()
                inicio_semana = hoy - timedelta(days=hoy.weekday())

                for venta in res.data:
                    id_v = venta.get("idVenta") or venta.get("idventa") or venta.get("id")
                    fecha_raw = venta.get("fecha_vent", "")
                    total = float(venta.get("total_vent", 0.0))
                    id_turno_v = venta.get("idturno")

                    # Formatear fecha
                    fecha_formateada = fecha_raw
                    fecha_obj = None
                    try:
                        if "T" in fecha_raw:
                            dt_str = fecha_raw.split(".")[0].replace("T", " ")
                            fecha_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            fecha_formateada = fecha_obj.strftime("%d/%m/%Y %I:%M %p")
                    except Exception:
                        pass

                    if fecha_obj and filtro != "Todos":
                        fecha_venta_date = fecha_obj.date()
                        if filtro == "Hoy":
                            if fecha_venta_date != hoy:
                                continue
                        elif filtro == "Esta Semana":
                            if fecha_venta_date < inicio_semana or fecha_venta_date > hoy:
                                continue

                    nombre_turno_final = mapa_turnos.get(id_turno_v, f"Turno ID: {id_turno_v}")

                    self.tree_mis_ventas.insert(
                        "", 
                        "end", 
                        values=(id_v, fecha_formateada, nombre_turno_final, f"${total:,.2f}")
                    )
        except Exception as e:
            print(f"Error al cargar historial: {e}")

    def cerrar_sesion(self):
        if hasattr(self, 'id_turno_actual') and self.id_turno_actual:
            try:
                supabase.table("turno").update({
                    "hora_fin": datetime.now().isoformat()
                }).eq("idturno", self.id_turno_actual).execute()
            except Exception as e:
                print(f"Error al cerrar el turno automáticamente: {e}")

        self.destroy()

if __name__ == "__main__":
    app = EmployeeDashboard("Cajero 1", id_usuario=2)
    app.mainloop()