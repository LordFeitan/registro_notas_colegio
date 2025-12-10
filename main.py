import re
import sys
import os
import warnings

# Suppress PyQt6 internal warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QTableWidgetItem, QVBoxLayout
from PyQt6.QtGui import QColor
from PyQt6 import uic

# Import models & data modules
from model.estudiante import Estudiante
from data.data_manager import DataManager

# ==========================================
# CLASES DE VENTANAS
# ==========================================

class MainApp(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        uic.loadUi("ui/dashboard.ui", self)
        
        self.db = db_manager
        
        # Conectar botones del Sidebar (Menu)
        self.btnEstudiantes.clicked.connect(self.abrir_registro_estudiantes)
        self.btnCursos.clicked.connect(self.abrir_gestion_cursos)
        self.btnMatricula.clicked.connect(self.abrir_matricula)
        self.btnNotas.clicked.connect(self.abrir_notas)
        self.btnReportes.clicked.connect(self.mostrar_reportes) # Placeholder
        self.btnAsistencia.clicked.connect(self.abrir_asistencia)
        
        # Cargar datos resumen (Dashboard)
        self.cargar_resumen_dashboard()

    def cargar_resumen_dashboard(self):
        """Carga KPIs y tabla de últimas notas"""
        
        # 1. Total Estudiantes
        estudiantes = self.db.obtener_estudiantes(activos=True)
        self.lblValEstudiantes.setText(str(len(estudiantes)))
        
        # 2. Total Cursos
        cursos = self.db.obtener_cursos()
        self.lblValCursos.setText(str(len(cursos)))
        
        # 3. Promedio General y Riesgo
        notas = self.db.obtener_todas_las_notas()
        if notas:
            promedios = [float(n['promedio']) for n in notas if n.get('promedio')]
            if promedios:
                general = sum(promedios) / len(promedios)
                self.lblValPromedio.setText(f"{general:.2f}")
                
                # Alumnos en riesgo (promedio < 10.5)
                riesgo = sum(1 for p in promedios if p < 10.5)
                self.lblValRiesgo.setText(str(riesgo))
            else:
                self.lblValPromedio.setText("0.0")
                self.lblValRiesgo.setText("0")
        else:
            self.lblValPromedio.setText("0.0")
            self.lblValRiesgo.setText("0")

        # 4. Tabla Ultimas Calificaciones
        self.tableWidget.setRowCount(0)
        # Mostrar ultimas 10
        for i, nota in enumerate(reversed(notas[-10:])): 
            self.tableWidget.insertRow(i)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(nota['id']))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(nota['nombre']))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(nota['curso']))
            
            # Formatear notas a 1 decimal
            try:
                n1 = f"{float(nota.get('n1', 0)):.1f}"
                n2 = f"{float(nota.get('n2', 0)):.1f}"
                n3 = f"{float(nota.get('n3', 0)):.1f}"
                prom = f"{float(nota.get('promedio', 0)):.1f}"
                val_prom = float(nota.get('promedio', 0))
            except ValueError:
                n1, n2, n3, prom = "0.0", "0.0", "0.0", "0.0"
                val_prom = 0.0

            self.tableWidget.setItem(i, 3, QTableWidgetItem(n1))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(n2))
            self.tableWidget.setItem(i, 5, QTableWidgetItem(n3))
            self.tableWidget.setItem(i, 6, QTableWidgetItem(prom))

            estado = "Aprobado" if val_prom >= 10.5 else "Desaprobado"
            item_estado = QTableWidgetItem(estado)
            
            if estado == "Desaprobado":
                item_estado.setForeground(QColor("red"))
            else:
                item_estado.setForeground(QColor("green"))
                
            self.tableWidget.setItem(i, 7, item_estado)

    def abrir_registro_estudiantes(self):
        self.ventana_estudiantes = VentanaRegistroEstudiantes(self.db)
        self.ventana_estudiantes.show()

    def abrir_gestion_cursos(self):
        self.ventana_cursos = VentanaGestionCursos(self.db)
        self.ventana_cursos.show()

    def abrir_matricula(self):
        self.ventana_matricula = VentanaMatricula(self.db)
        self.ventana_matricula.show()
    
    def abrir_notas(self):
        self.ventana_notas = VentanaNotas(self.db)
        self.ventana_notas.destroyed.connect(self.cargar_resumen_dashboard)
        self.ventana_notas.show()

    def abrir_asistencia(self):
        self.ventana_asistencia = VentanaAsistencia(self.db)
        self.ventana_asistencia.show()

    def mostrar_reportes(self):
        QMessageBox.information(self, "Reportes", "Módulo de Reportes en construcción.")
        self.ventana_estudiantes.show()

    def abrir_ventana_cursos(self):
        self.ventana_cursos = VentanaGestionCursos(self.db)
        self.ventana_cursos.show()

    def abrir_ventana_matricula(self):
        self.ventana_matricula = VentanaMatricula(self.db)
        self.ventana_matricula.show()

