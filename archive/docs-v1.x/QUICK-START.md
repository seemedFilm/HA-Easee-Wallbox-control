# ⚡ Quick Start Guide

Schnellstmöglicher Einstieg in 5 Minuten!

## 🚀 In 5 Schritten zum laufenden System

### 1️⃣ Node-RED Flow importieren (2 Min.)
```
1. Node-RED öffnen: http://homeassistant.local:1880
2. Menu → Import → Datei auswählen
3. smartes_pv_laden_flow_v1.6_2026-07-09.json
4. Deploy klicken
```

### 2️⃣ Home Assistant Input Select erstellen (1 Min.)
```
1. Settings → Devices & Services → Helpers
2. + Create Helper → Dropdown
3. Name: "Lade-Modus"
4. Entity ID: input_select.lade_modus
5. Options: automatik, laden, stoppen, überschuss
6. Create
```

### 3️⃣ Easee Device ID prüfen (30 Sek.)
```
Aktuell: b5b0134f3c9b9d7da1fe77ff580320f2

Falls abweichend:
1. Developer Tools → Services
2. easee.action_command aufrufen
3. Device ID notieren
4. In allen Easee-Nodes im Flow ersetzen
```

### 4️⃣ Flow testen (1 Min.)
```
1. Node-RED Debug-Sidebar öffnen
2. "Manueller Update" Inject-Button klicken
3. Prüfen: "Config geladen" + Sensordaten erscheinen
4. Lade-Modus auf "stoppen" setzen (sicher!)
```

### 5️⃣ Dashboard installieren (30 Sek.)
```
1. Settings → Dashboards → + Add Dashboard
2. Title: "PV-Laden", Icon: mdi:car-electric
3. Dashboard öffnen → Edit → Raw configuration editor
4. Inhalt von home-assistant-dashboard.yaml einfügen
5. Save
```

---

## ✅ Fertig!

**Dashboard:** Sidebar → PV-Laden  
**Steuerung:** Lade-Modus umschalten (Automatik empfohlen)  
**Monitoring:** Node-RED Debug-Sidebar

---

## ⚠️ Wichtige Hinweise

**Vor dem ersten Einsatz:**
- [ ] Teste mit "Stoppen"-Modus
- [ ] Prüfe alle Sensor-Werte im Dashboard
- [ ] Stelle sicher, dass Auto nicht dringend geladen werden muss
- [ ] Aktiviere "Automatik" nur bei Tageslicht (PV-Produktion)

**Sicherheit:**
- 80% Auto-SOC ist HARD-LIMIT (außer "Laden erzwingen")
- System stoppt automatisch bei 80%
- "Stoppen"-Modus für Notfall nutzen

---

## 🔧 Minimale Konfiguration (Optional)

Falls du nur das Nötigste willst:

**Helpers (via Settings → Helpers):**
1. `input_select.lade_modus` (Dropdown)
2. `input_boolean.system_enabled` (Toggle)

**Das wars!** Node-RED nutzt Standardwerte für alles andere.

---

## 📖 Weitere Dokumentation

- **README.md** — Vollständige Feature-Liste
- **INSTALLATION.md** — Detaillierte Anleitung mit Troubleshooting
- **PROJECT-OVERVIEW.md** — Technische Details & Architektur

---

**Geschätzte Zeit:** 5 Minuten  
**Schwierigkeitsgrad:** ⭐⭐☆☆☆ (Anfänger)  
**Voraussetzungen:** Home Assistant + Node-RED Add-on
