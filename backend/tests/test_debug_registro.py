"""
Script de diagnóstico para detectar el problema del doble registro
Ejecutar con: python tests/test_debug_registro.py
"""

import requests
import time
import threading
from collections import Counter

API_URL = "http://localhost:5000"


def test_registro_simple():
    """Test simple de registro para ver el comportamiento"""
    print("\n" + "=" * 80)
    print("TEST 1: REGISTRO SIMPLE")
    print("=" * 80)

    datos = {
        "nombre": "Test Simple",
        "email": f"simple_{int(time.time())}@test.com",
        "password": "password123"
    }

    print(f"\n📤 Enviando registro: {datos['email']}")
    start = time.time()

    response = requests.post(f"{API_URL}/api/auth/registro", json=datos)

    end = time.time()
    tiempo = (end - start) * 1000

    print(f"⏱️  Tiempo de respuesta: {tiempo:.2f}ms")
    print(f"📊 Status code: {response.status_code}")
    print(f"📄 Response: {response.json()}")

    return response.status_code == 200


def test_registro_duplicado():
    """Test de registro duplicado inmediato"""
    print("\n" + "=" * 80)
    print("TEST 2: REGISTRO DUPLICADO INMEDIATO")
    print("=" * 80)

    email = f"duplicate_{int(time.time())}@test.com"
    datos = {
        "nombre": "Test Duplicate",
        "email": email,
        "password": "password123"
    }

    print(f"\n📤 Primer registro: {email}")
    response1 = requests.post(f"{API_URL}/api/auth/registro", json=datos)
    print(f"   Status: {response1.status_code}")

    print(f"\n📤 Segundo registro (mismo email): {email}")
    response2 = requests.post(f"{API_URL}/api/auth/registro", json=datos)
    print(f"   Status: {response2.status_code}")
    print(f"   Response: {response2.json()}")

    return response1.status_code == 200 and response2.status_code == 400


