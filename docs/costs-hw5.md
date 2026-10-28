# Costos HW5 — Azure Machine Learning (East US, free account con $200)

| Recurso | Detalle | Costo estimado |
|---|---|---|
| Azure ML Workspace | Sin cargo fijo por el recurso | $0.00 |
| Compute cluster `cpu-cluster` | `Standard_DS3_v2` (~$0.293/h) × ~0.5 h (arranque + 10–20 min de trials) | ~$0.15 |
| Storage Account | < 1 GB (dataset y artefactos) | < $0.05 |
| Key Vault | Pocas operaciones | ~$0.00 |
| Application Insights / Log Analytics | Ingesta de unos MB y retención corta | < $0.05 |
| Transferencia | Mínima | ~$0.00 |
| **Total del trabajo** | | **< $0.50** (cubierto por el crédito de $200) |

Notas:
- El clúster tiene **mínimo 0 nodos** y baja a cero tras 5 min inactivo: solo se paga mientras entrena.
- El workspace y los servicios asociados no tienen costo fijo relevante para este alcance.
- Si se dejara el clúster con 1 nodo encendido 24/7 durante un mes, serían ~$214; por eso se usa
  escala a cero y se borra el grupo de recursos al terminar.
- Limpieza total: `az group delete --name rg-cloudtask-hw5 --yes --no-wait`.
