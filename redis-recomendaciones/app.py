from flask import Flask, render_template, request, redirect, url_for, jsonify
import redis

# Configurar Flask
app = Flask(__name__)

# Conectar a Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Datos iniciales con catálogo y popularidad
def inicializar_datos():
    # Solo inicializar si no hay datos (para persistencia)
    if not r.exists("user:1:genres"):
        print("Inicializando datos...")
        # Usuarios iniciales y sus géneros favoritos
        r.sadd("user:1:genres", "acción", "suspense", "ciencia ficción", "drama")
        r.hset("user:1:info", "nombre", "Ana")
        r.hset("user:1:info", "apellido", "Gómez")
        r.hset("user:1:info", "icono", "/static/icons/icon1.png")
        
        r.sadd("user:2:genres", "comedia", "aventura", "animación", "romance")
        r.hset("user:2:info", "nombre", "Luis")
        r.hset("user:2:info", "apellido", "Martínez")
        r.hset("user:2:info", "icono", "/static/icons/icon2.png")
        
        r.sadd("user:3:genres", "drama", "romance", "documental", "comedia")
        r.hset("user:3:info", "nombre", "Sofía")
        r.hset("user:3:info", "apellido", "López")
        r.hset("user:3:info", "icono", "/static/icons/icon3.png")
        
        r.sadd("user:4:genres", "terror", "suspense", "acción", "ciencia ficción")
        r.hset("user:4:info", "nombre", "Carlos")
        r.hset("user:4:info", "apellido", "Pérez")
        r.hset("user:4:info", "icono", "/static/icons/icon4.png")

        # Catálogo de películas y series por género con popularidad
        catalog = {
            "acción": {
                "películas": [
                    ("Matrix", 95), ("John Wick", 90), ("The Dark Knight", 98), ("Mad Max: Fury Road", 87),
                    ("Die Hard", 85), ("Mission: Impossible - Fallout", 82), ("Gladiator", 80), ("Speed", 78),
                    ("Avengers: Endgame", 92), ("The Raid", 75)
                ],
                "series": [
                    ("The Mandalorian", 93), ("Jack Ryan", 85), ("The Boys", 88), ("24", 80)
                ]
            },
            "drama": {
                "películas": [
                    ("The Shawshank Redemption", 98), ("Forrest Gump", 95), ("The Godfather", 97), ("Parasite", 94),
                    ("Schindler's List", 92), ("12 Years a Slave", 89), ("Fight Club", 91), ("The Green Mile", 87),
                    ("A Beautiful Mind", 85), ("American Beauty", 83), ("The Dark Knight", 98), ("Gladiator", 80),
                    ("Parasite", 94)
                ],
                "series": [
                    ("Breaking Bad", 96), ("The Crown", 90), ("This Is Us", 85), ("The Sopranos", 92),
                    ("The Boys", 88)
                ]
            },
            "comedia": {
                "películas": [
                    ("The Hangover", 88), ("Superbad", 85), ("Anchorman", 82), ("Step Brothers", 80),
                    ("Groundhog Day", 87), ("Mean Girls", 84), ("21 Jump Street", 83), ("The Grand Budapest Hotel", 90),
                    ("Crazy Rich Asians", 86), ("Deadpool", 89), ("Parasite", 94)
                ],
                "series": [
                    ("The Office", 94), ("Parks and Recreation", 90), ("Brooklyn Nine-Nine", 88), ("Friends", 92),
                    ("The Boys", 88)
                ]
            },
            "ciencia ficción": {
                "películas": [
                    ("Inception", 95), ("Blade Runner 2049", 88), ("Interstellar", 93), ("The Matrix", 94),
                    ("Star Wars: The Empire Strikes Back", 92), ("Arrival", 89), ("Ex Machina", 87), ("Her", 85),
                    ("Dune", 91), ("Back to the Future", 90), ("Avengers: Endgame", 92)
                ],
                "series": [
                    ("Stranger Things", 93), ("Westworld", 89), ("Black Mirror", 87), ("The Expanse", 85),
                    ("The Mandalorian", 93)
                ]
            },
            "aventura": {
                "películas": [
                    ("Indiana Jones: Raiders of the Lost Ark", 94), ("Jurassic Park", 90), 
                    ("Pirates of the Caribbean: The Curse of the Black Pearl", 88), ("The Hobbit", 85),
                    ("Jumanji: Welcome to the Jungle", 83), ("The Lord of the Rings: The Fellowship of the Ring", 95),
                    ("The Mummy", 80), ("King Kong", 78), ("The Revenant", 87), ("Zootopia", 86),
                    ("Star Wars: The Empire Strikes Back", 92), ("Avengers: Endgame", 92), ("Back to the Future", 90)
                ],
                "series": [
                    ("Lost", 88), ("The Witcher", 90), ("His Dark Materials", 85), ("The Mandalorian", 93)
                ]
            },
            "romance": {
                "películas": [
                    ("The Notebook", 87), ("La La Land", 91), ("Pride and Prejudice", 85), ("Amélie", 89),
                    ("Titanic", 90), ("Before Sunrise", 86), ("Crazy Stupid Love", 83), ("Silver Linings Playbook", 88),
                    ("The Fault in Our Stars", 84), ("Eternal Sunshine of the Spotless Mind", 90),
                    ("Crazy Rich Asians", 86), ("Groundhog Day", 87)
                ],
                "series": [
                    ("Outlander", 87), ("Bridgerton", 89), ("Normal People", 85), ("Jane the Virgin", 83),
                    ("This Is Us", 85)
                ]
            },
            "terror": {
                "películas": [
                    ("The Shining", 92), ("Get Out", 90), ("Hereditary", 88), ("The Exorcist", 87),
                    ("A Quiet Place", 85), ("It", 84), ("Halloween", 83), ("The Conjuring", 86),
                    ("Midsommar", 89), ("Scream", 82)
                ],
                "series": [
                    ("The Haunting of Hill House", 90), ("American Horror Story", 85), ("Stranger Things", 93), ("Penny Dreadful", 84)
                ]
            },
            "animación": {
                "películas": [
                    ("Toy Story", 95), ("Spider-Man: Into the Spider-Verse", 93), ("The Lion King", 92), ("Finding Nemo", 90),
                    ("Inside Out", 89), ("Coco", 91), ("Shrek", 88), ("Frozen", 87),
                    ("Moana", 86), ("Up", 90), ("Zootopia", 86)
                ],
                "series": [
                    ("Avatar: The Last Airbender", 94), ("Rick and Morty", 90), ("BoJack Horseman", 89), ("The Simpsons", 87)
                ]
            },
            "suspense": {
                "películas": [
                    ("Se7en", 93), ("Gone Girl", 90), ("Prisoners", 88), ("Shutter Island", 87),
                    ("The Sixth Sense", 86), ("Zodiac", 85), ("Memento", 91), ("No Country for Old Men", 89),
                    ("The Girl with the Dragon Tattoo", 84), ("Oldboy", 83), ("Fight Club", 91), ("Inception", 95),
                    ("Get Out", 90)
                ],
                "series": [
                    ("True Detective", 92), ("Your Honor", 85), ("Fargo", 90), ("Mindhunter", 88),
                    ("Black Mirror", 87), ("Westworld", 89)
                ]
            },
            "documental": {
                "películas": [
                    ("Free Solo", 90), ("Won't You Be My Neighbor?", 88), ("Blackfish", 87), ("The Social Dilemma", 86)
                ],
                "series": [
                    ("Planet Earth", 95), ("The Last Dance", 93), ("13th", 90), ("My Octopus Teacher", 89),
                    ("March of the Penguins", 87), ("Making a Murderer", 85), ("Cosmos", 88), ("Tiger King", 84)
                ]
            }
        }

        # Cargar catálogo en Redis
        for genero, tipos in catalog.items():
            for tipo, titulos in tipos.items():
                for titulo, popularidad in titulos:
                    # Agregar el título al set del género
                    r.sadd(f"genre:{genero}:{tipo}", titulo)
                    # Guardar la popularidad y contadores
                    r.hset(f"title:{titulo}", "popularidad", popularidad)
                    r.hset(f"title:{titulo}", "likes", 0)
                    r.hset(f"title:{titulo}", "dislikes", 0)
                    # Guardar los géneros del título en un set
                    r.sadd(f"title:{titulo}:genres", genero)

