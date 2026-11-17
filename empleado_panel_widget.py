import customtkinter as ctk

class EmpleadoPanelWidget(ctk.CTkFrame):
    def __init__(self, parent, supabase_client, id_turno_actual=None):
        super().__init__(parent, fg_color="transparent")
        
        self.supabase = supabase_client
        self.id_turno = id_turno_actual

        # --- 1. CABECERA CON INDICADOR DE TURNO ACTIVO ---
        header_empleado_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_empleado_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(header_empleado_frame, text="Punto de Venta - Mostrador", font=("Arial", 22, "bold"), text_color="#3E2723").pack(side="left")
        
        self.lbl_turno_activo = ctk.CTkLabel(
            header_empleado_frame, 
            text="🟢 Turno Activo", 
            font=("Arial", 12, "bold"), 
            text_color="#27AE60",
            fg_color="#E8F8F5",
            corner_radius=6,
            padx=10,
            pady=5
        )
        self.lbl_turno_activo.pack(side="right")

        # --- 2. MINI-MÉTRICAS EN TIEMPO REAL (Progreso del turno) ---
        metrics_empleado_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E6DCC3")
        metrics_empleado_frame.pack(fill="x", padx=10, pady=5, ipady=2)

        # Métrica 1: Ventas hechas en el turno
        me1 = ctk.CTkFrame(metrics_empleado_frame, fg_color="transparent")
        me1.pack(side="left", expand=True, padx=10, pady=8)
        ctk.CTkLabel(me1, text="Ventas en mi Turno", font=("Arial", 11), text_color="gray").pack()
        self.lbl_emp_ventas_count = ctk.CTkLabel(me1, text="0", font=("Arial", 16, "bold"), text_color="#5C3A21")
        self.lbl_emp_ventas_count.pack()

        # Métrica 2: Efectivo total acumulado en caja (Fondo + Ventas)
        me2 = ctk.CTkFrame(metrics_empleado_frame, fg_color="transparent")
        me2.pack(side="left", expand=True, padx=10, pady=8)
        ctk.CTkLabel(me2, text="Efectivo en Caja (Estimado)", font=("Arial", 11), text_color="gray").pack()
        self.lbl_emp_caja_total = ctk.CTkLabel(me2, text="$0.00", font=("Arial", 16, "bold"), text_color="#27AE60")
        self.lbl_emp_caja_total.pack()

        if self.id_turno:
            self.actualizar_metricas(self.id_turno)

    def actualizar_metricas(self, id_turno):
        self.id_turno = id_turno
        try:
            res = self.supabase.table("venta").select("total_vent").eq("idturno", id_turno).execute()
            ventas = res.data if res.data else []
            
            total_transacciones = len(ventas)
            ingresos_turno = sum(float(v.get("total_vent", 0.0)) for v in ventas)
            
            res_turno = self.supabase.table("turno").select("nombre_turno, fondo_caja").eq("idturno", id_turno).single().execute()
            if res_turno.data:
                nombre_t = res_turno.data.get("nombre_turno", "Turno")
                fondo_inicial = float(res_turno.data.get("fondo_caja", 0.0))
                efectivo_total = fondo_inicial + ingresos_turno

                self.lbl_turno_activo.configure(text=f"🟢 {nombre_t} | Fondo: ${fondo_inicial:,.2f}")
                self.lbl_emp_ventas_count.configure(text=str(total_transacciones))
                self.lbl_emp_caja_total.configure(text=f"${efectivo_total:,.2f}")
                
        except Exception as e:
            print(f"Error al actualizar métricas del empleado: {e}")