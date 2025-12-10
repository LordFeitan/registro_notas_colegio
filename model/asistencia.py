from datetime import datetime
import uuid

class Asistencia:
    def __init__(self, estudiante_id, curso_id, fecha=None, estado="Presente", asistencia_id=None):
        self.__id = asistencia_id if asistencia_id else str(uuid.uuid4())[:8]
        self.__estudiante_id = estudiante_id
        self.__curso_id = curso_id
        self.__fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d")
        self.__estado = estado
        self.__hora_registro = datetime.now().strftime("%H:%M:%S")

    @property
    def id(self):
        return self.__id

    @property
    def estudiante_id(self):
        return self.__estudiante_id

    @property
    def curso_id(self):
        return self.__curso_id

    @property
    def fecha(self):
        return self.__fecha

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, nuevo_estado):
        if nuevo_estado in ["Presente", "Tardanza", "Ausente"]:
            self.__estado = nuevo_estado
        else:
            raise ValueError("Estado inválido")

    def to_dict(self):
        """Para compatibilidad con el sistema de archivos actual"""
        return {
            "id": self.__estudiante_id, # Mapping to legacy format which used student ID as primary key ref in simple lists
            "curso": self.__curso_id,
            "fecha": self.__fecha,
            "estado": self.__estado
        }