def actualizar_preferencias(user_id, titulo, accion):
    """Actualiza las preferencias del usuario y ajusta los géneros favoritos"""
    # Guardar la preferencia del usuario para este título
    r.hset(f"user:{user_id}:preferencias_titulos", titulo, accion)
    
    # Encontrar los géneros del título
    generos_titulo = set()
    for genero in r.keys("genre:*:películas"):
        if r.sismember(genero, titulo):
            genero_nombre = genero.split(":")[1]
            generos_titulo.add(genero_nombre)
    for genero in r.keys("genre:*:series"):
        if r.sismember(genero, titulo):
            genero_nombre = genero.split(":")[1]
            generos_titulo.add(genero_nombre)
    
    if accion == 'like':
        r.hincrby(f"title:{titulo}", "likes", 1)
        # Si antes tenía dislike, lo removemos
        if r.hget(f"user:{user_id}:preferencias_titulos", titulo) == 'dislike':
            r.hincrby(f"title:{titulo}", "dislikes", -1)
        
        # Aumentar preferencia por los géneros
        for genero in generos_titulo:
            r.zincrby(f"user:{user_id}:preferencias", 2, genero)  # Aumentado a 2 para hacer más significativo el impacto
            
    elif accion == 'dislike':
        r.hincrby(f"title:{titulo}", "dislikes", 1)
        # Si antes tenía like, lo removemos
        if r.hget(f"user:{user_id}:preferencias_titulos", titulo) == 'like':
            r.hincrby(f"title:{titulo}", "likes", -1)
        
        # Reducir preferencia por los géneros
        for genero in generos_titulo:
            r.zincrby(f"user:{user_id}:preferencias", -1, genero)
            
            # Contar cuántos dislikes tiene en este género
            dislikes_en_genero = 0
            titulos_genero = r.smembers(f"genre:{genero}:películas").union(r.smembers(f"genre:{genero}:series"))
            for t in titulos_genero:
                if r.hget(f"user:{user_id}:preferencias_titulos", t) == 'dislike':
                    dislikes_en_genero += 1
            
            # Si más del 40% de los títulos vistos del género tienen dislike, remover el género de preferencias
            titulos_vistos = sum(1 for t in titulos_genero if r.hexists(f"user:{user_id}:preferencias_titulos", t))
            if titulos_vistos > 0 and (dislikes_en_genero / titulos_vistos) > 0.4:
                # Remover el género de las preferencias iniciales si existe
                r.srem(f"user:{user_id}:genres", genero)
                # Dar una penalización fuerte en las preferencias
                r.zadd(f"user:{user_id}:preferencias", {genero: -100})

