# PV-Laden Package v2.5.1

Home Assistant Konfiguration für das Smarte PV-Laden System (Node-RED Flow v2.5).

## Dateistruktur

```
pv_laden/
├── README.md                    # Diese Datei
└── pv_laden.yaml                # HA Package (Single-File: Helper, Templates, Automationen,
                                 #   Kostenauswertung, recorder/history/logbook)
```

## Installation

### 1. Package ablegen

Kopiere `pv_laden.yaml` nach `/config/packages/pv_laden.yaml` auf Home Assistant.

### 2. configuration.yaml anpassen (einmalig)

```yaml
homeassistant:
  packages: !include_dir_named packages
```

### 3. Prüfen & Neustarten

Developer Tools → YAML → Check Configuration → Restart

## Enthaltene Entities

### Input Helpers (11 Stück)

**Input Select (1):**
- `input_select.lade_modus` — automatik / laden / stoppen / überschuss / günstigster_strom

**Input Boolean (4):**
- `input_boolean.battery_priority` — Batterie-Priorität (erst ab 95% SOC Auto laden). Gilt für alle Modi außer "laden".
- `input_boolean.prevent_battery_discharge` — Entladungsschutz + RCT Battery Lock
- `input_boolean.soc_override` — Auto-Ziel-SOC überbrücken. Gilt jetzt einheitlich für **alle** Modi (auch Automatik). Persistent — wird automatisch zurückgesetzt bei Ausstecken oder nach `soc_override_max_duration` (siehe Automationen).
- `input_boolean.tibber_enabled` — Günstigstrom-Fallback **innerhalb von Automatik**, wenn PV-Überschuss nicht reicht. Der eigenständige Modus "günstigster_strom" funktioniert unabhängig von diesem Schalter.

**Input Number (7):**
- `input_number.min_charge_current` — Min. Ladestrom (Standard: 7A)
- `input_number.max_charge_current` — Max. Ladestrom (Standard: 32A)
- `input_number.phases` — Phasen (Standard: 3)
- `input_number.min_battery_soc` — Min. Batterie-SOC für Priorität (Standard: 95%)
- `input_number.car_target_soc` — Auto-Ziel-SOC (Standard: 80%), in allen Modi per `soc_override` überbrückbar
- `input_number.soc_override_max_duration` — Auto-Reset für `soc_override` nach X Minuten (Standard: 240 min, 0 = deaktiviert)
- `input_number.bridge_max_minutes` — Max. Dauer der Wolken-Überbrückung in Automatik/PV-Überschuss (Standard: 10 min)

### Template Sensoren

**Sensoren (6):**
- `sensor.calculated_pv_surplus` — Berechneter Überschuss (W)
- `sensor.calculated_charge_current` — Berechneter Ladestrom (A)
- `sensor.wallbox_charge_power_kw` — Wallbox-Leistung (kW)
- `sensor.battery_flow_direction` — Batterie: Laden/Entladen/Ruhend
- `sensor.grid_flow_direction` — Netz: Einspeisung/Bezug/Neutral
- `sensor.tibber_cheapest_now` — Aktueller vs. Schwellen-Preis
- `sensor.smart_charging_status` — System-Status-Text

**Binary Sensoren (3):**
- `binary_sensor.tibber_is_cheapest_now` — Strom gerade günstig?
- `binary_sensor.battery_soc_above_minimum` — Batterie über Minimum?
- `binary_sensor.car_soc_below_target` — Auto unter Ziel-SOC?

### Wallbox-Monatsauswertung (neu in v2.4)

- `sensor.wallbox_grid_charge_power` — Momentane Netz-Ladeleistung der Wallbox (W), Anteil, der NICHT aus PV-Überschuss stammt
- `sensor.wallbox_grid_charge_cost_rate` — Momentane Kostenrate des Netz-Anteils (EUR/h), auf Basis Tibber-Preis
- `sensor.wallbox_grid_charge_cost_total` — Riemann-Summe der Rate → kumulierte Netzladekosten seit Bestehen des Sensors (`platform: integration`)
- `sensor.wallbox_energy_monthly` — `utility_meter`, gesamte Wallbox-Ladeenergie pro Monat (unabhängig von PV/Netz), inkl. Vormonatswert im Attribut `last_period`
- `sensor.wallbox_grid_cost_monthly` — `utility_meter`, Netzladekosten pro Monat (nur Netz-Anteil), inkl. Vormonatswert im Attribut `last_period`

Zusätzlich enthält das Package jetzt `recorder`, `history` und `logbook`-Abschnitte für die paketeigenen Entities. Externe Entities (RCT/Easee/Zoe/Tibber) sind bewusst nicht enthalten — siehe "Externe Abhängigkeiten" unten.

### Automationen (4)

- **notify_car_80_percent** — Benachrichtigung wenn Auto 80% SOC erreicht (nicht ausgelöst, wenn SOC-Override aktiv weiterlädt)
- **notify_car_over_80_override_active** — Warn-Benachrichtigung, wenn bei aktivem SOC-Override über 80% hinaus geladen wird
- **reset_soc_override_on_unplug** — Setzt SOC-Override automatisch zurück, sobald das Fahrzeug ausgesteckt wird
- **reset_soc_override_timeout** — Setzt SOC-Override automatisch zurück, wenn er länger als `soc_override_max_duration` aktiv war

## Externe Abhängigkeiten (nicht in diesem Package)

Folgende Entities müssen von anderen Integrationen bereitgestellt werden:

| Entity | Integration |
|--------|-------------|
| `sensor.sectorchan_electricity_price` | Tibber |
| `switch.rct_lock_battery` | rctpower_writesupport |
| `sensor.rct_power_storage_*` | RCT Power |
| `sensor.easee_home_*` | Easee |
| `sensor.zoe_*` | My Renault |

