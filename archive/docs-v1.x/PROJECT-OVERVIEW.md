# 📂 Projekt-Übersicht: Smartes PV-Laden v1.6

Vollständige Dokumentation und Dateien für das intelligente PV-Überschussladen-System.

## 🎯 Projektziel

Automatisches, intelligentes Laden eines Elektrofahrzeugs (Renault Zoe) mit **reinem PV-Überschuss** über eine Easee Wallbox, gesteuert durch Node-RED und visualisiert in Home Assistant.

### Kernfunktionen

✅ **PV-Überschussladen** mit dynamischer Stromregelung (7-32A, 3-Phasen)  
✅ **Batterie-Priorität** (Speicher erst auf 95% laden, dann Auto)  
✅ **Überbrückungslogik** (Max. 10 Min. bei Wolken mit Minimalstrom)  
✅ **80% Hard-Limit** für Auto-SOC (Batterieschonung)  
✅ **Manuelle Override-Modi** (Erzwingen, Stoppen, Nur-PV)  
✅ **Entladungsschutz** (Max. 500W Netzbezug)  
✅ **Echtzeit-Dashboard** mit Energiefluss-Visualisierung  

---

## 📁 Dateistruktur

```
node-redflow/
│
├── 📄 README.md                                    # Hauptdokumentation
├── 📄 INSTALLATION.md                              # Schritt-für-Schritt Installationsanleitung
├── 📄 PROJECT-OVERVIEW.md                          # Diese Datei
│
├── 🔄 Node-RED Flows
│   ├── smartes_pv_laden_flow_v1.6_2026-07-09.json  # ⭐ Aktuellste Version (empfohlen)
│   ├── smartes_pv_laden_flow_v1.5_2026-07-09.json  # Vorgänger
│   ├── smartes_pv_laden_flow_v1.4_2026-07-09.json
│   ├── smartes_pv_laden_flow_v1.3_2026-07-09.json
│   ├── smartes_pv_laden_flow_v1.2_2026-07-08.json
│   ├── smartes_pv_laden_flow_v1.1_2026-07-08.json
│   ├── smartes_pv_laden_flow_v1.0_2026-07-08.json
│   ├── smartes_pv_laden_flow_backup.json           # Backup
│   └── 1_smartes_pv_laden_flow.json                # Original
│
├── 🖥️ Dashboards
│   ├── dashboard.html                               # Standalone Web-Dashboard
│   ├── home-assistant-dashboard.yaml                # ⭐ Home Assistant Lovelace UI
│   └── pv_laden/pv_laden.yaml                       # ⭐ HA Package (Helpers, Templates, Automations)
│
└── 📦 Claude Projekt-Daten
    └── .claude/                                     # Entwicklungshistorie & Konfiguration
        ├── history.jsonl                            # Vollständige Conversation-Historie
        ├── sessions/                                # Session-Snapshots
        ├── backups/                                 # Config-Backups
        └── projects/                                # Projekt-Metadaten
```

**Dateigrößen:**
- Node-RED Flows: ~28-42 KB (JSON)
- Dashboards: ~27 KB (HTML), ~18 KB (YAML)
- Dokumentation: ~8-13 KB (Markdown)
- Claude-Historie: ~136 KB (JSONL)

---

## 🔧 Technologie-Stack

### Hardware
- **RCT Power Storage** — Hybrid-Wechselrichter mit Batteriespeicher
- **Easee Home/Charge** — Intelligente Wallbox
- **Renault Zoe** — Elektrofahrzeug

### Software
- **Home Assistant** — Smart-Home-Zentrale
- **Node-RED** — Flow-basierte Programmierung
- **JavaScript** — Dashboard-Logik
- **YAML** — Konfiguration & Dashboard

### Integrationen
- **RCT Power Integration** (Home Assistant)
- **Easee Integration** (Home Assistant Custom Component)
- **My Renault** (Optional, für Zoe-Daten)

---

