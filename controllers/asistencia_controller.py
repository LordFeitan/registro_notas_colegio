from model.asistencia import Asistencia

class AsistenciaController:
    def __init__(self, db_manager):
        self.db = db_manager

    def registrar_asistencia(self, id_estudiante, cod_curso, fecha, estado):
        """
        Recibe datos de la Vista, crea un Objeto Asistencia (Validación),
        y lo pasa a la capa de Datos.
        """
        try:
            # 1. Creacion del Objeto (Aqui ocurre la validacion y encapsulamiento)
            nueva_asistencia = Asistencia(id_estudiante, cod_curso, fecha, estado)
            
            # 2. Persistencia (Desempaquetamos para el DataManager actual)
            # Nota: Idealmente el DataManager deberia recibir el objeto completo,
            # pero para no romper compatibilidad pasamos los datos primitivos.
            return self.db.registrar_asistencia(
                nueva_asistencia.estudiante_id,
                nueva_asistencia.curso_id,
                nueva_asistencia.fecha,
                nueva_asistencia.estado
            )
        except ValueError as e:
            print(f"Error de validación en controlador: {e}")
            return False
