from model.nota import Nota

class NotaController:
    def __init__(self, db_manager):
        self.db = db_manager

    def registrar_nota(self, id_estudiante, cod_curso, n1, n2, n3):
        """
        Registra o actualiza notas usando el modelo Nota.
        Aplica validaciones mediante el modelo antes de persistir.
        """
        try:
            # Crear objeto Nota (validación automática en setters)
            nota = Nota(id_estudiante, cod_curso, n1, n2, n3)
            
            # Validar rango de notas (0-20)
            if not (0 <= n1 <= 20 and 0 <= n2 <= 20 and 0 <= n3 <= 20):
                raise ValueError("Las notas deben estar entre 0 y 20")
            
            # Persistir usando DataManager
            return self.db.registrar_nota(id_estudiante, cod_curso, n1, n2, n3)
        except ValueError as e:
            print(f"Error de validación en NotaController: {e}")
            return False
        except Exception as e:
            print(f"Error en controlador al registrar nota: {e}")
            return False

    def obtener_notas_por_curso(self, cod_curso):
        """
        Obtiene todas las notas de un curso específico.
        """
        try:
            return self.db.obtener_notas_por_curso(cod_curso)
        except Exception as e:
            print(f"Error en controlador al obtener notas: {e}")
            return []

    def obtener_todas_las_notas(self):
        """
        Obtiene todas las notas del sistema.
        """
        try:
            return self.db.obtener_todas_las_notas()
        except Exception as e:
            print(f"Error en controlador al obtener todas las notas: {e}")
            return []