## Changelog

### v2.5.1 (2026-09-26)
- Fix: `sensor.easee_home_power` liefert kW → Templates für Netzladeleistung, Kostenrate und Wallbox-kW rechnen jetzt einheitenabhängig in W um (vorher Faktor 1000 zu klein)
- Fix: `calculated_pv_surplus` und `smart_charging_status` nutzen `sensor.easee_home_status` statt des entfernten `binary_sensor.easee_home_charging`

### v2.5 (2026-09-24)
- Wieder aufgenommen (nur fürs Dashboard, vom Node-RED-Flow v2.4 NICHT ausgewertet): `input_boolean.system_enabled`, `input_number.min_surplus_to_start`, `min_surplus_to_continue`, `hysteresis_time`, `max_grid_power_draw`, `car_soc_threshold_pure_surplus` — das Live-Dashboard referenziert sie noch
- Neu: `unique_id` für beide `utility_meter` (`wallbox_energy_monthly`, `wallbox_grid_cost_monthly`), damit die Entity-IDs in der Registry festgelegt werden können
- Hinweis: Entity-IDs der Kosten-Sensoren in HA per Registry auf die `unique_id` umbenannt (HA hatte sie aus dem deutschen `name` gebildet, z. B. `sensor.wallbox_netzladekosten_rate`)
- `home-assistant-configuration.yaml` (v1.7) nach `archive/home-assistant-configuration_v1.7.yaml` verschoben — nicht mehr einspielen, dieses Package ist die einzige gültige HA-Config

### v2.4 (2026-09-22)
- Neu: Wallbox-Monatsauswertung — `sensor.wallbox_grid_charge_power`, `sensor.wallbox_grid_charge_cost_rate`, `sensor.wallbox_grid_charge_cost_total` (Template- bzw. Integration-Sensoren)
- Neu: `utility_meter.wallbox_energy_monthly` und `utility_meter.wallbox_grid_cost_monthly` für monatliche Auswertung mit Vormonats-Vergleich
- Neu: `recorder`/`history`/`logbook`-Abschnitte für die paketeigenen Entities (bisher nicht Teil dieses Packages)
- Konsolidiert aus der zuvor separat gepflegten `home-assistant-configuration.yaml` (Alt-Version v1.6) — dabei bewusst NICHT übernommen: `system_enabled`, `bridge_*`-Helper, alte MQTT-Sync-Automation und veraltete Schwellenwert-Parameter, da diese bereits in v2.0/v2.1 aus dem Package entfernt wurden

### v2.3 (2026-08-11)
- Neu: Modus `günstigster_strom` — lädt ausschließlich preisgetrieben (Tagestief + 15%), unabhängig von PV-Überschuss
- Geändert: Automatik lädt PV-Überschuss zuerst, fällt bei Mangel (wenn `tibber_enabled = on`) auf Günstigstrom-Laden zurück
- Geändert: `input_boolean.soc_override` überbrückt das 80%-Ziel jetzt in **allen** Modi, auch Automatik (bisher Hard-Limit)
- Geändert: Günstigstrom-Schwelle von Tagestief + 20% auf Tagestief + 15% gesenkt
- Neu: `input_number.bridge_max_minutes` — Wolken-Überbrückung (kurzzeitiges Weiterladen mit Minimalstrom statt sofortigem Stopp) für Automatik + PV-Überschuss reaktiviert
- Umbenannt (nur Beschreibung, Entity-ID unverändert): `input_boolean.tibber_enabled` heißt jetzt sinngemäß "Günstigstrom-Fallback in Automatik"
- Vereinfacht: Benachrichtigungs-Automationen prüfen jetzt einheitlich nur noch `soc_override` statt modusspezifischer Bedingungen

### v2.2 (2026-08-04)
- Fix: `soc_override` konnte unbemerkt dauerhaft aktiv bleiben (führte zu ungewollter 100%-Ladung) — jetzt automatischer Reset bei Ausstecken und per Timeout
- Neu: `input_number.soc_override_max_duration`
- Neu: Automationen `reset_soc_override_on_unplug`, `reset_soc_override_timeout`, `notify_car_over_80_override_active`
- Fix: `notify_car_80_percent` behauptete fälschlich "wird gestoppt", obwohl bei aktivem Override weitergeladen wird
- Fix: `sensor.smart_charging_status` zeigte im Modus "laden" immer "Laden erzwungen" an, auch wenn die SOC-Prüfung eigentlich gerade gestoppt hat oder das Limit über Override überschritten wird — jetzt unterscheidbare Statustexte

### v2.1 (2026-07-22)
- Bereinigt auf tatsächlich vom Flow genutzte Helpers
- Entfernt: system_enabled, bridge_*, hysteresis_time, max_grid_power_draw, car_soc_threshold_pure_surplus, tibber_price_threshold, tibber_charge_current, min_surplus_to_start, min_surplus_to_continue, override_charge_current
- Entfernt: MQTT-Sync Automation (v2.0+ liest direkt via enableGlobalContextStore)
- Entfernt: Überbrückungs-Automation (in v2.0 entfernt)
- Neu: binary_sensor.tibber_is_cheapest_now
- Neu: sensor.tibber_cheapest_now
- Template-Fix: Stromberechnung P/(230*phases) statt P/(230*1.732*phases)

### v1.6 (2026-07-11)
- Erstversion des Packages (für Node-RED Flow v1.6/v1.7)

---

**Version:** 2.4
**Kompatibilität:** Node-RED Flow v2.5 (v2.4 kompatibel), Home Assistant 2024.x+
