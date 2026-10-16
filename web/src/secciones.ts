// Orden y textos fijos de las secciones de la página pública (docs/diseno.md §5.1). Aquí no van cifras: los datos salen de public/datos/.

export interface Seccion {
  id: string;
  numero: number;
  titulo: string;
  entrada: string;
  bases: string;
}

const LISTA: Omit<Seccion, 'numero'>[] = [
  {
    id: 'inicio',
    titulo: 'Inicio',
    entrada:
      'Cuánta atención digital recibe cada Pueblo Mágico de Puebla y cómo se compara con lo que pasa en el destino.',
    bases: 'Proyecto para el Hackathon «Puebla Turística 360°: datos que transforman experiencias», de Tech Capital 2026.',
  },
  {
    id: 'problema',
    titulo: 'El problema',
    entrada:
      'El turista decide a dónde ir viendo videos o preguntándole a un asistente. Hoy nadie mide qué encuentra ahí sobre Puebla.',
    bases: 'La convocatoria pide exponer el problema y la evidencia que lo sostiene (§8).',
  },
  {
    id: 'plataforma',
    titulo: 'La plataforma',
    entrada:
      'Cuatro vistas para decidir dónde promover: el radar de los 12 Pueblos Mágicos, la ficha de cada destino, lo que responden los asistentes y lo que se ve en redes.',
    bases: 'La convocatoria pide un prototipo funcional y demostrable (§8 y §9).',
  },
  {
    id: 'tianguis',
    titulo: 'Para el Tianguis 2027',
    entrada:
      'Cómo usa la Secretaría el radar rumbo al Tianguis Turístico y cómo se mide el efecto de la promoción antes y después.',
    bases: 'La convocatoria pide viabilidad, continuidad y escalamiento (§8 y §17).',
  },
  {
    id: 'metodo',
    titulo: 'Cómo se hizo',
    entrada: 'Fuentes, procesos, fórmulas y límites: lo necesario para revisar cada cifra.',
    bases: 'La convocatoria pide documentar los datos, la metodología y los componentes con IA (§9).',
  },
  {
    id: 'datos',
    titulo: 'Datos y código',
    entrada: 'Descarga las tablas y comprueba que son las mismas que usa el sitio.',
    bases: 'La convocatoria pide inventario de fuentes y reproducibilidad (§5, §9 y §12).',
  },
];

export const SECCIONES: Seccion[] = LISTA.map((s, i) => ({ ...s, numero: i + 1 }));

export function seccion(id: string): Seccion {
  const encontrada = SECCIONES.find((s) => s.id === id);
  if (!encontrada) throw new Error(`Sección desconocida: ${id}`);
  return encontrada;
}
