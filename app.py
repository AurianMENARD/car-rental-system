from datetime import date

import streamlit as st

from car_rental import Car, CarRentalSystem, Customer, Motorcycle, Truck


st.set_page_config(page_title="Systeme de location de voitures", layout="wide")

system = CarRentalSystem("car_rental.db")

st.title("Systeme de location de voitures")

vehicle_tab, customer_tab, rental_tab, report_tab = st.tabs(
    ["Vehicules", "Clients", "Locations", "Rapports"]
)

with vehicle_tab:
    st.subheader("Ajouter un vehicule")
    with st.form("add_vehicle"):
        v_type = st.selectbox("Type", ["car", "truck", "motorcycle"])
        brand = st.text_input("Marque")
        model = st.text_input("Modele")
        category = st.text_input("Categorie")
        rate = st.number_input("Tarif par jour", min_value=1.0, step=1.0)
        in_maintenance = st.checkbox("En maintenance")
        maintenance_notes = st.text_input("Notes de maintenance")
        submitted = st.form_submit_button("Ajouter le vehicule")

    if submitted:
        klass = {"car": Car, "truck": Truck, "motorcycle": Motorcycle}[v_type]
        vehicle = klass(
            id=None,
            brand=brand,
            model=model,
            category=category,
            rate_per_day=rate,
            in_maintenance=in_maintenance,
            maintenance_notes=maintenance_notes,
        )
        system.add_vehicle(vehicle)
        st.success("Vehicule ajoute.")

    st.subheader("Flotte")
    st.dataframe(system.list_vehicles(), width="stretch")

    st.subheader("Modifier ou supprimer un vehicule")
    fleet = system.list_vehicles()
    if not fleet:
        st.info("Aucun vehicule a modifier.")
    else:
        vehicle_labels = {
            f"{v['id']} - {v['brand']} {v['model']} ({v['type']})": v["id"] for v in fleet
        }
        selected_label = st.selectbox("Selectionner un vehicule", list(vehicle_labels.keys()))
        selected_id = vehicle_labels[selected_label]
        selected = next(v for v in fleet if v["id"] == selected_id)

        with st.form("edit_vehicle"):
            rate = st.number_input(
                "Tarif par jour",
                min_value=1.0,
                step=1.0,
                value=float(selected["rate"]),
            )
            in_maintenance = st.checkbox(
                "En maintenance",
                value=bool(selected["in_maintenance"]),
            )
            maintenance_notes = st.text_input(
                "Notes de maintenance",
                value=selected["maintenance_notes"],
            )
            submitted = st.form_submit_button("Mettre a jour le vehicule")

        if submitted:
            try:
                system.update_vehicle(selected_id, rate, in_maintenance, maintenance_notes)
                st.success("Vehicule mis a jour.")
            except ValueError as exc:
                st.error(str(exc))

        if st.button("Supprimer le vehicule"):
            try:
                system.delete_vehicle(selected_id)
                st.success("Vehicule supprime.")
            except ValueError as exc:
                st.error(str(exc))

