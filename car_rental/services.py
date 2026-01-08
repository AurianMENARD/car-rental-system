from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
from typing import Dict, List, Optional

from .database import Database
from .models import Car, Customer, Motorcycle, Rental, Truck, Vehicle


MIN_AGE_BY_TYPE = {
    "car": 18,
    "motorcycle": 21,
    "truck": 23,
}


def _parse_date(value: date | str) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


class CarRentalSystem:
    def __init__(self, db_path: str = "car_rental.db") -> None:
        self.db = Database(db_path)

    def add_vehicle(self, vehicle: Vehicle) -> int:
        data = {
            "type": vehicle.vehicle_type,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "category": vehicle.category,
            "rate": vehicle.rate_per_day,
            "status": vehicle.status,
            "in_maintenance": vehicle.in_maintenance,
            "maintenance_notes": vehicle.maintenance_notes,
        }
        return self.db.insert_vehicle(data)

    def list_vehicles(self, status: Optional[str] = None) -> List[Dict]:
        return [dict(row) for row in self.db.list_vehicles(status=status)]

    def set_vehicle_maintenance(self, vehicle_id: int, in_maintenance: bool, notes: str = "") -> None:
        self.db.update_vehicle_maintenance(vehicle_id, in_maintenance, notes)

    def update_vehicle(
        self, vehicle_id: int, rate: float, in_maintenance: bool, notes: str
    ) -> None:
        vehicle = self.db.get_vehicle(vehicle_id)
        if not vehicle:
            raise ValueError("Vehicle not found.")
        if vehicle["status"] == "rented":
            raise ValueError("Vehicle is currently rented.")
        self.db.update_vehicle(vehicle_id, rate, in_maintenance, notes)

    def delete_vehicle(self, vehicle_id: int) -> None:
        vehicle = self.db.get_vehicle(vehicle_id)
        if not vehicle:
            raise ValueError("Vehicle not found.")
        if vehicle["status"] == "rented":
            raise ValueError("Vehicle is currently rented.")
        self.db.delete_vehicle(vehicle_id)

    def add_customer(self, customer: Customer) -> int:
        data = {
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "age": customer.age,
            "license_number": customer.license_number,
        }
        return self.db.insert_customer(data)

    def list_customers(self) -> List[Dict]:
        return [dict(row) for row in self.db.list_customers()]

    def update_customer(
        self, customer_id: int, first_name: str, last_name: str, age: int, license_number: str
    ) -> None:
        customer = self.db.get_customer(customer_id)
        if not customer:
            raise ValueError("Customer not found.")
        if self.db.has_ongoing_rental_for_customer(customer_id):
            raise ValueError("Customer has an ongoing rental.")
        self.db.update_customer(customer_id, first_name, last_name, age, license_number)

    def delete_customer(self, customer_id: int) -> None:
        customer = self.db.get_customer(customer_id)
        if not customer:
            raise ValueError("Customer not found.")
        if self.db.has_ongoing_rental_for_customer(customer_id):
            raise ValueError("Customer has an ongoing rental.")
        self.db.delete_customer(customer_id)

    def _validate_rental(self, customer_id: int, vehicle_id: int, start_date: date, end_date: date) -> None:
        if end_date < start_date:
            raise ValueError("End date must be on or after start date.")

        customer = self.db.get_customer(customer_id)
        if not customer:
            raise ValueError("Customer not found.")

        vehicle = self.db.get_vehicle(vehicle_id)
        if not vehicle:
            raise ValueError("Vehicle not found.")

        if vehicle["status"] != "available":
            raise ValueError("Vehicle is not available.")

        if vehicle["in_maintenance"]:
            raise ValueError("Vehicle is in maintenance.")

        min_age = MIN_AGE_BY_TYPE.get(vehicle["type"], 18)
        if customer["age"] < min_age:
            raise ValueError("Customer does not meet the minimum age for this vehicle.")

    def _calculate_total_cost(
        self,
        rate: float,
        start_date: date,
        end_date: date,
        return_date: Optional[date] = None,
    ) -> float:
        base_days = (end_date - start_date).days + 1
        total = base_days * rate
        if return_date and return_date > end_date:
            extra_days = (return_date - end_date).days
            total += extra_days * rate * 1.2
        return round(total, 2)

    def create_rental(
        self,
        customer_id: int,
        vehicle_id: int,
        start_date: date | str,
        end_date: date | str,
    ) -> int:
        start = _parse_date(start_date)
        end = _parse_date(end_date)
        self._validate_rental(customer_id, vehicle_id, start, end)

        rental = Rental(
            id=None,
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            start_date=start,
            end_date=end,
        )
        rental_id = self.db.insert_rental(
            {
                "customer_id": rental.customer_id,
                "vehicle_id": rental.vehicle_id,
                "start_date": rental.start_date.isoformat(),
                "end_date": rental.end_date.isoformat(),
                "status": rental.status,
            }
        )
        self.db.update_vehicle_status(vehicle_id, "rented")
        return rental_id

    def return_vehicle(self, rental_id: int, return_date: date | str) -> float:
        rental = self.db.get_rental(rental_id)
        if not rental:
            raise ValueError("Rental not found.")
        if rental["status"] != "ongoing":
            raise ValueError("Rental is not ongoing.")

        vehicle = self.db.get_vehicle(rental["vehicle_id"])
        if not vehicle:
            raise ValueError("Vehicle not found.")

        return_dt = _parse_date(return_date)
        start = _parse_date(rental["start_date"])
        end = _parse_date(rental["end_date"])

        total_cost = self._calculate_total_cost(vehicle["rate"], start, end, return_dt)
        self.db.update_rental_completion(rental_id, return_dt.isoformat(), total_cost)
        self.db.update_vehicle_status(rental["vehicle_id"], "available")
        return total_cost

    def available_vehicles(self) -> List[Dict]:
        rows = self.db.list_vehicles(status="available")
        return [dict(row) for row in rows if not row["in_maintenance"]]

    def ongoing_rentals(self) -> List[Dict]:
        return [dict(row) for row in self.db.list_rentals(status="ongoing")]

    def revenue(self) -> float:
        return self.db.revenue()

    def stats_by_type(self) -> Dict[str, int]:
        stats: Dict[str, int] = {"car": 0, "truck": 0, "motorcycle": 0, "vehicle": 0}
        for vehicle in self.db.list_vehicles():
            stats[vehicle["type"]] = stats.get(vehicle["type"], 0) + 1
        return stats

    def export_vehicle(self, vehicle: Vehicle) -> Dict:
        data = asdict(vehicle)
        data["type"] = vehicle.vehicle_type
        return data

    def vehicle_from_row(self, row: Dict) -> Vehicle:
        vehicle_type = row["type"]
        klass = {
            "car": Car,
            "truck": Truck,
            "motorcycle": Motorcycle,
        }.get(vehicle_type, Vehicle)
        return klass(
            id=row["id"],
            brand=row["brand"],
            model=row["model"],
            category=row["category"],
            rate_per_day=row["rate"],
            status=row["status"],
            in_maintenance=bool(row["in_maintenance"]),
            maintenance_notes=row["maintenance_notes"],
        )
