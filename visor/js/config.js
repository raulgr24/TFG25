/**
 * Configuración global de la aplicación
 * @module config
 */

const CONFIG = {
    // Rutas de datos
    data: {
        folder: './Datos nuevos/',
        municipios: 'municipios.geojson',
        centroides: 'centroides.geojson',
        metadata: 'metadata.jsonld'
    },
    
    // Centro inicial del mapa (España)
    map: {
        center: {
            lon: -3.703,
            lat: 40.416
        },
        initialZoom: 6,
        minZoom: 3,
        maxZoom: 18,
        projection: 'EPSG:3857'
    },
    
    // Configuración de capas
    layers: {
        municipios: {
            name: 'Municipios',
            icon: 'fas fa-draw-polygon',
            color: '#3388ff',
            fillOpacity: 0.2,
            strokeWidth: 1,
            visible: true,
            opacity: 0.6
        },
        centroides: {
            name: 'Centroides',
            icon: 'fas fa-map-pin',
            color: '#dc3545',
            radius: 6,
            visible: true,
            opacity: 0.8
        }
    },
    
    // Mapas base disponibles
    basemaps: {
        osm: {
            name: 'OpenStreetMap',
            url: 'https://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attribution: '© OpenStreetMap contributors'
        },
        topo: {
            name: 'Topográfico',
            url: 'https://tile.opentopomap.org/{z}/{x}/{y}.png',
            attribution: '© OpenTopoMap'
        },
        satellite: {
            name: 'Satélite',
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attribution: '© Esri'
        },
        dark: {
            name: 'Oscuro',
            url: 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}.png',
            attribution: '© Stadia Maps'
        }
    },
    
    // Configuración de herramientas
    tools: {
        measure: {
            type: 'LineString',
            style: {
                color: '#ffcc33',
                width: 2,
                lineDash: [10, 10]
            }
        },
        draw: {
            type: 'Polygon',
            style: {
                fillColor: 'rgba(255, 255, 255, 0.2)',
                strokeColor: '#ffcc33',
                strokeWidth: 2
            }
        }
    },
    
    // Configuración de popup
    popup: {
        autoPan: true,
        autoPanAnimation: {
            duration: 250
        },
        maxWidth: 300
    },
    
    // Estilos por defecto
    styles: {
        default: {
            fillColor: 'rgba(0, 0, 0, 0.1)',
            strokeColor: '#000000',
            strokeWidth: 1
        },
        hover: {
            fillColor: 'rgba(255, 255, 0, 0.3)',
            strokeColor: '#ff0000',
            strokeWidth: 2
        },
        selected: {
            fillColor: 'rgba(0, 255, 0, 0.3)',
            strokeColor: '#00ff00',
            strokeWidth: 3
        }
    },
    
    // Opciones de exportación
    export: {
        formats: ['png', 'pdf'],
        defaultFormat: 'png',
        quality: 0.95
    },
    
    // Mensajes de la aplicación
    messages: {
        loading: 'Cargando datos...',
        loadError: 'Error al cargar los datos',
        noFeatureSelected: 'Haz clic en un elemento del mapa para ver su información',
        measureResult: 'Distancia medida: ',
        exportSuccess: 'Mapa exportado correctamente',
        exportError: 'Error al exportar el mapa'
    },
    
    // Configuración de debug
    debug: {
        enabled: true,
        logLevel: 'info' // 'error', 'warn', 'info', 'debug'
    }
};

// Función helper para obtener la URL completa de los datos
CONFIG.getDataUrl = function(dataset) {
    return this.data.folder + this.data[dataset];
};

// Función para logging condicional
CONFIG.log = function(message, level = 'info') {
    if (this.debug.enabled) {
        const levels = ['error', 'warn', 'info', 'debug'];
        const currentLevelIndex = levels.indexOf(this.debug.logLevel);
        const messageLevelIndex = levels.indexOf(level);
        
        if (messageLevelIndex <= currentLevelIndex) {
            console[level](message);
        }
    }
};

// Hacer CONFIG inmutable en producción
if (!CONFIG.debug.enabled) {
    Object.freeze(CONFIG);
}
