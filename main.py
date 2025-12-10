import re
import sys
import os
import warnings

# Suppress PyQt6 internal warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView, QVBoxLayout
from PyQt6.QtGui import QIcon, QPixmap, QColor
from PyQt6.QtCore import Qt, QDate
from PyQt6 import uic

# Import models & data modules
from model.estudiante import Estudiante
from controllers.asistencia_controller import AsistenciaController
from controllers.estudiante_controller import EstudianteController
from controllers.nota_controller import NotaController
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
                
                # Alumnos en riesgo (promedio < 13)
                riesgo = sum(1 for p in promedios if p < 13)
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

            estado = "Aprobado" if val_prom >= 13 else "Desaprobado"
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
        self.ventana_reportes = VentanaReportes(self.db)
        self.ventana_reportes.show()

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
        self.controller = EstudianteController(db_manager)  # MVC: Controller
        
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
                # MVC: Using Controller
                if self.controller.eliminar_estudiante(id_est):
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
        nombre = self.inputNombre.text().strip().title()
        apellido = self.inputApellido.text().strip().title()
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

        nacimiento = fecha_birth.toString("yyyy-MM-dd")

        # LOGICA UPDATE VS SAVE (MVC: Using Controller)
        if "Generado" in id_actual or not id_actual:
            # ES NUEVO
            if self.controller.crear_estudiante(nombre, apellido, carrera, nacimiento, correo, activo):
                QMessageBox.information(self, "Exito", "Estudiante registrado correctamente")
                self.limpiar_formulario()
                self.cargar_tabla()
            else:
                QMessageBox.critical(self, "Error", "Error al guardar estudiante")
        else:
            # ES EDICION
            if self.controller.actualizar_estudiante(id_actual, nombre, apellido, carrera, nacimiento, correo, activo):
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
        
        # UI Setup
        from PyQt6.QtCore import QDate
        from PyQt6.QtCore import Qt
        self.dateFecha.setDate(QDate.currentDate())
        self.cargar_combos()
        self.cargar_tabla()
        
        # Connections
        self.btnMatricular.clicked.connect(self.registrar_matricula)
        self.btnLimpiar.clicked.connect(self.limpiar_formulario)
        self.btnEliminar.clicked.connect(self.eliminar_seleccionado)
        self.inputBuscar.textChanged.connect(self.filtrar_tabla)

    def cargar_combos(self):
        self.comboEstudiante.clear()
        self.comboCurso.clear()
        
        # Estudiantes
        estudiantes = self.db.obtener_estudiantes(activos=True) # Filtramos activos
        for est in estudiantes:
            self.comboEstudiante.addItem(f"{est['nombre']} {est['apellido']} ({est['id']})", est['id'])
            
        # Cursos
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
        fecha = self.dateFecha.date().toString("yyyy-MM-dd")
        periodo = self.comboPeriodo.currentText()
        estado = self.comboEstado.currentText()
        
        exito, msg = self.db.registrar_matricula(id_est, cod_curso, fecha, periodo, estado)
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
            # Guardamos ID y Curso ocultos para eliminar
            item_est = QTableWidgetItem(m['estudiante'])
            item_est.setData(Qt.ItemDataRole.UserRole, m['id_est'])
            
            item_cur = QTableWidgetItem(m['curso'])
            item_cur.setData(Qt.ItemDataRole.UserRole, m['cod_curso'])
            
            self.tableMatriculas.setItem(i, 0, item_est)
            self.tableMatriculas.setItem(i, 1, item_cur)
            self.tableMatriculas.setItem(i, 2, QTableWidgetItem(m['fecha']))
            self.tableMatriculas.setItem(i, 3, QTableWidgetItem(m.get('periodo', '')))
            self.tableMatriculas.setItem(i, 4, QTableWidgetItem(m.get('estado', '')))

    def eliminar_seleccionado(self):
        row = self.tableMatriculas.currentRow()
        if row >= 0:
            est_name = self.tableMatriculas.item(row, 0).text()
            cur_name = self.tableMatriculas.item(row, 1).text()
            
            id_est = self.tableMatriculas.item(row, 0).data(Qt.ItemDataRole.UserRole)
            cod_curso = self.tableMatriculas.item(row, 1).data(Qt.ItemDataRole.UserRole)
            
            response = QMessageBox.question(
                self, "Confirmar", 
                f"¿Eliminar matrícula de\n{est_name}\nen {cur_name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if response == QMessageBox.StandardButton.Yes:
                if self.db.eliminar_matricula(id_est, cod_curso):
                    QMessageBox.information(self, "Exito", "Matrícula eliminada")
                    self.cargar_tabla()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo eliminar")
        else:
            QMessageBox.warning(self, "Aviso", "Seleccione una matrícula de la tabla.")

    def limpiar_formulario(self):
        self.comboEstudiante.setCurrentIndex(-1)
        self.comboCurso.setCurrentIndex(-1)
        from PyQt6.QtCore import QDate
        self.dateFecha.setDate(QDate.currentDate())
        self.comboPeriodo.setCurrentIndex(0)
        self.comboEstado.setCurrentIndex(0)

    def filtrar_tabla(self, texto):
        texto = texto.lower().strip()
        for i in range(self.tableMatriculas.rowCount()):
            item_est = self.tableMatriculas.item(i, 0)
            item_cur = self.tableMatriculas.item(i, 1)
            
            mostrar = (texto in item_est.text().lower() or 
                       texto in item_cur.text().lower())
            self.tableMatriculas.setRowHidden(i, not mostrar)


class VentanaNotas(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        uic.loadUi("ui/form_notas.ui", self)
        self.db = db_manager
        self.controller = NotaController(db_manager)  # MVC: Controller
        
        # Init
        self.cargar_cursos()
        
        # Conexiones
        self.comboCurso.currentIndexChanged.connect(self.cargar_tabla)
        self.btnGuardar.clicked.connect(self.guardar_nota)
        self.btnLimpiar.clicked.connect(self.limpiar_formulario)
        self.inputBuscar.textChanged.connect(self.filtrar_tabla)
        
        # Seleccion Tabla -> Cargar en Formulario
        self.tableNotas.cellClicked.connect(self.cargar_alumno_seleccionado)
        
        # Cargar inicial
        self.cargar_tabla()

    def cargar_cursos(self):
        self.comboCurso.clear()
        cursos = self.db.obtener_cursos()
        for c in cursos:
            self.comboCurso.addItem(f"{c['nombre']} ({c['codigo']})", c['codigo'])

    def cargar_tabla(self):
        idx = self.comboCurso.currentIndex()
        if idx == -1: return
        
        cod_curso = self.comboCurso.itemData(idx)
        
        # 1. Obtenemos matriculados (Roster base)
        matriculados = self.db.obtener_matriculados(cod_curso)
        
        # 2. Obtenemos notas existentes (Diccionario para O(1))
        notas_dict = self.db.obtener_notas_diccionario(cod_curso)
        
        self.tableNotas.setRowCount(0)
        self.tableNotas.setSortingEnabled(False)
        
        for i, est in enumerate(matriculados):
            self.tableNotas.insertRow(i)
            
            # Datos ocultos para facilitar guardado
            item_id = QTableWidgetItem(est['id'])
            self.tableNotas.setItem(i, 0, item_id)
            self.tableNotas.setItem(i, 1, QTableWidgetItem(est['nombre']))
            self.tableNotas.setItem(i, 2, QTableWidgetItem(est['apellido']))
            
            # Buscar si tiene notas
            notas = notas_dict.get(est['id'], {})
            n1 = notas.get('n1', 0.0)
            n2 = notas.get('n2', 0.0)
            n3 = notas.get('n3', 0.0)
            prom = notas.get('promedio', 0.0)
            
            self.tableNotas.setItem(i, 3, QTableWidgetItem(str(n1)))
            self.tableNotas.setItem(i, 4, QTableWidgetItem(str(n2)))
            self.tableNotas.setItem(i, 5, QTableWidgetItem(str(n3)))
            self.tableNotas.setItem(i, 6, QTableWidgetItem(str(prom)))
            
    def cargar_alumno_seleccionado(self, row, col):
        id_est = self.tableNotas.item(row, 0).text()
        nombre = self.tableNotas.item(row, 1).text()
        apellido = self.tableNotas.item(row, 2).text()
        
        n1 = float(self.tableNotas.item(row, 3).text())
        n2 = float(self.tableNotas.item(row, 4).text())
        n3 = float(self.tableNotas.item(row, 5).text())
        prom = self.tableNotas.item(row, 6).text()
        
        self.inputEstudiante.setText(f"{nombre} {apellido} ({id_est})")
        self.inputEstudiante.setProperty("id_oculto", id_est) # Guardamos ID en propiedad dinàmica
        
        self.spinN1.setValue(n1)
        self.spinN2.setValue(n2)
        self.spinN3.setValue(n3)
        self.inputPromedio.setText(prom)

    def guardar_nota(self):
        id_est_txt = self.inputEstudiante.text()
        if not id_est_txt:
            QMessageBox.warning(self, "Aviso", "Seleccione un alumno de la tabla primero.")
            return

        # Extraer ID (usando regex o la propiedad oculta si PyQt lo mantiene, mejor parseamos string o usamos fila seleccionada)
        # Manera segura: Recobrar de la fila seleccionada, pero el usuario pudo cambiar seleccion...
        # Usaremos propiedad dinamica si es posible, sino parseamos el texto
        try:
            # "Nombre Apellido (ID)" -> split '(', take last, remove ')'
            id_est = id_est_txt.split('(')[-1].replace(')', '')
        except:
             QMessageBox.warning(self, "Error", "No se pudo identificar al alumno.")
             return

        idx_curso = self.comboCurso.currentIndex()
        if idx_curso == -1: return
        cod_curso = self.comboCurso.itemData(idx_curso)

        n1 = self.spinN1.value()
        n2 = self.spinN2.value()
        n3 = self.spinN3.value()
        
        # MVC: Using Controller
        if self.controller.registrar_nota(id_est, cod_curso, n1, n2, n3):
            QMessageBox.information(self, "Exito", "Notas actualizadas correctamente.")
            self.cargar_tabla()
            self.limpiar_formulario()
        else:
            QMessageBox.critical(self, "Error", "Falló al guardar notas.")

    def limpiar_formulario(self):
        self.inputEstudiante.clear()
        self.spinN1.setValue(0)
        self.spinN2.setValue(0)
        self.spinN3.setValue(0)
        self.inputPromedio.clear()
        
    def filtrar_tabla(self, texto):
        texto = texto.lower().strip()
        for i in range(self.tableNotas.rowCount()):
            item_nom = self.tableNotas.item(i, 1)
            item_ape = self.tableNotas.item(i, 2)
            
            mostrar = (texto in item_nom.text().lower() or 
                       texto in item_ape.text().lower())
            self.tableNotas.setRowHidden(i, not mostrar)





class VentanaAsistencia(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        uic.loadUi("ui/form_asistencia.ui", self)
        self.db = db_manager
        self.controller = AsistenciaController(db_manager) # Instanciar Controlador
        
        # Init
        self.calendarWidget.setSelectedDate(QDate.currentDate())
        self.date_selected = QDate.currentDate().toString("yyyy-MM-dd")
        
        self.cargar_cursos()
        
        # Conexiones
        self.calendarWidget.selectionChanged.connect(self.on_date_changed)
        self.comboCurso.currentIndexChanged.connect(self.cargar_tabla)
        self.tableAsistencia.cellClicked.connect(self.cambiar_estado_celda)
        self.btnGuardar.clicked.connect(self.guardar_cambios)
        
        # Carga Inicial
        self.cargar_tabla()

    def cargar_cursos(self):
        self.comboCurso.clear()
        cursos = self.db.obtener_cursos()
        for c in cursos:
            self.comboCurso.addItem(f"{c['nombre']} ({c['codigo']})", c['codigo'])

    def on_date_changed(self):
        new_date = self.calendarWidget.selectedDate()
        hoy = QDate.currentDate()
        
        # Validación 1: No futuro
        if new_date > hoy:
             QMessageBox.warning(self, "Alerta", "No puedes registrar asistencia en fechas futuras.")
             self.calendarWidget.setSelectedDate(hoy)
             return
        
        # Validación 2: Max 2 dias atras
        limit = hoy.addDays(-2)
        if new_date < limit:
             QMessageBox.warning(self, "Alerta", "Solo puedes editar asistencia de los últimos 2 días.")
             self.calendarWidget.setSelectedDate(hoy)
             return

        self.date_selected = new_date.toString("yyyy-MM-dd")
        self.cargar_tabla()

    def cargar_tabla(self):
        idx = self.comboCurso.currentIndex()
        if idx == -1: return
        cod_curso = self.comboCurso.itemData(idx)
        
        # Estudiantes Matriculados
        estudiantes = self.db.obtener_matriculados(cod_curso)
        
        # Asistencia existente (si hay)
        # Optimizar esto en un futuro con un metodo en el controller que devuelva todo listo
        # Por ahora mantenemos logica de DB directa para lectura, y controller para escritura
        # Ojo: Para MVP MVC refactor, nos enfocamos en el "Guardar" que es el requerimiento principal
        
        self.tableAsistencia.setRowCount(0)
        
        for i, est in enumerate(estudiantes):
            self.tableAsistencia.insertRow(i)
            # ID
            self.tableAsistencia.setItem(i, 0, QTableWidgetItem(est['id']))
            # Nombre
            self.tableAsistencia.setItem(i, 1, QTableWidgetItem(est['nombre']))
            # Apellido
            self.tableAsistencia.setItem(i, 2, QTableWidgetItem(est['apellido']))
            
            # Estado (Buscar si ya tiene)
            estado = self.db.obtener_asistencia(est['id'], cod_curso, self.date_selected)
            texto_estado = estado if estado else "-"
            
            item_estado = QTableWidgetItem(texto_estado)
            item_estado.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._colorear_item(item_estado, texto_estado)
            
            self.tableAsistencia.setItem(i, 3, item_estado)

    def cambiar_estado_celda(self, row, col):
        if col == 3: # Columna Estado
            item = self.tableAsistencia.item(row, col)
            actual = item.text()
            
            # Ciclo de estados
            nuevo = "-"
            if actual == "-" or actual == "Ausente": new_st = "Presente"
            elif actual == "Presente": new_st = "Tardanza"
            elif actual == "Tardanza": new_st = "Ausente"
            else: new_st = "Presente"
            
            item.setText(new_st)
            self._colorear_item(item, new_st)

    def _colorear_item(self, item, estado):
        if estado == "Presente":
            item.setBackground(QColor(46, 204, 113)) # Verde
            item.setForeground(QColor("white"))
        elif estado == "Tardanza":
            item.setBackground(QColor(241, 196, 15)) # Amarillo
            item.setForeground(QColor("black"))
        elif estado == "Ausente":
            item.setBackground(QColor(231, 76, 60)) # Rojo
            item.setForeground(QColor("white"))
        else:
            item.setBackground(QColor("white"))
            item.setForeground(QColor("black"))

    def guardar_cambios(self):
        idx = self.comboCurso.currentIndex()
        if idx == -1: return
        cod_curso = self.comboCurso.itemData(idx)
        fecha = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        
        count = 0
        for i in range(self.tableAsistencia.rowCount()):
            id_est = self.tableAsistencia.item(i, 0).text()
            estado = self.tableAsistencia.item(i, 3).text()
            
            if estado in ["Presente", "Tardanza", "Ausente"]:
                # MVC REFACTOR: Usar Controller
                self.controller.registrar_asistencia(id_est, cod_curso, fecha, estado)
                count += 1
                
        QMessageBox.information(self, "Guardado", f"Se actualizaron {count} registros de asistencia.")



import csv
import json
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QTextDocument

class VentanaReportes(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        uic.loadUi("ui/form_reportes.ui", self)
        self.db = db_manager
        
        # UI Init
        self.dateFecha.setDate(QDate.currentDate())
        self.cargar_filtros()
        
        # Connections
        self.comboTipoReporte.currentIndexChanged.connect(self.actualizar_visibilidad_filtros)
        self.btnPreview.clicked.connect(self.generar_vista_previa)
        self.btnPdf.clicked.connect(self.exportar_pdf)
        self.btnCsv.clicked.connect(self.exportar_csv)
        self.btnJson.clicked.connect(self.exportar_json)
        
        # Initial State
        self.actualizar_visibilidad_filtros()

    def cargar_filtros(self):
        # Cursos
        self.comboCurso.clear()
        cursos = self.db.obtener_cursos()
        for c in cursos:
            self.comboCurso.addItem(f"{c['nombre']} ({c['codigo']})", c['codigo'])
            
        # Estudiantes (Todos)
        self.comboEstudiante.clear()
        self.comboEstudiante.addItem("Todos", None)
        estudiantes = self.db.obtener_estudiantes(activos=True)
        for est in estudiantes:
            self.comboEstudiante.addItem(f"{est['nombre']} {est['apellido']}", est['id'])

    def actualizar_visibilidad_filtros(self):
        tipo = self.comboTipoReporte.currentText()
        
        # Default visibility
        self.labelCurso.setVisible(True)
        self.comboCurso.setVisible(True)
        self.labelEstudiante.setVisible(True)
        self.comboEstudiante.setVisible(True)
        self.labelFecha.setVisible(False)
        self.dateFecha.setVisible(False)
        
        if tipo == "Historial Académico":
            self.labelCurso.setVisible(False)
            self.comboCurso.setVisible(False)
        elif tipo == "Lista de Asistencia":
            self.labelEstudiante.setVisible(False)
            self.comboEstudiante.setVisible(False)
        elif tipo == "Padrón de Matrícula":
            self.labelEstudiante.setVisible(False)
            self.comboEstudiante.setVisible(False)
        elif tipo == "Rendimiento / Riesgo":
             self.labelCurso.setVisible(False) # Global
             self.comboCurso.setVisible(False) 
             self.labelEstudiante.setVisible(False)
             self.comboEstudiante.setVisible(False)

    def generar_vista_previa(self):
        tipo = self.comboTipoReporte.currentText()
        data = []
        headers = []
        
        if tipo == "Historial Académico":
            headers = ["Curso", "N1", "N2", "N3", "Promedio", "Estado"]
            idx_est = self.comboEstudiante.currentIndex()
            id_est = self.comboEstudiante.itemData(idx_est)
            
            if not id_est:
                QMessageBox.warning(self, "Aviso", "Seleccione un estudiante")
                return
                
            # Logica: Buscar notas de este estudiante en todos los cursos
            notas_todas = self.db.obtener_todas_las_notas()
            # Filtrar
            notas_est = [n for n in notas_todas if n['id'] == id_est]
            
            for n in notas_est:
                valid_prom = float(n['promedio']) if n['promedio'] else 0.0
                estado = "Aprobado" if valid_prom >= 13 else "Desaprobado"
                data.append([n['curso'], str(n['n1']), str(n['n2']), str(n['n3']), str(n['promedio']), estado])

        elif tipo == "Lista de Asistencia":
            headers = ["ID", "Nombre", "Fecha", "Estado"]
            idx_cur = self.comboCurso.currentIndex()
            cod_curso = self.comboCurso.itemData(idx_cur)
            
            asistencias = self.db.obtener_historial_asistencia(cod_curso)
            estudiantes = {e['id']: f"{e['nombre']} {e['apellido']}" for e in self.db.obtener_estudiantes()}
            
            for a in asistencias:
                nombre = estudiantes.get(a['id_est'], "Desconocido")
                data.append([a['id_est'], nombre, a['fecha'], a['estado']])

        elif tipo == "Padrón de Matrícula":
            headers = ["ID", "Nombre", "Apellido", "Carrera", "Correo"]
            idx_cur = self.comboCurso.currentIndex()
            cod_curso = self.comboCurso.itemData(idx_cur)
            
            matriculados = self.db.obtener_matriculados(cod_curso)
            for m in matriculados:
                data.append([m['id'], m['nombre'], m['apellido'], m['carrera'], m['correo']])

        elif tipo == "Rendimiento / Riesgo":
            headers = ["ID", "Nombre", "Curso", "Promedio", "Estado"]
            notas = self.db.obtener_todas_las_notas()
            for n in notas:
                 prom = float(n['promedio'])
                 estado = "Riesgo" if prom < 13 else "OK"
                 # Solo mostrar riesgo? O todo? Mostremos todo y ordenemos
                 data.append([n['id'], n['nombre'], n['curso'], str(prom), estado])
        
        self._llenar_tabla(headers, data)

    def _llenar_tabla(self, headers, data):
        self.tablePreview.setColumnCount(len(headers))
        self.tablePreview.setHorizontalHeaderLabels(headers)
        self.tablePreview.setRowCount(0)
        self.tablePreview.horizontalHeader().setStretchLastSection(True)
        
        for i, row in enumerate(data):
            self.tablePreview.insertRow(i)
            for j, val in enumerate(row):
                self.tablePreview.setItem(i, j, QTableWidgetItem(str(val)))

    def exportar_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar CSV", "", "CSV Files (*.csv)")
        if not path: return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Headers
                headers = [self.tablePreview.horizontalHeaderItem(i).text() for i in range(self.tablePreview.columnCount())]
                writer.writerow(headers)
                
                # Data
                for i in range(self.tablePreview.rowCount()):
                    row = []
                    for j in range(self.tablePreview.columnCount()):
                        item = self.tablePreview.item(i, j)
                        row.append(item.text() if item else "")
                    writer.writerow(row)
            QMessageBox.information(self, "Exito", "Reporte exportado a CSV")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def exportar_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar JSON", "", "JSON Files (*.json)")
        if not path: return
        
        data = []
        headers = [self.tablePreview.horizontalHeaderItem(i).text() for i in range(self.tablePreview.columnCount())]
        
        for i in range(self.tablePreview.rowCount()):
            obj = {}
            for j, header in enumerate(headers):
                 item = self.tablePreview.item(i, j)
                 obj[header] = item.text() if item else ""
            data.append(obj)
            
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Exito", "Reporte exportado a JSON")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def exportar_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar PDF", "", "PDF Files (*.pdf)")
        if not path: return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        
        # Build HTML
        html = "<h1>Reporte Generado</h1>"
        html += f"<h3>Tipo: {self.comboTipoReporte.currentText()}</h3>"
        html += "<table border='1' cellspacing='0' cellpadding='5' width='100%'>"
        
        # Headers
        html += "<thead><tr>"
        headers = [self.tablePreview.horizontalHeaderItem(i).text() for i in range(self.tablePreview.columnCount())]
        for h in headers: html += f"<th style='background-color:#eee;'>{h}</th>"
        html += "</tr></thead><tbody>"
        
        # Rows
        for i in range(self.tablePreview.rowCount()):
            html += "<tr>"
            for j in range(self.tablePreview.columnCount()):
                item = self.tablePreview.item(i, j)
                val = item.text() if item else ""
                html += f"<td>{val}</td>"
            html += "</tr>"
        html += "</tbody></table>"
        
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print(printer)
        
        QMessageBox.information(self, "Exito", "Reporte explortado a PDF")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_manager = DataManager("notas_db.txt")
    window = MainApp(db_manager)
    window.show()
    sys.exit(app.exec())