with customer_tab:
    st.subheader("Ajouter un client")
    with st.form("add_customer"):
        first_name = st.text_input("Prenom")
        last_name = st.text_input("Nom")
        age = st.number_input("Age", min_value=16, step=1)
        license_number = st.text_input("Numero de permis")
        submitted = st.form_submit_button("Ajouter le client")

    if submitted:
        customer = Customer(
            id=None,
            first_name=first_name,
            last_name=last_name,
            age=int(age),
            license_number=license_number,
        )
        system.add_customer(customer)
        st.success("Client ajoute.")

    st.subheader("Clients")
    st.dataframe(system.list_customers(), width="stretch")

    st.subheader("Modifier ou supprimer un client")
    customer_list = system.list_customers()
    if not customer_list:
        st.info("Aucun client a modifier.")
    else:
        customer_labels = {
            f"{c['id']} - {c['first_name']} {c['last_name']}": c["id"] for c in customer_list
        }
        selected_label = st.selectbox("Selectionner un client", list(customer_labels.keys()))
        selected_id = customer_labels[selected_label]
        selected = next(c for c in customer_list if c["id"] == selected_id)

        with st.form("edit_customer"):
            first_name = st.text_input("Prenom", value=selected["first_name"])
            last_name = st.text_input("Nom", value=selected["last_name"])
            age = st.number_input("Age", min_value=16, step=1, value=int(selected["age"]))
            license_number = st.text_input("Numero de permis", value=selected["license_number"])
            submitted = st.form_submit_button("Mettre a jour le client")

        if submitted:
            try:
                system.update_customer(selected_id, first_name, last_name, int(age), license_number)
                st.success("Client mis a jour.")
            except ValueError as exc:
                st.error(str(exc))

        if st.button("Supprimer le client"):
            try:
                system.delete_customer(selected_id)
                st.success("Client supprime.")
            except ValueError as exc:
                st.error(str(exc))

with rental_tab:
    st.subheader("Creer une location")
    customers = system.list_customers()
    vehicles = system.available_vehicles()

    if not customers:
        st.info("Ajoutez au moins un client pour creer une location.")
    elif not vehicles:
        st.info("Aucun vehicule disponible pour le moment.")
    else:
        with st.form("create_rental"):
            customer_map = {
                f"{c['id']} - {c['first_name']} {c['last_name']}": c["id"] for c in customers
            }
            vehicle_map = {
                f"{v['id']} - {v['brand']} {v['model']} ({v['type']})": v["id"] for v in vehicles
            }
            customer_label = st.selectbox("Client", list(customer_map.keys()))
            vehicle_label = st.selectbox("Vehicule", list(vehicle_map.keys()))
            start = st.date_input("Date de debut", value=date.today())
            end = st.date_input("Date de fin", value=date.today())
            submitted = st.form_submit_button("Creer la location")

        if submitted:
            try:
                rental_id = system.create_rental(
                    customer_id=customer_map[customer_label],
                    vehicle_id=vehicle_map[vehicle_label],
                    start_date=start,
                    end_date=end,
                )
                st.success(f"Location creee (ID : {rental_id}).")
            except ValueError as exc:
                st.error(str(exc))

    st.subheader("Retourner un vehicule")
    ongoing = system.ongoing_rentals()
    if ongoing:
        customers_by_id = {c["id"]: c for c in system.list_customers()}
        vehicles_by_id = {v["id"]: v for v in system.list_vehicles()}
        rental_map = {}
        for rental in ongoing:
            vehicle = vehicles_by_id.get(rental["vehicle_id"], {})
            customer = customers_by_id.get(rental["customer_id"], {})
            vehicle_name = f"{vehicle.get('brand', '')} {vehicle.get('model', '')}".strip() or "Vehicule inconnu"
            customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or "Client inconnu"
            label = f"{rental['id']} - {vehicle_name} / {customer_name}"
            rental_map[label] = rental["id"]
        with st.form("return_rental"):
            rental_label = st.selectbox("Location", list(rental_map.keys()))
            return_date = st.date_input("Date de retour", value=date.today())
            submitted = st.form_submit_button("Terminer la location")

        if submitted:
            try:
                total_cost = system.return_vehicle(rental_map[rental_label], return_date)
                st.success(f"Location terminee. Cout total : {total_cost:.2f}")
            except ValueError as exc:
                st.error(str(exc))
    else:
        st.info("Aucune location en cours.")

with report_tab:
    st.subheader("Vehicules disponibles")
    st.dataframe(system.available_vehicles(), width="stretch")

    st.subheader("Locations en cours")
    st.dataframe(system.ongoing_rentals(), width="stretch")

    st.subheader("Revenu")
    st.metric("Revenu total", f"{system.revenue():.2f}")

    st.subheader("Statistiques")
    st.json(system.stats_by_type())
