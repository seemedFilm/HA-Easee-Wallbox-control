# 🐛 Bugfix-Analyse: Easee 403 Error & Template Fehler

## Fehler 1: Easee API 403 Error

```
ERROR [pyeasee.easee] SR start exception: ConnectionError: 403. Retry in 300 seconds
```

### Ursache

**403 Forbidden** bedeutet:
1. **Rate Limiting:** Zu viele API-Aufrufe in kurzer Zeit
2. **Ungültige Anfrage:** Service wird mit falschen Parametern aufgerufen
3. **Authentifizierung:** Token abgelaufen oder ungültig

### Wahrscheinlichste Ursache: Zu häufige Service Calls

**Problem:** Der Flow sendet **alle 30 Sekunden** einen Service Call, auch wenn:
- Nichts geändert werden muss
- Auto nicht angeschlossen ist
- Gleicher Strom bereits gesetzt ist

**Aktueller Flow:**
```
Alle 30s → Sensor-Update → Berechnung → Service Call
```

**Was die Easee API nicht mag:**
- ❌ Gleicher Strom mehrfach hintereinander setzen
- ❌ Service Calls ohne Änderung (z.B. 16A → 16A)
- ❌ Zu schnelle Aufrufe (< 60 Sekunden)

### Lösung 1: RBE-Filter VOR Service Call

**Bereits vorhanden für Stop:**
```
Node: "Duplizierte Stop-Messages filtern" (RBE)
```

**Fehlt für Dynamic Limit:**
```
[Lade-Logik] → [RBE: target_current] → [Service Call]
                     ↓
            Nur bei Änderung durchlassen
```

### Lösung 2: Debouncing (Warte-Zeit)

**Hysterese erhöhen:**
```javascript
// Aktuell: 2 Minuten
hysteresis_time: 2

// Besser für Easee API:
hysteresis_time: 3  // 3 Minuten zwischen Änderungen
```

### Lösung 3: Validierung VOR Service Call

```javascript
// Prüfe ob Änderung notwendig
const currentSetPoint = flow.get('last_set_current') || 0;

if (targetCurrent === currentSetPoint) {
    // Keine Änderung nötig
    return null;  // Service Call überspringen
}

// Speichere neuen Wert
flow.set('last_set_current', targetCurrent);
```

---

## Fehler 2: Template Error

```
ERROR [homeassistant.helpers.event] Error while processing template: 
Template<template=({{ states('sensor.calculated_pv_surplus') | float | round(0) }} W)>
```

### Ursache

**Sensor `sensor.calculated_pv_surplus` existiert nicht oder ist `unknown`/`unavailable`**

Mögliche Gründe:
1. Template-Sensor wurde nicht geladen (configuration.yaml fehlt)
2. Abhängige Sensoren fehlen (z.B. `sensor.rct_power_storage_grid_power`)
3. Template hat Syntax-Fehler
4. HA wurde nach Config-Änderung nicht neu gestartet

### Lösung: Fallback-Wert in Template

**Aktuell (fehleranfällig):**
```jinja
{{ states('sensor.calculated_pv_surplus') | float | round(0) }} W
```

**Besser (mit Fallback):**
```jinja
{{ states('sensor.calculated_pv_surplus') | float(0) | round(0) }} W
```

**Oder defensive Prüfung:**
```jinja
{% if states('sensor.calculated_pv_surplus') not in ['unknown', 'unavailable', 'none'] %}
  {{ states('sensor.calculated_pv_surplus') | float | round(0) }} W
{% else %}
  -- W
{% endif %}
```

---

## 🔧 Implementierung der Fixes

### Fix 1: RBE-Filter für Dynamic Limit

**Neuer RBE-Node einfügen:**

```json
{
  "type": "rbe",
  "name": "Filter identische Stromwerte",
  "func": "rbe",
  "property": "payload.control.target_current",
  "x": 650,
  "y": 620
}
```

**Flow-Änderung:**
```
[Lade-Logik] 
    → Output 2 (Start) → [Resume] → [RBE] → [Dynamic Limit]
    → Output 3 (Adjust) → [RBE] → [Dynamic Limit]
```

### Fix 2: Verbesserte Stromberechnung

**In "Lade-Logik & Modus-Auswahl" Function:**

```javascript
// ALT:
return Math.floor(current);

// NEU:
return Math.round(current);  // Mathematisch runden
```

