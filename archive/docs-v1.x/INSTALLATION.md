# 📦 Installation & Einrichtung

Komplette Anleitung zur Installation des Smartes PV-Laden Systems v1.6.

## 🔧 Voraussetzungen

### Hardware
- ✅ **RCT Power Storage** Wechselrichter (mit Home Assistant Integration)
- ✅ **Easee Wallbox** (mit Home Assistant Integration)
- ✅ **Renault Zoe** (optional: My Renault Integration für SOC)

### Software
- ✅ **Home Assistant** (empfohlen: Version 2024.x oder neuer)
- ✅ **Node-RED** Add-on für Home Assistant
- ✅ **HACS** (Home Assistant Community Store) — Optional, für Custom Cards

## 📋 Schritt-für-Schritt Installation

### 1️⃣ Node-RED Flow importieren

1. **Node-RED öffnen:**
   - In Home Assistant: Settings → Add-ons → Node-RED → "OPEN WEB UI"
   - Oder direkt: `http://homeassistant.local:1880`

2. **Flow importieren:**
   - Menu (☰) → Import
   - "select a file to import" klicken
   - Datei `smartes_pv_laden_flow_v1.6_2026-07-09.json` auswählen
   - "Import to: new flow" auswählen
   - **Import** klicken

3. **Flow deployen:**
   - Oben rechts: **Deploy** Button klicken
   - Warte auf "Successfully deployed"

4. **Test:**
   - Prüfe Debug-Sidebar (rechts) auf Meldungen
   - "Config geladen" sollte erscheinen

---

### 2️⃣ Home Assistant Helpers erstellen

#### Option A: Via UI (Empfohlen)

1. **Settings → Devices & Services → Helpers**

2. **Input Select erstellen:**
   - "+ Create Helper" → Dropdown
   - Name: `Lade-Modus`
   - Entity ID: `input_select.lade_modus`
   - Options:
     ```
     automatik
     laden
     stoppen
     überschuss
     ```
   - Icon: `mdi:lightning-bolt-circle`
   - **Create**

3. **Input Boolean erstellen** (5x wiederholen):

   | Name | Entity ID | Icon |
   |------|-----------|------|
   | System aktiv | `input_boolean.system_enabled` | `mdi:power` |
   | Batterie-Priorität | `input_boolean.battery_priority` | `mdi:battery-arrow-up` |
   | Entladungsschutz | `input_boolean.prevent_battery_discharge` | `mdi:battery-lock` |
   | Überbrückung aktiv | `input_boolean.bridge_enabled` | `mdi:bridge` |
   | Überbrückungs-Benachrichtigung | `input_boolean.bridge_notification` | `mdi:bell-alert` |

4. **Input Number erstellen** (12x wiederholen):

   | Name | Entity ID | Min | Max | Step | Unit | Initial |
   |------|-----------|-----|-----|------|------|---------|
   | Min. Ladestrom | `input_number.min_charge_current` | 6 | 16 | 1 | A | 7 |
   | Max. Ladestrom | `input_number.max_charge_current` | 6 | 32 | 1 | A | 32 |
   | Phasen | `input_number.phases` | 1 | 3 | 1 | - | 3 |
   | Hysterese-Zeit | `input_number.hysteresis_time` | 0 | 10 | 0.5 | min | 2 |
   | Min. Batterie-SOC | `input_number.min_battery_soc` | 50 | 100 | 5 | % | 95 |
   | Max. Netzbezug | `input_number.max_grid_power_draw` | 0 | 2000 | 100 | W | 500 |
   | Auto-Ziel-SOC | `input_number.car_target_soc` | 50 | 80 | 5 | % | 80 |
   | Auto-SOC Schwelle | `input_number.car_soc_threshold_pure_surplus` | 50 | 100 | 5 | % | 80 |
   | Max. Überbrückungszeit | `input_number.bridge_max_duration` | 1 | 30 | 1 | min | 10 |
   | Überbrückungs-Strom | `input_number.bridge_min_current` | 6 | 16 | 1 | A | 7 |
   | Min. Überschuss Start | `input_number.min_surplus_to_start` | 0 | 10000 | 100 | W | 4800 |
   | Min. Überschuss Weiterladen | `input_number.min_surplus_to_continue` | 0 | 10000 | 100 | W | 3000 |

