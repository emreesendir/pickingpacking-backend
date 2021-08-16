from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL
from django.conf import settings

# Create your models here.

class Connector(models.Model):
    RUNNING = 'RUNNING'
    STOPPED = 'STOPPED'
    FAILED = 'FAILED'
    STATUS_CHOICES = [
        (RUNNING, 'RUNNING'),
        (STOPPED, 'STOPPED'),
        (FAILED, 'FAILED'),
    ]

    RUN = 'RUN'
    STOP = 'STOP'
    COMMAND_CHOICES = [
        (RUN, 'RUN'),
        (STOP, 'STOP'),
    ]

    name = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STOPPED)
    command = models.CharField(max_length=30, choices=COMMAND_CHOICES, default=STOP)

    def __str__(self):
        return self.name

class Order(models.Model):
    NEW_ORDER = 'NEW ORDER'
    PICKING_IN_PROGRESS = 'PICKING IN PROGRESS'
    PICKING_COMPLETED = 'PICKING COMPLETED'
    PACKING_IN_PROGRESS = 'PACKING IN PROGRESS'
    SHIPPED = 'SHIPPED'
    CANCELED = 'CANCELED'
    STATUS_CHOICES = [
        (NEW_ORDER, 'NEW ORDER'),
        (PICKING_IN_PROGRESS, 'PICKING IN PROGRESS'),
        (PICKING_COMPLETED, 'PICKING COMPLETED'),
        (PACKING_IN_PROGRESS, 'PACKING IN PROGRESS'),
        (SHIPPED, 'SHIPPED'),
        (CANCELED, 'CANCELED'),
    ]

    connector = models.ForeignKey(Connector, on_delete=SET_NULL, null=True)
    remote_id = models.CharField(max_length=25)
    shipping_info = models.CharField(max_length=500)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=NEW_ORDER)
    picking_session = 0
    pick_cart_section = models.IntegerField()
    packing_session = 0

    def __str__(self):
        return '{}/{}'.format(self.connector.name, self.remote_id)

class OrderLine(models.Model):
    NEW_ORDER = 'NEW ORDER'
    PICKED = 'PICKED'
    PACKED = 'PACKED'
    STATUS_CHOICES = [
        (NEW_ORDER, 'NEW ORDER')
        (PICKED, 'PICKED'),
        (PACKED, 'PACKED'),
    ]

    order = models.ForeignKey('Order', on_delete=CASCADE)
    product_name = models.CharField(max_length=100)
    quantity = models.FloatField()
    location = models.IntegerField()
    barcode = models.CharField(max_length=50)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=NEW_ORDER)

    def __str__(self):
        return '{} piece(s) {} from shelf {}'.format(self.quantity, self.product_name, self.location)

class History(models.Model):
    order = models.ForeignKey('Order', on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length=200)
    status_before_event = models.CharField(max_length=30)

    def __str__(self):
        return '{}/{}/{}'.format(self.order.connector.name, self.order.remote_id, self.event)

class Event(models.Model):
    CANCEL = 'CANCEL'
    PICKING_SESSION_ASSIGNMENT = 'PICKING SESSION ASSIGNMENT'
    PACKING_SESSION_ASSIGNMENT = 'PACKING SESSION ASSIGNMENT'
    PACKING_PREPARATION = 'PACKING PREPARATION'
    HOLD = 'HOLD'
    CONTINUE = 'CONTINUE'
    TYPE_CHOICES = [
        (CANCEL, 'CANCEL'),
        (PICKING_SESSION_ASSIGNMENT, 'PICKING SESSION ASSIGNMENT'),
        (PACKING_SESSION_ASSIGNMENT, 'PACKING SESSION ASSIGNMENT'),
        (PACKING_PREPARATION, 'PACKING PREPARATION'),
        (HOLD, 'HOLD'),
        (CONTINUE, 'CONTINUE'),
    ]

    order = models.ForeignKey('Order', on_delete=CASCADE)
    priority = models.IntegerField() # High number = High priority
    created_at = models.DateTimeField(auto_now_add=True) # Earlier record will be processed earlier
    type = models.CharField(max_length=50)
    data = models.CharField(max_length=500)
    result = models.CharField(max_length=30)

    def __str__(self):
        return '{}/{}/{}'.format(self.order.connector.name, self.order.remote_id, self.type)

class PickingSession(models.Model):
    IN_PROGRESS = 'IN PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELED = 'CANCELED'
    PAUSED = 'PAUSED'
    STATUS_CHOICES = [
        (IN_PROGRESS, 'IN PROGRESS'),
        (COMPLETED, 'COMPLETED'),
        (CANCELED, 'CANCELED'),
        (PAUSED, 'PAUSED'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_created = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)
    current_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)
    pick_cart = models.ForeignKey('PickCart', on_delete=SET_NULL, null=True)
    total_steps = models.IntegerField()
    completed_steps = models.IntegerField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=IN_PROGRESS)

    def __str__(self):
        return '{}/{}'.format(self.pick_cart.name, self.created_at)

class PickCart(models.Model):
    name = models.CharField(max_length=50)
    total_sections = models.IntegerField()

    def __str__(self):
        return self.name

class PackingSession(models.Model):
    IN_PROGRESS = 'IN PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELED = 'CANCELED'
    PAUSED = 'PAUSED'
    STATUS_CHOICES = [
        (IN_PROGRESS, 'IN PROGRESS'),
        (COMPLETED, 'COMPLETED'),
        (CANCELED, 'CANCELED'),
        (PAUSED, 'PAUSED'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_created = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)
    current_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)
    packing_station = models.ForeignKey('PackingStation', on_delete=SET_NULL, null=True)
    total_steps = models.IntegerField()
    completed_steps = models.IntegerField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=IN_PROGRESS)

    def __str__(self):
        return '{}/{}'.format(self.pick_cart.name, self.created_at)

class PackingStation(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name