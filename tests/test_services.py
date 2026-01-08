import unittest
from datetime import date, timedelta

from car_rental import Car, CarRentalSystem, Customer, Motorcycle


class CarRentalSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.system = CarRentalSystem(":memory:")

    def test_create_rental_and_return(self) -> None:
        vehicle_id = self.system.add_vehicle(
            Car(
                id=None,
                brand="Toyota",
                model="Corolla",
                category="compact",
                rate_per_day=50.0,
            )
        )
        customer_id = self.system.add_customer(
            Customer(
                id=None,
                first_name="Alice",
                last_name="Martin",
                age=25,
                license_number="ABC123",
            )
        )
        start = date.today()
        end = start + timedelta(days=2)
        rental_id = self.system.create_rental(customer_id, vehicle_id, start, end)
        total_cost = self.system.return_vehicle(rental_id, end)
        self.assertEqual(total_cost, 150.0)
        self.assertEqual(self.system.revenue(), 150.0)

    def test_age_rule(self) -> None:
        vehicle_id = self.system.add_vehicle(
            Motorcycle(
                id=None,
                brand="Honda",
                model="CB500",
                category="road",
                rate_per_day=40.0,
            )
        )
        customer_id = self.system.add_customer(
            Customer(
                id=None,
                first_name="Bob",
                last_name="Petit",
                age=18,
                license_number="MOTO001",
            )
        )
        with self.assertRaises(ValueError):
            self.system.create_rental(customer_id, vehicle_id, "2025-01-01", "2025-01-02")


if __name__ == "__main__":
    unittest.main()
