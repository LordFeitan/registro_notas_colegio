import re
import os

class DataManager:
    """
    Clase encargada de la persistencia de datos.
    Cumple con el criterio de 'Manejo de Archivos' y uso de 'Regex'.
    """
    def __init__(self, archivo_notas):
        self.archivo_notas = archivo_notas
        self.archivo_estudiantes = "estudiantes.txt"
        self.archivo_cursos = "cursos.txt"
        self.archivo_matriculas = "matriculas.txt"
        self._inicializar_archivo_notas()
        self._inicializar_archivo_estudiantes()
        self._inicializar_archivo_cursos()
        self._inicializar_archivo_matriculas()

    def _inicializar_archivo_notas(self):
        if not os.path.exists(self.archivo_notas):
            with open(self.archivo_notas, 'w', encoding='utf-8') as f:
                f.write("ID_ESTUDIANTE|NOMBRE_ESTUDIANTE|CURSO|NOTA\n")

    def _inicializar_archivo_matriculas(self):
        if not os.path.exists(self.archivo_matriculas):
            with open(self.archivo_matriculas, 'w', encoding='utf-8') as f:
                f.write("ID_ESTUDIANTE|CODIGO_CURSO|FECHA\n")

    def _inicializar_archivo_cursos(self):
        if not os.path.exists(self.archivo_cursos):
            with open(self.archivo_cursos, 'w', encoding='utf-8') as f:
                f.write("CODIGO|NOMBRE\n")

    # --- CURSOS ---
    def registrar_curso(self, codigo, nombre):
        try:
            with open(self.archivo_cursos, 'a', encoding='utf-8') as f:
                linea = f"{codigo}|{nombre}\n"
                f.write(linea)
            return True
        except IOError:
            return False

    def obtener_cursos(self):
        data = []
        if not os.path.exists(self.archivo_cursos):
            return data
        with open(self.archivo_cursos, 'r', encoding='utf-8') as f:
            for i, linea in enumerate(f):
                if i == 0: continue
                partes = linea.strip().split('|')
                if len(partes) >= 2:
                    data.append({"codigo": partes[0], "nombre": partes[1]})
        return data

    def buscar_cursos(self, termino):
        termino = termino.lower().strip()
        todos = self.obtener_cursos()
        resultados = []
        for c in todos:
            if termino in c['codigo'].lower() or termino in c['nombre'].lower():
                resultados.append(c)
        return resultados

    # --- MATRICULAS ---
    def registrar_matricula(self, id_estudiante, cod_curso, fecha):
        # Validar duplicados
        if self.existe_matricula(id_estudiante, cod_curso):
            return False, "El estudiante ya esta matriculado en este curso."
            
        try:
            with open(self.archivo_matriculas, 'a', encoding='utf-8') as f:
                linea = f"{id_estudiante}|{cod_curso}|{fecha}\n"
                f.write(linea)
            return True, "Matricula exitosa"
        except IOError:
            return False, "Error al escribir en archivo"

    def existe_matricula(self, id_est, cod_curso):
        if not os.path.exists(self.archivo_matriculas):
            return False
        with open(self.archivo_matriculas, 'r', encoding='utf-8') as f:
            for linea in f:
                partes = linea.strip().split('|')
                if len(partes) >= 2:
                    if partes[0] == id_est and partes[1] == cod_curso:
                        return True
        return False

    def obtener_matriculas(self):
        data = []
        if not os.path.exists(self.archivo_matriculas):
            return data
        
        # Necesitamos cruzar datos para mostrar nombres
        estudiantes = {e['id']: f"{e['nombre']} {e['apellido']}" for e in self.obtener_estudiantes()}
        cursos = {c['codigo']: c['nombre'] for c in self.obtener_cursos()}
        
        with open(self.archivo_matriculas, 'r', encoding='utf-8') as f:
            for i, linea in enumerate(f):
                if i == 0: continue
                partes = linea.strip().split('|')
                if len(partes) >= 3:
                    id_est = partes[0]
                    cod_curso = partes[1]
                    fecha = partes[2]
                    
                    nombre_est = estudiantes.get(id_est, id_est)
                    nombre_curso = cursos.get(cod_curso, cod_curso)
                    
                    data.append({
                        "estudiante": nombre_est,
                        "curso": nombre_curso,
                        "fecha": fecha
                    })
        return data

    def _inicializar_archivo_estudiantes(self):
        """Crea el archivo de estudiantes con cabeceras si no existe."""
        if not os.path.exists(self.archivo_estudiantes):
            with open(self.archivo_estudiantes, 'w', encoding='utf-8') as f:
                f.write("ID|NOMBRE|APELLIDO|CARRERA|NACIMIENTO|CORREO|ACTIVO\n")

    def registrar_estudiante(self, nombre, apellido, carrera, nacimiento, correo, activo=True):
        """
        Genera ID automatico y guarda al estudiante.
        """
        nuevo_id = self._generar_nuevo_id()
        activo_str = "1" if activo else "0"
        try:
            with open(self.archivo_estudiantes, 'a', encoding='utf-8') as f:
                linea = f"{nuevo_id}|{nombre}|{apellido}|{carrera}|{nacimiento}|{correo}|{activo_str}\n"
                f.write(linea)
            return True
        except IOError as e:
            print(f"Error al guardar estudiante: {e}")
            return False

    def actualizar_estudiante(self, id_est, nombre, apellido, carrera, nacimiento, correo, activo):
        estudiantes = self.obtener_estudiantes()
        encontrado = False
        
        # Actualizamos la lista en memoria
        for est in estudiantes:
            if est['id'] == id_est:
                est['nombre'] = nombre
                est['apellido'] = apellido
                est['carrera'] = carrera
                est['nacimiento'] = nacimiento
                est['correo'] = correo
                est['activo'] = activo
                encontrado = True
                break
        
        if not encontrado:
            return False
            
        # Reescribimos todo el archivo
        try:
            with open(self.archivo_estudiantes, 'w', encoding='utf-8') as f:
                f.write("ID|NOMBRE|APELLIDO|CARRERA|NACIMIENTO|CORREO|ACTIVO\n")
                for est in estudiantes:
                    activo_str = "1" if est.get('activo', True) else "0"
                    linea = f"{est['id']}|{est['nombre']}|{est['apellido']}|{est['carrera']}|{est['nacimiento']}|{est['correo']}|{activo_str}\n"
                    f.write(linea)
            return True
        except IOError:
            return False

    def obtener_estudiantes(self):
        data = []
        if not os.path.exists(self.archivo_estudiantes):
            return data
            
        with open(self.archivo_estudiantes, 'r', encoding='utf-8') as f:
            for i, linea in enumerate(f):
                if i == 0: continue 
                partes = linea.strip().split('|')
                
                est = {
                    "id": "", "nombre": "", "apellido": "", "carrera": "", 
                    "nacimiento": "", "correo": "", "activo": True
                }
                
                if len(partes) >= 1: est["id"] = partes[0]
                if len(partes) >= 2: est["nombre"] = partes[1]
                if len(partes) >= 3: est["apellido"] = partes[2]
                if len(partes) >= 4: est["carrera"] = partes[3]
                if len(partes) >= 5: est["nacimiento"] = partes[4]
                if len(partes) >= 6: est["correo"] = partes[5]
                if len(partes) >= 7: est["activo"] = (partes[6].strip() == "1")
                
                if est["id"]: # Solo agregar si tiene ID
                    data.append(est)
                    
        return data

    def _generar_nuevo_id(self):
        """Lee el ultimo ID del archivo y retorna el siguiente."""
        if not os.path.exists(self.archivo_estudiantes):
            return "2024001"
            
        ids = []
        try:
            with open(self.archivo_estudiantes, 'r', encoding='utf-8') as f:
                next(f) # Skip header
                for linea in f:
                    partes = linea.strip().split('|')
                    if partes and partes[0].isdigit():
                        ids.append(int(partes[0]))
        except:
            pass
            
        if not ids:
            return "2024001"
            
        return str(max(ids) + 1)

    def buscar_estudiantes(self, termino):
        """Busca estudiantes por ID, nombre o apellido (case insensitive)."""
        termino = termino.lower().strip()
        data = []
        todos = self.obtener_estudiantes()
        
        for est in todos:
            # Busqueda simple: si el termino esta en id, nombre, apellido, carrera o correo
            if (termino in est['id'].lower() or 
                termino in est['nombre'].lower() or 
                termino in est['apellido'].lower() or
                termino in est['carrera'].lower() or
                termino in est['correo'].lower()):
                data.append(est)
        return data

        return data

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