def obtener_preferencias_usuario(user_id):
    """Obtiene todas las preferencias de títulos del usuario"""
    return r.hgetall(f"user:{user_id}:preferencias_titulos")

def obtener_generos_titulo(titulo):
    """Obtiene los géneros de un título específico"""
    return sorted(list(r.smembers(f"title:{titulo}:genres")))

def calcular_similitud_usuarios(user_id):
    """Calcula la similitud entre el usuario actual y otros usuarios"""
    similitudes = {}
    user_genres = r.smembers(f"user:{user_id}:genres")
    user_preferences = r.hgetall(f"user:{user_id}:preferencias_titulos")
    
    # Obtener todos los usuarios
    all_users = set()
    for key in r.keys("user:*:genres"):
        uid = int(key.split(":")[1])
        if uid != user_id:  # Excluir al usuario actual
            all_users.add(uid)
    
    for other_user in all_users:
        score = 0
        
        # Similitud por géneros (30% del peso)
        other_genres = r.smembers(f"user:{other_user}:genres")
        genres_in_common = len(user_genres.intersection(other_genres))
        total_genres = len(user_genres.union(other_genres))
        if total_genres > 0:
            score += (genres_in_common / total_genres) * 30
        
        # Similitud por preferencias de títulos (70% del peso)
        other_preferences = r.hgetall(f"user:{other_user}:preferencias_titulos")
        common_titles = set(user_preferences.keys()).intersection(other_preferences.keys())
        if common_titles:
            matches = sum(1 for title in common_titles 
                        if user_preferences[title] == other_preferences[title])
            score += (matches / len(common_titles)) * 70
        
        similitudes[other_user] = score
    
    # Ordenar usuarios por similitud y devolver los más similares
    return sorted(similitudes.items(), key=lambda x: x[1], reverse=True)

