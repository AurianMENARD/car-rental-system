import sqlite3
from typing import Any, Dict, Iterable, List, Optional


class Database:
    def __init__(self, db_path: str = "car_rental.db") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                category TEXT NOT NULL,
                rate REAL NOT NULL,
                status TEXT NOT NULL,
                in_maintenance INTEGER NOT NULL DEFAULT 0,
                maintenance_notes TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                license_number TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS rentals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                vehicle_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                return_date TEXT,
                total_cost REAL,
                status TEXT NOT NULL,
                FOREIGN KEY(customer_id) REFERENCES customers(id),
                FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
            );
            """
        )
        self.conn.commit()

    def _execute(
        self,
        sql: str,
        params: Iterable[Any] = (),
        *,
        fetchone: bool = False,
        fetchall: bool = False,
        commit: bool = False,
    ) -> Any:
        cur = self.conn.execute(sql, params)
        if commit:
            self.conn.commit()
        if fetchone:
            return cur.fetchone()
        if fetchall:
            return cur.fetchall()
        return cur

    def insert_vehicle(self, data: Dict[str, Any]) -> int:
        cur = self._execute(
            """
            INSERT INTO vehicles (type, brand, model, category, rate, status, in_maintenance, maintenance_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["type"],
                data["brand"],
                data["model"],
                data["category"],
                data["rate"],
                data["status"],
                1 if data["in_maintenance"] else 0,
                data["maintenance_notes"],
            ),
            commit=True,
        )
        return int(cur.lastrowid)

    def list_vehicles(self, status: Optional[str] = None) -> List[sqlite3.Row]:
        if status:
            return self._execute(
                "SELECT * FROM vehicles WHERE status = ?",
                (status,),
                fetchall=True,
            )
        return self._execute("SELECT * FROM vehicles", fetchall=True)

    def get_vehicle(self, vehicle_id: int) -> Optional[sqlite3.Row]:
        return self._execute(
            "SELECT * FROM vehicles WHERE id = ?",
            (vehicle_id,),
            fetchone=True,
        )

    def update_vehicle_status(self, vehicle_id: int, status: str) -> None:
        self._execute(
            "UPDATE vehicles SET status = ? WHERE id = ?",
            (status, vehicle_id),
            commit=True,
        )

    def update_vehicle(
        self,
        vehicle_id: int,
        rate: float,
        in_maintenance: bool,
        maintenance_notes: str,
    ) -> None:
        self._execute(
            """
            UPDATE vehicles
            SET rate = ?, in_maintenance = ?, maintenance_notes = ?
            WHERE id = ?
            """,
            (rate, 1 if in_maintenance else 0, maintenance_notes, vehicle_id),
            commit=True,
        )

    def delete_vehicle(self, vehicle_id: int) -> None:
        self._execute(
            "DELETE FROM vehicles WHERE id = ?",
            (vehicle_id,),
            commit=True,
        )

    def update_vehicle_maintenance(
        self, vehicle_id: int, in_maintenance: bool, notes: str
    ) -> None:
        self._execute(
            "UPDATE vehicles SET in_maintenance = ?, maintenance_notes = ? WHERE id = ?",
            (1 if in_maintenance else 0, notes, vehicle_id),
            commit=True,
        )

    def insert_customer(self, data: Dict[str, Any]) -> int:
        cur = self._execute(
            """
            INSERT INTO customers (first_name, last_name, age, license_number)
            VALUES (?, ?, ?, ?)
            """,
            (data["first_name"], data["last_name"], data["age"], data["license_number"]),
            commit=True,
        )
        return int(cur.lastrowid)

    def list_customers(self) -> List[sqlite3.Row]:
        return self._execute("SELECT * FROM customers", fetchall=True)

    def get_customer(self, customer_id: int) -> Optional[sqlite3.Row]:
        return self._execute(
            "SELECT * FROM customers WHERE id = ?",
            (customer_id,),
            fetchone=True,
        )

    def update_customer(
        self,
        customer_id: int,
        first_name: str,
        last_name: str,
        age: int,
        license_number: str,
    ) -> None:
        self._execute(
            """
            UPDATE customers
            SET first_name = ?, last_name = ?, age = ?, license_number = ?
            WHERE id = ?
            """,
            (first_name, last_name, age, license_number, customer_id),
            commit=True,
        )

    def delete_customer(self, customer_id: int) -> None:
        self._execute(
            "DELETE FROM customers WHERE id = ?",
            (customer_id,),
            commit=True,
        )

    def insert_rental(self, data: Dict[str, Any]) -> int:
        cur = self._execute(
            """
            INSERT INTO rentals (customer_id, vehicle_id, start_date, end_date, return_date, total_cost, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["customer_id"],
                data["vehicle_id"],
                data["start_date"],
                data["end_date"],
                data.get("return_date"),
                data.get("total_cost"),
                data["status"],
            ),
            commit=True,
        )
        return int(cur.lastrowid)

    def get_rental(self, rental_id: int) -> Optional[sqlite3.Row]:
        return self._execute(
            "SELECT * FROM rentals WHERE id = ?",
            (rental_id,),
            fetchone=True,
        )

    def list_rentals(self, status: Optional[str] = None) -> List[sqlite3.Row]:
        if status:
            return self._execute(
                "SELECT * FROM rentals WHERE status = ?",
                (status,),
                fetchall=True,
            )
        return self._execute("SELECT * FROM rentals", fetchall=True)

    def has_ongoing_rental_for_customer(self, customer_id: int) -> bool:
        row = self._execute(
            "SELECT 1 FROM rentals WHERE customer_id = ? AND status = 'ongoing' LIMIT 1",
            (customer_id,),
            fetchone=True,
        )
        return row is not None

    def update_rental_completion(
        self, rental_id: int, return_date: str, total_cost: float
    ) -> None:
        self._execute(
            """
            UPDATE rentals
            SET return_date = ?, total_cost = ?, status = 'completed'
            WHERE id = ?
            """,
            (return_date, total_cost, rental_id),
            commit=True,
        )

    def revenue(self) -> float:
        row = self._execute(
            "SELECT COALESCE(SUM(total_cost), 0) AS total FROM rentals WHERE status = 'completed'",
            fetchone=True,
        )
        return float(row["total"]) if row else 0.0
