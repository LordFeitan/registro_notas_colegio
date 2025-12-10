from .estudiante import Estudiante

class Curso:
    def __init__(self, nombre_curso, codigo):
        self.nombre = nombre_curso
        self.codigo = codigo
        self.estudiantes_inscritos = []

    def agregar_estudiante(self, estudiante: Estudiante):
        self.estudiantes_inscritos.append(estudiante)

    def listar_estudiantes(self):
        for est in self.estudiantes_inscritos:
            print(est.mostrar_info())
