# Proposal: Static Profile Opt-In and Production Performance Optimization

## Abstract

We propose standardizing SMonitor to run by default in an ultra-lightweight, static `production` profile, completely eliminating magic environment autodetection to prevent silent performance regressions. Under this profile, SMonitor acts as a central coordinator, communicating its active state to validation frameworks (like `argdigest`) so that both telemetry tracking and signature validation decorators statically short-circuit on hot paths, reducing total overhead in user environments to near-zero.

---

## The Problem

Performance benchmarks show that SMonitor introduces a non-trivial overhead when tracking high-frequency operations:
* **Baseline (None)**: ~21.06 ms mean latency.
* **SMonitor-only**: ~25.54 ms mean latency (+4.48 ms, **21.3% slowdown**).

This latency is driven by capturing signal events and particularly by dynamic stack-frame introspection (e.g. retrieving line numbers or local scopes).

Furthermore, if a normal scientific user session dynamically falls back to a slow "development" or "debug" profile due to a false positive in automatic environment detection, they will experience lag. Users should enjoy a correct, secure, and ultra-fast visual rendering experience without being forced to manage complex performance switches.

---

## Proposed Solution

We propose a deterministic, unified profile architecture:

### 1. Default to a Deterministic Production Profile
Auto-detection logic is deprecated. SMonitor will initialize strictly in the `"production"` profile:
* **Production Profile (Default)**: All heavy tracing, stack-frame capture, and calling context inspections are entirely disabled. Signals emit lightweight structural events only.
* **Development Profile (Explicit Opt-in)**: Active only when requested by:
  * An environment variable: `SMONITOR_PROFILE=development`
  * A programmatic call: `smonitor.set_profile("development")`

```python
# smonitor/config.py
import os

DEFAULT_PROFILE = "production"
PROFILE = os.getenv("SMONITOR_PROFILE", DEFAULT_PROFILE).lower()

if PROFILE not in ["production", "development", "disabled"]:
    PROFILE = "production"
```

### 2. Micro-Optimized Static Decorator Bypass
When SMonitor is in the `production` or `disabled` profile, decorators must short-circuit immediately. In particular, they must completely bypass calls to reflective functions (like `inspect` or `sys._getframe`) which are highly CPU-intensive:

```python
# smonitor/tracker.py
from .config import PROFILE

def track_signal(signal_name):
    def decorator(func):
        if PROFILE == "disabled":
            return func  # Total zero-cost import-time passthrough
            
        def wrapper(*args, **kwargs):
            if PROFILE == "production":
                # Production path: emit a lightweight, static event structure
                # completely avoiding call stack analysis
                emit_lightweight_event(signal_name)
                return func(*args, **kwargs)
                
            # Development path: capture full call stack trace and parameter states
            trace = capture_call_stack_trace()
            emit_detailed_event(signal_name, trace)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3. Unified Cross-Framework Coordination
During initialization, SMonitor will expose its profile state to sister libraries (such as `argdigest`). If `smonitor.PROFILE == "production"`, `argdigest` is automatically notified to activate its fast-path bypass on high-frequency validation decorators, achieving seamless, multi-library performance alignment:

```python
# smonitor/integration.py
def get_active_profile():
    return PROFILE
```
```python
# argdigest/decorators.py (ArgDigest queries SMonitor profile)
import smonitor

def arg_digest(*rules, high_frequency=False):
    # Read active profile directly from SMonitor
    is_production = getattr(smonitor, "PROFILE", "production") == "production"
    # Auto-bypass validation if in production and decorator is marked high-frequency
    ...
