#!/usr/bin/env python3
"""Gera previsões horárias estáticas para municípios brasileiros."""
import csv, io, json, os, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clima" / "dados"
OUT.mkdir(parents=True, exist_ok=True)
CATALOG = "https://raw.githubusercontent.com/kelvins/Municipios-Brasileiros/main/csv/municipios.csv"
API = "https://api.open-meteo.com/v1/forecast"
UF = {"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO","21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}

def get(url, attempts=4):
    for n in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"ClimaBrasil/1.0 (GitHub Pages)"})
            with urllib.request.urlopen(req, timeout=90) as res:
                return res.read()
        except Exception:
            if n == attempts-1: raise
            time.sleep(3*(n+1))

def main():
    cities = []
    for row in csv.DictReader(io.StringIO(get(CATALOG).decode("utf-8-sig"))):
        try:
            code = str(row["codigo_ibge"])
            uf = UF[code[:2]]
            cities.append({"id":code,"nome":row["nome"],"uf":uf,"lat":float(row["latitude"]),"lon":float(row["longitude"])})
        except (KeyError, ValueError):
            continue
    if len(cities) < 5500:
        raise RuntimeError("Catálogo incompleto; atualização abortada")
    cities.sort(key=lambda c:(c["uf"],c["nome"]))
    (OUT/"municipios.json").write_text(json.dumps([{"id":c["id"],"nome":c["nome"],"uf":c["uf"]} for c in cities],ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    timestamp=datetime.now(timezone.utc).isoformat()
    errors=[]
    # Uma requisição por lote de até 50 coordenadas; menos de 120 chamadas por execução.
    for start in range(0,len(cities),50):
        group=cities[start:start+50]
        from urllib.parse import urlencode
        params={"latitude":",".join(str(c["lat"]) for c in group),"longitude":",".join(str(c["lon"]) for c in group),
                "hourly":"temperature_2m,relative_humidity_2m,precipitation,precipitation_probability,rain,showers,wind_speed_10m,wind_direction_10m,weather_code",
                "forecast_days":3,"timezone":"America/Sao_Paulo"}
        try:
            response=json.loads(get(API+"?"+urlencode(params)))
            items=response if isinstance(response,list) else [response]
            if len(items)!=len(group): raise ValueError("Quantidade de previsões divergente")
            for city,forecast in zip(group,items):
                if "hourly" not in forecast: raise ValueError("Previsão horária ausente")
                city["previsao"]={"atualizado":timestamp,"horas":forecast["hourly"]}
        except Exception as exc:
            errors.append(f"{start}: {exc}")
        time.sleep(0.25)
    for uf in sorted(set(c["uf"] for c in cities)):
        data={c["id"]:c["previsao"] for c in cities if c["uf"]==uf and "previsao" in c}
        if data:
            (OUT/f"{uf}.json").write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    coverage=sum("previsao" in c for c in cities)
    (OUT/"status.json").write_text(json.dumps({"atualizado":timestamp,"total":len(cities),"disponiveis":coverage,"falhas":errors[:15]},ensure_ascii=False),encoding="utf-8")
    print(f"{coverage}/{len(cities)} municípios; {len(errors)} lotes com falha")
    if coverage < len(cities)*0.95:
        raise RuntimeError("Cobertura abaixo de 95%; verificar provedor")

if __name__=="__main__": main()
