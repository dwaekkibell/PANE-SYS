import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

class VentanaCobroModal(ctk.CTkToplevel):
    def __init__(self, parent, total_venta, id_usuario, id_turno_actual, supabase, carrito, on_cobro_exito):
        super().__init__(parent)
        
        self.total_venta = total_venta
        self.id_usuario = id_usuario
        self.id_turno_actual = id_turno_actual
        self.supabase = supabase
        self.carrito = carrito
        self.on_cobro_exito = on_cobro_exito

        self.title("Cobro en Efectivo - PANE-SYS")
        self.geometry("360x310")
        self.resizable(False, False)
        self.configure(fg_color="#FDFBF7")
        self.grab_set() 

        # UI
        ctk.CTkLabel(self, text="💰 Cobro y Cambio", font=("Arial", 16, "bold"), text_color="#5C3A21").pack(pady=(20, 5))
        ctk.CTkLabel(self, text=f"Total a Pagar: ${self.total_venta:,.2f}", font=("Arial", 15, "bold"), text_color="#3E2723").pack(pady=5)

        ctk.CTkLabel(self, text="Efectivo Recibido ($):", font=("Arial", 12, "bold"), text_color="#5C3A21").pack(anchor="w", padx=35, pady=(10, 0))
        
        self.entry_efectivo = ctk.CTkEntry(self, width=290, height=38, font=("Arial", 14, "bold"), fg_color="#FFFFFF", border_color="#D7CCC8")
        self.entry_efectivo.pack(padx=35, pady=5)
        self.entry_efectivo.focus()

        self.lbl_cambio = ctk.CTkLabel(self, text="Cambio: $0.00", font=("Arial", 14, "bold"), text_color="#27AE60")
        self.lbl_cambio.pack(pady=8)

        self.entry_efectivo.bind("<KeyRelease>", self.calcular_cambio)

        btn_cobrar = ctk.CTkButton(
            self, 
            text="✔ Confirmar Cobro", 
            command=self.procesar_cobro, 
            fg_color="#27AE60", 
            hover_color="#1E8449", 
            height=40, 
            font=("Arial", 13, "bold")
        )
        btn_cobrar.pack(pady=(10, 20))

    def calcular_cambio(self, event=None):
        try:
            texto = self.entry_efectivo.get().strip()
            if not texto:
                self.lbl_cambio.configure(text="Cambio: $0.00", text_color="#27AE60")
                return
            efectivo = float(texto)
            if efectivo >= self.total_venta:
                cambio = efectivo - self.total_venta
                self.lbl_cambio.configure(text=f"Cambio: ${cambio:,.2f}", text_color="#27AE60")
            else:
                falta = self.total_venta - efectivo
                self.lbl_cambio.configure(text=f"Falta: ${falta:,.2f} (Insuficiente)", text_color="#C0392B")
        except ValueError:
            self.lbl_cambio.configure(text="Ingrese un número válido", text_color="#C0392B")

    def procesar_cobro(self):
        try:
            texto = self.entry_efectivo.get().strip()
            efectivo = float(texto)
            if efectivo < self.total_venta:
                messagebox.showwarning("Monto Insuficiente", "El efectivo recibido es menor al total de la venta.", parent=self)
                return
            
            self.ejecutar_guardado_venta()
        except ValueError:
            messagebox.showwarning("Error", "Por favor ingrese una cantidad en efectivo válida.", parent=self)

    def ejecutar_guardado_venta(self):
        try:
            fecha_actual = datetime.now().isoformat()

            res_venta = self.supabase.table("venta").insert({
                "total_vent": self.total_venta,
                "fecha_vent": fecha_actual,
                "idUsuario": self.id_usuario,
                "idturno": self.id_turno_actual
            }).execute()

            if res_venta.data:
                v_row = res_venta.data[0]
                id_venta_generada = v_row.get("idVenta") or v_row.get("idventa") or v_row.get("id")

                conteo_productos = {}
                for item in self.carrito:
                    pid = item.get("idProducto") or item.get("idproducto") or item.get("id")
                    
                    if pid not in conteo_productos:
                        conteo_productos[pid] = {"cantidad": 0, "precio": item["precio"], "nombre": item["nombre"]}
                    conteo_productos[pid]["cantidad"] += 1

                for pid, info in conteo_productos.items():
                    cant = info["cantidad"]
                    precio_u = info["precio"]
                    subtotal = cant * precio_u

                    self.supabase.table("detalleventa").insert({
                        "idVenta": id_venta_generada,
                        "idProducto": pid,
                        "cantidad": cant,
                        "precio_unit": precio_u,
                        "subtot": subtotal
                    }).execute()

                for pid, info in conteo_productos.items():
                    cant = info["cantidad"]
                    
                    res_det = self.supabase.table("detalle_turno").select("cantidad, iddetalle").eq("idturno", self.id_turno_actual).eq("idproducto", pid).execute()
                    
                    if not res_det.data:
                        
                        res_det = self.supabase.table("detalle_turno").select("cantidad, iddetalle").eq("idturno", self.id_turno_actual).eq("idProducto", pid).execute()

                    if res_det.data:
                        det_row = res_det.data[0]
                        id_detalle = det_row.get("iddetalle")
                        stock_actual_turno = int(det_row.get("cantidad", 0))
                        nuevo_stock = max(0, stock_actual_turno - cant)

                        self.supabase.table("detalle_turno").update({"cantidad": nuevo_stock}).eq("iddetalle", id_detalle).execute()

            messagebox.showinfo("¡Venta Exitosa!", f"Venta cobrada con éxito por ${self.total_venta:,.2f}")
            self.destroy()
            self.on_cobro_exito() 

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la venta:\n{e}", parent=self)