import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

def cargar_csv_robusto(ruta_archivo):
    """Función para cargar CSV con diferentes configuraciones"""
    print(f"Intentando cargar archivo: {ruta_archivo}")
    
    # Verificar que el archivo existe
    if not os.path.exists(ruta_archivo):
        print(f"ERROR: El archivo {ruta_archivo} no existe")
        return None
    
    # Inspeccionar primeras líneas del archivo
    print("\nInspeccionando archivo...")
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f.readlines()[:5]):
                print(f"Línea {i+1}: {repr(line[:100])}")
    except UnicodeDecodeError:
        print("Problema con UTF-8, probando con latin-1...")
        with open(ruta_archivo, 'r', encoding='latin-1') as f:
            for i, line in enumerate(f.readlines()[:5]):
                print(f"Línea {i+1}: {repr(line[:100])}")
    
    # Diferentes configuraciones para probar
    configuraciones = [
        {'sep': ',', 'encoding': 'utf-8'},
        {'sep': ';', 'encoding': 'utf-8'},
        {'sep': ',', 'encoding': 'latin-1'},
        {'sep': ';', 'encoding': 'latin-1'},
        {'sep': '\t', 'encoding': 'utf-8'},
        {'sep': None, 'engine': 'python', 'encoding': 'utf-8'},
    ]
    
    for i, config in enumerate(configuraciones):
        try:
            print(f"\nProbando configuración {i+1}: {config}")
            df = pd.read_csv(ruta_archivo, **config)
            print(f"✓ ÉXITO - CSV cargado con configuración {i+1}")
            print(f"  Forma del DataFrame: {df.shape}")
            print(f"  Primeras 5 columnas: {list(df.columns[:5])}")
            return df
        except Exception as e:
            print(f"✗ Falló configuración {i+1}: {str(e)[:100]}")
            continue
    
    print("\nERROR: No se pudo cargar el archivo con ninguna configuración")
    return None

def analizar_datos(df):
    """Analizar y mostrar información básica del DataFrame"""
    print("\n" + "="*60)
    print("ANÁLISIS DE DATOS")
    print("="*60)
    print(f"Filas: {len(df)}")
    print(f"Columnas: {len(df.columns)}")
    print(f"\nPrimeras 10 columnas:")
    for i, col in enumerate(df.columns[:10]):
        print(f"  {i+1:2d}. {col}")
    
    # Buscar columnas de distancia
    columnas_distancia = [col for col in df.columns if 'w_avg_dis' in col and 'total' in col]
    print(f"\nColumnas de distancia encontradas:")
    for col in columnas_distancia:
        print(f"  - {col}")
    
    return columnas_distancia