class VentanaRegistroEstudiantes(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        uic.loadUi("ui/form_registro_estudiantes.ui", self)
        self.db = db_manager
        
        self.btnGuardar.clicked.connect(self.registrar_estudiante)
        
        # Conectar Busqueda
        self.btnBuscar.clicked.connect(self.filtrar_estudiantes)
        self.inputBusqueda.textChanged.connect(self.filtrar_estudiantes)
        
        # Conectar Edicion
        self.tableEstudiantes.itemDoubleClicked.connect(self.cargar_estudiante_para_editar)
        try:
            self.btnEditar.clicked.connect(self.editar_seleccionado)
        except AttributeError:
            pass

        try:
            self.btnEliminar.clicked.connect(self.eliminar_seleccionado)
        except AttributeError:
            print("Warning: btnEliminar not found in UI")

        # Nuevo boton limpiar (asegurate de haberlo agregado al UI o manejar error si no existe)
        try:
            self.btnLimpiar.clicked.connect(self.limpiar_formulario)
        except AttributeError:
            pass # Si no existe aun en el UI cargado
            
        self.cargar_carreras()
        self.cargar_tabla()

    def filtrar_estudiantes(self):
        termino = self.inputBusqueda.text()
        if not termino:
            self.cargar_tabla()
            return
            
        resultados = self.db.buscar_estudiantes(termino)
        self.actualizar_tabla(resultados)

    def editar_seleccionado(self):
        row = self.tableEstudiantes.currentRow()
        if row >= 0:
            item = self.tableEstudiantes.item(row, 0) # Item ID
            self.cargar_estudiante_para_editar(item)
        else:
            QMessageBox.warning(self, "Aviso", "Seleccione un estudiante de la tabla para editar.")

    def eliminar_seleccionado(self):
        row = self.tableEstudiantes.currentRow()
        if row >= 0:
            id_est = self.tableEstudiantes.item(row, 0).text()
            nombre = self.tableEstudiantes.item(row, 1).text()
            
            confirm = QMessageBox.question(
                self, "Confirmar Eliminación",
                f"¿Está seguro de eliminar al estudiante {nombre} (ID: {id_est})?\nEsta acción es irreversible.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                if self.db.eliminar_estudiante(id_est):
                    QMessageBox.information(self, "Eliminado", "Estudiante eliminado correctamente.")
                    self.limpiar_formulario()
                    self.cargar_tabla()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo eliminar el estudiante.")
        else:
            QMessageBox.warning(self, "Aviso", "Seleccione un estudiante de la tabla para eliminar.")

    def cargar_carreras(self):
        """Carga las carreras desde el txt al ComboBox"""
        self.comboCarrera.clear()
        try:
            if os.path.exists("carreras.txt"):
                with open("carreras.txt", 'r', encoding='utf-8') as f:
                    carreras = [line.strip() for line in f if line.strip()]
                    self.comboCarrera.addItems(carreras)
            else:
                self.comboCarrera.addItems(["Ingeniería de Sistemas", "Administración", "Contabilidad"]) # Default
        except Exception as e:
            print(f"Error cargando carreras: {e}")

    def registrar_estudiante(self):
        # El ID ahora es read-only, pero si tiene texto, es edicion
        id_actual = self.inputID.text()
        nombre = self.inputNombre.text().strip()
        apellido = self.inputApellido.text().strip()
        carrera = self.comboCarrera.currentText()
        correo = self.inputCorreo.text().strip()
        activo = self.checkActivo.isChecked()
        
        # 1. Validar campos obligatorios
        if not nombre or not apellido or not correo:
            QMessageBox.warning(self, "Error", "Complete los campos obligatorios")
            return

        # 2. Validar Nombre (Solo letras y espacios, min 2 chars)
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre) or len(nombre) < 2:
            QMessageBox.warning(self, "Error", "El Nombre es inválido. Use solo letras y mínimo 2 caracteres.")
            return

        # 3. Validar Apellido (Solo letras y espacios, min 2 chars)
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", apellido) or len(apellido) < 2:
            QMessageBox.warning(self, "Error", "El Apellido es inválido. Use solo letras y mínimo 2 caracteres.")
            return

        # 4. Validar Correo (Formato simple)
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo):
            QMessageBox.warning(self, "Error", "El formato del correo es inválido (ejemplo@dominio.com).")
            return

        # Validacion de fecha
        from PyQt6.QtCore import QDate
        fecha_birth = self.dateNacimiento.date()
        if fecha_birth >= QDate.currentDate():
             QMessageBox.warning(self, "Error", "La fecha de nacimiento debe ser anterior a hoy")
             return

        # LOGICA UPDATE VS SAVE
        if "Generado" in id_actual or not id_actual:
            # ES NUEVO
            if self.db.registrar_estudiante(nombre, apellido, carrera, nacimiento, correo, activo):
                QMessageBox.information(self, "Exito", "Estudiante registrado correctamente")
                self.limpiar_formulario()
                self.cargar_tabla()
            else:
                QMessageBox.critical(self, "Error", "Error al guardar estudiante")
        else:
            # ES EDICION
            if self.db.actualizar_estudiante(id_actual, nombre, apellido, carrera, nacimiento, correo, activo):
                QMessageBox.information(self, "Exito", "Estudiante actualizado correctamente")
                self.limpiar_formulario()
                self.cargar_tabla()
            else:
                QMessageBox.critical(self, "Error", "Error al actualizar estudiante")

    def cargar_estudiante_para_editar(self, item):
        row = item.row()
        id_est = self.tableEstudiantes.item(row, 0).text()
        
        # Buscamos el objeto completo en la DB para sacar todos los datos (incluido activo)
        estudiante = None
        for est in self.db.obtener_estudiantes():
            if est['id'] == id_est:
                estudiante = est
                break
                
        if estudiante:
            self.inputID.setText(estudiante['id'])
            self.inputNombre.setText(estudiante['nombre'])
            self.inputApellido.setText(estudiante['apellido'])
            self.comboCarrera.setCurrentText(estudiante['carrera'])
            self.inputCorreo.setText(estudiante['correo'])
            self.checkActivo.setChecked(estudiante.get('activo', True))
            
            from PyQt6.QtCore import QDate
            if estudiante['nacimiento']:
                 self.dateNacimiento.setDate(QDate.fromString(estudiante['nacimiento'], "yyyy-MM-dd"))
                 
            self.btnGuardar.setText("Actualizar Estudiante")

    def limpiar_formulario(self):
        self.inputID.setText("Generado automáticamente")
        self.inputNombre.clear()
        self.inputApellido.clear()
        self.inputCorreo.clear()
        self.checkActivo.setChecked(True)
        self.dateNacimiento.setDate(self.dateNacimiento.minimumDate()) 
        self.btnGuardar.setText("Guardar Estudiante")

    def cargar_tabla(self):
        estudiantes = self.db.obtener_estudiantes()
        self.actualizar_tabla(estudiantes)

    def actualizar_tabla(self, estudiantes):
        self.tableEstudiantes.setRowCount(0)
        # La tabla tiene 6 columnas, podriamos agregar una 7ma visual para "Estado"
        # Por ahora lo dejaremos asi, ya que el checkbox muestra el estado al editar
        for row_idx, data in enumerate(estudiantes):
            self.tableEstudiantes.insertRow(row_idx)
            
            # Determinar color segun estado
            es_activo = data.get('activo', True)
            color_fondo = QColor(255, 255, 255) # Blanco
            if not es_activo:
                color_fondo = QColor(255, 230, 230) # Rojo suave
            
            items = [
                data['id'], data['nombre'], data['apellido'], 
                data['carrera'], data.get('nacimiento', ''), data.get('correo', '')
            ]
            
            for col_idx, valor in enumerate(items):
                item = QTableWidgetItem(str(valor))
                item.setBackground(color_fondo)
                self.tableEstudiantes.setItem(row_idx, col_idx, item)