#### Option B: Via YAML

1. **Packages in configuration.yaml aktivieren** (einmalig):
   - Settings → Add-ons → File Editor (oder SSH)
   - In `/config/configuration.yaml` unter `homeassistant:` ergänzen: `packages: !include_dir_named packages`

2. **`pv_laden/pv_laden.yaml` als Package ablegen:**
   - Nach `/config/packages/pv_laden.yaml` kopieren (NICHT in die `configuration.yaml` einfügen)

3. **Configuration prüfen:**
   - Developer Tools → YAML → "Check Configuration"
   - Warte auf ✅ "Configuration valid"

4. **Home Assistant neu starten:**
   - Settings → System → Restart
   - Warte ~2 Minuten

---

### 3️⃣ Template Sensoren hinzufügen

Die Template-Sensoren aus `pv_laden/pv_laden.yaml` sind bereits enthalten, falls du Option B gewählt hast.

**Falls du Option A gewählt hast:**

1. **configuration.yaml bearbeiten**

2. **Template-Block hinzufügen:**
   ```yaml
   template:
     - sensor:
         - name: "Calculated PV Surplus"
           unique_id: calculated_pv_surplus
           # ... (siehe pv_laden/pv_laden.yaml)
   ```

3. **Configuration prüfen & neu starten**

---

### 4️⃣ Dashboard installieren

#### Variante 1: Lovelace Dashboard (Home Assistant)

1. **Neues Dashboard erstellen:**
   - Settings → Dashboards
   - "+ Add Dashboard"
   - **Title:** PV-Laden
   - **Icon:** `mdi:car-electric`
   - ✅ Show in sidebar
   - **Create**

2. **Raw Configuration Editor öffnen:**
   - Dashboard öffnen
   - Oben rechts: ⋮ (drei Punkte)
   - "Edit Dashboard"
   - Oben rechts: ⋮ → "Raw configuration editor"

3. **YAML einfügen:**
   - Kompletten Inhalt löschen
   - Inhalt von `home-assistant-dashboard.yaml` einfügen
   - **Save**

4. **Dashboard verlassen:**
   - Oben rechts: ✅ "Done"

#### Variante 2: Standalone HTML Dashboard

1. **Web-Server aufsetzen:**
   - Kopiere `dashboard.html` nach `/config/www/`
   - Oder nutze einen separaten Web-Server

2. **Dashboard öffnen:**
   - Browser: `http://homeassistant.local:8123/local/dashboard.html`
   - Oder: Öffne Datei direkt im Browser

3. **Für Echtzeit-Daten:**
   - Erstelle Node-RED HTTP Endpoint (siehe unten)
   - Passe JavaScript in `dashboard.html` an

---

### 5️⃣ Custom Cards installieren (Optional, aber empfohlen)

Für das volle Dashboard-Erlebnis werden folgende HACS-Cards benötigt:

#### Via HACS installieren:

1. **HACS öffnen:**
   - Sidebar → HACS

2. **Frontend-Repositories hinzufügen:**

   **Mushroom Cards** (für moderne KPI-Karten)
   - HACS → Frontend → "+ EXPLORE & DOWNLOAD REPOSITORIES"
   - Suche: "Mushroom"
   - **Mushroom** von Paul Bottein → Download

   **ApexCharts Card** (für Charts im Verlauf-Tab)
   - Suche: "ApexCharts"
   - **ApexCharts Card** → Download

   **Power Flow Card Plus** (für Energiefluss-Visualisierung)
   - Suche: "Power Flow Card Plus"
   - **Power Flow Card Plus** → Download

3. **Home Assistant neu starten**

#### Falls Custom Cards fehlen:

