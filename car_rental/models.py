from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Vehicle:
    id: Optional[int]
    brand: str
    model: str
    category: str
    rate_per_day: float
    status: str = "available"
    in_maintenance: bool = False
    maintenance_notes: str = ""

    @property
    def vehicle_type(self) -> str:
        return "vehicle"


@dataclass
class Car(Vehicle):
    @property
    def vehicle_type(self) -> str:
        return "car"


@dataclass
class Truck(Vehicle):
    @property
    def vehicle_type(self) -> str:
        return "truck"


@dataclass
class Motorcycle(Vehicle):
    @property
    def vehicle_type(self) -> str:
        return "motorcycle"


@dataclass
class Customer:
    id: Optional[int]
    first_name: str
    last_name: str
    age: int
    license_number: str


@dataclass
class Rental:
    id: Optional[int]
    customer_id: int
    vehicle_id: int
    start_date: date
    end_date: date
    status: str = "ongoing"
    return_date: Optional[date] = None
    total_cost: Optional[float] = None
