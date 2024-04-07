from django.db import models



#Product Model for the table in the database 

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    description = models.TextField()
    size = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name



#Order Model for the table in the database 

class Order(models.Model):
    STATUS_CHOICES = (
        ('waiting', 'Waiting'),
        ('picked', 'Picked'),
        ('packed', 'Packed'),
        ('sent', 'Sent'),
        ('canceled', 'Canceled'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('high', 'High'),
    )
    customer_id = models.IntegerField()
    order_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    location = models.CharField(max_length=100)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    pack_date = models.DateField(null=True, blank=True)
    cancel_date = models.DateField(null=True, blank=True)



#OrderDetail Model for the table in the database 

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)



#Warehouse Model for the table in the database 

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)



#Shelf Model for the table in the database 

class Shelf(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()



#Inventory Model for the table in the database 

class Inventory(models.Model):
    STATUS_CHOICES = (
        ('good', 'Good'),
        ('nearly_expiring', 'Nearly Expiring'),
        ('expired', 'Expired'),
    )
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='good')



#Shipment Model for the table in the database 

class Shipment(models.Model):
    STATUS_CHOICES = (
        ('waiting', 'Waiting'),
        ('received', 'Received'),
        ('put_away', 'Put Away'),
    )
    name = models.CharField(max_length=100)
    supplier = models.CharField(max_length=100)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')



#Shipmentdetail Model for the table in the database 

class ShipmentDetail(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20)



#Notificatio Model for the table in the database 

class Notification(models.Model):
    STATUS_CHOICES = (
        ('not_read', 'Not Read'),
        ('read', 'Read'),
    )
    receiver_id = models.IntegerField()
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Read')
    date = models.DateTimeField(auto_now_add=True)


