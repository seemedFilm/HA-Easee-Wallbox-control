# 🔧 Bugfix-Patches für Flow v1.6 → v1.7

## Änderung 1: Math.round() statt Math.floor()

**In Node: "Lade-Logik & Modus-Auswahl"**

**Suche nach:**
```javascript
function calculateCurrent(power_watts) {
    const voltage = 230;
    const phases = config.phases;
    let current;
    
    if (phases === 3) {
        current = power_watts / (voltage * Math.sqrt(3) * phases);
    } else {
        current = power_watts / voltage;
    }
    
    return Math.floor(current);  // ← DIESE ZEILE
}
```

**Ersetze mit:**
```javascript
function calculateCurrent(power_watts) {
    const voltage = 230;
    const phases = config.phases;
    let current;
    
    if (phases === 3) {
        current = power_watts / (voltage * Math.sqrt(3) * phases);
    } else {
        current = power_watts / voltage;
    }
    
    return Math.round(current);  // ✅ GEÄNDERT: round statt floor
}
```

---

## Änderung 2: API-Call Validierung hinzufügen

**In Node: "Lade-Logik & Modus-Auswahl"**

**Nach der Hysterese-Prüfung, VOR "Update Charging State", füge ein:**

```javascript
// === NEU: Validierung für API-Call ===
// Verhindere redundante Service Calls (403 Error Prevention)
const lastSetCurrent = flow.get('last_api_current') || 0;
const lastApiCall = flow.get('last_api_timestamp') || 0;
const timeSinceLastCall = (now - lastApiCall) / 1000;  // Sekunden

// Regel 1: Kein API-Call wenn Strom gleich ist
if (action === 'charge' && targetCurrent === lastSetCurrent) {
    node.warn('Überspringe API-Call: Strom unverändert (' + targetCurrent + 'A)');
    action = 'hold';  // Ändere Action auf 'hold' (kein Service Call)
}

// Regel 2: Mindestens 60 Sekunden zwischen API-Calls
if (action === 'charge' && timeSinceLastCall < 60 && targetCurrent !== lastSetCurrent) {
    node.warn('API-Call zu früh (' + Math.round(timeSinceLastCall) + 's). Warte...');
    action = 'hold';
}

// Regel 3: Nur signifikante Änderungen (≥1A Differenz)
if (action === 'charge' && Math.abs(targetCurrent - lastSetCurrent) < 1) {
    node.warn('Stromänderung zu gering: ' + lastSetCurrent + 'A → ' + targetCurrent + 'A');
    targetCurrent = lastSetCurrent;
    action = 'hold';
}

// Speichere für API-Call Tracking
if (action === 'charge' || action === 'start') {
    flow.set('last_api_current', targetCurrent);
    flow.set('last_api_timestamp', now);
}
// === ENDE NEU ===
```

**Vollständiger Kontext (wo einfügen):**
```javascript
// ... Hysterese-Prüfung ...

// === NEU: HIER EINFÜGEN ===

// Update Charging State
if (targetCurrent !== chargingState.last_current) {
    // ...
}
```

---

## Änderung 3: Debug-Logging hinzufügen

**In Node: "Lade-Logik & Modus-Auswahl"**

**VOR "// Route zu entsprechendem Output", füge ein:**

```javascript
// === NEU: Debug-Logging ===
if (action !== 'hold') {
    node.warn('═══════════════════════════════════');
    node.warn('🔋 Überschuss: ' + surplus + 'W');
    node.warn('⚡ Berechnet: ' + calculateCurrent(surplus) + 'A (roh)');
    node.warn('🎯 Target: ' + targetCurrent + 'A (nach Limits)');
    node.warn('📊 Modus: ' + newMode);
    node.warn('▶️  Action: ' + action);
    node.warn('⏱️  Hysterese: ' + (chargingState.last_current_change ? 
        Math.round((now - chargingState.last_current_change) / 1000 / 60) + ' Min' : 
        'erstmalig'));
    node.warn('═══════════════════════════════════');
}
// === ENDE NEU ===

// Route zu entsprechendem Output
if (action === 'stop') {
    // ...
}
```

---

## Änderung 4: RBE-Filter für Dynamic Limit

**Manuelle Änderung in Node-RED UI:**

1. **Neuen RBE-Node erstellen:**
   - Palette → "rbe" ziehen
   - Name: `Filter identische Stromwerte`
   - Mode: `rbe` (block unless value changes)
   - Property: `payload.control.target_current`

2. **Verbindungen ändern:**

   **ALT:**
   ```
   [Lade-Logik Output 2: Start] → [Wallbox fortsetzen]
   [Lade-Logik Output 3: Adjust] → [Dynamic Limit]
   [Wallbox fortsetzen] → [Dynamic Limit]
   ```

   **NEU:**
   ```
   [Lade-Logik Output 2: Start] → [Wallbox fortsetzen]
   [Lade-Logik Output 3: Adjust] → [RBE Filter]
   [Wallbox fortsetzen] → [RBE Filter]
   [RBE Filter] → [Dynamic Limit]
   ```

