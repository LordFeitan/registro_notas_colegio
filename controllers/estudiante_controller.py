from model.estudiante import Estudiante

class EstudianteController:
    def __init__(self, db_manager):
        self.db = db_manager

    def crear_estudiante(self, nombre, apellido, carrera, nacimiento, correo, activo=True):
        """
        Crea un nuevo estudiante usando el modelo Estudiante.
        Aplica validaciones y encapsulamiento antes de persistir.
        """
        try:
            # Aquí podríamos instanciar un objeto Estudiante si tuviera lógica de validación
            # Por ahora, delegamos a DataManager que ya tiene la lógica
            return self.db.registrar_estudiante(nombre, apellido, carrera, nacimiento, correo, activo)
        except Exception as e:
            print(f"Error en controlador al crear estudiante: {e}")
            return False

    def actualizar_estudiante(self, id_estudiante, nombre, apellido, carrera, nacimiento, correo, activo):
        """
        Actualiza un estudiante existente.
        """
        try:
            return self.db.actualizar_estudiante(id_estudiante, nombre, apellido, carrera, nacimiento, correo, activo)
        except Exception as e:
            print(f"Error en controlador al actualizar estudiante: {e}")
            return False

    def eliminar_estudiante(self, id_estudiante):
        """
        Elimina un estudiante.
        """
        try:
            return self.db.eliminar_estudiante(id_estudiante)
        except Exception as e:
            print(f"Error en controlador al eliminar estudiante: {e}")
            return False

    def buscar_estudiantes(self, termino):
        """
        Busca estudiantes por término de búsqueda.
        """
        try:
            return self.db.buscar_estudiantes(termino)
        except Exception as e:
            print(f"Error en controlador al buscar estudiantes: {e}")
            return []

    def obtener_estudiantes(self, activos=False):
        """
        Obtiene lista de estudiantes.
        """
        try:
            return self.db.obtener_estudiantes(activos=activos)
        except Exception as e:
            print(f"Error en controlador al obtener estudiantes: {e}")
            return []
