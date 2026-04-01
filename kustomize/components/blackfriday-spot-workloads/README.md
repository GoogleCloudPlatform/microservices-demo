# blackfriday-spot-workloads

Objectif:
- orienter les workloads non critiques vers les nodes Spot,
- sans rendre le scheduling fragile si Spot indisponible.

Strategie:
- `tolerations` pour accepter le taint `spot-instance=true:NoSchedule`,
- `nodeAffinity` en mode `preferred` (et pas `required`) pour preferer les nodes labels `capacity-type=spot`.

Workloads cibles:
- `loadgenerator`
- `recommendationservice`
