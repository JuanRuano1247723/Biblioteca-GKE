
# Estimación de costos - Biblioteca GKE

## Proyecto

- Universidad Rafael Landívar
- Curso: Virtualización
- Proyecto Final: Caso 4 - Biblioteca
- Equipo: Holdovers
- Región: `us-central1`
- Zona: `us-central1-a`

## Objetivo

Estimar los costos de la infraestructura necesaria
para desplegar el sistema Biblioteca en Google Cloud,
utilizando Google Kubernetes Engine y Terraform.

Los importes representan estimaciones previas
al despliegue, no cargos reales.

## Infraestructura considerada

| Recurso | Configuración |
|---|---|
| GKE | Standard zonal |
| Clúster | holdovers-gke |
| Node pool | pool-holdovers |
| Nodos | 2 e2-small Spot |
| Disco de arranque | 30 GB por nodo |
| Artifact Registry | Repositorio holdovers |
| Imágenes Docker | Frontend, Ejemplares y Préstamos |
| Base de datos | PVC persistente |
| Acceso público | LoadBalancer |
| Infraestructura | Terraform |

## Estimación mensual preliminar

Escenario de referencia: funcionamiento continuo
durante aproximadamente 730 horas mensuales.

| Servicio | Costo mensual estimado |
|---|---:|
| GKE Standard y nodos Spot | US$89.68 |
| Persistent Disk de 10 GiB | US$1.00 |
| Cloud Load Balancing | US$18.25 |
| Artifact Registry de 3 GiB | US$0.25 |
| **Subtotal provisional** | **US$109.18** |

### Consideraciones

El subtotal procede de la configuración inicial
de Google Cloud Pricing Calculator.

La estimación de GKE utilizó discos de arranque
de 10 GiB por nodo.

El archivo `main.tf` del repositorio oficial
establece 30 GB por nodo.

Por lo tanto, el costo de GKE deberá recalcularse
para representar la infraestructura definitiva.

El disco persistente de 10 GiB de la base de datos
es una estimación independiente de los discos
de arranque de los nodos.

El tráfico saliente hacia Internet todavía no
está incluido.

Los cargos de administración del clúster,
almacenamiento, balanceador y tráfico deberán
revisarse para evitar omisiones o duplicaciones.

## Escenarios de funcionamiento

### Escenario A - Uso continuo

- 2 nodos e2-small Spot.
- Aproximadamente 730 horas por nodo.
- Clúster disponible durante todo el mes.
- Costo parcial inicial: US$109.18 mensuales.
- Pendiente de ajuste por discos y tráfico.

### Escenario B - Sesiones de laboratorio

- 2 nodos e2-small Spot.
- Aproximadamente 20 horas por nodo.
- Infraestructura activa durante las sesiones.
- Costo pendiente de calcular.

Los recursos que permanezcan aprovisionados,
como discos, imágenes o balanceadores, pueden
seguir generando cargos fuera de las sesiones.

## Medidas para controlar gastos

- Configurar alertas de presupuesto.
- Mantener únicamente dos nodos.
- Utilizar máquinas e2-small Spot.
- Evitar recursos innecesarios.
- Supervisar el consumo en Cloud Billing.
- Ejecutar `terraform destroy` al finalizar,
  previa coordinación con el equipo.
- Verificar recursos residuales después del destroy.

Las alertas de presupuesto no detienen
automáticamente la facturación.

## Evidencias

- Enlace a Google Cloud Pricing Calculator.
- Captura de la estimación de costos.
- Captura de configuración del presupuesto.
- Evidencia de destrucción de infraestructura.
- Captura del gasto final registrado.

## Estado

Estimación preliminar documentada.

Pendiente de actualizar los discos de arranque
a 30 GB por nodo, estimar el tráfico y calcular
el escenario de 20 horas.

Los importes definitivos se confirmarán antes
de entregar el informe final.