Das Dashboard funktioniert auch ohne Custom Cards, nutzt dann aber:
- Standard `entities` Cards statt Mushroom
- Standard `gauge` Cards statt Power Flow
- Standard `history-graph` statt ApexCharts

---

### 6️⃣ Easee Device ID finden (falls abweichend)

Deine aktuelle Device ID: **`b5b0134f3c9b9d7da1fe77ff580320f2`**

**Falls du eine andere Easee Wallbox hast:**

1. **Developer Tools öffnen:**
   - Developer Tools → Services

2. **Service aufrufen:**
   - Service: `easee.action_command`
   - "GO TO YAML MODE"

3. **YAML anzeigen:**
   ```yaml
   service: easee.action_command
   data:
     action_command: pause
   target:
     device_id: <DEINE_DEVICE_ID>
   ```

4. **Device ID kopieren:**
   - Notiere die `device_id`

5. **Node-RED Flow anpassen:**
   - Öffne alle Easee-Service-Nodes im Flow
   - Ersetze `b5b0134f3c9b9d7da1fe77ff580320f2` mit deiner Device ID
   - **Deploy**

---

### 7️⃣ Automationen aktivieren (Optional)

Die Automationen in `pv_laden/pv_laden.yaml` sind bereits enthalten.

**Wichtige Automationen:**

1. **Sync HA → Node-RED:**
   - Synchronisiert `input_select.lade_modus` mit Node-RED
   - Nutzt MQTT (Node-RED muss MQTT-Broker haben)

2. **Benachrichtigungen:**
   - Überbrückung aktiv
   - Auto 80% erreicht

**Falls MQTT fehlt:**
- Kommentiere die Automation `sync_lade_modus_to_nodered` aus
- Nutze stattdessen die Inject-Buttons im Node-RED Flow

---

## ✅ Test & Verifikation

### Node-RED Flow testen

1. **Debug-Sidebar öffnen** (rechts in Node-RED)

2. **Manueller Trigger:**
   - Klicke auf Inject-Button "Manueller Update (alle 30s)"
   - Prüfe Debug-Ausgaben

3. **Erwartete Meldungen:**
   ```
   ✅ Config geladen: { enabled: true, ... }
   ✅ Alle Sensordaten: { rct: {...}, easee: {...}, zoe: {...} }
   ✅ Status: Idle/Hold / Aktion ausgeführt
   ```

### Home Assistant Dashboard testen

1. **Dashboard öffnen:**
   - Sidebar → PV-Laden

2. **Prüfe KPIs:**
   - Verfügbarer Überschuss: Sollte aktuellen Wert zeigen
   - Lade-Modus: Sollte `input_select.lade_modus` widerspiegeln
   - Ladestrom: Sollte Easee-Sensor zeigen
   - Auto SOC: Sollte Zoe-Sensor zeigen

3. **Teste Steuerung:**
   - Klicke "⚡ Laden erzwingen"
   - Prüfe, ob `input_select.lade_modus` auf "laden" wechselt
   - Prüfe Node-RED Debug: Sollte `override_mode: 'force_charge'` zeigen

### Wallbox-Steuerung testen (VORSICHTIG!)

⚠️ **Nur wenn Auto NICHT angeschlossen oder Laden nicht kritisch ist!**

1. **Auto anschließen** (falls verfügbar)

2. **Lade-Modus auf "Automatik" stellen**

3. **Prüfe Node-RED Debug:**
   - Sollte Sensordaten sammeln
   - Sollte Überschuss berechnen
   - Sollte Aktion zeigen (Start/Stop/Adjust Current/Hold)

4. **Prüfe Wallbox:**
   - Sollte auf Pause/Resume oder Dynamic Limit reagieren
   - Easee App sollte Stromänderungen zeigen

5. **Bei Problemen:**
   - Lade-Modus auf "🛑 Stoppen" setzen
   - Node-RED Flow stoppen (Deploy → Stop)

---

## 🔍 Troubleshooting

