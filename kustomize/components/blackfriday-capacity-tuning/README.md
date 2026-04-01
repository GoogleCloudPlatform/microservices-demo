# blackfriday-capacity-tuning

Component Kustomize pour les tests de charge Black Friday.

Objectif:
- garder un autoscaling 100% automatique (HPA + Cluster Autoscaler),
- éviter les crashes OOM du `frontend` et du `loadgenerator` pendant les paliers élevés.

Patches appliqués:
- `frontend`: ressources CPU/RAM augmentées + probes HTTP plus tolérantes.
- `loadgenerator`: ressources CPU/RAM augmentées pour supporter les profils 20K/50K.