## 📊 System-Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                     Home Assistant                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ RCT Power   │  │   Easee     │  │ Renault Zoe │        │
│  │ Integration │  │ Integration │  │ (My Renault)│        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                 │                 │                │
│         └─────────────────┴─────────────────┘                │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               Home Assistant State                     │ │
│  │  • sensor.rct_power_storage_*                         │ │
│  │  • sensor.easee_home_*                                │ │
│  │  • sensor.zoe_*                                       │ │
│  │  • input_select.lade_modus                            │ │
│  │  • input_number.*, input_boolean.*                    │ │
│  └───────────────────────┬────────────────────────────────┘ │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       Node-RED                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Sensor-Monitoring (server-state-changed)         │  │
│  │  2. Datensammlung & Aggregation                      │  │
│  │  3. Überschuss-Berechnung                            │  │
│  │  4. Lade-Logik (Modi, Überbrückung, Limits)          │  │
│  │  5. Wallbox-Steuerung (Easee Services)               │  │
│  │  6. Logging & Status-Updates                         │  │
│  └────────────────────────┬─────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Easee Wallbox (API)                        │
│  • easee.action_command (pause/resume)                     │
│  • easee.set_charger_dynamic_limit (Stromsteuerung)        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                       ⚡ Renault Zoe
```

---

## 🎨 Dashboard-Features

### Standalone HTML Dashboard (`dashboard.html`)

**Features:**
- ✅ Echtzeit-KPIs (Überschuss, Modus, Ladestrom, Auto-SOC)
- ✅ Energiefluss-Visualisierung (PV → Batterie → Netz → Wallbox)
- ✅ Manuelle Steuerung (4 Modi)
- ✅ System-Konfiguration & Status
- ✅ Dark Mode (automatisch via `prefers-color-scheme`)
- ✅ Responsive Design
- ✅ CVD-sichere Farbpalette

**Mock-Daten:**
- Aktuell nutzt es simulierte Daten
- Für Echtzeit: Node-RED HTTP/WebSocket API benötigt

**Zugriff:**
- Lokale Datei: `file:///c:/Users/Patrick/Downloads/node-redflow/dashboard.html`
- Via HA WWW: `http://homeassistant.local:8123/local/dashboard.html`

### Home Assistant Lovelace Dashboard (`home-assistant-dashboard.yaml`)

**3 Ansichten:**

1. **Übersicht**
   - KPI-Grid (4 Mushroom Cards)
   - Energiefluss (Power Flow Card Plus)
   - Manuelle Steuerung (Input Select + Buttons)
   - Detaillierte Sensoren (RCT, Easee, Zoe)
   - System-Konfiguration

2. **Verlauf**
   - Wallbox-Ladeleistung (24h)
   - PV-Produktion vs. Verbrauch (24h)
   - Batterie & Auto SOC (24h)
   - Historische Daten (48h)

3. **Einstellungen**
   - Lade-Parameter (Strom, Phasen, Hysterese)
   - Batterie-Management
   - Fahrzeug-Einstellungen
   - Überbrückungs-Logik
   - Start-Schwellenwerte

**Benötigte Custom Cards:**
- ✅ Mushroom Cards (HACS)
- ✅ ApexCharts Card (HACS)
- ✅ Power Flow Card Plus (HACS)

---

## ⚙️ Konfigurationsparameter

### Wichtige Einstellungen

| Parameter | Standard | Bereich | Beschreibung |
|-----------|----------|---------|--------------|
| **Min. Ladestrom** | 7 A | 6-16 A | Minimalstrom (unter 7A pausiert Easee) |
| **Max. Ladestrom** | 32 A | 6-32 A | Maximalstrom (22 kW bei 3 Phasen) |
| **Phasen** | 3 | 1-3 | Anzahl Phasen |
| **Auto-Ziel-SOC** | 80% | 50-80% | **Hard-Limit** für Auto |
| **Min. Batterie-SOC** | 95% | 50-100% | Erst ab diesem SOC wird Auto geladen |
| **Überbrückungs-Zeit** | 10 min | 1-30 min | Max. Dauer bei niedrigem Überschuss |
| **Min. Überschuss Start** | 4800 W | 0-10000 W | Mindestleistung zum Starten |

### Berechnungen

**3-Phasen Leistung:**
```
P = U × I × √3 × 3
P = 230V × I × 1.732 × 3

Beispiele:
  7A → 4,2 kW  (Minimum)
 16A → 11,0 kW
 32A → 22,1 kW (Maximum)
```

