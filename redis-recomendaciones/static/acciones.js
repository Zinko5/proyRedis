document.addEventListener('DOMContentLoaded', () => {
    // Manejar todos los formularios de acciones
    document.querySelectorAll('.accion-form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Obtener el botón que fue clickeado
            const botonClickeado = e.submitter;
            const accion = botonClickeado.value;
            
            // Crear FormData y agregar la acción
            const formData = new FormData(form);
            formData.set('accion', accion); // Asegurarnos que la acción se incluya
            
            try {
                // Enviar la acción de manera asíncrona
                const response = await fetch('/actualizar_preferencias', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('Error al actualizar preferencias');
                }
                
                // Actualizar estado visual de los botones
                const likeBtn = form.querySelector('button[value="like"]');
                const dislikeBtn = form.querySelector('button[value="dislike"]');
                
                // Remover clase active de ambos botones
                likeBtn.classList.remove('active');
                dislikeBtn.classList.remove('active');
                
                // Agregar clase active al botón clickeado
                botonClickeado.classList.add('active');
                
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });
}); 