class VentanaGestionCursos(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        uic.loadUi("ui/form_gestion_cursos.ui", self)
        self.db = db_manager
        
        # Conexiones Eventos
        self.btnGuardar.clicked.connect(self.registrar_curso)
        self.btnBuscar.clicked.connect(self.filtrar_cursos)
        self.inputBusqueda.textChanged.connect(self.filtrar_cursos)
        
        # Nuevos botones
        self.btnLimpiar.clicked.connect(self.limpiar_formulario)
        self.btnEditar.clicked.connect(self.editar_seleccionado)
        self.btnEliminar.clicked.connect(self.eliminar_seleccionado)
        self.tableCursos.itemDoubleClicked.connect(self.cargar_curso_para_editar)
        
        # Configurar Tabla
        self.tableCursos.setColumnCount(4)
        self.tableCursos.setHorizontalHeaderLabels(["Código", "Nombre", "Profesor", "Créditos"])
        self.tableCursos.horizontalHeader().setStretchLastSection(True)
        
        self.cargar_tabla()
        
    def registrar_curso(self):
        # 1. Validar y Formatear Entradas
        codigo = self.inputCodigo.text().strip().upper() # Codigo siempre mayus
        nombre = self.inputNombre.text().strip()
        profesor = self.inputProfesor.text().strip()
        creditos = self.spinCreditos.value()
        
        # Capitalizar nombre y profesor (Titulo) para consistencia
        nombre = " ".join([p.capitalize() for p in nombre.split()])
        profesor = " ".join([p.capitalize() for p in profesor.split()])
        
        if not codigo or not nombre or not profesor:
             QMessageBox.warning(self, "Error", "Complete todos los campos obligatorios")
             return
             
        # Check if ID is ReadOnly - means we are EDITING
        if self.inputCodigo.isReadOnly():
            if self.db.actualizar_curso(codigo, nombre, profesor, creditos):
                QMessageBox.information(self, "Exito", "Curso actualizado")
                self.limpiar_formulario()
                self.cargar_tabla()
            else:
                QMessageBox.critical(self, "Error", "Error al actualizar")
        else:
            # CREATE
            # Check duplicate ID simple (optional or rely on DB)
            if any(c['codigo'] == codigo for c in self.db.obtener_cursos()):
                QMessageBox.warning(self, "Error", "El código de curso ya existe.")
                return 

            if self.db.registrar_curso(codigo, nombre, profesor, creditos):
                QMessageBox.information(self, "Exito", "Curso registrado")
                self.limpiar_formulario()
                self.cargar_tabla()
            else:
                QMessageBox.critical(self, "Error", "Error al guardar")

    def cargar_curso_para_editar(self, item):
        row = item.row()
        return self._cargar_desde_fila(row)

    def editar_seleccionado(self):
        row = self.tableCursos.currentRow()
        if row >= 0:
            self._cargar_desde_fila(row)
        else:
            QMessageBox.warning(self, "Aviso", "Seleccione un curso.")

    def _cargar_desde_fila(self, row):
        codigo = self.tableCursos.item(row, 0).text()
        # Buscar objeto completo para tener profesor y creditos veraces (aunque esten en tabla)
        curso = None
        for c in self.db.obtener_cursos():
            if c['codigo'] == codigo:
                curso = c
                break
        
        if curso:
            self.inputCodigo.setText(curso['codigo'])
            self.inputCodigo.setReadOnly(True) # Modificar clave primaria no permitido
            self.inputNombre.setText(curso['nombre'])
            self.inputProfesor.setText(curso.get('profesor', ''))
            try:
                self.spinCreditos.setValue(int(curso.get('creditos', 3)))
            except:
                self.spinCreditos.setValue(3)
                
            self.btnGuardar.setText("Actualizar Curso")

    def eliminar_seleccionado(self):
        row = self.tableCursos.currentRow()
        if row >= 0:
            codigo = self.tableCursos.item(row, 0).text()
            nombre = self.tableCursos.item(row, 1).text()
            
            confirm = QMessageBox.question(
                self, "Confirmar", 
                f"¿Eliminar curso {nombre} ({codigo})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                self.db.eliminar_curso(codigo)
                self.limpiar_formulario()
                self.cargar_tabla()
        else:
             QMessageBox.warning(self, "Aviso", "Seleccione un curso.")
    
    def limpiar_formulario(self):
        self.inputCodigo.clear()
        self.inputCodigo.setReadOnly(False)
        self.inputNombre.clear()
        self.inputProfesor.clear()
        self.spinCreditos.setValue(3)
        self.btnGuardar.setText("Guardar Curso")

    def cargar_tabla(self):
        cursos = self.db.obtener_cursos()
        self.actualizar_tabla(cursos)
        
    def filtrar_cursos(self):
        termino = self.inputBusqueda.text()
        if not termino:
            self.cargar_tabla()
            return
        resultados = self.db.buscar_cursos(termino)
        self.actualizar_tabla(resultados)
        
    def actualizar_tabla(self, cursos):
        self.tableCursos.setRowCount(0)
        for i, c in enumerate(cursos):
            self.tableCursos.insertRow(i)
            self.tableCursos.setItem(i, 0, QTableWidgetItem(c['codigo']))
            self.tableCursos.setItem(i, 1, QTableWidgetItem(c['nombre']))
            self.tableCursos.setItem(i, 2, QTableWidgetItem(c.get('profesor', '')))
            self.tableCursos.setItem(i, 3, QTableWidgetItem(str(c.get('creditos', ''))))


class VentanaMatricula(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        uic.loadUi("ui/form_matricula.ui", self)
        self.db = db_manager
        
        self.btnMatricular.clicked.connect(self.registrar_matricula)
        
        self.cargar_combos()
        self.cargar_tabla()
        
    def cargar_combos(self):
        self.comboEstudiante.clear()
        self.comboCurso.clear()
        
        # Cargar estudiantes
        estudiantes = self.db.obtener_estudiantes()
        for est in estudiantes:
            # Guardamos ID en el data del item
            self.comboEstudiante.addItem(f"{est['nombre']} {est['apellido']} ({est['id']})", est['id'])
            
        # Cargar cursos
        cursos = self.db.obtener_cursos()
        for cur in cursos:
            self.comboCurso.addItem(f"{cur['nombre']} ({cur['codigo']})", cur['codigo'])
            
    def registrar_matricula(self):
        idx_est = self.comboEstudiante.currentIndex()
        idx_cur = self.comboCurso.currentIndex()
        
        if idx_est == -1 or idx_cur == -1:
            QMessageBox.warning(self, "Error", "Seleccione estudiante y curso")
            return
            
        id_est = self.comboEstudiante.itemData(idx_est)
        cod_curso = self.comboCurso.itemData(idx_cur)
        
        from PyQt6.QtCore import QDate
        fecha = QDate.currentDate().toString("yyyy-MM-dd")
        
        exito, msg = self.db.registrar_matricula(id_est, cod_curso, fecha)
        if exito:
            QMessageBox.information(self, "Exito", msg)
            self.cargar_tabla()
        else:
            QMessageBox.warning(self, "Atención", msg)
            
    def cargar_tabla(self):
        matriculas = self.db.obtener_matriculas()
        self.tableMatriculas.setRowCount(0)
        for i, m in enumerate(matriculas):
            self.tableMatriculas.insertRow(i)
            self.tableMatriculas.setItem(i, 0, QTableWidgetItem(m['estudiante']))
            self.tableMatriculas.setItem(i, 1, QTableWidgetItem(m['curso']))
            self.tableMatriculas.setItem(i, 2, QTableWidgetItem(m['fecha']))


class VentanaNotas(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        uic.loadUi("ui/form_notas.ui", self)
        self.db = db_manager
        
        # Configurar UI inicial
        self.cargar_combos()
        self.comboCurso.currentIndexChanged.connect(self.actualizar_combo_estudiantes)
        self.btnRegistrar.clicked.connect(self.registrar_nota)
        self.cargar_datos_tabla()

    def cargar_combos(self):
        self.comboCurso.clear()
        # Cargar Cursos
        cursos = self.db.obtener_cursos()
        for c in cursos:
            self.comboCurso.addItem(c['nombre'], c['codigo'])
            
        # Trigger initial update
        self.actualizar_combo_estudiantes()

    def actualizar_combo_estudiantes(self):
        self.comboEstudiante.clear()
        idx = self.comboCurso.currentIndex()
        if idx == -1: return
        
        cod_curso = self.comboCurso.itemData(idx)
        
        # Filtramos SOLO los matriculados
        estudiantes = self.db.obtener_estudiantes_por_curso(cod_curso)
        
        if estudiantes:
            self.comboEstudiante.setEnabled(True)
            for est in estudiantes:
                if est.get('activo', True):
                    self.comboEstudiante.addItem(f"{est['nombre']} {est['apellido']} ({est['id']})", est['id'])
        else:
            self.comboEstudiante.addItem("No hay estudiantes matriculados", None)
            self.comboEstudiante.setEnabled(False)

    def registrar_nota(self):
        # Obtener datos de la UI
        idx_curso = self.comboCurso.currentIndex()
        idx_est = self.comboEstudiante.currentIndex()
        
        if idx_curso == -1 or idx_est == -1:
             QMessageBox.warning(self, "Error", "Seleccione Curso y Estudiante")
             return
             
        cod_curso = self.comboCurso.itemData(idx_curso)
        id_est = self.comboEstudiante.itemData(idx_est)
        
        n1 = self.spinNota1.value()
        n2 = self.spinNota2.value()
        n3 = self.spinNota3.value()
        
        if self.db.registrar_nota(id_est, cod_curso, n1, n2, n3):
            QMessageBox.information(self, "Exito", "Notas registradas correctamente")
            # Reset spins
            self.spinNota1.setValue(0)
            self.spinNota2.setValue(0)
            self.spinNota3.setValue(0)
            self.cargar_datos_tabla()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar en el archivo")

    def cargar_datos_tabla(self):
        self.tableNotas.setRowCount(0)
        notas_guardadas = self.db.obtener_todas_las_notas()
        for row_idx, data in enumerate(notas_guardadas):
            self.tableNotas.insertRow(row_idx)
            self.tableNotas.setItem(row_idx, 0, QTableWidgetItem(data['nombre']))
            self.tableNotas.setItem(row_idx, 1, QTableWidgetItem(data['curso']))
            self.tableNotas.setItem(row_idx, 2, QTableWidgetItem(str(data['n1'])))
            self.tableNotas.setItem(row_idx, 3, QTableWidgetItem(str(data['n2'])))
            self.tableNotas.setItem(row_idx, 4, QTableWidgetItem(str(data['n3'])))
            self.tableNotas.setItem(row_idx, 5, QTableWidgetItem(str(data['promedio'])))



class VentanaAsistencia(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        uic.loadUi("ui/form_asistencia.ui", self)
        self.db = db_manager
        
        # UI Setup
        self.tableEstudiantes.setColumnCount(4)
        self.tableEstudiantes.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Estado Actual"])
        self.tableEstudiantes.setColumnWidth(0, 80)
        self.tableEstudiantes.setColumnWidth(3, 100)
        self.tableEstudiantes.horizontalHeader().setStretchLastSection(True)
        
        # Cargar Cursos
        self.cargar_cursos()
        
        # Conexiones
        self.comboCurso.currentIndexChanged.connect(self.cargar_tabla_estudiantes)
        self.calendarWidget.selectionChanged.connect(self.cargar_tabla_estudiantes)
        self.tableEstudiantes.itemSelectionChanged.connect(self.cargar_estado_seleccionado)
        self.btnMarcarAsistencia.clicked.connect(self.guardar_asistencia)
        
        # Cargar tabla inicial
        self.cargar_tabla_estudiantes()
        
    def cargar_cursos(self):
        self.comboCurso.clear()
        cursos = self.db.obtener_cursos()
        for c in cursos:
            self.comboCurso.addItem(c['nombre'], c['codigo'])
            
    def cargar_tabla_estudiantes(self):
        # Obtener filtros
        idx_curso = self.comboCurso.currentIndex()
        if idx_curso == -1: return
        cod_curso = self.comboCurso.itemData(idx_curso)
        fecha = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        
        # Actualizar Label de fecha para claridad
        self.labelCalendar.setText(f"Fecha Seleccionada: {fecha}")
        
        # Obtener Estudiantes ACTIVOS (Idealmente filtrados por matricula, pero usaremos todos por simplicidad o estudiantes matriculados si existiera esa logica facil)
        # Para ser precisos con el requerimiento de "curso a que asisto", deberiamos usar matriculas.
        # Filtremos por matricula:
        matriculas = self.db.obtener_matriculas() # Esto devuelve diccionarios con nombres, no IDs...
        # DataManager.obtener_matriculas devuelve nombres procesados, no raw data.
        # Usaremos busqueda bruta en raw matriculas para obtener IDs
        ids_matriculados = []
        if os.path.exists(self.db.archivo_matriculas):
             with open(self.db.archivo_matriculas, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.split('|')
                    if len(parts) >= 2 and parts[1] == cod_curso:
                        ids_matriculados.append(parts[0])
                        
        estudiantes = self.db.obtener_estudiantes()
        
        # Logica de Filtrado:
        # 1. Intentar buscar estudiantes matriculados en estecurso
        ids_en_curso = []
        if os.path.exists("matriculas.txt"):
             with open("matriculas.txt", 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.split('|')
                    if len(parts) >= 2 and parts[1] == cod_curso:
                        ids_en_curso.append(parts[0])

        estudiantes_curso = []
        if ids_en_curso:
             # Si hay inscritos, mostramos SOLO esos
             estudiantes_curso = [e for e in estudiantes if e['id'] in ids_en_curso and e.get('activo', True)]
        else:
             # Si NO hay nadie inscrito (o archivo no existe), mostramos TODOS los activos (Modo Demo/Fallback)
             # Esto evita la tabla vacia que confunde al usuario
             estudiantes_curso = [e for e in estudiantes if e.get('activo', True)]

        self.tableEstudiantes.setRowCount(0)
        
        for i, est in enumerate(estudiantes_curso):
            self.tableEstudiantes.insertRow(i)
            self.tableEstudiantes.setItem(i, 0, QTableWidgetItem(est['id']))
            self.tableEstudiantes.setItem(i, 1, QTableWidgetItem(est['nombre']))
            self.tableEstudiantes.setItem(i, 2, QTableWidgetItem(est['apellido']))
            
            # Buscar estado previo
            estado_previo = self.db.obtener_asistencia_estudiante(est['id'], cod_curso, fecha)
            item_estado = QTableWidgetItem(estado_previo if estado_previo else "-")
            
            if estado_previo == "Presente": item_estado.setBackground(QColor(200, 255, 200)) # Verde
            elif estado_previo == "Ausente": item_estado.setBackground(QColor(255, 200, 200)) # Rojo
            elif estado_previo == "Tardanza": item_estado.setBackground(QColor(255, 255, 200)) # Amarillo
            
            self.tableEstudiantes.setItem(i, 3, item_estado)

    def cargar_estado_seleccionado(self):
        row = self.tableEstudiantes.currentRow()
        if row >= 0:
            item_estado = self.tableEstudiantes.item(row, 3)
            texto = item_estado.text()
            
            if texto == "Presente": self.rbPresente.setChecked(True)
            elif texto == "Tardanza": self.rbTardanza.setChecked(True)
            elif texto == "Ausente": self.rbAusente.setChecked(True)
            else: self.rbPresente.setChecked(True) # Default

    def guardar_asistencia(self):
        idx_curso = self.comboCurso.currentIndex()
        if idx_curso == -1: return
        cod_curso = self.comboCurso.itemData(idx_curso)
        fecha = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        
        row = self.tableEstudiantes.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Atención", "Seleccione un estudiante de la tabla para calificar")
            return
            
        id_est = self.tableEstudiantes.item(row, 0).text()
        nombre = self.tableEstudiantes.item(row, 1).text()
        
        estado = "Presente"
        if self.rbTardanza.isChecked(): estado = "Tardanza"
        if self.rbAusente.isChecked(): estado = "Ausente"
        
        exito, msg = self.db.registrar_asistencia(id_est, cod_curso, fecha, estado)
        
        if exito:
            # Actualizar solo la celda visualmente
            item_st = QTableWidgetItem(estado)
            if estado == "Presente": item_st.setBackground(QColor(200, 255, 200))
            elif estado == "Ausente": item_st.setBackground(QColor(255, 200, 200))
            elif estado == "Tardanza": item_st.setBackground(QColor(255, 255, 200))
            
            self.tableEstudiantes.setItem(row, 3, item_st)
            
            # Feedback sutil en barra de estado o print, no popup molesto para flujo rapido
            print(f"Asistencia guardada: {nombre} -> {estado}")
        else:
            QMessageBox.critical(self, "Error", msg)

# Matplotlib integration
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def plot_grades(self, data):
        """
        Data format: {'Curso A': 15, 'Curso B': 12, ...}
        """
        self.ax.clear()
        cursos = list(data.keys())
        promedios = list(data.values())
        
        bars = self.ax.bar(cursos, promedios, color='#3498db')
        self.ax.set_title("Promedio de Notas por Curso")
        self.ax.set_ylim(0, 20)
        self.ax.set_ylabel("Nota Promedio")
        
        # Rotar etiquetas si son muchas
        plt.setp(self.ax.get_xticklabels(), rotation=15, ha="right")
        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_manager = DataManager("notas_db.txt")
    window = MainApp(db_manager)
    window.show()
    sys.exit(app.exec())
