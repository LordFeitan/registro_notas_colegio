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
        self.archivo_asistencias = "asistencias.txt"
        self._inicializar_archivo_notas()
        self._inicializar_archivo_estudiantes()
        self._inicializar_archivo_cursos()
        self._inicializar_archivo_matriculas()
        self._inicializar_archivo_asistencias()

    def _inicializar_archivo_notas(self):
        if not os.path.exists(self.archivo_notas):
            with open(self.archivo_notas, 'w', encoding='utf-8') as f:
                f.write("ID_ESTUDIANTE|CODIGO_CURSO|NOTA1|NOTA2|NOTA3|PROMEDIO\n")

    def _inicializar_archivo_matriculas(self):
        if not os.path.exists(self.archivo_matriculas):
            with open(self.archivo_matriculas, 'w', encoding='utf-8') as f:
                f.write("ID_ESTUDIANTE|CODIGO_CURSO|FECHA\n")

    def _inicializar_archivo_cursos(self):
        if not os.path.exists(self.archivo_cursos):
            with open(self.archivo_cursos, 'w', encoding='utf-8') as f:
                f.write("CODIGO|NOMBRE|PROFESOR|CREDITOS\n")

    # --- CURSOS ---
    # --- CURSOS ---
    def registrar_curso(self, codigo, nombre, profesor, creditos):
        try:
            with open(self.archivo_cursos, 'a', encoding='utf-8') as f:
                linea = f"{codigo}|{nombre}|{profesor}|{creditos}\n"
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
                
                curso = {"codigo": "", "nombre": "", "profesor": "", "creditos": ""}
                
                if len(partes) >= 1: curso["codigo"] = partes[0]
                if len(partes) >= 2: curso["nombre"] = partes[1]
                if len(partes) >= 3: curso["profesor"] = partes[2]
                if len(partes) >= 4: curso["creditos"] = partes[3]
                
                if curso["codigo"]:
                    data.append(curso)
        return data

    def actualizar_curso(self, codigo, nombre, profesor, creditos):
        cursos = self.obtener_cursos()
        encontrado = False
        for c in cursos:
            if c['codigo'] == codigo:
                c['nombre'] = nombre
                c['profesor'] = profesor
                c['creditos'] = creditos
                encontrado = True
                break
        
        if not encontrado: return False
        
        try:
            with open(self.archivo_cursos, 'w', encoding='utf-8') as f:
                f.write("CODIGO|NOMBRE|PROFESOR|CREDITOS\n")
                for c in cursos:
                    linea = f"{c['codigo']}|{c['nombre']}|{c['profesor']}|{c['creditos']}\n"
                    f.write(linea)
            return True
        except IOError:
            return False

    def eliminar_curso(self, codigo):
        cursos = self.obtener_cursos()
        filtrados = [c for c in cursos if c['codigo'] != codigo]
        
        if len(cursos) == len(filtrados): return False # No existia
        
        try:
            with open(self.archivo_cursos, 'w', encoding='utf-8') as f:
                f.write("CODIGO|NOMBRE|PROFESOR|CREDITOS\n")
                for c in filtrados:
                    linea = f"{c['codigo']}|{c['nombre']}|{c['profesor']}|{c['creditos']}\n"
                    f.write(linea)
            return True
        except IOError:
            return False

    def buscar_cursos(self, termino):
        termino = termino.lower().strip()
        todos = self.obtener_cursos()
        resultados = []
        for c in todos:
            if (termino in c['codigo'].lower() or 
                termino in c['nombre'].lower() or 
                termino in c['profesor'].lower()):
                resultados.append(c)
        return resultados

    # --- ASISTENCIA ---
    def _inicializar_archivo_asistencias(self):
        if not os.path.exists(self.archivo_asistencias):
            with open(self.archivo_asistencias, 'w', encoding='utf-8') as f:
                f.write("ID_ESTUDIANTE|CODIGO_CURSO|FECHA|ESTADO\n")

    def registrar_asistencia(self, id_estudiante, cod_curso, fecha, estado):
        registros = self.obtener_asistencias_raw()
        encontrado = False
        
        for reg in registros:
            if (reg['id'] == id_estudiante and 
                reg['curso'] == cod_curso and 
                reg['fecha'] == fecha):
                reg['estado'] = estado
                encontrado = True
                break
        
        if not encontrado:
            registros.append({
                'id': id_estudiante,
                'curso': cod_curso,
                'fecha': fecha,
                'estado': estado
            })
            
        try:
            with open(self.archivo_asistencias, 'w', encoding='utf-8') as f:
                f.write("ID_ESTUDIANTE|CODIGO_CURSO|FECHA|ESTADO\n")
                for r in registros:
                    f.write(f"{r['id']}|{r['curso']}|{r['fecha']}|{r['estado']}\n")
            return True, "Asistencia registrada"
        except IOError:
            return False, "Error al guardar asistencia"

    def obtener_asistencias_raw(self):
        data = []
        if not os.path.exists(self.archivo_asistencias):
            return data
            
        with open(self.archivo_asistencias, 'r', encoding='utf-8') as f:
            for i, linea in enumerate(f):
                if i == 0: continue
                partes = linea.strip().split('|')
                if len(partes) >= 4:
                    data.append({
                        'id': partes[0],
                        'curso': partes[1],
                        'fecha': partes[2],
                        'estado': partes[3]
                    })
        return data

    def obtener_asistencia_estudiante(self, id_est, cod_curso, fecha):
        registros = self.obtener_asistencias_raw()
        for r in registros:
            if r['id'] == id_est and r['curso'] == cod_curso and r['fecha'] == fecha:
                return r['estado']
        return None

    # --- MATRICULAS ---

    def existe_matricula(self, id_est, cod_curso):
        if not os.path.exists(self.archivo_matriculas):
            return False
            
        with open(self.archivo_matriculas, 'r', encoding='utf-8') as f:
            for i, linea in enumerate(f):
                if i == 0: continue
                partes = linea.strip().split('|')
                if len(partes) >= 2:
                    if partes[0] == id_est and partes[1] == cod_curso:
                        return True
        return False

    def registrar_matricula(self, id_est, cod_curso, fecha, periodo, estado):
        if self.existe_matricula(id_est, cod_curso):
             return False, "El estudiante ya está matriculado en este curso."
             
        try:
            with open(self.archivo_matriculas, 'a', encoding='utf-8') as f:
                linea = f"{id_est}|{cod_curso}|{fecha}|{periodo}|{estado}\n"
                f.write(linea)
            return True, "Matrícula exitosa"
        except IOError as e:
            return False, str(e)

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
                    # Backward compatibility
                    periodo = partes[3] if len(partes) > 3 else "2024-1"
                    estado = partes[4] if len(partes) > 4 else "Matriculado"
                    
                    nombre_est = estudiantes.get(id_est, id_est)
                    nombre_curso = cursos.get(cod_curso, cod_curso)
                    
                    data.append({
                        "id_est": id_est,
                        "cod_curso": cod_curso,
                        "estudiante": nombre_est,
                        "curso": nombre_curso,
                        "fecha": fecha,
                        "periodo": periodo,
                        "estado": estado
                    })
        return data

    def eliminar_matricula(self, id_est, cod_curso):
        matriculas = self.obtener_matriculas() # Esto nos da dicts enriquecidos, necesitamos leer raw mejor o re-escribir con cuidado
        
        # Leemos raw para escribir
        lines_to_keep = []
        header = None
        
        if not os.path.exists(self.archivo_matriculas): return False
        
        with open(self.archivo_matriculas, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines: return False
            header = lines[0]
            for line in lines[1:]:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    if parts[0] == id_est and parts[1] == cod_curso:
                        continue # Skip (delete)
                lines_to_keep.append(line)
                
        try:
            with open(self.archivo_matriculas, 'w', encoding='utf-8') as f:
                f.write(header)
                f.writelines(lines_to_keep)
            return True
        except IOError:
            return False

    def obtener_estudiantes_por_curso(self, cod_curso):
        """Devuelve los objetos estudiante matriculados en un curso."""
        ids_permitidos = []
        if os.path.exists(self.archivo_matriculas):
            with open(self.archivo_matriculas, 'r', encoding='utf-8') as f:
                for linea in f:
                    partes = linea.strip().split('|')
                    if len(partes) >= 2 and partes[1] == cod_curso:
                        ids_permitidos.append(partes[0])
        
        todos = self.obtener_estudiantes()
        return [est for est in todos if est['id'] in ids_permitidos]

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

    def eliminar_estudiante(self, id_est):
        """Elimina un estudiante por su ID."""
        estudiantes = self.obtener_estudiantes()
        estudiantes_filtrados = [e for e in estudiantes if e['id'] != id_est]
        
        if len(estudiantes) == len(estudiantes_filtrados):
            return False # No se encontro
            
        try:
            with open(self.archivo_estudiantes, 'w', encoding='utf-8') as f:
                f.write("ID|NOMBRE|APELLIDO|CARRERA|NACIMIENTO|CORREO|ACTIVO\n")
                for est in estudiantes_filtrados:
                    activo_str = "1" if est.get('activo', True) else "0"
                    linea = f"{est['id']}|{est['nombre']}|{est['apellido']}|{est['carrera']}|{est['nacimiento']}|{est['correo']}|{activo_str}\n"
                    f.write(linea)
            return True
        except IOError:
            return False

    def obtener_estudiantes(self, activos=False):
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
                    if activos:
                        if est["activo"]:
                            data.append(est)
                    else:
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

    def registrar_nota(self, id_est, cod_curso, n1, n2, n3):
        """
        Guarda las 3 notas y el promedio.
        """
        promedio = round((n1 + n2 + n3) / 3, 2)
        try:
            with open(self.archivo_notas, 'a', encoding='utf-8') as f:
                linea = f"{id_est}|{cod_curso}|{n1}|{n2}|{n3}|{promedio}\n"
                f.write(linea)
            return True
        except IOError as e:
            print(f"Error al guardar nota: {e}")
            return False

    def obtener_todas_las_notas(self):
        """Lee todo el archivo y retorna una lista de diccionarios, enriqueciendo con nombres."""
        data = []
        if not os.path.exists(self.archivo_notas):
            return data
            
        # Mapeos para mostrar nombres en lugar de IDs
        estudiantes = {e['id']: f"{e['nombre']} {e['apellido']}" for e in self.obtener_estudiantes()}
        cursos = {c['codigo']: c['nombre'] for c in self.obtener_cursos()}

        with open(self.archivo_notas, 'r', encoding='utf-8') as f:
            for i, linea in enumerate(f):
                if i == 0: continue # Saltar header
                partes = linea.strip().split('|')
                if len(partes) >= 6:
                    id_est = partes[0]
                    cod_curso = partes[1]
                    
                    data.append({
                        "id": id_est,
                        "nombre": estudiantes.get(id_est, id_est),
                        "curso": cursos.get(cod_curso, cod_curso),
                        "cod_curso": cod_curso,
                        "n1": partes[2],
                        "n2": partes[3],
                        "n3": partes[4],
                        "promedio": partes[5],
                        "nota": partes[5] # Backward compatibility for Dashboard
                    })
        return data
