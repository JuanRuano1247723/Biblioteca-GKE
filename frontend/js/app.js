/* ==========================================================================
   Biblioteca · Holdovers · Logica del frontend
   Habla con los microservicios a traves del proxy de nginx (/api/...).
   ========================================================================== */

const API = "/api";
let ejemplaresCache = [];

/* Utilidades ------------------------------------------------------------- */

function mostrarError(msg) {
  document.getElementById("error").textContent = msg || "";
}

async function llamar(metodo, ruta, cuerpo) {
  const opciones = { method: metodo, headers: { "Content-Type": "application/json" } };
  if (cuerpo !== undefined) opciones.body = JSON.stringify(cuerpo);

  const res = await fetch(API + ruta, opciones);
  if (res.status === 204) return null;

  const datos = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(datos.error || ("Error " + res.status));
  return datos;
}

function celda(tr, texto) {
  const td = document.createElement("td");
  td.textContent = texto ?? "";
  tr.appendChild(td);
  return td;
}

function boton(texto, onClick) {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = texto;
  b.onclick = onClick;
  return b;
}

/* Carga de datos --------------------------------------------------------- */

async function cargarIntegrantes() {
  const lista = await llamar("GET", "/integrantes");
  const tbody = document.getElementById("integrantes");
  tbody.replaceChildren();

  for (const i of lista) {
    const tr = document.createElement("tr");
    celda(tr, i.carne);
    celda(tr, i.nombre);
    tbody.appendChild(tr);
  }
}

async function cargarEjemplares() {
  ejemplaresCache = await llamar("GET", "/ejemplares");
  const tbody = document.getElementById("ejemplares");
  const select = document.getElementById("select-ejemplar");
  tbody.replaceChildren();
  select.replaceChildren();

  for (const e of ejemplaresCache) {
    const tr = document.createElement("tr");
    celda(tr, e.id);
    celda(tr, e.titulo);
    celda(tr, e.autor);
    celda(tr, e.anio);
    const acciones = celda(tr, "");
    acciones.appendChild(boton("Eliminar", () => eliminar("/ejemplares/" + e.id)));
    tbody.appendChild(tr);

    const opt = document.createElement("option");
    opt.value = e.id;
    opt.textContent = e.titulo;
    select.appendChild(opt);
  }
}

async function cargarPrestamos() {
  const lista = await llamar("GET", "/prestamos");
  const tbody = document.getElementById("prestamos");
  tbody.replaceChildren();

  for (const p of lista) {
    const tr = document.createElement("tr");
    const ejemplar = ejemplaresCache.find(e => e.id === p.ejemplar_id);
    celda(tr, p.id);
    celda(tr, ejemplar ? ejemplar.titulo : p.ejemplar_id);
    celda(tr, p.prestatario);
    celda(tr, p.fecha_prestamo);
    celda(tr, p.fecha_devolucion || "Pendiente");

    const acciones = celda(tr, "");
    if (!p.fecha_devolucion) acciones.appendChild(boton("Devolver", () => devolver(p)));
    acciones.appendChild(boton("Eliminar", () => eliminar("/prestamos/" + p.id)));
    tbody.appendChild(tr);
  }
}

async function cargarTodo() {
  try {
    await cargarIntegrantes();
    await cargarEjemplares();
    await cargarPrestamos();
  } catch (err) {
    mostrarError(err.message);
  }
}

/* Acciones --------------------------------------------------------------- */

async function eliminar(ruta) {
  try {
    await llamar("DELETE", ruta);
    mostrarError("");
    cargarTodo();
  } catch (err) {
    mostrarError(err.message);
  }
}

async function devolver(prestamo) {
  try {
    const hoy = new Date().toISOString().slice(0, 10);
    await llamar("PUT", "/prestamos/" + prestamo.id, {
      ejemplar_id: prestamo.ejemplar_id,
      prestatario: prestamo.prestatario,
      fecha_prestamo: prestamo.fecha_prestamo,
      fecha_devolucion: hoy
    });
    mostrarError("");
    cargarTodo();
  } catch (err) {
    mostrarError(err.message);
  }
}

/* Formularios ------------------------------------------------------------ */

document.getElementById("form-ejemplar").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const f = new FormData(ev.target);
  const cuerpo = { titulo: f.get("titulo"), autor: f.get("autor") };
  if (f.get("anio")) cuerpo.anio = Number(f.get("anio"));

  try {
    await llamar("POST", "/ejemplares", cuerpo);
    ev.target.reset();
    mostrarError("");
    cargarTodo();
  } catch (err) {
    mostrarError(err.message);
  }
});

document.getElementById("form-prestamo").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const f = new FormData(ev.target);

  try {
    await llamar("POST", "/prestamos", {
      ejemplar_id: Number(f.get("ejemplar_id")),
      prestatario: f.get("prestatario")
    });
    ev.target.reset();
    mostrarError("");
    cargarTodo();
  } catch (err) {
    mostrarError(err.message);
  }
});

/* Arranque --------------------------------------------------------------- */
cargarTodo();
