import re
import os

class DataManager:
    """
    Clase encargada de la persistencia de datos.
    Cumple con el criterio de 'Manejo de Archivos' y uso de 'Regex'.
    """
    def __init__(self, archivo_notas="notas.txt"):
        # Guardamos el archivo dentro de la misma carpeta data por defecto, o en config
        # Para simplificar, lo dejaremos en la raiz del proyecto o en data. 
        # Vamos a ponerlo en la raiz para facilitar su lectura manual por el usuario
        self.archivo_notas = archivo_notas
        self._inicializar_archivo()

    def _inicializar_archivo(self):
        """Crea el archivo con cabeceras si no existe."""
        if not os.path.exists(self.archivo_notas):
            with open(self.archivo_notas, 'w', encoding='utf-8') as f:
                f.write("ID|NOMBRE|CURSO|NOTA\n")

    def registrar_nota(self, id_est, nombre, curso, nota):
        """
        Guarda una nueva nota en el archivo de texto (Modo 'a' - Append).
        """
        try:
            with open(self.archivo_notas, 'a', encoding='utf-8') as f:
                linea = f"{id_est}|{nombre}|{curso}|{nota}\n"
                f.write(linea)
            return True
        except IOError as e:
            print(f"Error al guardar nota: {e}")
            return False

    def buscar_notas_por_estudiante(self, id_busqueda):
        """
        Busca todas las notas de un estudiante usando REGEX.
        Retorna lista de diccionarios.
        """
        resultados = []
        # Regex: Inicio de linea (^), ID exacto, seguido de pipe (|), y resto de linea (.*)
        patron = re.compile(rf"^{re.escape(id_busqueda)}\|.*$", re.MULTILINE)

        if not os.path.exists(self.archivo_notas):
            return []

        try:
            with open(self.archivo_notas, 'r', encoding='utf-8') as f:
                contenido = f.read()
                # Uso de Regex para encontrar coincidencias
                coincidencias = patron.findall(contenido)
                
                for linea in coincidencias:
                    # Parsear la linea pipe-separated para devolver objetos limpios
                    partes = linea.strip().split('|')
                    if len(partes) >= 4:
                        resultados.append({
                            "id": partes[0],
                            "nombre": partes[1],
                            "curso": partes[2],
                            "nota": partes[3]
                        })
        except Exception as e:
            print(f"Error al leer archivo: {e}")
        
        return resultados

    def obtener_todas_las_notas(self):
        """Lee todo el archivo y retorna una lista de diccionarios."""
        data = []
        if not os.path.exists(self.archivo_notas):
            return data
            
        with open(self.archivo_notas, 'r', encoding='utf-8') as f:
            for i, linea in enumerate(f):
                if i == 0: continue # Saltar header
                partes = linea.strip().split('|')
                if len(partes) >= 4:
                    data.append({
                        "id": partes[0],
                        "nombre": partes[1],
                        "curso": partes[2],
                        "nota": partes[3]
                    })
        return data
