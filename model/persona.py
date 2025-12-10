class Persona:
    """
    Clase Base que representa a una persona genérica.
    Aplica ENCAPSULAMIENTO protegiendo atributos sensibles como el DNI/ID.
    """
    def __init__(self, id_persona, nombre, apellido):
        self._id = id_persona      # Atributo protegido
        self._nombre = nombre      # Atributo protegido
        self._apellido = apellido  # Atributo protegido

    @property
    def id(self):
        return self._id

    @property
    def nombre_completo(self):
        return f"{self._nombre} {self._apellido}"
    
    def mostrar_info(self):
        """Método que será sobrescrito (POLIMORFISMO)"""
        return f"ID: {self._id} | Nombre: {self.nombre_completo}"
