# Azure ML — assets reproducibles (HW5)

Despliegue completo del experimento AutoML de regresión sobre el dataset UCI Automobile.

## Archivos

| Archivo | Propósito |
|---|---|
| `data/automobile_price.csv` | Dataset limpio: 201 filas, 25 features, objetivo `price` |
| `data/MLTable` | Descriptor MLTable (lectura CSV con cabecera) |
| `compute.yml` | Clúster `cpu-cluster` (DS3_v2, 0–2 nodos, idle 5 min) |
| `automl-automobile.yml` | Job AutoML (regresión, R², 5-fold CV, 10 trials) |

## Comandos

```bash
RG=rg-cloudtask-hw5
WS=azureml-hw5

az ml workspace create -n $WS -g $RG -l eastus
az ml compute create --file compute.yml -g $RG -w $WS
az ml data create --name automobile-price --version 1 --type mltable \
  --path data -g $RG -w $WS
az ml job create --file automl-automobile.yml -g $RG -w $WS
```

## Limpieza

```bash
az group delete -n rg-cloudtask-hw5 --yes --no-wait
```
