PRAGMA foreign_keys = ON;

/* =====================
   Correspondientes al sector hotel
   ===================== */
CREATE TABLE IF NOT EXISTS habitacion (
  id INTEGER PRIMARY KEY,
  numero TEXT NOT NULL UNIQUE,
  piso INTEGER,
  tipo TEXT,                    -- single, doble, triple, cuadruple
  capacidad INTEGER,
  estado TEXT DEFAULT 'activa',
  frigobar INTEGER DEFAULT 0,   -- bool 0/1
  jacuzzi  INTEGER DEFAULT 0,   -- bool 0/1
  balcon   INTEGER DEFAULT 0,   -- bool 0/1
  precio NUMERIC
);

CREATE TABLE IF NOT EXISTS persona (
  id INTEGER PRIMARY KEY,
  nombre TEXT,
  apellido TEXT,
  doc_tipo TEXT,
  doc_num TEXT,
  tel TEXT,
  email TEXT
);

CREATE TABLE IF NOT EXISTS reserva (
  id INTEGER PRIMARY KEY,
  titular_persona_id INTEGER NOT NULL,
  fecha_checkin DATE NOT NULL,
  fecha_checkout DATE NOT NULL,
  estado TEXT DEFAULT 'pendiente',   -- pendiente, confirmada, ingresada, completada, cancelada
  canal TEXT,                        -- web, presenciañ, telefono
  observaciones TEXT,
  FOREIGN KEY (titular_persona_id) REFERENCES persona(id)
);

CREATE TABLE IF NOT EXISTS reserva_habitacion (
  id INTEGER PRIMARY KEY,
  reserva_id INTEGER NOT NULL,
  habitacion_id INTEGER NOT NULL,
  precio_noche_acordado NUMERIC,
  notas TEXT,
  UNIQUE (reserva_id, habitacion_id),
  FOREIGN KEY (reserva_id) REFERENCES reserva(id),
  FOREIGN KEY (habitacion_id) REFERENCES habitacion(id)
);

CREATE TABLE IF NOT EXISTS reserva_habitacion_persona (
  id INTEGER PRIMARY KEY,
  reserva_habitacion_id INTEGER NOT NULL,
  persona_id INTEGER NOT NULL,
  UNIQUE (reserva_habitacion_id, persona_id),
  FOREIGN KEY (reserva_habitacion_id) REFERENCES reserva_habitacion(id),
  FOREIGN KEY (persona_id) REFERENCES persona(id)
);

/* =====================
   Correspondientes al sector restaurant
   ===================== */
CREATE TABLE IF NOT EXISTS plato (
  id INTEGER PRIMARY KEY,
  nombre TEXT,
  descripcion TEXT,
  precio NUMERIC,
  activo INTEGER DEFAULT 1          
);

CREATE TABLE IF NOT EXISTS guarnicion (
  id INTEGER PRIMARY KEY,
  nombre TEXT,
  precio NUMERIC,
  activa INTEGER DEFAULT 1         
);

CREATE TABLE IF NOT EXISTS pedido (
  id INTEGER PRIMARY KEY,
  fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  origen_tipo TEXT,                 -- mesa, servicio al cuarto
  mesa TEXT,                        -- nullable
  reserva_habitacion_id INTEGER,    
  estado TEXT DEFAULT 'PENDIENTE',  -- PAGADO, PENDIENTE
  observaciones TEXT,
  FOREIGN KEY (reserva_habitacion_id) REFERENCES reserva_habitacion(id)

);

CREATE TABLE IF NOT EXISTS pedido_item (
  id INTEGER PRIMARY KEY,
  pedido_id INTEGER NOT NULL,
  plato_id INTEGER,                 -- nullable
  guarnicion_id INTEGER,            -- nullable
  comentario TEXT,
  precio_plato NUMERIC,             -- para guardar el precio del momento
  precio_guarnicion NUMERIC,        -- para guardar el precio del momento
  FOREIGN KEY (pedido_id) REFERENCES pedido(id),
  FOREIGN KEY (plato_id) REFERENCES plato(id),
  FOREIGN KEY (guarnicion_id) REFERENCES guarnicion(id)
);

/* =====================
   Corresponde a la parte de stock, puede ser eliminado.
   ===================== */
CREATE TABLE IF NOT EXISTS insumo (
  id INTEGER PRIMARY KEY,
  nombre TEXT,
  unidad TEXT, 
  stock_min NUMERIC
);
