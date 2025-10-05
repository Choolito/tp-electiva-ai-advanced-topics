/* =========================================================
   SEED COMPLETO — 20 FILAS POR TABLA (SQLite)
   ========================================================= */

-- =======================
-- HABITACION (20)
-- =======================
INSERT OR IGNORE INTO habitacion (id, numero, piso, tipo, capacidad, estado, frigobar, jacuzzi, balcon, precio) VALUES
(1,'101',1,'single',1,'activa',0,0,0,18000),
(2,'102',1,'doble',2,'activa',1,0,0,28000),
(3,'103',1,'doble',2,'activa',0,0,0,26000),
(4,'104',1,'single',1,'activa',0,0,0,18500),
(5,'201',2,'doble',2,'activa',1,1,1,38000),
(6,'202',2,'single',1,'activa',0,0,1,19000),
(7,'203',2,'familiar',4,'activa',1,0,1,52000),
(8,'204',2,'doble',2,'activa',1,0,1,30000),
(9,'301',3,'familiar',5,'activa',1,0,1,61000),
(10,'302',3,'doble',2,'fuera_de_servicio',0,0,0,0),
(11,'303',3,'single',1,'activa',0,0,0,20000),
(12,'304',3,'doble',2,'activa',1,0,0,31000),
(13,'401',4,'familiar',4,'activa',1,1,1,64000),
(14,'402',4,'doble',2,'activa',0,0,1,29500),
(15,'403',4,'single',1,'activa',0,0,0,21000),
(16,'404',4,'doble',2,'activa',1,0,0,33000),
(17,'501',5,'familiar',4,'activa',1,0,1,65000),
(18,'502',5,'doble',2,'activa',0,0,0,28500),
(19,'503',5,'single',1,'activa',0,0,0,20500),
(20,'504',5,'doble',2,'activa',1,0,1,34000);

-- =======================
-- PERSONA (20)
-- =======================
INSERT OR IGNORE INTO persona (id, nombre, apellido, doc_tipo, doc_num, tel, email) VALUES
(1,'Juan','Pérez','DNI','10000001','+54 111 0001','juan1@example.com'),
(2,'Ana','García','DNI','10000002','+54 111 0002','ana2@example.com'),
(3,'Lucía','Benítez','DNI','10000003','+54 111 0003','lucia3@example.com'),
(4,'Carlos','Rossi','DNI','10000004','+54 111 0004','carlos4@example.com'),
(5,'Sofía','Luna','DNI','10000005','+54 111 0005','sofia5@example.com'),
(6,'Marcos','Suárez','DNI','10000006','+54 111 0006','marcos6@example.com'),
(7,'Paula','Molina','DNI','10000007','+54 111 0007','paula7@example.com'),
(8,'Diego','Fernández','DNI','10000008','+54 111 0008','diego8@example.com'),
(9,'Julia','Rico','DNI','10000009','+54 111 0009','julia9@example.com'),
(10,'Matías','Soto','DNI','10000010','+54 111 0010','matias10@example.com'),
(11,'Valeria','Quintana','DNI','10000011','+54 111 0011','valeria11@example.com'),
(12,'Nicolás','Vega','DNI','10000012','+54 111 0012','nicolas12@example.com'),
(13,'Brenda','Silva','DNI','10000013','+54 111 0013','brenda13@example.com'),
(14,'Hernán','Ibarra','DNI','10000014','+54 111 0014','hernan14@example.com'),
(15,'Agustina','Rivas','DNI','10000015','+54 111 0015','agustina15@example.com'),
(16,'Tomás','Romero','DNI','10000016','+54 111 0016','tomas16@example.com'),
(17,'Camila','Acosta','DNI','10000017','+54 111 0017','camila17@example.com'),
(18,'Federico','Méndez','DNI','10000018','+54 111 0018','federico18@example.com'),
(19,'Elena','Paz','DNI','10000019','+54 111 0019','elena19@example.com'),
(20,'Santiago','León','DNI','10000020','+54 111 0020','santiago20@example.com');

-- =======================
-- RESERVA (20)
-- estados: pendiente, confirmada, checkin, checkout, cancelada
-- =======================
INSERT OR IGNORE INTO reserva (id, titular_persona_id, fecha_checkin, fecha_checkout, estado, canal, observaciones) VALUES
(1,1,'2025-10-01','2025-10-03','confirmada','web',''),
(2,2,'2025-10-02','2025-10-05','pendiente','mostrador',''),
(3,3,'2025-10-04','2025-10-06','checkin','teléfono',''),
(4,4,'2025-10-05','2025-10-08','confirmada','web',''),
(5,5,'2025-10-07','2025-10-10','cancelada','teléfono',''),
(6,6,'2025-10-09','2025-10-12','confirmada','web',''),
(7,7,'2025-10-11','2025-10-13','pendiente','mostrador',''),
(8,8,'2025-10-12','2025-10-15','confirmada','web',''),
(9,9,'2025-10-14','2025-10-16','checkin','teléfono',''),
(10,10,'2025-10-15','2025-10-18','confirmada','web',''),
(11,11,'2025-10-17','2025-10-19','pendiente','mostrador',''),
(12,12,'2025-10-18','2025-10-21','confirmada','web',''),
(13,13,'2025-10-20','2025-10-22','checkout','teléfono',''),
(14,14,'2025-10-21','2025-10-24','confirmada','web',''),
(15,15,'2025-10-23','2025-10-25','pendiente','mostrador',''),
(16,16,'2025-10-24','2025-10-27','confirmada','web',''),
(17,17,'2025-10-26','2025-10-28','checkin','teléfono',''),
(18,18,'2025-10-27','2025-10-30','confirmada','web',''),
(19,19,'2025-10-29','2025-10-31','pendiente','mostrador',''),
(20,20,'2025-10-30','2025-11-02','confirmada','web','');

