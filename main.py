import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QTableWidgetItem
from PyQt6 import uic

# Import models & data modules
from model.estudiante import Estudiante
from data.data_manager import DataManager

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Cargar la interfaz principal directamente desde el archivo .ui
        uic.loadUi("dashboard.ui", self)
        
        # Inicializar DataManager
        self.db = DataManager("notas_db.txt")
        
        # Conectar botones del Dashboard a funciones
        self.btnNotas.clicked.connect(self.abrir_ventana_notas)
        self.btnAsistencia.clicked.connect(self.abrir_ventana_asistencia)
        
        # Cargar datos iniciales en el Dashboard
        self.cargar_resumen_dashboard()
        
        # Referencias a sub-ventanas
        self.ventana_notas = None
        self.ventana_asistencia = None

    def cargar_resumen_dashboard(self):
        """Carga las ultimas notas registradas en la tabla del dashboard"""
        notas = self.db.obtener_todas_las_notas()
        # Tomar solo las ultimas 5 para mostrar "Recientes"
        ultimas_notas = notas[-5:] if notas else []
        
        # El nombre del widget en dashboard.ui es 'tableWidget'
        self.tableWidget.setRowCount(0)
        
        for row_idx, data in enumerate(ultimas_notas):
            self.tableWidget.insertRow(row_idx)
            self.tableWidget.setItem(row_idx, 0, QTableWidgetItem(data['id']))
            self.tableWidget.setItem(row_idx, 1, QTableWidgetItem(data['nombre']))
            self.tableWidget.setItem(row_idx, 2, QTableWidgetItem(data['curso']))
            
            # Columna estado (simulada basada en nota)
            nota_val = int(data['nota'])
            estado = "Aprobado" if nota_val >= 11 else "Desaprobado"
            self.tableWidget.setItem(row_idx, 3, QTableWidgetItem(estado))

    def abrir_ventana_notas(self):
        self.ventana_notas = VentanaNotas(self.db)
        # Recargar dashboard al cerrar (opcional, aqui simple)
        self.ventana_notas.destroyed.connect(self.cargar_resumen_dashboard)
        self.ventana_notas.show()

    def abrir_ventana_asistencia(self):
        self.ventana_asistencia = VentanaAsistencia()
        self.ventana_asistencia.show()

class VentanaNotas(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        uic.loadUi("form_notas.ui", self)
        self.db = db_manager
        
        # Configurar UI inicial
        self.btnRegistrar.clicked.connect(self.registrar_nota)
        self.cargar_datos_tabla()

    def registrar_nota(self):
        # Obtener datos de la UI
        curso_actual = self.comboCurso.currentText()
        id_est = self.inputEstudianteID.text()
        nota_valor = self.spinNota.value()
        
        if not id_est:
            QMessageBox.warning(self, "Error", "Debe ingresar un ID de estudiante")
            return

        # Crear objeto Estudiante (POO)
        est = Estudiante(id_est, "Nombre", "Desconocido", "Carrera X")
        
        if est.registrar_nota(curso_actual, nota_valor):
            exito = self.db.registrar_nota(id_est, "Estudiante G.", curso_actual, nota_valor)
            if exito:
                QMessageBox.information(self, "Exito", "Nota registrada correctamente")
                self.inputEstudianteID.clear()
                self.cargar_datos_tabla()
            else:
                QMessageBox.critical(self, "Error", "No se pudo guardar en el archivo")

    def cargar_datos_tabla(self):
        self.tableNotas.setRowCount(0)
        notas_guardadas = self.db.obtener_todas_las_notas()
        for row_idx, data in enumerate(notas_guardadas):
            self.tableNotas.insertRow(row_idx)
            self.tableNotas.setItem(row_idx, 0, QTableWidgetItem(data['id']))
            self.tableNotas.setItem(row_idx, 1, QTableWidgetItem(data['curso']))
            self.tableNotas.setItem(row_idx, 2, QTableWidgetItem(data['nota']))



class VentanaAsistencia(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("form_asistencia.ui", self)
        
        self.btnMarcarAsistencia.clicked.connect(self.guardar_asistencia)
        
    def guardar_asistencia(self):
        fecha = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        
        estado = "Presente"
        if self.rbTardanza.isChecked(): estado = "Tardanza"
        if self.rbAusente.isChecked(): estado = "Ausente"
        
        # Validar seleccion de lista
        student_item = self.listEstudiantes.currentItem()
        if not student_item:
            QMessageBox.warning(self, "Atencion", "Seleccione un estudiante de la lista")
            return
            
        estudiante_texto = student_item.text()
        
        QMessageBox.information(self, "Guardado", f"Asistencia {estado} registrada para {estudiante_texto} el {fecha}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
