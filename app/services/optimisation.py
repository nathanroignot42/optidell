# app/services/optimisation.py
import requests
import os
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from datetime import datetime

# URL de votre serveur OSRM
if os.getenv("RENDER") == "1":
    OSRM_TABLE_URL = "https://router.project-osrm.org/table/v1/driving/"
    OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving/"
else:
    OSRM_TABLE_URL = "https://router.project-osrm.org/table/v1/driving/"
    OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving/"

def get_osrm_matrix(locations):
    if len(locations) < 2:
        return [[0]]
    coords = ";".join([f"{lon},{lat}" for lat, lon in locations])
    url = f"{OSRM_TABLE_URL}{coords}?annotations=duration"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"Erreur OSRM Table: {r.text}")
    data = r.json()
    durations_sec = data["durations"]
    return [[int(d/60) if d is not None else 0 for d in row] for row in durations_sec]

def get_osrm_route(locations):
    if len(locations) < 2:
        return locations
    coords = ";".join([f"{lon},{lat}" for lat, lon in locations])
    url = f"{OSRM_ROUTE_URL}{coords}?overview=full&geometries=geojson"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"Erreur OSRM Route: {r.text}")
    data = r.json()
    return [[lat, lon] for lon, lat in data['routes'][0]['geometry']['coordinates']]

def optimiser_tournee_visites(visites, cabinet):
    """
    Optimise l'ordre des visites avec OR-Tools en tenant compte :
      - des fenêtres horaires
      - des durées des soins (service time)
    visites: liste d'objets avec latitude, longitude, duree_minutes, heure_debut, heure_fin
    Retour: (ordre_visites, polyline_OSRM)
    """
    if not visites:
        return [], []

    # 1️⃣ Préparer les données
    locations = [(cabinet.latitude, cabinet.longitude)]
    locations += [(v.latitude, v.longitude) for v in visites]
    n = len(locations)
    durations = [0] + [v.duree_minutes or 30 for v in visites]  # Durée des visites en minutes

    # 2️⃣ Fenêtres horaires
    debut_visites = [v.heure_debut for v in visites if v.heure_debut is not None]
    base_min = min([v.hour*60 + v.minute for v in debut_visites], default=0)
    time_windows = [(0, 1440)]
    for v, dur in zip(visites, durations[1:]):
        start = (v.heure_debut.hour*60 + v.heure_debut.minute - base_min) if v.heure_debut else 0
        end = (v.heure_fin.hour*60 + v.heure_fin.minute - base_min) if v.heure_fin else 1440
        start = max(0, start)
        end = max(start + 1, end)  # au moins 1 min
        time_windows.append((start, end))

    # 3️⃣ Matrice des temps de trajet
    distance_matrix = get_osrm_matrix(locations)

    # 4️⃣ Initialiser OR-Tools
    depot = 0
    manager = pywrapcp.RoutingIndexManager(n, 1, depot)
    routing = pywrapcp.RoutingModel(manager)

    # 5️⃣ Transit callback prenant en compte le temps de trajet + durée de visite
    def transit_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        service_time = durations[from_node]  # durée de la visite à partir du point actuel
        travel_time = distance_matrix[from_node][to_node]
        return service_time + travel_time

    transit_index = routing.RegisterTransitCallback(transit_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_index)

    # 6️⃣ Dimension Temps
    routing.AddDimension(
        transit_index,
        1440,  # slack max
        1440,  # horizon max
        False, # start cumul to zero
        "Time"
    )
    time_dimension = routing.GetDimensionOrDie("Time")

    # Ajouter les fenêtres horaires
    for i in range(n):
        index = manager.NodeToIndex(i)
        start, end = time_windows[i]
        time_dimension.CumulVar(index).SetRange(int(start), int(end))

    # 7️⃣ Résolution
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.time_limit.seconds = 10

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        ordre = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != 0:
                ordre.append(node - 1)
            index = solution.Value(routing.NextVar(index))

        ordered_locations = [locations[0]] + [locations[i+1] for i in ordre] + [locations[0]]
        route = get_osrm_route(ordered_locations)
        return ordre, route

    else:
        raise Exception("Impossible d'optimiser la tournée avec fenêtres horaires")