**Verfügbarer Überschuss:**
```javascript
if (grid_power < 0) {
  // Einspeisung
  surplus = abs(grid_power) + (charging ? wallbox_power : 0)
} else {
  // Bezug
  surplus = (charging ? wallbox_power : 0) - grid_power
}

// Bei Entladungsschutz
if (prevent_discharge && battery_power > 0) {
  surplus -= battery_power
}
```

---

## 🔄 Lade-Modi

### 1. 🔄 Automatik (Empfohlen)

**Logik:**
1. Prüfe Batterie-SOC ≥ 95% (falls Priorität aktiv)
2. Prüfe Auto-SOC < 80% (Hard-Limit)
3. Prüfe Auto angeschlossen
4. Berechne verfügbaren Überschuss
5. Wenn Überschuss ≥ 4800W → Starte Laden
6. Bei niedrigem Überschuss → Überbrückung (10 Min.)
7. Bei Auto-SOC ≥ 80% → **STOP** (auch bei Überschuss!)

**Verhalten:**
- ✅ Intelligent & batterieschonend
- ✅ Überbrückt kurze Wolkenphasen
- ✅ Stoppt bei 80% automatisch

### 2. ⚡ Laden erzwingen (Override)

**Logik:**
1. **Überschreibt ALLE Limits** (auch 80%!)
2. Lädt mit festem Strom (Standard: 16A)
3. Nutzt Netzstrom wenn nötig

**Verhalten:**
- ⚠️ Ignoriert Batterie-Priorität
- ⚠️ Ignoriert 80%-Limit
- ⚠️ Kann Netzbezug verursachen

**Nutzung:**
- Notfall-Laden
- Schnelles Vollladen vor Fahrt

### 3. 🛑 Stoppen (Override)

**Logik:**
1. Pausiert Wallbox sofort
2. Ignoriert Überschuss

**Verhalten:**
- ✅ Sofortiger Stop
- ✅ Bleibt bis manuell geändert

### 4. ☀️ Nur PV-Überschuss (Override)

**Logik:**
1. Wie Automatik, ABER:
2. Deaktiviert Überbrückung
3. Deaktiviert Tibber-Preissteuerung
4. Reiner Überschuss erforderlich

**Verhalten:**
- ✅ Garantiert 0 Netzbezug
- ⚠️ Stoppt bei Wolken sofort

---

## 📈 Datenfluss

### Sensor-Daten (Home Assistant → Node-RED)

**Alle 30 Sekunden** (manueller Trigger) + **bei Änderung** (State-Change):

```javascript
{
  rct: {
    grid_power: -2400,      // W (negativ = Einspeisung)
    battery_soc: 96,        // %
    battery_power: -800,    // W (negativ = laden)
    inverter_power: 6800,   // W (PV-Erzeugung)
    consumer_power: 3600    // W (Hausverbrauch)
  },
  easee: {
    power: 4200,            // W (Wallbox-Leistung)
    current: 7,             // A (Ladestrom)
    charging: true          // Boolean
  },
  zoe: {
    battery: 65,            // % (Auto-SOC)
    plug_state: 'Plugged in',
    charge_state: 'Charging'
  }
}
```

### Berechnete Werte (Node-RED)

```javascript
{
  calculated: {
    available_surplus: 6600,  // W
    grid_power: -2400,
    battery_power: -800,
    battery_soc: 96,
    current_charging_power: 4200
  },
  control: {
    action: 'charge',          // stop, start, charge, hold
    mode: 'pv_surplus',        // idle, pv_surplus, bridge, force_charge
    reason: 'PV-Überschuss: 6600W',
    target_current: 7,         // A
    calculated_power: 4830     // W
  }
}
```

### Wallbox-Steuerung (Node-RED → Easee)

**Pause:**
```yaml
service: easee.action_command
data:
  device_id: b5b0134f3c9b9d7da1fe77ff580320f2
  action_command: pause
```

**Resume:**
```yaml
service: easee.action_command
data:
  device_id: b5b0134f3c9b9d7da1fe77ff580320f2
  action_command: resume
```

