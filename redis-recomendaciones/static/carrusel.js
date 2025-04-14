document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.carrusel').forEach(carrusel => {
        const container = carrusel.parentElement;
        const prevBtn = container.querySelector('.prev');
        const nextBtn = container.querySelector('.next');
        const items = carrusel.querySelectorAll('.item');
        const itemWidth = 215; // Ancho de ítem (200px) + gap (15px)

        // Clonar ítems suficientes veces para efecto circular
        const clonesNeeded = Math.ceil(carrusel.clientWidth / (itemWidth * items.length)) + 1;
        for (let i = 0; i < clonesNeeded; i++) {
            items.forEach(item => {
                const clone = item.cloneNode(true);
                carrusel.appendChild(clone);
            });
        }

        // Posicionar en el primer conjunto de ítems reales
        carrusel.scrollLeft = itemWidth * items.length;

        // Botón "Siguiente"
        nextBtn.addEventListener('click', () => {
            carrusel.scrollBy({ left: itemWidth, behavior: 'smooth' });
            // Verificar si está cerca del final
            if (carrusel.scrollLeft + carrusel.clientWidth >= carrusel.scrollWidth - itemWidth) {
                carrusel.scrollLeft = itemWidth * items.length;
            }
        });

        // Botón "Anterior"
        prevBtn.addEventListener('click', () => {
            carrusel.scrollBy({ left: -itemWidth, behavior: 'smooth' });
            // Verificar si está al inicio
            if (carrusel.scrollLeft <= itemWidth * items.length - itemWidth) {
                carrusel.scrollLeft = carrusel.scrollWidth - carrusel.clientWidth - itemWidth * items.length;
            }
        });

        // Ajuste circular al desplazar manualmente
        carrusel.addEventListener('scroll', () => {
            const maxScroll = carrusel.scrollWidth - carrusel.clientWidth;
            const middleScroll = itemWidth * items.length;

            if (carrusel.scrollLeft >= maxScroll - itemWidth) {
                carrusel.scrollLeft = middleScroll;
            } else if (carrusel.scrollLeft <= middleScroll - itemWidth) {
                carrusel.scrollLeft = maxScroll - itemWidth * items.length;
            }
        });
    });
});