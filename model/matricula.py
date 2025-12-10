from datetime import datetime

class Matricula:
    def __init__(self, estudiante_id, curso_id, fecha=None, periodo="2024-1", estado="Matriculado"):
        self.__estudiante_id = estudiante_id
        self.__curso_id = curso_id
        self.__fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d")
        self.__periodo = periodo
        self.__estado = estado

    @property
    def estudiante_id(self): return self.__estudiante_id

    @property
    def curso_id(self): return self.__curso_id
    
    @property
    def fecha(self): return self.__fecha

    @property
    def periodo(self): return self.__periodo

    @property
    def estado(self): return self.__estado

    def to_dict(self):
        return {
            "id_estudiante": self.__estudiante_id,
            "codigo_curso": self.__curso_id,
            "fecha": self.__fecha,
            "periodo": self.__periodo,
            "estado": self.__estado
        }