3. **Positionierung:**
   - X: 650
   - Y: 620

---

## Änderung 5: Hysterese-Zeit erhöhen

**In Node: "Standard-Konfiguration"**

**Suche nach:**
```javascript
hysteresis_time: config.hysteresis_time || 2, // Minuten
```

**Ersetze mit:**
```javascript
hysteresis_time: config.hysteresis_time || 3, // Minuten (erhöht für Easee API)
```

---

## Änderung 6: Hysterese-Schwelle anpassen

**In Node: "Lade-Logik & Modus-Auswahl"**

**Suche nach:**
```javascript
if (minutesSinceChange < config.hysteresis_time && 
    Math.abs(targetCurrent - chargingState.last_current) <= 2) {
```

**Ersetze mit:**
```javascript
if (minutesSinceChange < config.hysteresis_time && 
    Math.abs(targetCurrent - chargingState.last_current) <= 1) {  // ✅ GEÄNDERT: 1A statt 2A
```

---

## Änderung 7: Tab-Label aktualisieren

**Im ersten Node (Tab):**

**Suche nach:**
```json
"label": "Smartes PV-Laden 1.6"
```

**Ersetze mit:**
```json
"label": "Smartes PV-Laden 1.7 (Bugfix)"
```

---

## Änderung 8: Info-Text aktualisieren

**Im ersten Node (Tab):**

**Suche nach:**
```
"info": "Intelligentes PV-Überschussladen für Easee Wallbox mit RCT Wechselrichter version 1.6"
```

**Ersetze mit:**
```
"info": "Intelligentes PV-Überschussladen für Easee Wallbox mit RCT Wechselrichter version 1.7\n\nBugfixes:\n- Math.round() statt floor() für präzisere Stromberechnung\n- API-Call Validierung gegen 403 Errors\n- RBE-Filter für Dynamic Limit\n- Hysterese auf 3 Min erhöht\n- Debug-Logging verbessert"
```

---

## 📋 Checkliste: Änderungen anwenden

### In Node-RED:

- [ ] Ändere **"Lade-Logik & Modus-Auswahl"** Function:
  - [ ] Math.round() statt Math.floor()
  - [ ] API-Call Validierung hinzufügen
  - [ ] Debug-Logging hinzufügen
  - [ ] Hysterese-Schwelle auf 1A ändern

- [ ] Ändere **"Standard-Konfiguration"** Function:
  - [ ] Hysterese-Zeit auf 3 Min

- [ ] Füge **RBE-Node** hinzu:
  - [ ] Node erstellen
  - [ ] Verbindungen anpassen

- [ ] Ändere **Tab-Info**:
  - [ ] Label → v1.7
  - [ ] Info-Text aktualisieren

- [ ] **Deploy** klicken

### Test:

- [ ] Debug-Sidebar öffnen
- [ ] Inject-Button "Manueller Update" klicken
- [ ] Prüfe Debug-Ausgaben (sollte neue Logs zeigen)
- [ ] Warte 5 Minuten ohne Änderung
- [ ] Prüfe, dass KEINE wiederholten Service Calls kommen

### In Home Assistant:

- [ ] Prüfe Logs nach 1 Stunde:
  ```bash
  grep "pyeasee.*403" home-assistant.log
  # Sollte LEER sein (keine 403 Errors mehr)
  ```

---

## 🚀 Schnelle Anwendung (Copy & Paste)

### Für "Lade-Logik & Modus-Auswahl" Function:

1. Doppelklick auf den Node
2. Im Code-Editor:
   - `Strg+H` (Suchen & Ersetzen)
   - Suche: `return Math.floor(current);`
   - Ersetze: `return Math.round(current);`
   - **Replace**

3. Scrolle zur Hysterese-Prüfung
4. Füge NACH der Hysterese, VOR "Update Charging State" ein:
   ```javascript
   // === API-Call Validierung (siehe oben) ===
   ```

5. Scrolle zum Ende
6. Füge VOR "// Route zu entsprechendem Output" ein:
   ```javascript
   // === Debug-Logging (siehe oben) ===
   ```

7. **Done** klicken

---

## 📊 Erwartete Verbesserungen

| Metrik | Vorher | Nachher |
|--------|--------|---------|
| **API Calls/Stunde** | ~120 (alle 30s) | ~5-10 (nur bei Änderung) |
| **403 Errors/Tag** | 10-50 | 0 |
| **Stromberechnung Präzision** | ±0.5A (floor) | ±0A (round) |
| **Hysterese-Flapping** | Häufig | Selten |
| **Debug-Info** | Minimal | Detailliert |

---

## ⚠️ Wichtig: Backup vor Änderung

**Erstelle Backup:**
1. Node-RED → Menu → Export → All flows
2. Speichere als `smartes_pv_laden_flow_v1.6_backup_2026-07-12.json`

**Falls Probleme auftreten:**
1. Menu → Import
2. Wähle Backup-Datei
3. Deploy

---

**Version:** 1.6 → 1.7 Bugfix  
**Erstellt:** 2026-07-12  
**Priorität:** 🔴 Kritisch (403 Error beheben)
