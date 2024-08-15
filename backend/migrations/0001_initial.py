# Generated by Django 5.0.3 on 2024-07-17 15:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('photo', models.ImageField(blank=True, null=True, upload_to='category_photos/')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('aisle', models.CharField(max_length=10)),
                ('rack', models.CharField(max_length=10)),
                ('level', models.CharField(max_length=10)),
                ('barcode', models.CharField(max_length=50, unique=True)),
                ('capacity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrival_date', models.DateField()),
                ('receive_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('received', 'Received'), ('put_away', 'Put Away')], default='pending', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('contact_person', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='supplier_photos/')),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('warehouse_location', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('activity_type', models.CharField(choices=[('put_away', 'Put Away'), ('pick', 'Pick'), ('pack', 'Pack'), ('delivery', 'Delivery'), ('receive', 'Receive'), ('transfer', 'Transfer'), ('adjustment', 'Adjustment'), ('cycle_count', 'Cycle Count'), ('replenishment', 'Replenishment'), ('other', 'Other')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('unread', 'Unread'), ('read', 'Read')], default='unread', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('delivered_at', models.DateField(blank=True, null=True)),
                ('priority', models.CharField(choices=[('high', 'High'), ('low', 'Low')], default='low', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('picked', 'Picked'), ('packed', 'Packed'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_company', models.CharField(max_length=100)),
                ('delivery_man_name', models.CharField(max_length=100)),
                ('delivery_man_phone', models.CharField(max_length=15)),
                ('date_assigned', models.DateField(auto_now_add=True)),
                ('orders', models.ManyToManyField(to='backend.order')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('size', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('barcode', models.CharField(max_length=50, unique=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='product_photos/')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.category')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_at_sale', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('picked', 'Picked'), ('packed', 'Packed'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.product')),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('available', 'Available'), ('out_of_stock', 'Out Of Stock'), ('expired', 'Expired')], default='available', max_length=20)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.location')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.product')),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.product')),
            ],
        ),
        migrations.CreateModel(
            name='CycleCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counted_quantity', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.location')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.product')),
            ],
        ),
        migrations.CreateModel(
            name='BarcodeScanning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('put_away', 'Put Away'), ('pick', 'Pick'), ('receive', 'Receive')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('scanned_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.location')),
                ('scanned_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.product')),
            ],
        ),
        migrations.CreateModel(
            name='ReplenishmentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('reason', models.TextField(null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.location')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.product')),
            ],
        ),
        migrations.CreateModel(
            name='ShipmentDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_at_shipment', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('received', 'Received'), ('put_away', 'Put Away')], default='pending', max_length=20)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.product')),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.shipment')),
            ],
        ),
        migrations.CreateModel(
            name='StockAdjustment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('adjustment_type', models.CharField(choices=[('increase', 'Increase'), ('decrease', 'Decrease')], max_length=20)),
                ('reason', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.location')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.product')),
            ],
        ),
        migrations.CreateModel(
            name='StockMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('movement_type', models.CharField(choices=[('put_away', 'Put Away'), ('pick', 'Pick'), ('transfer', 'Transfer'), ('receive', 'Receive'), ('adjustment', 'Adjustment')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('from_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_location', to='backend.location')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.product')),
                ('to_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_location', to='backend.location')),
            ],
        ),
        migrations.AddField(
            model_name='shipment',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.supplier'),
        ),
        migrations.CreateModel(
            name='TransactionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('deposit', 'Deposit'), ('purchase', 'Purchase'), ('refund', 'Refund')], max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StaffPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_permitted', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='staff_permission', to=settings.AUTH_USER_MODEL)),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('sales', 'Sales Report'), ('inventory', 'Inventory Report'), ('activity', 'Activity Report'), ('other', 'Other Report')], max_length=20)),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('data', models.TextField()),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.warehouse')),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.warehouse'),
        ),
    ]
