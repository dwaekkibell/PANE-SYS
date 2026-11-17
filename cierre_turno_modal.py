import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class CierreTurnoModal(ctk.CTkToplevel):
    def __init__(self, parent, id_turno_actual, id_usuario, supabase_client, callback_cierre_exito):
        super().__init__(parent)
        self.title("PANE-SYS - Cierre de Turno y Corte de Caja")
        self.geometry("460x580")
        self.resizable(False, False)
        self.configure(fg_color="#FDFBF7")
        
        # Ventana modal de bloqueo
        self.transient(parent)
        self.grab_set()

        self.id_turno = id_turno_actual
        self.id_usuario = id_usuario
        self.supabase = supabase_client
        self.callback_exito = callback_cierre_exito

        self.fondo_caja = 0.0
        self.total_ventas = 0.0
        self.cantidad_transacciones = 0
        self.resumen_inventario = []

        # Títulos
        ctk.CTkLabel(self, text="📋 Corte de Caja y Cierre de Turno", font=("Arial", 18, "bold"), text_color="#3E2723").pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Resumen de operaciones del turno actual:", font=("Arial", 12), text_color="gray").pack(pady=(0, 10))

        self.scroll_resumen = ctk.CTkScrollableFrame(self, fg_color="#FFFFFF", corner_radius=10, height=380, border_width=1, border_color="#E6DCC3")
        self.scroll_resumen.pack(fill="x", padx=20, pady=5)

        # Botón de confirmación
        self.btn_cerrar = ctk.CTkButton(
            self, 
            text="🔒 Confirmar Cierre y Finalizar Turno", 
            command=self.procesar_cierre_turno, 
            fg_color="#C0392B", 
            hover_color="#962D22", 
            height=42, 
            font=("Arial", 13, "bold")
        )
        self.btn_cerrar.pack(fill="x", padx=20, pady=(15, 20))

        self.cargar_datos_corte()

    def cargar_datos_corte(self):
        try:
            res_turno = self.supabase.table("turno").select("*").eq("idturno", self.id_turno).execute()
            if res_turno.data:
                t_data = res_turno.data[0]
                self.fondo_caja = float(t_data.get("fondo_caja", 0.0))
                nombre_turno = t_data.get("nombre_turno", "Turno Activo")
            else:
                nombre_turno = "Turno Activo"

            res_ventas = self.supabase.table("venta").select("*").eq("idturno", self.id_turno).execute()
            ventas_lista = res_ventas.data if res_ventas.data else []
            self.cantidad_transacciones = len(ventas_lista)
            self.total_ventas = sum(float(v.get("total_vent", 0.0)) for v in ventas_lista)

            ids_ventas = [v.get("idVenta") or v.get("idventa") or v.get("id") for v in ventas_lista]
            
            vendidos_dict = {}
            if ids_ventas:
                res_det_v = self.supabase.table("detalleventa").select("*").in_("idVenta", ids_ventas).execute()
                if res_det_v.data:
                    for dv in res_det_v.data:
                        pid = dv.get("idProducto") or dv.get("idproducto")
                        cant = int(dv.get("cantidad", 0))
                        vendidos_dict[pid] = vendidos_dict.get(pid, 0) + cant

            res_det_t = self.supabase.table("detalle_turno").select("*").eq("idturno", self.id_turno).execute()
            det_actual = res_det_t.data if res_det_t.data else []

            res_prod = self.supabase.table("producto").select("*").execute()
            nombres_prod = {}
            if res_prod.data:
                for p in res_prod.data:
                    pid_val = p.get("idProducto") or p.get("idproducto") or p.get("id")
                    p_nombre = p.get("nombre") or p.get("nombre_producto") or "Producto"
                    nombres_prod[pid_val] = p_nombre

            for det in det_actual:
                pid = det.get("idproducto") or det.get("idProducto")
                stock_restante = int(det.get("cantidad", 0))
                vendido = vendidos_dict.get(pid, 0)
                inicial = stock_restante + vendido
                nombre_pan = nombres_prod.get(pid, f"Prod ID {pid}")
                
                self.resumen_inventario.append({
                    "nombre": nombre_pan,
                    "inicial": inicial,
                    "vendido": vendido,
                    "restante": stock_restante
                })

            self.construir_interfaz_resumen(nombre_turno)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo calcular el corte de caja:\n{e}", parent=self)
            self.destroy()

    def construir_interfaz_resumen(self, nombre_turno):
        for widget in self.scroll_resumen.winfo_children():
            widget.destroy()

        # --- SECCIÓN 1: REPORTE FINANCIERO ---
        ctk.CTkLabel(self.scroll_resumen, text=f"📊 Reporte Financiero ({nombre_turno})", font=("Arial", 13, "bold"), text_color="#5C3A21").pack(anchor="w", padx=10, pady=(10, 5))
        
        frame_fin = ctk.CTkFrame(self.scroll_resumen, fg_color="#FDFBF7", corner_radius=8, border_width=1, border_color="#E6DCC3")
        frame_fin.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_fin, text=f"Fondo de Caja Inicial: ${self.fondo_caja:,.2f}", font=("Arial", 12), text_color="#3E2723").pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(frame_fin, text=f"Total de Ventas: ${self.total_ventas:,.2f} ({self.cantidad_transacciones} tickets)", font=("Arial", 12), text_color="#27AE60").pack(anchor="w", padx=10, pady=2)
        
        efectivo_esperado = self.fondo_caja + self.total_ventas
        ctk.CTkLabel(frame_fin, text=f"Efectivo Esperado en Caja: ${efectivo_esperado:,.2f}", font=("Arial", 12, "bold"), text_color="#5C3A21").pack(anchor="w", padx=10, pady=(2, 8))

        # --- SECCIÓN 2: BALANCE DE INVENTARIO ---
        ctk.CTkLabel(self.scroll_resumen, text="🥐 Balance de Canasta (Piezas)", font=("Arial", 13, "bold"), text_color="#5C3A21").pack(anchor="w", padx=10, pady=(15, 5))

        if not self.resumen_inventario:
            ctk.CTkLabel(self.scroll_resumen, text="No hay registros de inventario en este turno.", font=("Arial", 11), text_color="gray").pack(padx=10, pady=10)
        else:
            header_frame = ctk.CTkFrame(self.scroll_resumen, fg_color="#E6DCC3", corner_radius=6)
            header_frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(header_frame, text="Producto", font=("Arial", 11, "bold"), text_color="#3E2723", width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Inic.", font=("Arial", 11, "bold"), text_color="#3E2723", width=35).pack(side="left")
            ctk.CTkLabel(header_frame, text="Vend.", font=("Arial", 11, "bold"), text_color="#3E2723", width=35).pack(side="left")
            ctk.CTkLabel(header_frame, text="Rest.", font=("Arial", 11, "bold"), text_color="#3E2723", width=35).pack(side="left")

            for item in self.resumen_inventario:
                fila = ctk.CTkFrame(self.scroll_resumen, fg_color="#FFFFFF", corner_radius=6, border_width=1, border_color="#EFEBE9")
                fila.pack(fill="x", padx=10, pady=2)

                ctk.CTkLabel(fila, text=item["nombre"], font=("Arial", 11), text_color="#3E2723", width=150, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(fila, text=str(item["inicial"]), font=("Arial", 11), text_color="#7F8C8D", width=35).pack(side="left")
                ctk.CTkLabel(fila, text=str(item["vendido"]), font=("Arial", 11, "bold"), text_color="#27AE60", width=35).pack(side="left")
                ctk.CTkLabel(fila, text=str(item["restante"]), font=("Arial", 11, "bold"), text_color="#D35400", width=35).pack(side="left")

    def procesar_cierre_turno(self):
        if messagebox.askyesno("Confirmar Cierre de Turno", "¿Estás seguro de cerrar el turno? Se registrará la hora final de salida y se concluirá el corte de caja.", parent=self):
            try:
                self.supabase.table("turno").update({
                    "hora_fin": datetime.now().isoformat()
                }).eq("idturno", self.id_turno).execute()

                messagebox.showinfo("¡Turno Finalizado!", "El corte de caja se ha guardado correctamente y el turno ha concluido.", parent=self)
                self.destroy()
                self.callback_exito()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo procesar el cierre del turno:\n{e}", parent=self)