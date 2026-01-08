# Car Rental System

Petit systeme de location de voitures en Python avec SQLite et une interface Streamlit.

## Fonctionnalites

- Gestion de la flotte (Vehicle, Car, Truck, Motorcycle)
- Gestion des clients
- Locations avec regles d'age, disponibilite et penalites
- Rapports simples (vehicules disponibles, locations en cours, chiffre d'affaires, stats)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancer l'application

```bash
streamlit run app.py
```

## Tests unitaires

```bash
python -m unittest
```

## Structure

- `car_rental/models.py` : modeles OOP
- `car_rental/database.py` : stockage SQLite
- `car_rental/services.py` : logique metier
- `app.py` : interface Streamlit
- `UML.md` : diagramme de classes