```

---

## Benefits

* **Seamless User Experience**: Normal users run in a highly responsive visual environment with zero telemetry-induced lag and zero configuration requirements.
* **Coordinated Performance**: A single config state (`smonitor.PROFILE`) automatically scales down both tracking and signature validations across the entire ecosystem.
* **Safety In Testing**: Comprehensive validation and signal tracing remain fully operational for developers running in the explicit development profile.

---

## Evidencia medida (2026-07-12) — esto no es una micro-optimización

Añadido tras perfilar el ecosistema desde MolSysViewer. Ver
`molsysviewer/devguide/pending_proposals/import_cost_and_lazy_loading.md` y
`pyunitwizard/devguide/pending_proposals/python_overhead_before_rusterization.md`.

**La propuesta de arriba estaba escrita sin números. Aquí están, y cambian su prioridad.**

Medido sobre `puw.get_value(q, to_unit="nanometers")` — una conversión de unidades trivial, la
operación más caliente del ecosistema:

| | coste | % |
|---|---|---|
| el trabajo real (pint desnudo) | **17 µs** | 7 % |
| **overhead del decorador con SMonitor DESACTIVADO** | **127 µs** | **49 %** |
| telemetría activa | 118 µs | 45 % |
| **total** | **262 µs** | **15× pint** |

**El "modo apagado" cuesta 7,5 veces el trabajo real.** Ésa es la frase que justifica la propuesta.

### La causa exacta: el check llega después

`smonitor/core/decorator.py:52`:

```python
def wrapper(*args, **kwargs):
    try:
        manager = get_manager()      # ← se ejecuta SIEMPRE
        config = manager.config      # ← SIEMPRE
    except Exception as exc:
        ...
    if not config.enabled:           # ← el check llega DESPUÉS
        return fn(*args, **kwargs)
```

Aunque la telemetría esté apagada, cada función decorada paga `get_manager()`, el acceso a
`config` y un `try/except` **antes** de descubrir que no tenía nada que hacer.

**Y se paga muchas veces por llamada.** Perfilando 300 llamadas a `puw.get_value`: **4.800
invocaciones del wrapper de SMonitor** — 16 por llamada, porque PyUnitWizard decora también sus
helpers internos.

### El arreglo

```python
def wrapper(*args, **kwargs):
    if not _ENABLED:                 # flag de módulo: ~20 ns
        return fn(*args, **kwargs)
    ...
```

Un `if` sobre un bool cacheado, antes de tocar el manager. No cambia la API.

### Cómo verificar que ha funcionado

```bash
python -c "
import timeit
from pyunitwizard import ...    # configurado con pint
q = puw.quantity(1.5,'angstroms')
t = timeit.timeit(lambda: puw.get_value(q, to_unit='nanometers'), number=3000)/3000
print(f'{t*1e6:.1f} µs   (hoy: 262 µs con telemetría, 143 µs sin ella | pint desnudo: 17 µs)')"
```

**Objetivo con la telemetría apagada: acercarse a los 17 µs, no quedarse en 143.**

## Fast path implementado y medido (2026-07-12)

La parte autocontenida de esta propuesta ya está implementada: el decorador consulta un estado
runtime compartido antes de llamar a `get_manager()`, y `Manager.configure(enabled=...)` mantiene
ese estado sincronizado tanto para `smonitor.configure(...)` como para la configuración directa
del manager. Desactivar y volver a activar en ejecución conserva la semántica anterior.

Benchmark reproducible: `python benchmarks/signal_disabled.py`.

| llamada | antes | después |
|---|---:|---:|
| función desnuda | 76 ns | 77 ns |
| `@signal`, SMonitor desactivado | 339 ns | 253 ns |
| overhead del wrapper | 263 ns | 175 ns |

La medición integrada de `puw.get_value(..., to_unit="nanometers")`, con SMonitor desactivado,
dio **137,9 µs** en este host. Por tanto, este cambio elimina el acceso innecesario al manager,
pero no puede cumplir por sí solo el objetivo de 17 µs: siguen existiendo el coste intrínseco de
los wrappers variádicos y el trabajo de DepDigest y PyUnitWizard descrito en sus propuestas. La
optimización de perfiles estáticos y la coordinación entre librerías continúan pendientes; no son
necesarias para conservar este fast path.
