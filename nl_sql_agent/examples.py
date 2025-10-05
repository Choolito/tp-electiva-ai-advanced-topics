FEW_SHOTS_TEMPLATE = '''
-- Usuario: "Cuántas reservas se confirmaron este mes?"
SELECT COUNT(*) AS total_reservas_confirmadas
FROM RESERVA
WHERE estado = 'confirmada'
  AND strftime('%Y-%m', fecha_checkin) = strftime('%Y-%m', 'now')
LIMIT 1;

-- Usuario: "Listado de habitaciones dobles con frigobar disponibles esta semana"
SELECT h.numero, h.piso, h.precio
FROM HABITACION h
LEFT JOIN RESERVA_HABITACION rh ON rh.habitacion_id = h.id
LEFT JOIN RESERVA r ON r.id = rh.reserva_id
WHERE h.tipo = 'doble'
  AND h.frigobar = 1
  AND (r.id IS NULL OR r.estado NOT IN ('confirmada','en_uso'))
LIMIT 50;
'''