### Problem: "Entity nicht verfügbar"

**Ursache:** Sensor-Namen stimmen nicht überein.

**Lösung:**
1. Developer Tools → States
2. Suche deine tatsächlichen Entity-IDs:
   - `sensor.rct*`
   - `sensor.easee*`
   - `sensor.zoe*`
3. Passe Node-RED Flow & Dashboard YAML an

### Problem: "Config geladen" erscheint nicht

**Ursache:** Flow nicht gestartet.

**Lösung:**
1. Node-RED neu laden (F5)
2. Deploy erneut klicken
3. Inject-Button "Konfiguration laden" manuell klicken

### Problem: Dashboard zeigt keine Daten

**Ursache:** Template-Sensoren nicht erstellt.

**Lösung:**
1. Developer Tools → States
2. Suche `sensor.calculated_pv_surplus`
3. Falls nicht vorhanden: configuration.yaml prüfen, neu starten

### Problem: Wallbox reagiert nicht

**Ursache:** Falsche Device ID oder Service-Name.

**Lösung:**
1. Prüfe Device ID (siehe Schritt 6)
2. Teste Service manuell:
   ```yaml
   service: easee.action_command
   data:
     device_id: b5b0134f3c9b9d7da1fe77ff580320f2
     action_command: pause
   ```
3. Falls Fehler: Easee Integration neu installieren

### Problem: Auto lädt trotz 80% weiter

**Ursache:** `force_charge` Modus aktiv.

**Lösung:**
1. Prüfe `input_select.lade_modus` → sollte NICHT "laden" sein
2. Setze auf "automatik"
3. Prüfe Node-RED Global Context: `global.get('smart_charging_config').override_mode` sollte 'auto' sein

---

## 📊 Datenquellen & API

### Node-RED Global Context

```javascript
// Konfiguration abrufen
global.get('smart_charging_config')

// Sensordaten abrufen
global.get('sensor_data')

// Lade-Status abrufen
global.get('charging_state')

// Logs abrufen (letzte 100)
global.get('charging_logs')
```

### HTTP API erstellen (TODO)

Für externes Dashboard oder Apps:

**Node-RED HTTP Endpoint:**
1. Füge `http in` Node hinzu: `GET /api/status`
2. Verbinde mit Function Node:
   ```javascript
   msg.payload = {
       config: global.get('smart_charging_config'),
       status: global.get('charging_status'),
       sensors: global.get('sensor_data')
   };
   return msg;
   ```
3. Verbinde mit `http response` Node

---

## 🚀 Erweiterte Features

### MQTT Integration

Falls du MQTT nutzen möchtest:

1. **MQTT Broker installieren:**
   - Settings → Add-ons → Mosquitto broker

2. **Node-RED MQTT-Nodes hinzufügen:**
   - Subscribe: `nodered/smart_charging/#`
   - Publish: Status-Updates an `homeassistant/sensor/smart_charging/state`

3. **Home Assistant MQTT Discovery:**
   - Automatische Sensor-Erstellung via MQTT

### Telegram-Benachrichtigungen

1. **Telegram Bot erstellen:**
   - Settings → Integrations → Telegram

2. **Automation anpassen:**
   ```yaml
   - service: notify.telegram
     data:
       message: "Ladevorgang gestartet!"
   ```

### Grafana Dashboard

1. **InfluxDB Add-on installieren**
2. **Node-RED → InfluxDB:**
   - Speichere Logs in Datenbank
3. **Grafana Visualisierung:**
   - Historische Charts & Analysen

---

## 📄 Weitere Dokumentationen

- **README.md** — Projekt-Übersicht & Features
- **pv_laden/pv_laden.yaml** — Komplette HA-Config
- **home-assistant-dashboard.yaml** — Dashboard YAML
- **dashboard.html** — Standalone Web-Dashboard

---

**Installation abgeschlossen!** 🎉

Bei Fragen oder Problemen: Prüfe die Debug-Logs in Node-RED und Home Assistant.
