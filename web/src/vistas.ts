// Vistas de la plataforma (docs/diseno.md §5.2). Aquí no van cifras: los datos salen de public/datos/.

export interface Vista {
  id: 'radar' | 'fichas' | 'asistentes' | 'redes';
  titulo: string;
  descripcion: string;
  vacio: string;
}

export const VISTAS: Vista[] = [
  {
    id: 'radar',
    titulo: 'Radar',
    descripcion:
      'Qué Pueblos Mágicos reciben más atención de la que su ocupación refleja, y al revés.',
    vacio: 'Todavía no hay datos del radar. Aparecen al exportar el desempeño oficial y los componentes de atención.',
  },
  {
    id: 'fichas',
    titulo: 'Fichas',
    descripcion: 'Una hoja por destino, lista para imprimir y llevar a cada cita del Tianguis.',
    vacio: 'Todavía no hay fichas. Se generan junto con el radar.',
  },
  {
    id: 'asistentes',
    titulo: 'Asistentes',
    descripcion:
      'Qué destinos recomiendan los asistentes conversacionales en cinco idiomas y qué fuentes citan.',
    vacio: 'Todavía no hay corridas de asistentes publicadas.',
  },
  {
    id: 'redes',
    titulo: 'Redes',
    descripcion: 'Qué muestra TikTok a las personas del panel y qué se ve en YouTube sobre cada destino.',
    vacio: 'Todavía no hay resultados del panel ni de YouTube.',
  },
];