def crear_histogramas(df):
    """Crear histogramas de las columnas de accesibilidad"""
    
    # Definir las columnas de interés
    columnas_servicios = {
        'w_avg_dis_B_total': 'Bomberos',
        'w_avg_dis_H2_total': 'Hospitales Grupo 2', 
        'w_avg_dis_H3_total': 'Hospitales Grupo 3',
        'w_avg_dis_J_total': 'Juzgados',
        'w_avg_dis_M_total': 'Centros Salud Mental',
        'w_avg_dis_total': 'Media Global'
    }
    
    # Verificar qué columnas existen en el DataFrame
    columnas_existentes = {}
    for col, nombre in columnas_servicios.items():
        if col in df.columns:
            columnas_existentes[col] = nombre
        else:
            print(f"ADVERTENCIA: Columna {col} no encontrada")
    
    if not columnas_existentes:
        print("ERROR: No se encontraron columnas de servicios")
        return
    
    print(f"\nCreando histogramas para {len(columnas_existentes)} servicios...")
    
    # Configurar matplotlib
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (15, 12)
    plt.rcParams['font.size'] = 10
    
    # Calcular número de subplots necesarios
    n_servicios = len(columnas_existentes)
    n_cols = 2
    n_rows = (n_servicios + 1) // 2
    
    # Crear subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4*n_rows))
    fig.suptitle('Distribución de Distancias a Servicios Públicos\nNúcleos Urbanos', 
                 fontsize=16, fontweight='bold')
    
    # Si solo hay una fila, convertir axes a array 2D
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    # Colores para cada histograma
    colores = ['#e74c3c', '#3498db', '#9b59b6', '#f39c12', '#27ae60', '#34495e']
    
    # Crear histogramas
    for i, (columna, nombre) in enumerate(columnas_existentes.items()):
        row = i // n_cols
        col = i % n_cols
        
        # Filtrar valores válidos
        datos_validos = df[columna].dropna()
        
        if len(datos_validos) > 0:
            # Crear histograma
            axes[row, col].hist(datos_validos, bins=20, color=colores[i % len(colores)], 
                               alpha=0.7, edgecolor='white', linewidth=0.5)
            
            # Configurar el subplot
            media = datos_validos.mean()
            axes[row, col].set_title(f'{nombre}\n(Media: {media:.0f}m, n={len(datos_validos)})', 
                                    fontweight='bold')
            axes[row, col].set_xlabel('Distancia (metros)')
            axes[row, col].set_ylabel('Frecuencia')
            axes[row, col].grid(True, alpha=0.3)
            
            # Agregar línea de media
            axes[row, col].axvline(media, color='red', linestyle='--', 
                                  alpha=0.8, label=f'Media: {media:.0f}m')
            axes[row, col].legend()
            
            # Estadísticas básicas
            print(f"\n{nombre}:")
            print(f"  Registros válidos: {len(datos_validos)}")
            print(f"  Media: {datos_validos.mean():.0f} metros")
            print(f"  Mediana: {datos_validos.median():.0f} metros")
            print(f"  Mín: {datos_validos.min():.0f} metros")
            print(f"  Máx: {datos_validos.max():.0f} metros")
            print(f"  Desv. Estándar: {datos_validos.std():.0f} metros")
        else:
            axes[row, col].text(0.5, 0.5, 'Sin datos válidos', 
                               ha='center', va='center', transform=axes[row, col].transAxes)
            axes[row, col].set_title(nombre)
    
    # Ocultar subplots vacíos
    for i in range(len(columnas_existentes), n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        axes[row, col].set_visible(False)
    
    # Ajustar layout con más espacio
    # plt.tight_layout()  # Comentado para usar ajuste manual
    plt.subplots_adjust(
        left=0.08,    # Margen izquierdo
        bottom=0.08,  # Margen inferior  
        right=0.95,   # Margen derecho
        top=0.92,     # Margen superior
        wspace=0.3,   # Espacio horizontal entre subplots
        hspace=0.4    # Espacio vertical entre subplots
    )
    plt.show()
    
    # Crear tabla resumen con casos extremos
    print("\n" + "="*80)
    print("RESUMEN ESTADÍSTICO CON CASOS EXTREMOS")
    print("="*80)
    
    resumen = []
    casos_extremos = []
    
    for columna, nombre in columnas_existentes.items():
        datos = df[columna].dropna()
        if len(datos) > 0:
            # Estadísticas básicas
            resumen.append({
                'Servicio': nombre,
                'N': len(datos),
                'Media': f"{datos.mean():.0f}",
                'Mediana': f"{datos.median():.0f}",
                'Min': f"{datos.min():.0f}",
                'Max': f"{datos.max():.0f}",
                'Desv.Est': f"{datos.std():.0f}"
            })
            
            # Casos extremos
            datos_completos = df[df[columna].notna()]
            valor_min = datos_completos[columna].min()
            valor_max = datos_completos[columna].max()
            
            caso_min = datos_completos[datos_completos[columna] == valor_min].iloc[0]
            caso_max = datos_completos[datos_completos[columna] == valor_max].iloc[0]
            
            # Usar DESCR o ETIQUETA si están disponibles
            descripcion_col = 'DESCR' if 'DESCR' in df.columns else ('ETIQUETA' if 'ETIQUETA' in df.columns else None)
            
            if descripcion_col:
                desc_min = caso_min[descripcion_col]
                desc_max = caso_max[descripcion_col]
            else:
                desc_min = f"ID: {caso_min.name}"
                desc_max = f"ID: {caso_max.name}"
            
            casos_extremos.append({
                'Servicio': nombre,
                'Mejor_Acceso': f"{valor_min:.0f}m",
                'Lugar_Mejor': desc_min[:40] + ('...' if len(str(desc_min)) > 40 else ''),
                'Peor_Acceso': f"{valor_max:.0f}m", 
                'Lugar_Peor': desc_max[:40] + ('...' if len(str(desc_max)) > 40 else '')
            })
    
    if resumen:
        resumen_df = pd.DataFrame(resumen)
        print("ESTADÍSTICAS GENERALES:")
        print(resumen_df.to_string(index=False))
        
        print("\n" + "="*120)
        print("CASOS EXTREMOS:")
        print("="*120)
        casos_df = pd.DataFrame(casos_extremos)
        print(casos_df.to_string(index=False))
    
    return columnas_existentes

def crear_histograma_detallado(df, columnas_existentes):
    """Crear un histograma detallado para un servicio específico"""
    
    if not columnas_existentes:
        return
        
    # Usar la primera columna disponible o 'avg_dis_total' si existe
    if 'avg_dis_total' in columnas_existentes:
        servicio_detalle = 'avg_dis_total'
    else:
        servicio_detalle = list(columnas_existentes.keys())[0]
    
    nombre_servicio = columnas_existentes[servicio_detalle]
    datos = df[servicio_detalle].dropna()
    
    if len(datos) == 0:
        print("No hay datos válidos para el histograma detallado")
        return
    
    plt.figure(figsize=(12, 7))
    
    # Histograma con más bins
    n, bins, patches = plt.hist(datos, bins=30, color='#27ae60', alpha=0.7, 
                               edgecolor='white', linewidth=0.5)
    
    # Personalizar colores por percentiles
    for i, p in enumerate(patches):
        if i < len(bins) - 1:
            percentil = (bins[i] - datos.min()) / (datos.max() - datos.min())
            p.set_facecolor(plt.cm.RdYlGn_r(percentil))
    
    plt.title(f'Distribución Detallada: {nombre_servicio}', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Distancia (metros)', fontsize=12)
    plt.ylabel('Frecuencia', fontsize=12)
    
    # Agregar estadísticas al gráfico
    stats_text = f'Media: {datos.mean():.0f}m\nMediana: {datos.median():.0f}m\nDesv. Est.: {datos.std():.0f}m\nN: {len(datos)}'
    plt.text(0.7, 0.8, stats_text, transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
             fontsize=11)
    
    # Líneas de percentiles
    percentiles = [25, 50, 75]
    colors = ['blue', 'red', 'purple']
    for p, color in zip(percentiles, colors):
        valor = np.percentile(datos, p)
        plt.axvline(valor, color=color, linestyle='--', alpha=0.7, 
                   label=f'P{p}: {valor:.0f}m')
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def main():
    """Función principal"""
    print("ANÁLISIS DE ACCESIBILIDAD GEOGRÁFICA")
    print("="*50)
    
    # Verificar directorio actual
    print(f"Directorio actual: {os.getcwd()}")
    
    # Buscar el archivo CSV
    posibles_rutas = [
        'Datos nuevos/municipios_stats.csv'
    ]
    
    archivo_encontrado = None
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            archivo_encontrado = ruta
            break
    
    if not archivo_encontrado:
        print("ERROR: No se encontró el archivo CSV")
        print("Archivos en el directorio actual:")
        for item in os.listdir('.'):
            print(f"  {item}")
        return
    
    # Cargar el CSV
    df = cargar_csv_robusto(archivo_encontrado)
    
    if df is None:
        print("ERROR: No se pudo cargar el archivo CSV")
        return
    
    # Analizar datos
    columnas_distancia = analizar_datos(df)
    
    # Crear histogramas
    columnas_existentes = crear_histogramas(df)
    
    # Crear histograma detallado
    crear_histograma_detallado(df, columnas_existentes)
    
    print("\n¡Análisis completado!")

# Ejecutar el programa
if __name__ == "__main__":
    main()
