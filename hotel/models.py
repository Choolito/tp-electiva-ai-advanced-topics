from django.db import models

class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    doc_tipo = models.CharField(max_length=20, blank=True, null=True)
    doc_num = models.CharField(max_length=50, blank=True, null=True)
    tel = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = "PERSONA"

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

class Habitacion(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    piso = models.IntegerField()
    tipo = models.CharField(max_length=50)
    capacidad = models.IntegerField()
    estado = models.CharField(max_length=20, default="activa")
    frigobar = models.BooleanField(default=False)
    jacuzzi = models.BooleanField(default=False)
    balcon = models.BooleanField(default=False)
    precio = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "HABITACION"

    def __str__(self):
        return f"Hab {self.numero} (piso {self.piso})"

class Reserva(models.Model):
    titular_persona = models.ForeignKey(Persona, on_delete=models.PROTECT)
    fecha_checkin = models.DateField()
    fecha_checkout = models.DateField()
    estado = models.CharField(max_length=20, default="pendiente")  # pendiente, confirmada, en_uso, cancelada
    canal = models.CharField(max_length=50, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "RESERVA"

class ReservaHabitacion(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.PROTECT)

    class Meta:
        db_table = "RESERVA_HABITACION"
        unique_together = [("reserva", "habitacion")]