**Zusätzlich: Validierung**

```javascript
// Nach Berechnung von targetCurrent:
const lastCurrent = flow.get('last_target_current') || 0;

// Prüfe ob Änderung groß genug (mindestens 1A Differenz)
if (Math.abs(targetCurrent - lastCurrent) < 1) {
    node.warn('Stromänderung zu gering: ' + lastCurrent + 'A → ' + targetCurrent + 'A');
    targetCurrent = lastCurrent;  // Behalte alten Wert
}

// Speichere für nächsten Durchlauf
flow.set('last_target_current', targetCurrent);
```

### Fix 3: Debug-Logging

**In "Lade-Logik" Function hinzufügen:**

```javascript
// VOR dem Service Call:
node.warn('═══ Stromberechnung ═══');
node.warn('Überschuss: ' + surplus + 'W');
node.warn('Berechnet: ' + calculatedCurrent + 'A');
node.warn('Nach Limits: ' + targetCurrent + 'A');
node.warn('Modus: ' + newMode);
node.warn('Action: ' + action);
```

### Fix 4: Template-Sensor Fix

**In `pv_laden/template.yaml`:**

```yaml
# ALT:
state: >
  {{ (states('sensor.easee_home_power') | float(0) / 1000) | round(2) }}

# NEU (defensiv):
state: >
  {% set power = states('sensor.easee_home_power') %}
  {% if power not in ['unknown', 'unavailable', 'none'] %}
    {{ (power | float / 1000) | round(2) }}
  {% else %}
    0.0
  {% endif %}
```

---

## 📋 Priorität der Fixes

### Kritisch (sofort):
1. ✅ **RBE-Filter** für Dynamic Limit → Verhindert 403 Error
2. ✅ **Template Fallbacks** → Behebt Template-Fehler

### Wichtig (bald):
3. ✅ **Math.round()** statt floor() → Bessere Stromberechnung
4. ✅ **Hysterese erhöhen** → Weniger API-Calls

### Optional (Nice-to-have):
5. ⚪ Debug-Logging → Besseres Troubleshooting
6. ⚪ Flow-Context Validierung → Verhindert redundante Calls

---

## 🧪 Test-Plan

### Test 1: RBE-Filter
1. Flow mit RBE deployen
2. Warte 5 Minuten ohne Änderung
3. Prüfe Home Assistant Logs
4. **Erwartung:** Keine wiederholten Service Calls

### Test 2: Template-Sensor
1. Developer Tools → Template
2. Test-Template:
   ```jinja
   {{ states('sensor.calculated_pv_surplus') | float(0) }}
   ```
3. **Erwartung:** Zahl oder 0, kein Fehler

### Test 3: Stromberechnung
1. Setze Überschuss manuell: 5500W
2. Erwartete Berechnung: 5500 / 1195 = 4.6A → **5A** (gerundet)
3. Mit Min=7A: Target = **7A**
4. Prüfe Debug-Log in Node-RED

---

## 📊 Vergleich: Vorher/Nachher

| Aspekt | Vorher | Nachher |
|--------|--------|---------|
| **API Calls** | Alle 30s (auch ohne Änderung) | Nur bei tatsächlicher Änderung |
| **Stromberechnung** | `floor()` → oft zu niedrig | `round()` → präziser |
| **403 Error** | ❌ Häufig | ✅ Verhindert |
| **Template Error** | ❌ Bei fehlenden Sensoren | ✅ Fallback auf 0 |
| **Hysterese** | 2 Min + Δ≤2A | 3 Min + Δ<1A |

---

## 🚀 Deployment

### Schritt 1: Template-Fixes
```bash
# In Home Assistant:
1. pv_laden/template.yaml bearbeiten
2. Developer Tools → YAML → Template Reloading
3. Prüfe: Developer Tools → States
```

### Schritt 2: Node-RED Flow-Update
```bash
# In Node-RED:
1. Importiere verbesserten Flow (siehe nächste Datei)
2. Deploy
3. Prüfe Debug-Sidebar
```

### Schritt 3: Monitoring (24h)
```bash
# Überwache in Home Assistant Logs:
grep "pyeasee" home-assistant.log
grep "template" home-assistant.log

# Erwartung: Keine Fehler mehr
```

---

**Erstellt:** 2026-07-12  
**Status:** ✅ Fixes identifiziert, bereit für Implementierung
