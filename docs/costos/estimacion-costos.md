
# Estimación de costos - Biblioteca GKE

## Proyecto

- Universidad Rafael Landívar
- Curso: Virtualización
- Proyecto Final: Caso 4 - Biblioteca
- Equipo: Holdovers
- Región: `us-central1`
- Zona: `us-central1-a`

## Objetivo

Estimar los costos de la infraestructura necesaria para desplegar el sistema Biblioteca en Google Cloud, utilizando Google Kubernetes Engine (GKE) y Terraform.

Los importes representan estimaciones previas al despliegue y no cargos reales.

## Infraestructura considerada

| Recurso | Configuración |
|---|---|
| GKE | Standard zonal |
| Clúster | `holdovers-gke` |
| Node pool | `pool-holdovers` |
| Nodos | 2 `e2-small` Spot |
| Discos de arranque | 30 GiB por nodo, Balanced PD |
| Artifact Registry | Repositorio `holdovers` |
| Imágenes Docker | Frontend, Ejemplares y Préstamos |
| Base de datos | PVC de 10 GiB estimados |
| Acceso público | LoadBalancer |
| Infraestructura | Terraform |

## Estimación mensual

Se analizaron tres escenarios para comparar los costos de operación continua y uso temporal.

### Escenario A - Uso continuo

Infraestructura disponible durante aproximadamente 730 horas mensuales, con dos nodos Spot activos durante todo el período.

| Servicio | Costo mensual estimado |
|---|---:|
| GKE Standard y nodos Spot | US$93.68 |
| Persistent Disk de 10 GiB | US$1.00 |
| Cloud Load Balancing | US$18.25 |
| Artifact Registry de 3 GiB | US$0.25 |
| Transferencia de datos de 10 GiB | US$1.71 |
| **Total estimado** | **US$114.89** |

### Escenario B - Nodos activos durante 20 horas

Se consideran dos nodos Spot utilizados durante 20 horas por nodo, mientras el clúster y los demás servicios permanecen aprovisionados durante el mes.

| Servicio | Costo mensual estimado |
|---|---:|
| GKE Standard y nodos Spot | US$73.57 |
| Persistent Disk de 10 GiB | US$1.00 |
| Cloud Load Balancing | US$18.25 |
| Artifact Registry de 3 GiB | US$0.25 |
| Transferencia de datos de 10 GiB | US$1.71 |
| **Total estimado** | **US$94.78** |

La reducción de horas de los nodos no elimina los cargos de administración del clúster.

### Escenario C - Infraestructura temporal durante 20 horas

Se considera la creación de la infraestructura para las sesiones de trabajo y su destrucción al finalizar, con un total acumulado de 20 horas mensuales.

| Servicio | Costo orientativo |
|---|---:|
| Administración GKE durante 20 horas | US$2.00 |
| Nodos Spot durante 40 horas-nodo | US$0.57 |
| LoadBalancer durante 20 horas | US$0.50 |
| Persistent Disk durante 20 horas | US$0.03 |
| Artifact Registry durante el mes | US$0.25 |
| Transferencia de datos de 10 GiB | US$1.71 |
| **Total orientativo** | **US$5.06** |

Este escenario es una aproximación basada en los componentes de los escenarios anteriores, no una cotización directa de Google Cloud Pricing Calculator.

Supone que el clúster, los nodos, el balanceador y el disco de pruebas se eliminan correctamente al finalizar las sesiones, mientras las imágenes Docker permanecen almacenadas.

Los costos efectivos pueden variar según el tiempo real de uso, almacenamiento residual, tráfico, créditos de facturación y otros recursos.

## Comparación de escenarios

| Escenario | Costo mensual |
|---|---:|
| A - Uso continuo | US$114.89 |
| B - Nodos 20 horas, clúster permanente | US$94.78 |
| C - Infraestructura temporal | US$5.06 orientativos |

El escenario C representa la alternativa de menor costo bajo los supuestos establecidos, pero requiere coordinación del equipo y procedimientos de despliegue reproducibles.

## Estrategia para controlar gastos

- Configurar alertas de presupuesto en Cloud Billing.
- Mantener dos nodos `e2-small` Spot.
- Crear la infraestructura únicamente durante las sesiones necesarias.
- Coordinar los horarios de despliegue y destrucción.
- Respaldar los datos necesarios antes de eliminar recursos.
- Comprobar que los LoadBalancers y discos no permanezcan aprovisionados.
- Supervisar el gasto real desde Cloud Billing.

Las alertas de presupuesto no detienen automáticamente la facturación.

### Consideraciones sobre Terraform Destroy

El archivo `main.tf` administra tanto el clúster GKE como el repositorio de Artifact Registry.

Por lo tanto, ejecutar `terraform destroy` completo también intentará eliminar el repositorio de imágenes.

Antes de utilizar este procedimiento, el equipo deberá definir cómo conservar Artifact Registry o cómo reconstruir y publicar nuevamente las imágenes.

No se recomienda ejecutar destrucciones selectivas sin revisar previamente las dependencias y el estado de Terraform.

## Referencias de Google Cloud Pricing Calculator

### Escenario A

https://cloud.google.com/products/calculator?dl=CjhDaVJpTXpJMVl6Vm1aaTFpTW1KakxUUXdOalF0T0dGak5pMWxPRE15WldVM01XUmlPVFlRQVE9PRAOGiQ1NUU3QjA3Qy0xMTkzLTQ4MzUtQTI3RC05MzRBNDQwQjZFMzI

### Escenario B

https://cloud.google.com/products/calculator?dl=CjhDaVE1TlRnME5XRTVZeTFoT0dKa0xUUXlOVFV0T0RjeU5DMDFORE0wTXpSa00yWmtNRGNRQVE9PRAPGiREMTc0ODMwQy1BNjZBLTRDNTktOTYwRC0xNkM3RTUwNzY4MEM

## Evidencias pendientes

- Capturas de las estimaciones de Google Cloud Pricing Calculator.
- Captura de configuración del presupuesto.
- Evidencias del despliegue de infraestructura.
- Evidencia de destrucción y verificación de recursos residuales.
- Captura del gasto real registrado en Cloud Billing.

## Estado

Estimaciones A y B completadas mediante Google Cloud Pricing Calculator.

Escenario C documentado como estimación orientativa, pendiente de validación según la estrategia definitiva de infraestructura.

Pendiente de recopilar las evidencias finales y contrastar las estimaciones con los cargos reales.