def test_multiples_requests_rapidos():
    """Test de múltiples requests rápidos al mismo endpoint"""
    print("\n" + "=" * 80)
    print("TEST 3: MÚLTIPLES REQUESTS RÁPIDOS (mismo email)")
    print("=" * 80)

    email = f"multi_{int(time.time())}@test.com"
    datos = {
        "nombre": "Test Multi",
        "email": email,
        "password": "password123"
    }

    resultados = []

    def hacer_request():
        try:
            response = requests.post(f"{API_URL}/api/auth/registro", json=datos)
            resultados.append({
                'status': response.status_code,
                'time': time.time(),
                'json': response.json()
            })
        except Exception as e:
            resultados.append({
                'status': 'ERROR',
                'error': str(e)
            })

    # Lanzar 5 requests simultáneos
    threads = []
    print(f"\n🚀 Lanzando 5 requests simultáneos para: {email}")

    for i in range(5):
        thread = threading.Thread(target=hacer_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Analizar resultados
    status_codes = [r['status'] for r in resultados]
    counter = Counter(status_codes)

    print(f"\n📊 Resultados:")
    for status, count in counter.items():
        print(f"   Status {status}: {count} requests")

    print(f"\n📝 Detalles:")
    for i, r in enumerate(resultados, 1):
        print(f"   Request {i}: Status {r['status']}")
        if r['status'] == 200:
            print(f"              ✅ Success")
        elif r['status'] == 400:
            print(f"              ❌ {r['json'].get('detail', 'Error')}")

    # Debe haber exactamente 1 success y 4 errores 400
    success_count = counter.get(200, 0)
    error_count = counter.get(400, 0)

    print(f"\n✅ Exitosos: {success_count}")
    print(f"❌ Fallidos: {error_count}")

    return success_count == 1 and error_count == 4


def test_timing_request():
    """Test para medir tiempos de respuesta y detectar llamadas duplicadas"""
    print("\n" + "=" * 80)
    print("TEST 4: ANÁLISIS DE TIMING")
    print("=" * 80)

    # Hacer 10 registros y medir tiempos
    tiempos = []

    for i in range(10):
        email = f"timing_{i}_{int(time.time() * 1000)}@test.com"
        datos = {
            "nombre": f"Timing Test {i}",
            "email": email,
            "password": "password123"
        }

        start = time.time()
        response = requests.post(f"{API_URL}/api/auth/registro", json=datos)
        end = time.time()

        tiempo = (end - start) * 1000
        tiempos.append(tiempo)

        print(f"Request {i + 1:2d}: {tiempo:6.2f}ms - Status {response.status_code}")

        time.sleep(0.1)  # Pequeña pausa entre requests

    # Estadísticas
    promedio = sum(tiempos) / len(tiempos)
    minimo = min(tiempos)
    maximo = max(tiempos)

    print(f"\n📊 Estadísticas de tiempo:")
    print(f"   Promedio: {promedio:.2f}ms")
    print(f"   Mínimo:   {minimo:.2f}ms")
    print(f"   Máximo:   {maximo:.2f}ms")

    # Si algún tiempo es muy largo, puede indicar un problema
    if maximo > 2000:
        print(f"\n⚠️  ADVERTENCIA: Tiempo máximo muy alto ({maximo:.2f}ms)")

    return promedio < 1000


def test_interceptar_network():
    """Test para capturar headers y detectar requests duplicados"""
    print("\n" + "=" * 80)
    print("TEST 5: ANÁLISIS DE NETWORK")
    print("=" * 80)

    email = f"network_{int(time.time())}@test.com"
    datos = {
        "nombre": "Network Test",
        "email": email,
        "password": "password123"
    }

    # Configurar sesión con logs detallados
    import logging
    from http.client import HTTPConnection

    HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    print(f"\n📤 Enviando request con logs detallados...")
    response = requests.post(f"{API_URL}/api/auth/registro", json=datos)

    print(f"\n📊 Status: {response.status_code}")
    print(f"📊 Headers: {dict(response.headers)}")

    return True


def main():
    """Ejecutar todos los tests de diagnóstico"""
    print("\n" + "🔍" * 40)
    print("DIAGNÓSTICO DE REGISTRO - DETECCIÓN DE DOBLE REQUEST")
    print("🔍" * 40)

    try:
        # Verificar que la API está corriendo
        print("\n✅ Verificando API...")
        response = requests.get(f"{API_URL}/health")
        if response.status_code != 200:
            print("❌ Error: API no está corriendo en", API_URL)
            return
        print("✅ API está corriendo correctamente")

        # Ejecutar tests
        resultados = {
            "Test 1 - Registro Simple": test_registro_simple(),
            "Test 2 - Registro Duplicado": test_registro_duplicado(),
            "Test 3 - Requests Concurrentes": test_multiples_requests_rapidos(),
            "Test 4 - Análisis de Timing": test_timing_request(),
        }

        # Resumen
        print("\n" + "=" * 80)
        print("RESUMEN DE TESTS")
        print("=" * 80)

        for test_name, passed in resultados.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {test_name}")

        total = len(resultados)
        passed = sum(1 for p in resultados.values() if p)
        print(f"\n📊 Total: {passed}/{total} tests pasados")

        # Recomendaciones
        print("\n" + "=" * 80)
        print("DIAGNÓSTICO Y RECOMENDACIONES")
        print("=" * 80)

        if not resultados["Test 3 - Requests Concurrentes"]:
            print("\n⚠️  PROBLEMA DETECTADO: Múltiples registros con el mismo email")
            print("   Posibles causas:")
            print("   1. Race condition en la base de datos")
            print("   2. Falta de constraint UNIQUE en el email")
            print("   3. Frontend enviando múltiples requests")
            print("\n   Soluciones sugeridas:")
            print("   - Verificar constraint UNIQUE en tabla usuarios")
            print("   - Añadir debounce en el frontend")
            print("   - Implementar idempotency key")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: No se puede conectar a {API_URL}")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   python -m uvicorn backend.main:app --reload --port 5000")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()