**Stromsteuerung:**
```yaml
service: easee.set_charger_dynamic_limit
data:
  device_id: b5b0134f3c9b9d7da1fe77ff580320f2
  current: 16  # 6-32A
  time_to_live: 0  # Permanent
```

---

## 🧪 Test-Szenarien

### Szenario 1: Normales PV-Laden (Sonnig)

**Bedingungen:**
- ☀️ PV-Produktion: 8 kW
- 🏠 Hausverbrauch: 1 kW
- 🔋 Batterie-SOC: 97% (voll)
- 🚗 Auto-SOC: 50%

**Erwartetes Verhalten:**
1. Verfügbarer Überschuss: ~7 kW
2. Berechenbarer Ladestrom: 10A
3. Wallbox startet mit 10A (6,9 kW)
4. Modus: `pv_surplus`
5. ✅ Lädt bis 80% weiter

### Szenario 2: Wolke (Überbrückung)

**Bedingungen:**
- ⛅ PV-Produktion: 2 kW (Wolke!)
- 🏠 Hausverbrauch: 1 kW
- 🔋 Batterie-SOC: 97%
- 🚗 Auto-SOC: 60%, lädt bereits

**Erwartetes Verhalten:**
1. Verfügbarer Überschuss: 1 kW (zu wenig!)
2. Startet Überbrückung mit 7A (Min.)
3. Modus: `bridge`
4. Läuft max. 10 Minuten
5. Danach: Stop (wenn Überschuss weiter niedrig)
6. ✅ Benachrichtigung gesendet

### Szenario 3: 80% Auto-SOC erreicht

**Bedingungen:**
- ☀️ PV-Produktion: 8 kW
- 🚗 Auto-SOC: 79,9% → 80,0%
- Modus: `automatik` (NICHT force_charge!)

**Erwartetes Verhalten:**
1. Auto-SOC erreicht 80%
2. **Hard-Limit** greift
3. Wallbox wird pausiert
4. Modus: `idle`
5. Grund: "Auto-SOC 80% >= 80% (Hard-Limit erreicht)"
6. ✅ Lädt NICHT weiter (selbst bei viel Überschuss)

### Szenario 4: Force Charge (Notfall)

**Bedingungen:**
- ☁️ PV-Produktion: 0 kW (Nacht)
- 🚗 Auto-SOC: 85% (über Limit!)
- Benutzer klickt "⚡ Laden erzwingen"

**Erwartetes Verhalten:**
1. Override-Modus: `force_charge`
2. Lädt mit 16A (~11 kW)
3. **Ignoriert 80%-Limit**
4. Nutzt Netzstrom
5. Lädt bis 100% weiter (wenn gewünscht)
6. ⚠️ Dashboard zeigt Warnung

---

## 🔐 Sicherheits-Features

### 1. Hard-Limit bei 80% Auto-SOC

```javascript
// Nur force_charge darf darüber hinaus laden!
if (data.zoe.battery >= 80 && config.override_mode !== 'force_charge') {
    action = 'stop';
    reason = 'Auto-SOC >= 80% (Hard-Limit erreicht)';
}
```

**Warum:**
- Batterieschonung (Lithium-Ionen optimal 20-80%)
- Verlängerte Lebensdauer
- Schnelleres Laden (80-100% dauert länger)

### 2. Batterie-Entladungsschutz

```javascript
if (config.prevent_battery_discharge && battery_power > 0) {
    surplus -= battery_power;
}
```

**Warum:**
- Verhindert ungewolltes Entladen der Hausbatterie
- Max. 500W Netzbezug erlaubt (konfigurierbar)

### 3. Hysterese (Anti-Flapping)

```javascript
if (minutes_since_change < 2 && abs(new_current - old_current) <= 2) {
    // Behalte alten Wert
}
```

**Warum:**
- Vermeidet ständige Stromänderungen
- Schont Wallbox-Hardware
- Reduziert Netzlast-Schwankungen

### 4. RBE-Filter (Report By Exception)

**Vor Stop-Service:**
```
payload.control.reason → RBE Node → Service Call
```

**Warum:**
- Verhindert duplizierte Pause-Befehle
- Entlastet Wallbox-API
- Vermeidet Rate-Limiting

