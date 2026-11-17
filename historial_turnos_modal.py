import customtkinter as ctk
from tkinter import messagebox
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False

class HistorialTurnosModal(ctk.CTkToplevel):
    def __init__(self, parent, supabase_client):
        super().__init__(parent)
        self.title("PANE-SYS - Historial y Rendimiento de Turnos")
        self.geometry("620x560")
        self.resizable(False, False)
        self.configure(fg_color="#FDFBF7")
        
        self.transient(parent)
        self.grab_set()

        self.supabase = supabase_client
        self.datos_turnos = [] 

        ctk.CTkLabel(self, text="📊 Historial y Rendimiento de Turnos", font=("Arial", 16, "bold"), text_color="#3E2723").pack(anchor="w", padx=20, pady=(20, 10))

        self.scroll_turnos = ctk.CTkScrollableFrame(self, fg_color="#FFFFFF", corner_radius=10, height=360, border_width=1, border_color="#E6DCC3")
        self.scroll_turnos.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        btn_exportar = ctk.CTkButton(
            self, 
            text="🖨️ Exportar Reporte de Turnos a PDF", 
            command=self.exportar_pdf_turnos, 
            fg_color="#27AE60", 
            hover_color="#1E8449", 
            height=40, 
            font=("Arial", 13, "bold")
        )
        btn_exportar.pack(fill="x", padx=20, pady=(5, 20))

        self.cargar_historial_turnos()

    def cargar_historial_turnos(self):
        try:
            res_turnos = self.supabase.table("turno").select("*").order("idturno", desc=True).execute()
            turnos = res_turnos.data if res_turnos.data else []

            if not turnos:
                ctk.CTkLabel(self.scroll_turnos, text="No hay turnos registrados en el sistema.", font=("Arial", 12), text_color="gray").pack(pady=20)
                return

            header = ctk.CTkFrame(self.scroll_turnos, fg_color="#E6DCC3", corner_radius=6)
            header.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(header, text="Turno / Horario", font=("Arial", 11, "bold"), text_color="#3E2723", width=160, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Fondo", font=("Arial", 11, "bold"), text_color="#3E2723", width=70).pack(side="left")
            ctk.CTkLabel(header, text="Ventas", font=("Arial", 11, "bold"), text_color="#3E2723", width=80).pack(side="left")
            ctk.CTkLabel(header, text="Total Caja", font=("Arial", 11, "bold"), text_color="#3E2723", width=80).pack(side="left")
            ctk.CTkLabel(header, text="Estado", font=("Arial", 11, "bold"), text_color="#3E2723", width=80).pack(side="left")

            for t in turnos:
                id_t = t.get("idturno")
                nombre_t = t.get("nombre_turno", "Turno")
                fondo = float(t.get("fondo_caja", 0.0))
                h_inicio = t.get("hora_inicio", "")[:16].replace("T", " ")
                h_fin = t.get("hora_fin", "")[:16].replace("T", " ") if t.get("hora_fin") else "En curso 🟢"

                res_v = self.supabase.table("venta").select("total_vent").eq("idturno", id_t).execute()
                ventas_turno = sum(float(v.get("total_vent", 0.0)) for v in res_v.data) if res_v.data else 0.0
                total_caja = fondo + ventas_turno
                estado = "Cerrado" if t.get("hora_fin") else "Activo"

                self.datos_turnos.append({
                    "nombre": nombre_t,
                    "inicio": h_inicio,
                    "fin": h_fin,
                    "fondo": fondo,
                    "ventas": ventas_turno,
                    "total": total_caja,
                    "estado": estado
                })

                fila = ctk.CTkFrame(self.scroll_turnos, fg_color="#FDFBF7", corner_radius=6, border_width=1, border_color="#EFEBE9")
                fila.pack(fill="x", padx=10, pady=3)

                info_txt = f"{nombre_t}\nIn: {h_inicio}\nOut: {h_fin}"
                ctk.CTkLabel(fila, text=info_txt, font=("Arial", 10), text_color="#3E2723", width=160, anchor="w", justify="left").pack(side="left", padx=5, pady=5)
                ctk.CTkLabel(fila, text=f"${fondo:,.2f}", font=("Arial", 11), text_color="#7F8C8D", width=70).pack(side="left")
                ctk.CTkLabel(fila, text=f"${ventas_turno:,.2f}", font=("Arial", 11, "bold"), text_color="#27AE60", width=80).pack(side="left")
                ctk.CTkLabel(fila, text=f"${total_caja:,.2f}", font=("Arial", 11, "bold"), text_color="#D35400", width=80).pack(side="left")
                
                estado_txt = "Cerrado 🔴" if t.get("hora_fin") else "Activo 🟢"
                ctk.CTkLabel(fila, text=estado_txt, font=("Arial", 10, "bold"), text_color="#273746", width=80).pack(side="left")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial de turnos:\n{e}", parent=self)

    def exportar_pdf_turnos(self):
        if not REPORTLAB_DISPONIBLE:
            messagebox.showerror("Error", "La librería 'reportlab' no está instalada. Ejecuta 'pip install reportlab'.", parent=self)
            return

        if not self.datos_turnos:
            messagebox.showwarning("Aviso", "No hay datos de turnos para exportar.", parent=self)
            return

        try:
            carpeta_reportes = "Reportes de Turnos"
            if not os.path.exists(carpeta_reportes):
                os.makedirs(carpeta_reportes)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nombre_archivo = os.path.join(carpeta_reportes, f"reporte_turnos_{timestamp}.pdf")

            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            elementos = []
            estilos = getSampleStyleSheet()

            estilo_titulo_derecha = ParagraphStyle(
                'TituloDerecha',
                parent=estilos['Normal'],
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=colors.HexColor("#5C3A21"),
                alignment=2 
            )
            estilo_sub_derecha = ParagraphStyle(
                'SubDerecha',
                parent=estilos['Normal'],
                fontName='Helvetica',
                fontSize=9,
                textColor=colors.HexColor("#7F8C8D"),
                alignment=2
            )

            logo_path = "logo.png" 
            if os.path.exists(logo_path):
                img_logo = RLImage(logo_path, width=70, height=70)
            else:
                img_logo = Paragraph("<b>[PANE-SYS]</b>", estilos['Normal'])

            texto_header = [
                Paragraph("PANE-SYS - PANADERÍA", estilo_titulo_derecha),
                Paragraph("REPORTE HISTORIAL DE TURNOS", estilo_titulo_derecha),
                Paragraph("Admin: Dueño", estilo_sub_derecha),
                Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}", estilo_sub_derecha)
            ]

            tabla_header = Table([[img_logo, texto_header]], colWidths=[90, 434])
            tabla_header.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ]))

            elementos.append(tabla_header)
            elementos.append(Spacer(1, 10))

            data_tabla = [["Turno / Nombre", "Inicio / Cierre", "Fondo", "Ventas", "Total Caja", "Estado"]]
            
            for item in self.datos_turnos:
                horarios = f"In: {item['inicio']}\nOut: {item['fin']}"
                data_tabla.append([
                    item["nombre"],
                    horarios,
                    f"${item['fondo']:,.2f}",
                    f"${item['ventas']:,.2f}",
                    f"${item['total']:,.2f}",
                    item["estado"]
                ])

            tabla_pdf = Table(data_tabla, colWidths=[94, 130, 70, 70, 70, 90])
            tabla_pdf.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E6DCC3")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#3E2723")),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D7CCC8")),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))

            elementos.append(tabla_pdf)
            doc.build(elementos)

            messagebox.showinfo("¡Exportado con Éxito!", f"El reporte en PDF se ha guardado correctamente en la carpeta:\n'{carpeta_reportes}'", parent=self)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}", parent=self)