-- =======================
-- RESERVA_HABITACION (20)
-- (una habitación por reserva en este seed)
-- =======================
INSERT OR IGNORE INTO reserva_habitacion (id, reserva_id, habitacion_id, precio_noche_acordado, notas) VALUES
(1,1,2,27000,''),
(2,2,3,26000,''),
(3,3,5,38000,''),
(4,4,6,19000,''),
(5,5,8,30000,''),
(6,6,7,52000,''),
(7,7,11,20000,''),
(8,8,12,31000,''),
(9,9,14,29500,''),
(10,10,16,33000,''),
(11,11,18,28500,''),
(12,12,19,20500,''),
(13,13,20,34000,''),
(14,14,4,18500,''),
(15,15,1,18000,''),
(16,16,9,61000,''),
(17,17,13,64000,''),
(18,18,15,21000,''),
(19,19,6,19000,''),
(20,20,7,52000,'');

-- =======================
-- RESERVA_HABITACION_PERSONA (20)
-- =======================
INSERT OR IGNORE INTO reserva_habitacion_persona (id, reserva_habitacion_id, persona_id) VALUES
(1,1,1),
(2,2,2),
(3,3,3),
(4,4,4),
(5,5,5),
(6,6,6),
(7,7,7),
(8,8,8),
(9,9,9),
(10,10,10),
(11,11,11),
(12,12,12),
(13,13,13),
(14,14,14),
(15,15,15),
(16,16,16),
(17,17,17),
(18,18,18),
(19,19,19),
(20,20,20);

-- =======================
-- PLATO (20)
-- =======================
INSERT OR IGNORE INTO plato (id, nombre, descripcion, precio, activo) VALUES
(1,'Milanesa','Milanesa con guarnición',6000,1),
(2,'Ravioles','Ravioles caseros',6500,1),
(3,'Ensalada César','Clásica',5200,1),
(4,'Sopa del día','Consulta',3800,1),
(5,'Bife de chorizo','300g',8900,1),
(6,'Risotto','De hongos',7200,1),
(7,'Pizza muzza','8 porciones',5400,1),
(8,'Hamburguesa','Completa',5800,1),
(9,'Tarta de verduras','Porción',4300,1),
(10,'Ñoquis','Con salsa',6100,1),
(11,'Pollo grillado','Con ensalada',7700,1),
(12,'Paella','Mixta',9900,1),
(13,'Empanadas','Carne/pollo',1200,1),
(14,'Lasaña','Boloñesa',6800,1),
(15,'Sándwich veggie','Con papas',5600,1),
(16,'Omelette','Jamón y queso',4500,1),
(17,'Tortilla','De papas',4800,1),
(18,'Bagel','Salmón y queso',6200,1),
(19,'Fetuccine','Alfredo',6400,1),
(20,'Wok de verduras','Salteado',5900,1);

-- =======================
-- GUARNICION (20)
-- =======================
INSERT OR IGNORE INTO guarnicion (id, nombre, precio, activa) VALUES
(1,'Puré',1800,1),
(2,'Ensalada mixta',1600,1),
(3,'Papas fritas',1900,1),
(4,'Arroz',1500,1),
(5,'Verduras grilladas',2200,1),
(6,'Batatas fritas',2000,1),
(7,'Quinoa',2300,1),
(8,'Ensalada César',2100,1),
(9,'Rúcula y parmesano',2400,1),
(10,'Brócoli al vapor',1700,1),
(11,'Zanahorias glaseadas',1750,1),
(12,'Hummus',1850,1),
(13,'Cuscús',1950,1),
(14,'Papas españolas',2050,1),
(15,'Ensalada caprese',2500,1),
(16,'Tabule',2150,1),
(17,'Coleslaw',1650,1),
(18,'Pure de calabaza',1800,1),
(19,'Mix verdes',1600,1),
(20,'Tomates asados',1900,1);

