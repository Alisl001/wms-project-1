import random
from django.core.management.base import BaseCommand
from backend.models import Location

class Command(BaseCommand):
    help = 'Populate the database with warehouse locations'

    def handle(self, *args, **kwargs):
        warehouse_id = 1
        random_prefix = '123456789'

        # Create Docking Area
        Location.objects.create(
            warehouse_id=warehouse_id,
            name='Docking Area',
            aisle='0',
            rack='0',
            level='0',
            barcode=f'{random_prefix}1000',
            capacity=250000
        )
        self.stdout.write(self.style.SUCCESS('Successfully created Docking Area'))

        for aisle in range(1, 4):
            for rack in range(1, 5):
                for level in range(0, 4):
                    if level == 0:
                        capacity = 50000
                    else:
                        capacity = 20000
                    name = f'A{aisle}R{rack}L{level}'
                    barcode_suffix = f'{warehouse_id}{aisle}{rack}{level}'
                    barcode = f'{random_prefix}{barcode_suffix}'
                    
                    Location.objects.create(
                        warehouse_id=warehouse_id,
                        name=name,
                        aisle=str(aisle),
                        rack=str(rack),
                        level=str(level),
                        barcode=barcode,
                        capacity=capacity
                    )
                    self.stdout.write(self.style.SUCCESS(f'Successfully created {name}'))
