from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from sensors.models import MilkData
from analysis.models import AnalysisResult
from alerts.models import Alert
from inventory.models import Inventory
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


# ─────────────────────────────────────────────
#  CHANGE THESE VALUES TO TEST DIFFERENT RESULTS
# ─────────────────────────────────────────────
USERS = [
    {'username': 'admin',    'email': 'admin@milk.com',    'password': 'Admin@1234',    'role': 'ADMIN'},
    {'username': 'supplier', 'email': 'supplier@milk.com', 'password': 'Supplier@1234', 'role': 'SUPPLIER'},
    {'username': 'seller',   'email': 'seller@milk.com',   'password': 'Seller@1234',   'role': 'SELLER'},
]

# Sensor readings — change ph, temperature, gas, turbidity to test different statuses
# ph normal range: 6.4–6.8 | turbidity normal: <50 | temperature normal: 20–25
SENSOR_SAMPLES = [
    # GOOD milk samples
    {'ph': 6.6, 'temperature': 22.0, 'gas': 180, 'turbidity': 25, 'days_ago': 1},
    {'ph': 6.7, 'temperature': 21.5, 'gas': 190, 'turbidity': 28, 'days_ago': 2},
    {'ph': 6.5, 'temperature': 23.0, 'gas': 175, 'turbidity': 30, 'days_ago': 3},
    {'ph': 6.6, 'temperature': 22.5, 'gas': 185, 'turbidity': 27, 'days_ago': 4},
    {'ph': 6.7, 'temperature': 20.0, 'gas': 170, 'turbidity': 22, 'days_ago': 5},
    # BAD milk samples (low pH or high turbidity)
    {'ph': 6.2, 'temperature': 28.0, 'gas': 380, 'turbidity': 75, 'days_ago': 6},
    {'ph': 5.9, 'temperature': 30.0, 'gas': 420, 'turbidity': 85, 'days_ago': 7},
    {'ph': 6.1, 'temperature': 27.0, 'gas': 350, 'turbidity': 65, 'days_ago': 8},
    {'ph': 7.1, 'temperature': 26.5, 'gas': 310, 'turbidity': 60, 'days_ago': 9},
    {'ph': 6.0, 'temperature': 29.0, 'gas': 400, 'turbidity': 90, 'days_ago': 10},
    # More GOOD samples
    {'ph': 6.6, 'temperature': 21.0, 'gas': 165, 'turbidity': 20, 'days_ago': 11},
    {'ph': 6.5, 'temperature': 22.0, 'gas': 172, 'turbidity': 26, 'days_ago': 12},
    {'ph': 6.7, 'temperature': 23.5, 'gas': 188, 'turbidity': 29, 'days_ago': 13},
    # More BAD samples
    {'ph': 5.8, 'temperature': 31.0, 'gas': 450, 'turbidity': 95, 'days_ago': 14},
    {'ph': 6.3, 'temperature': 27.5, 'gas': 320, 'turbidity': 55, 'days_ago': 15},
]
# ─────────────────────────────────────────────


class Command(BaseCommand):
    help = 'Delete all users and seed fresh realistic test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        AnalysisResult.objects.all().delete()
        MilkData.objects.all().delete()
        Alert.objects.all().delete()
        try:
            Inventory.objects.all().delete()
        except Exception:
            pass
        User.objects.all().delete()
        self.stdout.write(self.style.WARNING('All data cleared.'))

        # Create users
        self.stdout.write('Creating users...')
        for u in USERS:
            is_admin = u['role'] == 'ADMIN'
            user = User.objects.create_user(
                username=u['username'],
                email=u['email'],
                password=u['password'],
                is_staff=is_admin,
                is_superuser=is_admin,
            )
            user.role = u['role']
            user.save()
            self.stdout.write(f"  {u['role']}: {u['email']} / {u['password']}")

        # Create sensor + analysis data
        self.stdout.write('Creating milk samples and analysis results...')
        for s in SENSOR_SAMPLES:
            ts = timezone.now() - timedelta(days=s['days_ago'])
            milk = MilkData.objects.create(
                ph=s['ph'],
                temperature=s['temperature'],
                gas=s['gas'],
                turbidity=s['turbidity'],
            )
            milk.timestamp = ts
            milk.save()

            # Analysis logic (same as backend)
            if s['ph'] < 6.4 or s['ph'] > 6.8 or s['turbidity'] > 50:
                result_status = 'BAD'
                adulteration_type = 'Water' if s['turbidity'] > 60 else 'Urea'
                percentage = round(random.uniform(12, 25), 1)
                reasons = 'Abnormal pH or High Turbidity detected.'
            else:
                result_status = 'GOOD'
                adulteration_type = None
                percentage = 0.0
                reasons = 'All parameters are within normal range.'

            analysis = AnalysisResult.objects.create(
                milk_data=milk,
                status=result_status,
                adulteration_type=adulteration_type,
                percentage=percentage,
                reasons=reasons,
            )
            analysis.created_at = ts
            analysis.save()

            if result_status == 'BAD':
                alert = Alert.objects.create(
                    message=f"Adulterated milk detected! Type: {adulteration_type}, {percentage}%",
                    severity='HIGH',
                )
                alert.created_at = ts
                alert.save()

        # Create inventory entries
        self.stdout.write('Creating inventory...')
        inventory_items = [
            {'milk_quantity': 500, 'status': 'AVAILABLE'},
            {'milk_quantity': 300, 'status': 'SOLD'},
            {'milk_quantity': 150, 'status': 'REJECTED'},
            {'milk_quantity': 200, 'status': 'AVAILABLE'},
            {'milk_quantity': 100, 'status': 'SOLD'},
        ]
        for item in inventory_items:
            try:
                Inventory.objects.create(**item)
            except Exception:
                pass

        good = sum(1 for s in SENSOR_SAMPLES if s['ph'] >= 6.4 and s['ph'] <= 6.8 and s['turbidity'] <= 50)
        bad = len(SENSOR_SAMPLES) - good

        self.stdout.write(self.style.SUCCESS(f'\nDone! Created:'))
        self.stdout.write(f'  {len(USERS)} users')
        self.stdout.write(f'  {len(SENSOR_SAMPLES)} milk samples ({good} GOOD, {bad} BAD)')
        self.stdout.write(f'  {bad} alerts')
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        for u in USERS:
            self.stdout.write(f'  {u["role"]}: {u["email"]} / {u["password"]}')