-- =======================
-- PEDIDO (20)
-- mitad asociados a habitación, mitad a mesa
-- =======================
INSERT OR IGNORE INTO pedido (id, fecha_hora, origen_tipo, mesa, reserva_habitacion_id, estado, observaciones) VALUES
(1,  datetime('2025-10-01 20:15:00'), 'habitación', NULL, 1,  'PENDIENTE',''),
(2,  datetime('2025-10-02 13:10:00'), 'mesa',       'A1', NULL, 'PAGADO',''),
(3,  datetime('2025-10-03 21:00:00'), 'habitación', NULL, 2,  'PAGADO',''),
(4,  datetime('2025-10-03 12:40:00'), 'mesa',       'A2', NULL, 'PAGADO',''),
(5,  datetime('2025-10-04 19:30:00'), 'habitación', NULL, 3,  'PENDIENTE',''),
(6,  datetime('2025-10-04 13:05:00'), 'mesa',       'B1', NULL, 'PAGADO',''),
(7,  datetime('2025-10-05 20:50:00'), 'habitación', NULL, 4,  'PENDIENTE',''),
(8,  datetime('2025-10-05 12:20:00'), 'mesa',       'B2', NULL, 'PAGADO',''),
(9,  datetime('2025-10-06 21:10:00'), 'habitación', NULL, 5,  'PAGADO',''),
(10, datetime('2025-10-06 12:00:00'), 'mesa',       'B3', NULL, 'PAGADO',''),
(11, datetime('2025-10-07 20:00:00'), 'habitación', NULL, 6,  'PENDIENTE',''),
(12, datetime('2025-10-07 12:50:00'), 'mesa',       'C1', NULL, 'PAGADO',''),
(13, datetime('2025-10-08 20:40:00'), 'habitación', NULL, 7,  'PAGADO',''),
(14, datetime('2025-10-08 13:30:00'), 'mesa',       'C2', NULL, 'PAGADO',''),
(15, datetime('2025-10-09 22:10:00'), 'habitación', NULL, 8,  'PENDIENTE',''),
(16, datetime('2025-10-09 12:10:00'), 'mesa',       'C3', NULL, 'PAGADO',''),
(17, datetime('2025-10-10 19:10:00'), 'habitación', NULL, 9,  'PAGADO',''),
(18, datetime('2025-10-10 12:15:00'), 'mesa',       'D1', NULL, 'PAGADO',''),
(19, datetime('2025-10-11 21:20:00'), 'habitación', NULL, 10, 'PENDIENTE',''),
(20, datetime('2025-10-11 13:15:00'), 'mesa',       'D2', NULL, 'PAGADO','');

-- =======================
-- PEDIDO_ITEM (20)
-- alterno plato/guarnición; cuando no aplica, el otro es NULL
-- =======================
INSERT OR IGNORE INTO pedido_item (id, pedido_id, plato_id, guarnicion_id, comentario, precio_plato, precio_guarnicion) VALUES
(1, 1, 1, NULL,'', 6000, NULL),
(2, 1, NULL, 3,'', NULL, 1900),
(3, 2, 8, NULL,'sin cebolla', 5800, NULL),
(4, 3, 2, NULL,'al dente', 6500, NULL),
(5, 4, NULL, 1,'', NULL, 1800),
(6, 5, 11, NULL,'poco sal', 7700, NULL),
(7, 6, 7, NULL,'mitad muzza', 5400, NULL),
(8, 7, NULL, 5,'', NULL, 2200),
(9, 8, 10, NULL,'', 6100, NULL),
(10, 9, NULL, 2,'', NULL, 1600),
(11,10, 5, NULL,'jugoso', 8900, NULL),
(12,11, NULL, 4,'', NULL, 1500),
(13,12, 14, NULL,'', 6800, NULL),
(14,13, NULL, 6,'', NULL, 2000),
(15,14, 19, NULL,'', 6400, NULL),
(16,15, 6, NULL,'', 7200, NULL),
(17,16, NULL, 9,'', NULL, 2400),
(18,17, 3, NULL,'', 5200, NULL),
(19,18, 16, NULL,'', 4500, NULL),
(20,19, NULL, 14,'', NULL, 2050);

-- =======================
-- INSUMO (20)
-- =======================
INSERT OR IGNORE INTO insumo (id, nombre, unidad, stock_min) VALUES
(1,'Harina 0000','kg',10),
(2,'Pechuga de pollo','kg',8),
(3,'Lechuga','kg',5),
(4,'Papas','kg',12),
(5,'Aceite','l',6),
(6,'Arroz','kg',10),
(7,'Fideos','kg',8),
(8,'Queso parmesano','kg',4),
(9,'Manteca','kg',3),
(10,'Crema','l',5),
(11,'Huevos','unidades',60),
(12,'Tomates','kg',6),
(13,'Cebolla','kg',6),
(14,'Zanahoria','kg',5),
(15,'Pechito de cerdo','kg',7),
(16,'Carne picada','kg',9),
(17,'Levadura','kg',1),
(18,'Salsa de tomate','l',7),
(19,'Pan lactal','unidades',10),
(20,'Pescado blanco','kg',6);
