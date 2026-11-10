#!/usr/bin/env bash
set -e
BASE=${1:-http://localhost:8000}
H='Content-Type: application/json'
echo "== healthz";  curl -s $BASE/healthz; echo
echo "== CREATE";   R=$(curl -s -X POST $BASE/api/prestamos -H "$H" -d '{"ejemplar_id":1,"prestatario":"Prueba Débora"}'); echo $R
ID=$(echo $R | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
echo "== READ";     curl -s $BASE/api/prestamos/$ID; echo
echo "== UPDATE";   curl -s -X PUT $BASE/api/prestamos/$ID -H "$H" -d '{"ejemplar_id":1,"prestatario":"Prueba Débora","fecha_devolucion":"2026-11-12"}'; echo
echo "== LIST";     curl -s $BASE/api/prestamos; echo
echo "== ERROR 400 (ejemplar inexistente)"; curl -s -w " -> %{http_code}\n" -X POST $BASE/api/prestamos -H "$H" -d '{"ejemplar_id":9999,"prestatario":"X"}'
echo "== DELETE";   curl -s -o /dev/null -w "%{http_code}\n" -X DELETE $BASE/api/prestamos/$ID
echo "== READ tras DELETE (404)"; curl -s -w " -> %{http_code}\n" $BASE/api/prestamos/$ID