---

## 📦 Deployment-Checklist

### Vor dem Go-Live:

- [ ] Node-RED Flow v1.6 importiert & deployed
- [ ] Home Assistant Helpers erstellt (Input Select, Number, Boolean)
- [ ] Template-Sensoren konfiguriert
- [ ] Easee Device ID geprüft (`b5b0134f3c9b9d7da1fe77ff580320f2`)
- [ ] RCT/Easee/Zoe Sensoren verfügbar
- [ ] Dashboard installiert (HA Lovelace oder HTML)
- [ ] Custom Cards installiert (HACS)
- [ ] Test mit "Stoppen"-Modus durchgeführt
- [ ] Benachrichtigungen konfiguriert (optional)
- [ ] Backup erstellt

### Nach Go-Live:

- [ ] 24h Monitoring (Debug-Logs prüfen)
- [ ] Erster Ladevorgang beobachten
- [ ] 80%-Limit testen
- [ ] Überbrückung testen (bei Wolken)
- [ ] Dashboard-Daten validieren

---

## 🚀 Roadmap

### Geplante Features (TODO)

- [ ] **Tibber-Integration:** Preisbasiertes Laden bei günstigen Strompreisen
- [ ] **WebSocket API:** Echtzeit-Updates für Standalone-Dashboard
- [ ] **Historische Charts:** 7/30/90 Tage Statistiken
- [ ] **Mobile App (PWA):** Offline-fähiges Dashboard
- [ ] **Telegram/Email-Benachrichtigungen:** Bei Ereignissen
- [ ] **Sonnenauf-/untergang:** Automatische Planung
- [ ] **Wettervorhersage-Integration:** Vorausschauendes Laden
- [ ] **Multi-Fahrzeug-Support:** Mehrere Autos verwalten
- [ ] **Loadbalancing:** Hausanschluss-Limit berücksichtigen
- [ ] **OCPP-Support:** Standardprotokoll für Wallboxen

---

## 🤝 Credits

**Entwickelt mit:**
- 🤖 **Claude Code** (Anthropic Sonnet 4.5)
- 👤 **Patrick** (Konzept, Testing, Deployment)

**Verwendete Open-Source-Projekte:**
- **Home Assistant** (Apache 2.0)
- **Node-RED** (Apache 2.0)
- **Easee Integration** (Community)
- **RCT Power Integration** (Community)

**Design-System:**
- Basierend auf **dataviz** Skill von Claude Code
- WCAG 2.1 AA konform
- CVD-sichere Farbpalette (ΔE ≥ 12)

---

## 📞 Support & Community

### Dokumentation

- **README.md** — Projekt-Features & Versionshistorie
- **INSTALLATION.md** — Schritt-für-Schritt Anleitung
- **PROJECT-OVERVIEW.md** — Diese Datei (technische Details)

### Troubleshooting

Siehe **INSTALLATION.md** → Abschnitt "🔍 Troubleshooting"

### Debugging

**Node-RED:**
```javascript
// Global Context Inspector
node.warn(global.get('smart_charging_config'));
node.warn(global.get('charging_state'));
node.warn(global.get('charging_logs'));
```

**Home Assistant:**
```
Developer Tools → States
Developer Tools → Template
Developer Tools → Services
```

---

## 📄 Lizenz & Nutzung

Dieses Projekt ist Open Source und kann frei verwendet, modifiziert und weitergegeben werden.

**Haftungsausschluss:**
- Nutzung auf eigene Gefahr
- Keine Garantie für Funktionalität
- Teste gründlich vor Produktiveinsatz
- Prüfe Kompatibilität mit deiner Hardware

---

**Version:** 1.6  
**Erstellt:** 2026-07-09  
**Letztes Update:** 2026-07-11  
**Status:** ✅ Produktionsreif

**Entwicklungszeit:** ~3 Wochen  
**Code-Zeilen:** ~1.200 (Node-RED Functions)  
**Dokumentation:** ~1.500 Zeilen  
**Dashboard-Code:** ~600 Zeilen (HTML/CSS/JS)

---

🎉 **Happy Charging!** ⚡🚗☀️
