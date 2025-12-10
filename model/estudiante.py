from .persona import Persona

class Estudiante(Persona):
    """
    Clase Hija de Persona.
    Aplica HERENCIA para reutilizar atributos básicos.
    """
    def __init__(self, id_persona, nombre, apellido, carrera):
        super().__init__(id_persona, nombre, apellido)
        self.carrera = carrera
        self.__notas = {}        # Atributo privado para guardar notas por curso
        self.__asistencias = []  # Atributo privado para historial de asistencia

    def registrar_nota(self, curso, nota):
        """
        Método para registrar una calificación.
        Valida que la nota esté en rango (ENCAPSULAMIENTO de lógica).
        """
        if 0 <= nota <= 20:
            self.__notas[curso] = nota
            return True
        else:
            print(f"Error: La nota {nota} no es válida (0-20).")
            return False

    def registrar_asistencia(self, fecha, estado):
        self.__asistencias.append({"fecha": fecha, "estado": estado})

    def obtener_promedio(self):
        if not self.__notas:
            return 0.0
        return sum(self.__notas.values()) / len(self.__notas)

    def mostrar_info(self):
        # Polimorfismo: Reutiliza el método padre y agrega info específica
        base_info = super().mostrar_info()
        return f"{base_info} | Carrera: {self.carrera} | Promedio: {self.obtener_promedio():.2f}"
