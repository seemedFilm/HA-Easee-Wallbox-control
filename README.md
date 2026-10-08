# Smartes PV-Laden

Intelligentes PV-Überschussladen für Easee Wallbox mit RCT Power Wechselrichter und Renault Zoe.

Das System regelt den Ladestrom der Wallbox automatisch anhand des verfügbaren PV-Überschusses, schützt die Hausbatterie vor ungewollter Entladung und nutzt optional den günstigsten Netzstrompreis des Tages zum Laden. Zusätzlich werden die Kosten für den aus dem Netz geladenen Anteil pro Monat ausgewertet.

**Aktueller Stand:** Node-RED Flow **v2.6** · HA Package **v2.7** · Dashboard **v1.8**

[![Lizenz: CC BY-NC-SA 4.0](https://img.shields.io/badge/Lizenz-CC%20BY--NC--SA%204.0-lightgrey.svg)](#lizenz) — nicht kommerziell; kommerzielle Nutzung nur nach Rücksprache.

## Inhalt dieses Repos

| Datei | Zweck |
|---|---|
| [`smartes_pv_laden_flow_v2.9_2026-10-08.json`](smartes_pv_laden_flow_v2.9_2026-10-08.json) | Node-RED Flow — die eigentliche Lade-Logik (30-s-Zyklus) |
| [`wallbox_telegram_flow_v1.4_2026-10-08.json`](wallbox_telegram_flow_v1.4_2026-10-08.json) | Optional: Node-RED Tab „Wallbox Telegram“ — `/wallbox`-Menü zum Bedienen per Telegram |
| [`pv_laden/pv_laden.yaml`](pv_laden/pv_laden.yaml) | Home Assistant Package — Helper, Template-Sensoren, Automationen, Kostenauswertung |
| [`pv_laden/README.md`](pv_laden/README.md) | Detail-Doku aller Entities des Packages |
| [`home-assistant-dashboard.yaml`](home-assistant-dashboard.yaml) | Lovelace-Dashboard (Übersicht, Verlauf, Einstellungen) |
| [`archive/`](archive/) | Ältere Flow-, Package- und Doku-Versionen (nur zur Referenz) |

---

## Betriebsmodi

Das System kennt 5 Modi, steuerbar über `input_select.lade_modus`. Das Auto-Ziel-SOC (Standard 80%) gilt in **allen** Modi identisch. Ohne SOC-Override ist es auf höchstens 80 % begrenzt. Mit `soc_override` lädt das Auto entweder bis zu einem Ziel über 80 % (z. B. 90 %) oder, bei einem Ziel ≤ 80 %, ohne Grenze bis voll.

### Automatik (empfohlen)

Der Standardmodus für den täglichen Betrieb — kombiniert die beiden anderen Automatik-Strategien.

- **Priorität 1 — PV-Überschuss:** Dynamische Stromregelung (7–32A) basierend auf verfügbarer Einspeisung, startet ab **3600W** Überschuss
- **Priorität 2 — Günstigster Strom (Fallback):** Reicht der PV-Überschuss nicht und ist `tibber_enabled = on`, prüft das System den aktuellen Strompreis. Ist er ≤ Tagesminimum + Toleranz (`cheap_price_tolerance_ct`, Standard 3 ct), wird trotzdem mit `max_charge_current` geladen (PV + Netz)
- **Wolken-Überbrückung:** Bricht der Überschuss kurzzeitig ein (z. B. Wolke) und greift kein Preis-Fallback, wird bis zu `bridge_max_minutes` (Standard 10 min) mit Minimalstrom weitergeladen statt sofort zu stoppen
- Batterie-Priorität gilt nur für das PV-Laden (Hausbatterie erst auf 95 %, dann Auto). Der Günstigstrom-Fallback lädt das Auto auch bei leerem Hausakku (Auto-Vorrang)
- Auto-Ziel-SOC per `soc_override` überbrückbar (wie alle anderen Modi)

### Laden erzwingen

Für Situationen wo schnell geladen werden muss (Reise, Notfall).

- Lädt **sofort mit dem eingestellten `max_charge_current`-Wert vom Netz**
- Ignoriert PV-Überschuss, Batterie-Priorität und Wetterlage
- Auto-Ziel-SOC gilt — **ABER:** per SOC-Override bis 100% umgehbar
- Kein Warten auf Sonne, kein Warten auf Hausbatterie

### Nur PV-Überschuss

Strenger als Automatik — ausschließlich direkter Solarstrom, ohne Preis-Fallback.

- Identische PV-Berechnung wie Automatik (= tatsächliche Einspeisung ins Netz)
- **Kein** Günstigstrom-Fallback — lädt wirklich nur mit dem, was eingespeist würde
- Wolken-Überbrückung aktiv (wie Automatik)
- Auto-Ziel-SOC per SOC-Override umgehbar
- Anwendungsfall: Maximal ökologisches Laden, bewusst über 80% mit PV

### Günstigster Strom

Lädt unabhängig von PV-Erzeugung rein preisgetrieben aus dem Netz.

- Ermittelt laufend den günstigsten Strompreis des Tages über das `min_price`-Attribut von `sensor.sectorchan_electricity_price`
- Lädt mit `max_charge_current`, sobald der aktuelle Preis ≤ Tagesminimum + `cheap_price_tolerance_ct` (Standard 3 ct) liegt, sonst wird gewartet (kein Netzbezug)
- Auto-Ziel-SOC per SOC-Override umgehbar
- Funktioniert unabhängig vom Schalter `tibber_enabled` (der steuert nur den Fallback *innerhalb* von Automatik)

### Stoppen

Wallbox wird sofort pausiert. Keine weitere Logik.

---

## Vergleich der Modi

| Eigenschaft | Automatik | Laden erzwingen | Nur PV-Überschuss | Günstigster Strom | Stoppen |
|---|---|---|---|---|---|
| **Stromquelle** | PV-Überschuss (+Netz bei Preis-Fallback) | Netz + PV | Nur PV-Überschuss | Nur Netz | — |
| **Auto-Ziel-SOC** | SOFT (per Override umgehbar) | SOFT (per Override umgehbar) | SOFT (per Override umgehbar) | SOFT (per Override umgehbar) | — |
| **Günstigstrom-Logik** | Ja, als Fallback (wenn aktiviert) | Nicht relevant | Nein | Ja, als Hauptkriterium | — |
| **Batterie-Priorität** | Ja | Nein | Ja | Nein | — |
| **Wolken-Überbrückung** | Ja (max. `bridge_max_minutes`) | Nicht relevant | Ja (max. `bridge_max_minutes`) | Nein | — |
| **Stromregelung** | Dynamisch 7–32A | Fest auf `max_charge_current` | Dynamisch 7–32A | Fest auf `max_charge_current` | — |
| **Min. Überschuss** | 3600W | Keiner | 3600W | Keiner | — |
| **Battery Lock (RCT)** | Ja (wenn aktiviert) | Ja (wenn aktiviert) | Ja (wenn aktiviert) | Ja (wenn aktiviert) | Unlock |

---

## Einstellmöglichkeiten

Alle Parameter werden live aus Home Assistant gelesen und sofort wirksam.

### Schalter (input_boolean)

| Parameter | Standard | Beschreibung |
|-----------|----------|--------------|
| `battery_priority` | an | Hausbatterie hat beim **PV-Laden** Vorrang — Auto wird erst mit PV geladen, wenn Haus-SOC ≥ `min_battery_soc`. Gilt nicht für „Laden erzwingen“, „Günstigster Strom“ und den Automatik-Günstigstrom-Fallback |
| `prevent_battery_discharge` | an | Aktiviert den RCT Battery Lock während die Wallbox lädt + korrigiert die Überschussberechnung |
| `soc_override` | aus | Erlaubt Laden über das Ziel-SOC hinaus — gilt einheitlich in **allen** Modi |
| `tibber_enabled` | aus | Aktiviert den Günstigstrom-**Fallback im Automatik-Modus** bei PV-Mangel. Der eigenständige Modus "Günstigster Strom" ist davon unabhängig |

### Zahlenwerte (input_number)

| Parameter | Standard | Bereich | Beschreibung |
|-----------|----------|---------|--------------|
| `min_charge_current` | 7A | 6–16A | Minimaler Ladestrom (unter 6A kann Wallbox nicht laden), auch Strom während der Wolken-Überbrückung |
| `max_charge_current` | 32A | 6–32A | Maximaler Ladestrom (= 22 kW bei 3 Phasen), auch fester Wert für "Laden erzwingen" und "Günstigster Strom" |
| `phases` | 3 | 1–3 | Anzahl der genutzten Phasen |
| `min_battery_soc` | 95% | 50–100% | Haus-Batterie erst auf diesen SOC laden, bevor Auto dran ist |
| `session_soc_limit` | 0 (aus) | 0–100% | Nur dieser Ladevorgang: Laden bis Auto-SOC, ersetzt `car_target_soc` (über 80 % nur mit Override). Reset beim Ausstecken |
| `session_cost_limit` | 0 (aus) | 0–50 € | Nur dieser Ladevorgang: Netzladekosten-Budget (`sensor.wallbox_session_cost`). Erreicht → „Laden“/„Günstigster Strom“ stoppen, Automatik/Nur PV laden nur noch mit PV. Reset beim Ausstecken |
| `car_target_soc` | 80% | 50–100% | Auto-Ziel-SOC. Über 80 % nur mit `soc_override` (sonst automatisch auf 80 % zurückgesetzt) |
| `cheap_price_tolerance_ct` | 3 ct | 0–15 ct | Toleranz über dem Tagestief, bis zu der Strom als „günstig“ gilt (Modus Günstigster Strom + Automatik-Fallback) |
| `bridge_max_minutes` | 10 min | 1–30 min | Max. Dauer der Wolken-Überbrückung (Automatik + Nur PV-Überschuss) |
| `soc_override_max_duration` | 240 min | 0–720 min | `soc_override` wird nach dieser Zeit automatisch zurückgesetzt (0 = nie) |

> Das Package enthält zusätzlich einige Helper aus v1.7 (`system_enabled`, `min_surplus_to_start`, `min_surplus_to_continue`, `hysteresis_time`, `max_grid_power_draw`, `car_soc_threshold_pure_surplus`). Sie werden nur noch im Dashboard angezeigt — der Flow (ab v2.4) wertet sie **nicht** aus.

---

## Features im Detail

### RCT Battery Lock

**Problem:** Der RCT Wechselrichter entlädt die Hausbatterie automatisch wenn im Haus Strom verbraucht wird — er unterscheidet nicht zwischen Kühlschrank und 20-kW-Wallbox.

**Lösung:** Über die `rctpower_writesupport` Integration wird `switch.rct_lock_battery` gesteuert:
- Wallbox startet → Battery Lock ON → Batterie eingefroren (weder Laden noch Entladen)
- Wallbox stoppt → Battery Lock OFF → Normalbetrieb
- Nur aktiv wenn `prevent_battery_discharge = on`

**Voraussetzung:** [rctpower_writesupport](https://github.com/do-gooder/rctpower_writesupport) muss in Home Assistant installiert sein.

### Günstigster Strom (Preis-Logik)

**Idee:** Bei dynamischen Tarifen gibt es Zeitfenster mit sehr günstigem Strom. Diese werden erkannt und entweder direkt genutzt (Modus "Günstigster Strom") oder als Fallback in Automatik, wenn PV-Überschuss fehlt.

**Berechnung:**
- Tagesminimum wird laufend aus dem `min_price`-Attribut von `sensor.sectorchan_electricity_price` gelesen
- Schwelle = Tagesminimum + `input_number.cheap_price_tolerance_ct` (feste Toleranz in ct/kWh, Standard 3 ct, im Dashboard einstellbar)
- Wenn aktueller Preis ≤ Schwelle → günstig → Wallbox auf `max_charge_current`

**Beispiel:** Tagesminimum 15,3 ct + 3 ct → Schwelle 18,3 ct → günstig solange Preis ≤ 18,3 ct

**Warum Cent statt Prozent (seit v2.6):** Eine prozentuale Toleranz wird bei teuren Tagen breiter und bei billigen Tagen schmaler (15 % = 2,3 ct bei 15 ct, aber 4,3 ct bei 29 ct). Eine feste Toleranz bedeutet immer denselben Aufpreis pro kWh. Auswertung der Tibber-15-Minuten-Preise (21.–30.09.2026): Das Fenster liegt praktisch immer zwischen ca. 11:30 und 15:30 Uhr; +3 ct ergibt im Schnitt ~3,1 h pro Tag in meist einem zusammenhängenden Block, +4 ct ~3,8 h, zerfällt aber häufiger in mehrere Blöcke (Wallbox stoppt/startet dazwischen).

**Sensor:** `sensor.sectorchan_electricity_price` (Tibber Integration mit Pulse)

**Wo aktiv:**
- Modus "Günstigster Strom": immer, unabhängig von `tibber_enabled`
- Modus "Automatik": nur als Fallback bei PV-Mangel, nur wenn `tibber_enabled = on`
- Modus "Nur PV-Überschuss": nie

### Überschussberechnung

```
Wenn Einspeisung (grid_power < 0):
    Überschuss = |grid_power| + aktuelle Wallbox-Leistung (falls lädt)

Wenn Netzbezug (grid_power > 0):
    Überschuss = Wallbox-Leistung - grid_power (falls lädt)
    Überschuss = -grid_power (falls nicht lädt)

Wenn Entladungsschutz aktiv UND Batterie entlädt:
    Überschuss -= Batterie-Entladung
```

### Monatsauswertung & Netzladekosten

Das Package berechnet, was das Laden aus dem Netz kostet — PV-Strom zählt als kostenlos.

```
sensor.wallbox_grid_charge_power      = min(Wallbox-Leistung, Netzbezug)          [W]
sensor.wallbox_grid_charge_cost_rate  = Strompreis × Netzladeleistung / 1000       [EUR/h]
sensor.wallbox_grid_charge_cost_total = Riemann-Summe der Rate (platform: integration) [EUR]
sensor.wallbox_grid_cost_monthly      = utility_meter, monatlicher Reset           [EUR]
sensor.wallbox_energy_monthly         = utility_meter auf Easee-Lifetime-Energie   [kWh]
```

Beide Monatszähler haben im Attribut `last_period` den Vormonatswert. Der Kostenzähler liefert erst einen Wert, sobald zum ersten Mal mit Netzbezug geladen wurde (vorher `unknown`/`unavailable`).

> **Wichtig:** Die Entity-IDs entstehen in HA aus dem `name` (z. B. `sensor.wallbox_netzladekosten_rate`), nicht aus der `unique_id`. Flow, Package und Dashboard erwarten aber die englischen IDs. Nach der Erstinstallation daher unter *Einstellungen → Entitäten* die fünf oben genannten Sensoren auf die angegebenen IDs umbenennen (die `unique_id` ist jeweils identisch mit dem Zielnamen).

### API-Throttling

Um 403-Fehler bei der Easee API zu vermeiden:
- Min. 30 Sekunden zwischen API-Calls
- Kein Call wenn Strom unverändert
- Nur bei Änderungen ≥ 1A

---

## Entscheidungsablauf

```
1. Modus = Stoppen?                                    → STOP
2. Auto angeschlossen?                                 → Nein: STOP
3. Auto-SOC ≥ Ziel-SOC (ohne Override max. 80 %)?       → STOP (gilt für ALLE Modi)
   Mit Override: STOP nur bei Ziel > 80 % und Auto-SOC ≥ Ziel
4. Modus = Laden erzwingen?                            → CHARGE mit max_charge_current
5. Batterie-Priorität aktiv UND Haus-SOC < min_battery_soc? → PV-Laden gesperrt
   (Günstigster Strom und Automatik-Fallback laden trotzdem)
6. Modus = Günstigster Strom?
   - Preis ≤ Tagestief + Toleranz (ct)                  → CHARGE mit max_charge_current
   - Sonst                                              → STOP/HOLD (warten auf Tagestief)
7. PV-Überschuss ≥ 3600W?                               → CHARGE mit berechnetem Strom
8. Modus = Automatik UND tibber_enabled UND Preis ≤ Tagestief + Toleranz (ct)? → CHARGE mit max_charge_current (Fallback)
9. Überschuss < 3600W UND bereits am Laden?
   - Modus = Automatik/Überschuss: Wolken-Überbrückung starten/fortsetzen (max. bridge_max_minutes mit min_charge_current)
   - Nach Ablauf der Überbrückung                       → STOP
10. Sonst                                               → HOLD (warten)
```

---

## System-Anforderungen

### Hardware
- **RCT Power Storage** Wechselrichter (PS 6.0 oder vergleichbar)
- **Easee Home/Charge** Wallbox
- **Renault Zoe** (oder anderes EV mit HA-Integration für SOC + Plug-State)
- **Tibber Pulse** (optional, für Günstigstrom-Boost)

### Software
- **Home Assistant** 2024.x oder neuer
- **Node-RED** Add-on mit `node-red-contrib-home-assistant-websocket`
- **Home Assistant Integrationen:**
  - RCT Power (Sensoren)
  - [rctpower_writesupport](https://github.com/do-gooder/rctpower_writesupport) (Battery Lock)
  - Easee (Wallbox-Steuerung)
  - My Renault (Zoe SOC/Plug-State)
  - Tibber (optional, Strompreise)

---

## Installation

### 1. HA Package installieren

1. In `configuration.yaml` Packages aktivieren (einmalig):
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
2. `pv_laden/pv_laden.yaml` nach `/config/packages/pv_laden.yaml` kopieren (**nicht** in die `configuration.yaml` einfügen).
3. Eine evtl. vorhandene alte `pv_loading.yaml` oder frühere Kopien der Helper löschen.
4. In `pv_laden.yaml` den Benachrichtigungsdienst `notify.mobile_app_sm_s938b` (4×) durch deinen eigenen ersetzen (*Entwicklerwerkzeuge → Aktionen* → nach `notify.mobile_app_` suchen).
5. *Entwicklerwerkzeuge → YAML → Konfiguration prüfen* → Neustart.
6. Entity-IDs der Kosten-Sensoren prüfen/umbenennen (siehe [Monatsauswertung](#monatsauswertung--netzladekosten)).

### 2. Node-RED Flow importieren

1. Node-RED öffnen (Add-on, z. B. `http://homeassistant.local:1880`)
2. Menü → Import → Datei: `smartes_pv_laden_flow_v2.9_2026-10-08.json` → *Import to: new flow*
3. Im Flow den **Home-Assistant-Server-Node** auf deine Instanz setzen.
4. Die **Easee Device-ID** anpassen: Der Flow enthält die Device-ID `b5b0134f3c9b9d7da1fe77ff580320f2`. Deine eigene findest du in HA unter *Geräte → Easee → URL* (`/config/devices/device/<id>`). Am einfachsten per Suchen/Ersetzen in der JSON-Datei vor dem Import.
5. Deploy.

In den Node-RED Settings muss aktiviert sein (damit der Flow die HA-States live lesen kann):
```
enableGlobalContextStore: true
```

### 3. Telegram-Menü (optional)

Steuert die Wallbox per Telegram-Bot: `/wallbox` schickt Status + Buttons (Modus, SOC-Override, Ziel-SOC ±5 %, für diesen Ladevorgang: bis SOC ±5 % und Kostenbudget −1/+1/+5 €, Aktualisieren). Die Buttons setzen nur die HA-Helfer (`input_select.lade_modus`, `input_boolean.soc_override`, `input_number.car_target_soc`) — die eigentliche Steuerung macht weiterhin der PV-Laden-Flow.

1. Palette `node-red-contrib-telegrambot` installieren und einen Bot-Config-Node anlegen (Token von @BotFather, unter *Users/ChatIds* nur die eigenen Chat-IDs freigeben).
2. Menü → Import → `wallbox_telegram_flow_v1.4_2026-10-08.json` → *Import to: new flow*.
3. In den Telegram-Nodes (`/wallbox`, *Button gedrückt*, *senden*) den eigenen Bot wählen, im Node *HA-Helfer setzen* den Home-Assistant-Server.
4. Deploy, dann im Chat `/wallbox` senden.

### 4. Dashboard einrichten

1. Über HACS installieren: **Mushroom**, **ApexCharts Card**, **Power Flow Card Plus**
2. *Einstellungen → Dashboards → Dashboard hinzufügen* → neues Dashboard öffnen → ⋮ → *Rohdaten-Konfigurationseditor*
3. Inhalt von `home-assistant-dashboard.yaml` einfügen → Speichern

---

## Konfiguration anpassen

Alle Parameter über **Home Assistant UI**:
- Settings → Devices & Services → Helpers
- Oder: Developer Tools → States → `input_*` suchen

Änderungen werden sofort wirksam (nächster 30s-Zyklus).

---

## Sensoren (von Integrationen bereitgestellt)

| Entity | Quelle | Verwendet für |
|--------|--------|---------------|
| `sensor.rct_power_storage_grid_power` | RCT | Überschussberechnung (negativ = Einspeisung) |
| `sensor.rct_power_storage_battery_state_of_charge` | RCT | Batterie-Priorität |
| `sensor.rct_power_storage_battery_power` | RCT | Entladungsschutz (positiv = Entladung) |
| `sensor.easee_home_power` | Easee | Aktuelle Wallbox-Leistung |
| `sensor.easee_home_status` | Easee | Lade-Status (`charging`, `awaiting_start`, …) |
| `sensor.easee_home_dynamic_charger_limit` | Easee | Aktuell gesetztes Ladestrom-Limit (Dashboard) |
| `sensor.easee_home_lifetime_energy` | Easee | Basis für den Monatszähler Ladeenergie |
| `sensor.rct_power_storage_consumer_power` | RCT | Hausverbrauch |
| `sensor.rct_power_storage_inverter_ac_power` | RCT | PV-Leistung |
| `sensor.zoe_charge_state` | My Renault | Lade-Status des Autos |
| `sensor.zoe_battery` | My Renault | Auto-SOC |
| `sensor.zoe_plug_state` | My Renault | Anschluss-Status |
| `sensor.sectorchan_electricity_price` | Tibber | Strompreis + min_price Attribut |
| `switch.rct_lock_battery` | rctpower_writesupport | Battery Lock |

---

## Easee API

Die Device-ID unten ist die der Beispiel-Installation — für deine Wallbox ersetzen.

```yaml
# Pausieren
easee.action_command:
  device_id: b5b0134f3c9b9d7da1fe77ff580320f2
  action_command: pause

# Fortsetzen
easee.action_command:
  device_id: b5b0134f3c9b9d7da1fe77ff580320f2
  action_command: resume

# Stromsteuerung
easee.set_charger_dynamic_limit:
  device_id: b5b0134f3c9b9d7da1fe77ff580320f2
  current: 16  # 6-32A
  time_to_live: 0
```

---

## Troubleshooting

**Lädt nicht trotz Sonne?**
Prüfe in Reihenfolge:
1. `sensor.zoe_plug_state` = "Plugged in"?
2. `sensor.zoe_battery` < 80%?
3. `sensor.rct_power_storage_battery_state_of_charge` ≥ 95% (falls battery_priority an)?
4. Berechneter Überschuss ≥ 3600W? (Node-RED Debug-Sidebar)

**Batterie entlädt trotz Schutz?**
- `prevent_battery_discharge` = on?
- `switch.rct_lock_battery` Entity vorhanden? (rctpower_writesupport installiert?)
- Node-RED Debug: "[v2.1] RCT Batterie LOCK aktiviert" sichtbar?

**Tibber-Boost springt nicht an?**
- `input_boolean.tibber_enabled` = on?
- Modus = automatik?
- Aktueller Preis ≤ Schwelle? Prüfe: `sensor.tibber_cheapest_now`

**403 Error bei Easee?**
- API-Throttling ist eingebaut (30s Minimum). Sollte nicht mehr vorkommen.
- Falls doch: Node-RED Debug prüfen ob Calls zu häufig kommen.

---

## Bekannte Probleme

Derzeit keine bekannten Probleme.

---

## Dateien

```
├── README.md                                        # Diese Datei
├── smartes_pv_laden_flow_v2.9_2026-10-08.json       # Node-RED Flow (aktuell)
├── wallbox_telegram_flow_v1.4_2026-10-08.json       # optional: Telegram-Menü /wallbox
├── home-assistant-dashboard.yaml                    # Lovelace-Dashboard
├── pv_laden/
│   ├── pv_laden.yaml                                # HA Package (Single-File)
│   ├── pv_laden_recorder.yaml                       # optional: nur bei eigener Recorder-Whitelist
│   └── README.md                                    # Package-Dokumentation
└── archive/                                         # Alte Flows, Packages, Dashboards, Doku v1.x
```

---

## Changelog

### Flow v2.9 / Package v2.9 / Dashboard v1.9 / Telegram-Menü v1.4 (2026-10-08)
- **Laden bis Auto-SOC (nur dieser Ladevorgang):** `input_number.session_soc_limit` (0 = aus) ersetzt für den aktuellen Ladevorgang den Ziel-SOC; über 80 % nur mit SOC-Override (`clamp_session_soc_limit`)
- **Laden bis Kosten (nur dieser Ladevorgang):** `input_number.session_cost_limit` in € (0 = aus). `sensor.wallbox_session_cost` = Netzladekosten seit dem Einstecken (Startwert `input_number.session_cost_start`, gesetzt von `session_start_on_plug`). Budget erreicht → „Laden“ und „Günstigster Strom“ stoppen, Automatik/Nur PV laden nur noch mit PV-Überschuss (kein Fallback, keine Überbrückung); Push-Nachricht `notify_session_cost_limit`
- Beide Grenzen werden beim Ausstecken zurückgesetzt (`session_reset_on_unplug`)
- Telegram: Zeile „Ladung“ (Kosten seit Einstecken / Budget), Buttons „Ladung ±5 %“ und „−1 € / +1 € / +5 €“, Mitte-Button ✕ = aus. Dashboard: neue Einträge in den Einstellungen

### Flow v2.8.1 (2026-10-05)
- Battery Lock: kein Entsperren, solange `input_boolean.akku_halten` an ist (externes Package hält den vollen Hausakku bis zum Abend)

### Flow v2.8 (2026-10-03)
- **Auto-Vorrang beim Netzladen:** Batterie-Priorität (`battery_priority`/`min_battery_soc`) sperrt nur noch das PV-Laden. „Günstigster Strom“ und der Automatik-Günstigstrom-Fallback laden das Auto auch bei leerem Hausakku. Abgestimmt mit einem separaten HA-Package, das den Hausakku im günstigsten Tibber-Fenster aus dem Netz lädt und pausiert, solange die Wallbox lädt
- **Battery Lock robuster:** Nach Deploy/Neustart ist der Lock-Zustand unbekannt → beim nächsten Stop wird der Akku sicherheitshalber entsperrt (vorher blieb er gesperrt). Kein Entsperren, solange `input_boolean.akku_netzladen_laeuft` an ist (falls vorhanden)

### Flow v2.7 / Package v2.8 / Telegram-Menü v1.3 (2026-10-02)
- **Ziel-SOC über 80 % mit SOC-Override:** `input_number.car_target_soc` geht jetzt bis 100 %. Mit Override und Ziel > 80 % lädt der Flow bis zum Ziel und stoppt dort, mit Override und Ziel ≤ 80 % wie bisher ohne Grenze
- **Ohne Override höchstens 80 %:** Neue Automation `clamp_car_target_soc` setzt ein höheres Ziel auf 80 % zurück, auch wenn der Override ausgeschaltet wird (manuell, beim Ausstecken oder per Timeout)
- **Telegram:** Ziel ±5 % mit aktuellem Wert in der Mitte, „(max)“/„(min)“ an der Grenze; +5 % bis 80 %, mit Override bis 100 %. Hinweis an der Grenze als Dialog. „message is not modified“-Fehler werden wieder ausgefiltert

### Telegram-Menü v1.1 (2026-10-02)
- **Neu im Repo:** Node-RED-Tab „Wallbox Telegram“ (`/wallbox`), seit v1.0 (2026-10-01) im Einsatz
- **Übersichtlicher:** Emojis entfernt; aktiver Lademodus fett in Großbuchstaben im Text und als einziger Button markiert (`▶ AUTOMATIK ◀`); Werte als ausgerichtete Tabelle

### Package v2.7 (2026-10-01)
- **Recorder nicht mehr global:** Das Package enthält keine `recorder`/`history`/`logbook`-Abschnitte mehr. Ohne Filter zeichnet HA alles auf. Für Installationen mit eigener Whitelist gibt es das optionale Zusatz-Package `pv_laden/pv_laden_recorder.yaml`, das seine Entities an die bestehende Whitelist anhängt

### Package v2.6.1 (2026-10-01)
- **Fix Dashboard-Verläufe:** Die globale `recorder`-Whitelist im Package enthielt seit v2.4 keine externen Sensoren mehr (RCT/Easee/Zoe/Tibber) → ab 27.09.2026 keine Historie, Charts zeigten konstante Werte. Wieder aufgenommen

### Flow v2.6 / Package v2.6 / Dashboard v1.8 (2026-10-01)
- **Günstigstrom-Schwelle in Cent statt Prozent:** Schwelle = Tagestief + `input_number.cheap_price_tolerance_ct` (Standard 3 ct, 0–15 ct) statt Tagestief × 1,15. Gilt für den Modus „Günstigster Strom“, den Automatik-Fallback, `binary_sensor.tibber_is_cheapest_now` und `sensor.tibber_cheapest_now`
- Dashboard: Sektion „Günstigstrom (Tibber)“ in der System-Konfiguration, neue Karte in den Einstellungen, Lade-Modus-Kachel zeigt im Modus „Günstigster Strom“ Preis / Schwelle

### Flow v2.5 (2026-09-26)
- **Fix Automatik / Nur PV-Überschuss:** `sensor.easee_home_power` liefert kW, der Flow rechnete mit W. Während einer PV-Ladung wurde dadurch nur ~15 statt ~15000 W zum Überschuss addiert → der Überschuss fiel unter die Startschwelle (3600 W), der Flow ging in die Wolken-Überbrückung (Minimalstrom) und **stoppte nach `bridge_max_minutes`**. Die Leistung wird jetzt anhand der Einheit in W umgerechnet.
- Fix: `current` wird aus `sensor.easee_home_dynamic_charger_limit` gelesen (`…maximum_allowed_charge_current` existiert nicht mehr)

### Package v2.5.2 (2026-09-26)
- Fix: Benachrichtigungs-Automationen riefen den nicht existierenden Dienst `notify.mobile_app` auf → jetzt `notify.mobile_app_sm_s938b` (für eigene Installation anpassen, siehe Installation)

### Package v2.5.1 (2026-09-26)
- Fix: `sensor.easee_home_power` liefert **kW**, die Templates rechneten mit W → Netzladeleistung, Kostenrate und Wallbox-kW waren um Faktor 1000 zu klein (z. B. 0,0027 € statt ca. 2,09 € für eine 16,8-kWh-Ladung). Umrechnung prüft jetzt die Einheit des Sensors.
- Fix: `calculated_pv_surplus` und `smart_charging_status` nutzten noch `binary_sensor.easee_home_charging` → jetzt `sensor.easee_home_status == 'charging'`

### Package v2.5 (2026-09-24)
- Konsolidiert: `pv_laden.yaml` ist die einzige gültige HA-Konfiguration (alte `home-assistant-configuration.yaml` → `archive/`)
- Dashboard-Helper aus v1.7 wieder aufgenommen (nur Anzeige, vom Flow nicht ausgewertet)
- `unique_id` für beide `utility_meter`
- Dashboard: veraltete Easee-Entities ersetzt (`binary_sensor.easee_home_charging` → `sensor.easee_home_status`, `…maximum_allowed_charge_current` → `…dynamic_charger_limit`)

### v2.4 (2026-09-03 / Package 2026-09-22)
- Fix: RBE-Filter auf den Pause-Grund blockierte weitere Pause-Calls, wenn die Wallbox unabhängig vom Flow gestartet wurde
- Neu: Wallbox-Monatsauswertung mit Netzladekosten (siehe oben)

### v2.3 (2026-08-11)
- Neu: Modus "Günstigster Strom" — lädt rein preisgetrieben (Tagestief + 15%), unabhängig von PV
- Automatik lädt jetzt PV-Überschuss zuerst und fällt bei Mangel optional auf Günstigstrom-Laden zurück
- Auto-Ziel-SOC (80%) ist in allen Modi einheitlich per `soc_override` überbrückbar (Automatik hatte bisher ein Hard-Limit)
- Günstigstrom-Schwelle von Tagestief + 20% auf Tagestief + 15% gesenkt
- Wolken-Überbrückung (max. `bridge_max_minutes`, Standard 10 min) für Automatik + Nur PV-Überschuss reaktiviert

### v2.2 (2026-08-04)
- Fix: `soc_override` konnte unbemerkt dauerhaft aktiv bleiben — jetzt automatischer Reset bei Ausstecken oder nach `soc_override_max_duration`
- Verbesserte Status- und Benachrichtigungstexte je nach Modus/Override-Zustand

### v2.1 (2026-07-21)
- RCT Battery Lock (`switch.rct_lock_battery`) verhindert physische Batterie-Entladung
- Tibber Günstigstrom-Boost im Automatik-Modus (min_price × 1,20)
- HA Package bereinigt (10 Helpers statt 22)

### v2.0 (2026-07-15)
- 4 Modi direkt aus `input_select.lade_modus`
- Config live aus HA States (enableGlobalContextStore)
- Überbrückungslogik entfernt (war in v1.7)

### v1.7 (2026-07-12)
- Math.round() für Präzision
- API-Validierung (92% weniger Calls)
- Hysterese 3 Min / 1A Schwelle

---

## Lizenz

© 2026 Patrick Lang — lizenziert unter [**CC BY-NC-SA 4.0**](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.de) (Namensnennung – Nicht kommerziell – Weitergabe unter gleichen Bedingungen). Vollständiger Text: [`LICENSE`](LICENSE).

Du darfst dieses Projekt:
- **nutzen, kopieren und weitergeben**
- **verändern und darauf aufbauen**

unter folgenden Bedingungen:
- **Namensnennung:** Patrick Lang als Urheber nennen, auf dieses Repository und die Lizenz verweisen und angeben, ob Änderungen vorgenommen wurden — das gilt auch für abgeänderte Versionen.
- **Nicht kommerziell:** Keine Nutzung, mit der Geld verdient wird.
- **Weitergabe unter gleichen Bedingungen:** Veränderte Versionen müssen ebenfalls unter CC BY-NC-SA 4.0 stehen.

### Kommerzielle Nutzung nur nach Rücksprache

Wer mit diesem Projekt Geld verdienen möchte — z. B. durch Verkauf, Einbau in kostenpflichtige Produkte oder bezahlte Installation/Dienstleistungen —, braucht **vorher eine gesonderte, schriftliche Erlaubnis** von Patrick Lang. Anfrage bitte über ein [GitHub-Issue](https://github.com/seemedFilm/HA-Easee-Wallbox-control/issues) in diesem Repository.

---

**Version:** Flow 2.5 · Package 2.5.2
**Aktualisiert:** 2026-09-24

Entwickelt von Patrick mit Claude Code.