def obtener_recomendaciones_colaborativas(user_id, limite=10):
    """Obtiene recomendaciones basadas en usuarios similares"""
    usuarios_similares = calcular_similitud_usuarios(user_id)
    titulos_recomendados = {}
    preferencias_usuario = r.hgetall(f"user:{user_id}:preferencias_titulos")
    
    # Considerar solo los usuarios con similitud > 40
    usuarios_relevantes = [u for u, score in usuarios_similares if score > 40]
    
    for similar_user in usuarios_relevantes[:5]:  # Usar top 5 usuarios similares
        prefs_similar = r.hgetall(f"user:{similar_user}:preferencias_titulos")
        
        for titulo, accion in prefs_similar.items():
            # Solo considerar títulos que le gustaron al usuario similar
            # y que el usuario actual no ha visto
            if accion == 'like' and titulo not in preferencias_usuario:
                if titulo not in titulos_recomendados:
                    titulos_recomendados[titulo] = {
                        'score': 0,
                        'count': 0
                    }
                # Aumentar score basado en cuántos usuarios similares les gusta
                titulos_recomendados[titulo]['score'] += 1
                titulos_recomendados[titulo]['count'] += 1
    
    # Ordenar por score y obtener los títulos
    recomendaciones_ordenadas = sorted(
        [(t, data['score'] / data['count']) 
         for t, data in titulos_recomendados.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    return [titulo for titulo, _ in recomendaciones_ordenadas[:limite]]

def recomendar_peliculas(user_id):
    """Genera recomendaciones basadas en preferencias del usuario y usuarios similares"""
    # Obtener todos los géneros y sus puntuaciones
    generos_puntuaciones = r.zrange(f"user:{user_id}:preferencias", 0, -1, withscores=True)
    generos_puntuaciones = dict(generos_puntuaciones)
    
    # Obtener géneros altamente preferidos (score > 40% del máximo posible)
    max_score = max(generos_puntuaciones.values()) if generos_puntuaciones else 0
    umbral_preferido = max_score * 0.4 if max_score > 0 else 0
    generos_preferidos = [g for g, score in generos_puntuaciones.items() if score > umbral_preferido]
    
    if not generos_preferidos:
        # Si no hay preferencias claras, usar géneros iniciales
        generos_preferidos = r.smembers(f"user:{user_id}:genres")
    
    # Obtener todos los géneros disponibles
    todos_generos = set()
    for key in r.keys("genre:*:películas"):
        genero = key.split(":")[1]
        todos_generos.add(genero)
    
    # Identificar géneros para descubrimiento
    generos_descubrimiento = todos_generos - set(generos_preferidos)
    
    # Obtener las calificaciones del usuario
    preferencias_usuario = r.hgetall(f"user:{user_id}:preferencias_titulos")
    
    # Obtener recomendaciones colaborativas
    recomendaciones_colaborativas = set(obtener_recomendaciones_colaborativas(user_id))
    
    total = set()
    peliculas = set()
    series = set()
    descubrimientos = set()
    
    # Agregar títulos de géneros preferidos
    for genero in generos_preferidos:
        if r.exists(f"genre:{genero}:películas"):
            peliculas.update(r.smembers(f"genre:{genero}:películas"))
        if r.exists(f"genre:{genero}:series"):
            series.update(r.smembers(f"genre:{genero}:series"))
    
    # Agregar recomendaciones colaborativas a los conjuntos correspondientes
    for titulo in recomendaciones_colaborativas:
        es_pelicula = any(r.sismember(f"genre:{g}:películas", titulo) for g in todos_generos)
        if es_pelicula:
            peliculas.add(titulo)
        else:
            series.add(titulo)
    
    # Agregar títulos para descubrimiento
    for genero in generos_descubrimiento:
        score = generos_puntuaciones.get(genero, 0)
        import random
        if score >= 0 or random.random() < (1 + score/10):
            if r.exists(f"genre:{genero}:películas"):
                descubrimientos.update(r.smembers(f"genre:{genero}:películas"))
            if r.exists(f"genre:{genero}:series"):
                descubrimientos.update(r.smembers(f"genre:{genero}:series"))
    
    total.update(peliculas, series)
    
    def calcular_puntuacion(titulo, es_descubrimiento=False):
        import random
        
        likes = int(r.hget(f"title:{titulo}", "likes") or 0)
        dislikes = int(r.hget(f"title:{titulo}", "dislikes") or 0)
        popularidad = float(r.hget(f"title:{titulo}", "popularidad") or 0)
        
        # Puntuación base (25% popularidad)
        puntuacion_base = popularidad * 0.25
        
        # Factor de likes/dislikes (50% del peso total)
        factor_likes = (likes * 0.5) - (dislikes * 0.5)
        puntuacion_base += factor_likes
        
        # Bonus por recomendación colaborativa (15% extra)
        if titulo in recomendaciones_colaborativas:
            puntuacion_base *= 1.15
        
        # Bonus por género (parte del 50% de likes)
        bonus_genero = 0
        generos_titulo = set()
        
        for genero in r.keys("genre:*:películas"):
            if r.sismember(genero, titulo):
                genero_nombre = genero.split(":")[1]
                generos_titulo.add(genero_nombre)
                if genero_nombre in generos_preferidos:
                    bonus_genero += 25  # Aumentado para dar más peso a géneros preferidos
                else:
                    score = generos_puntuaciones.get(genero_nombre, 0)
                    bonus_genero += max(0, score)
        
        # Penalización por dislikes
        penalizacion = 0
        for genero in generos_titulo:
            titulos_genero = r.smembers(f"genre:{genero}:películas").union(r.smembers(f"genre:{genero}:series"))
            dislikes_genero = sum(1 for t in titulos_genero if preferencias_usuario.get(t) == 'dislike')
            penalizacion += dislikes_genero * 3
        
        if preferencias_usuario.get(titulo) == 'dislike':
            penalizacion += 100
        
        # Factor aleatorio (10%)
        factor_aleatorio = random.uniform(-10, 10) if es_descubrimiento else random.uniform(-5, 5)
        
        return puntuacion_base + bonus_genero - penalizacion + factor_aleatorio
    
    def limitar_y_ordenar(items, limite=25, es_descubrimiento=False):
        import random
        
        if len(items) > limite:
            items_con_puntuacion = [(item, calcular_puntuacion(item, es_descubrimiento)) for item in items]
            items_ordenados = sorted(items_con_puntuacion, key=lambda x: x[1], reverse=True)
            
            pool_size = 60 if es_descubrimiento else 40
            top_items = items_ordenados[:min(pool_size, len(items_ordenados))]
            
            selected_items = random.sample(top_items, min(limite, len(top_items)))
            selected_items.sort(key=lambda x: x[1], reverse=True)
            
            items_seleccionados = [item[0] for item in selected_items]
        else:
            items_con_puntuacion = [(item, calcular_puntuacion(item, es_descubrimiento)) for item in items]
            items_ordenados = sorted(items_con_puntuacion, key=lambda x: x[1], reverse=True)
            items_seleccionados = [item[0] for item in items_ordenados]
        
        return [(item, obtener_generos_titulo(item)) for item in items_seleccionados]
    
    return {
        "total": limitar_y_ordenar(total),
        "peliculas": limitar_y_ordenar(peliculas),
        "series": limitar_y_ordenar(series),
        "descubrimientos": limitar_y_ordenar(descubrimientos, es_descubrimiento=True),
        "generos": sorted(list(generos_preferidos))
    }

# Ruta para la pantalla de inicio
@app.route('/')
def inicio():
    inicializar_datos()
    # Obtener todos los usuarios
    user_keys = r.keys("user:*:info")
    usuarios = []
    for key in sorted(user_keys):
        user_id = key.split(":")[1]
        info = r.hgetall(f"user:{user_id}:info")
        usuarios.append({"id": user_id, "nombre": info["nombre"], "apellido": info["apellido"], "icono": info["icono"]})
    return render_template('inicio.html', usuarios=usuarios)

# Ruta para crear cuenta
@app.route('/crear_cuenta', methods=['GET', 'POST'])
def crear_cuenta():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        icono = request.form['icono']
        
        # Generar nuevo ID
        user_keys = r.keys("user:*:genres")
        new_id = max([int(key.split(":")[1]) for key in user_keys] + [0]) + 1
        
        # Guardar datos
        r.hset(f"user:{new_id}:info", "nombre", nombre)
        r.hset(f"user:{new_id}:info", "apellido", apellido)
        r.hset(f"user:{new_id}:info", "icono", icono)
        
        return redirect(url_for('cuestionario', user_id=new_id))
    
    # Galería de íconos predefinida
    iconos = [
        "/static/icons/icon1.png",
        "/static/icons/icon2.png",
        "/static/icons/icon3.png",
        "/static/icons/icon4.png",
        "/static/icons/icon5.png",
        "/static/icons/icon6.png",
        "/static/icons/icon7.png",
        "/static/icons/icon8.png"
    ]
    return render_template('crear_cuenta.html', iconos=iconos)

# Ruta para el cuestionario
@app.route('/cuestionario/<int:user_id>', methods=['GET', 'POST'])
def cuestionario(user_id):
    if request.method == 'POST':
        generos = request.form.getlist('generos')
        if len(generos) >= 3:  # Validar al menos 3 géneros
            r.sadd(f"user:{user_id}:genres", *generos)
            # Inicializar las preferencias con los géneros seleccionados
            for genero in generos:
                r.zadd(f"user:{user_id}:preferencias", {genero: 1})
            print(generos)  # Esto debería mostrar la lista de géneros en la consola
            return redirect(url_for('inicio', user_id=user_id))
        else:
            return render_template('cuestionario.html', user_id=user_id, generos=[
                "acción", "drama", "comedia", "ciencia ficción", "aventura",
                "romance", "terror", "animación", "suspense", "documental"
            ], error="Por favor, selecciona al menos 3 géneros.")
    
    # Lista de géneros
    generos = [
        "acción", "drama", "comedia", "ciencia ficción", "aventura",
        "romance", "terror", "animación", "suspense", "documental"
    ]
    return render_template('cuestionario.html', user_id=user_id, generos=generos)

# Ruta para las recomendaciones
@app.route('/recomendaciones', methods=['GET', 'POST'])
@app.route('/recomendaciones/<int:user_id>')
def recomendaciones(user_id=None):
    # Asegurarse de que los datos estén inicializados
    inicializar_datos()
    
    recomendaciones = {"total": [], "peliculas": [], "series": [], "descubrimientos": [], "generos": []}
    preferencias_usuario = {}
    info_usuario = None
    
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
    
    if user_id:
        # Obtener información del usuario
        info_usuario = {
            'nombre': r.hget(f"user:{user_id}:info", "nombre"),
            'apellido': r.hget(f"user:{user_id}:info", "apellido"),
            'icono': r.hget(f"user:{user_id}:info", "icono")
        }
        
        # Obtener las preferencias del usuario
        preferencias_usuario = obtener_preferencias_usuario(user_id)
        
        # Asegurarse de que el usuario tenga géneros seleccionados
        if not r.exists(f"user:{user_id}:genres"):
            return redirect(url_for('cuestionario', user_id=user_id))
        
        # Usar la función recomendar_peliculas para obtener recomendaciones personalizadas
        recomendaciones = recomendar_peliculas(user_id)
    
    return render_template('recomendaciones.html', 
                         recomendaciones=recomendaciones, 
                         user_id=user_id, 
                         preferencias_usuario=preferencias_usuario,
                         info_usuario=info_usuario)

@app.route('/actualizar_preferencias', methods=['POST'])
def actualizar_preferencias_route():
    user_id = request.form['user_id']
    titulo = request.form['titulo']
    accion = request.form['accion']
    actualizar_preferencias(user_id, titulo, accion)
    return jsonify({'success': True, 'message': f'Preferencia actualizada: {accion} para {titulo}'})

@app.route('/eliminar_usuario', methods=['POST'])
def eliminar_usuario():
    data = request.get_json()
    user_id = data.get('user_id')
    if user_id:
        # Eliminar datos del usuario
        r.delete(f"user:{user_id}:genres")
        r.delete(f"user:{user_id}:info")
        r.delete(f"user:{user_id}:preferencias")
        r.delete(f"user:{user_id}:preferencias_titulos")
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'ID de usuario no proporcionado'})

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)

    