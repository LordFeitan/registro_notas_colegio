class Nota:
    def __init__(self, estudiante_id, curso_id, n1=0.0, n2=0.0, n3=0.0):
        self.__estudiante_id = estudiante_id
        self.__curso_id = curso_id
        self.__n1 = float(n1)
        self.__n2 = float(n2)
        self.__n3 = float(n3)

    @property
    def promedio(self):
        return (self.__n1 + self.__n2 + self.__n3) / 3.0

    @property
    def estado(self):
        return "Aprobado" if self.promedio >= 13.0 else "Desaprobado"

    @property
    def n1(self): return self.__n1
    
    @n1.setter
    def n1(self, val):
        if 0 <= val <= 20: self.__n1 = val
        else: raise ValueError("Nota invalida")

    @property
    def n2(self): return self.__n2

    @n2.setter
    def n2(self, val):
        if 0 <= val <= 20: self.__n2 = val
        else: raise ValueError("Nota invalida")

    @property
    def n3(self): return self.__n3

    @n3.setter
    def n3(self, val):
        if 0 <= val <= 20: self.__n3 = val
        else: raise ValueError("Nota invalida")

    def to_dict(self):
        return {
            "nombre": "", # DataManager fills this usually
            "curso": self.__curso_id,
            "n1": self.__n1,
            "n2": self.__n2,
            "n3": self.__n3,
            "promedio": self.promedio
        }
