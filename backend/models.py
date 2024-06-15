from asyncio.windows_events import NULL
from django.db import models
from django.contrib.auth.models import User

# 1. User model default in django but this is for staff permission.
class StaffPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_permission')
    warehouse = models.ForeignKey('Warehouse', on_delete=models.CASCADE)
    is_permitted = models.BooleanField(default=False)

# 2. Product model:
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    size = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    barcode = models.CharField(max_length=50, unique=True)
    photo = models.ImageField(upload_to='product_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.barcode}"

# 3. Category model:
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    photo = models.ImageField(upload_to='category_photos/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.name}"

# 4. Supplier model:
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='supplier_photos/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.name}"

# 5. Warehouse model:
class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    warehouse_location = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name}"

# 6. Location model:
class Location(models.Model):
    warehouse = models.ForeignKey('Warehouse', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    aisle = models.CharField(max_length=10)
    rack = models.CharField(max_length=10)
    level = models.CharField(max_length=10)
    barcode = models.CharField(max_length=50, unique=True)
    capacity = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} ({self.barcode}) - Capacity: {self.capacity}"

# 7. Inventory model:
class Inventory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    expiry_date = models.DateField(blank=True, null=True)
    status_choices = [
        ('available', 'Available'),
        ('out_of_stock', 'Out Of Stock'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='available')

# 8. Shipment model:
class Shipment(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    arrival_date = models.DateField()
    receive_date = models.DateField(blank=True, null=True)
    status_choices = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('put_away', 'Put Away'),

    ]
    status = models.CharField(max_length=20, choices=status_choices, default='pending')
    
    def __str__(self):
        return f"Shipment from {self.supplier.name} - Status: {self.status}"

# 9. ShipmentDetail model:
class ShipmentDetail(models.Model):
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    price_at_shipment = models.DecimalField(max_digits=10, decimal_places=2) 
    quantity = models.IntegerField()

    status_choices = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('put_away', 'Put Away'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='pending')
    
    def __str__(self):
        return f"Detail {self.id} of Shipment {self.shipment.id} - Product: {self.product.name}"

# 10. Order model:
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateField(blank=True, null=True)
    priority_choices = [
        ('high', 'High'),
        ('low', 'Low'),
    ]
    priority = models.CharField(max_length=20, choices=priority_choices, default='low')
    status_choices = [
        ('pending', 'Pending'),
        ('picked', 'Picked'),
        ('packed', 'Packed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='pending')
    
    def __str__(self):
        return f"Order {self.id} by {self.customer.username} - Total: ${self.total_price}"

# 11. OrderDetail model:
class OrderDetail(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2) 
    quantity = models.IntegerField()
    status_choices = [
        ('pending', 'Pending'),
        ('picked', 'Picked'),
        ('packed', 'Packed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='pending')

# 12. Activity model:
class Activity(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    activity_type_choices = [
        ('put_away', 'Put Away'),
        ('pick', 'Pick'),
        ('pack', 'Pack'),
        ('delivery', 'Delivery'),
        ('receive', 'Receive'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
        ('cycle_count', 'Cycle Count'),
        ('replenishment', 'Replenishment'),
        ('other', 'Other'),
    ]
    activity_type = models.CharField(max_length=20, choices=activity_type_choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.activity_type} by {self.staff.username} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

# 13. Favorite model:
class Favorite(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

# 14. Report model: 
class Report(models.Model):
    report_type_choices = [
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('activity', 'Activity Report'),
        ('other', 'Other Report'),
    ]
    report_type = models.CharField(max_length=20, choices=report_type_choices)
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return f"{self.report_type} generated on {self.generated_at.strftime('%Y-%m-%d')} in the warehouse {self.warehouse.name}."

# 15. Notification model:
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status_choices = [
        ('unread', 'Unread'),
        ('read', 'Read'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='unread')

# 16. BarcodeScanning model:
class BarcodeScanning(models.Model):
    scanned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    scanned_item = models.ForeignKey('Product', on_delete=models.CASCADE)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    action_choices = [
        ('put_away', 'Put Away'),
        ('pick', 'Pick'),
        ('receive', 'Receive'),
    ]
    action = models.CharField(max_length=20, choices=action_choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action} of {self.scanned_item.name} by {self.scanned_by.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

# 17. Wallet model:
class Wallet(models.Model):
    customer = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet of {self.customer.username} - Balance: ${self.balance}"

# 18. TransactionLog model:
class TransactionLog(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('purchase', 'Purchase'),
        ('refund', 'Refund'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction #{self.id} - User: {self.customer.username} - Type: {self.transaction_type} - Amount: {self.amount}"

# 19. StockMovement model: 
class StockMovement(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    from_location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='from_location')
    to_location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='to_location', null=True, blank=True)
    quantity = models.IntegerField()
    movement_type_choices = [
        ('put_away', 'Put Away'),
        ('pick', 'Pick'),
        ('transfer', 'Transfer'),
        ('receive', 'Receive'),
        ('adjustment', 'Adjustment'),
    ]
    movement_type = models.CharField(max_length=20, choices=movement_type_choices)
    timestamp = models.DateTimeField(auto_now_add=True)

# 20. StockAdjustment model: 
class StockAdjustment(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    adjustment_type_choices = [
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
    ]
    adjustment_type = models.CharField(max_length=20, choices=adjustment_type_choices)
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

# 21. CycleCount model: 
class CycleCount(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    counted_quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

# 22. ReplenishmentRequest model: 
class ReplenishmentRequest(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='pending')
    reason = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

# DeliveryRecord model:
class DeliveryRecord(models.Model):
    delivery_company = models.CharField(max_length=100)
    delivery_man_name = models.CharField(max_length=100)
    delivery_man_phone = models.CharField(max_length=15)
    orders = models.ManyToManyField(Order)
    date_assigned = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Delivery by {self.delivery_man_name} from {self.delivery_company}"
