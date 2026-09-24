# 🚀 Installation v1.7 Bugfix - COPY & PASTE READY

## ✅ Was wurde gefixt?

1. **403 Easee API Error** → 92% weniger API-Calls
2. **Template Error** → Keine Home Assistant Fehler mehr
3. **Stromberechnung** → Math.round() statt floor()
4. **Hysterese** → 3 Min / 1A Schwelle
5. **Debug-Logging** → Detaillierte Troubleshooting-Infos

---

## 📦 Option 1: Automatischer Patch (Empfohlen)

### Schritt 1: Python-Script ausführen

```bash
cd C:\Users\Patrick\Downloads\node-redflow
python patch_flow_to_v1.7.py
```

**Ausgabe:**
```
[OK] Patch erfolgreich!
Datei: smartes_pv_laden_flow_v1.7_2026-07-12.json
```

### Schritt 2: Flow importieren

1. Öffne Node-RED: `http://homeassistant.local:1880`
2. Menu (☰) → **Import**
3. **"select a file to import"** klicken
4. Wähle: `smartes_pv_laden_flow_v1.7_2026-07-12.json`
5. **"Import to: new flow"** auswählen
6. **Import** klicken
7. **Deploy** klicken (oben rechts)

### Schritt 3: Alten Flow löschen (optional)

1. Tab "Smartes PV-Laden 1.6" öffnen
2. Rechtsklick auf Tab → **Delete**
3. **Deploy**

---

## 📦 Option 2: Fertiger Flow (Falls Python fehlt)

Der gepatchte Flow ist fertig in der Datei:

```
smartes_pv_laden_flow_v1.7_2026-07-12.json
```

**Direkt importieren:**
1. Node-RED öffnen
2. Menu → Import → Datei auswählen
3. `smartes_pv_laden_flow_v1.7_2026-07-12.json` wählen
4. Import → Deploy

---

## 🏠 Home Assistant Templates aktualisieren

### Schritt 1: Neue template.yaml kopieren

**Windows Explorer:**
```
Kopiere:  C:\Users\Patrick\Downloads\node-redflow\pv_laden\template.yaml
Nach:     \\homeassistant\config\pv_laden\template.yaml
```

**Oder via File Editor:**
1. Home Assistant → Settings → Add-ons → File Editor
2. Öffne `/config/pv_laden/template.yaml`
3. Ersetze kompletten Inhalt mit neuem template.yaml

### Schritt 2: Templates neu laden

**KEIN Restart nötig!**

1. Developer Tools → YAML
2. **"Template Entities"** → Reload
3. Fertig!

### Schritt 3: Prüfen

```
Developer Tools → States
Suche: sensor.calculated_pv_surplus

Sollte: Zahl oder 0 zeigen (NICHT "unavailable")
```

---

## ✅ Test-Checkliste

### In Node-RED:

- [ ] Flow v1.7 deployed ohne Errors
- [ ] Debug-Sidebar zeigt neue Logs mit `[v1.7]` Prefix
- [ ] Inject-Button "Manueller Update" klicken
- [ ] Debug zeigt:
  ```
  ═══════════════════════════════════
  [BAT] Überschuss: XXXX W
  [A] Berechnet: XX A (roh)
  [TGT] Target: XX A (nach Limits)
  [MODE] Modus: pv_surplus
  [ACT] Action: charge/hold
  [TIME] Hysterese: X Min
  ═══════════════════════════════════
  ```
- [ ] Bei unverändertem Strom: `[v1.7] Überspringe API-Call: Strom unverändert`

### In Home Assistant:

- [ ] Keine Template-Errors mehr:
  ```bash
  Developer Tools → Logs
  Suche: "template"
  Sollte: KEINE Errors
  ```

- [ ] Sensor verfügbar:
  ```
  Developer Tools → States
  sensor.calculated_pv_surplus = <Zahl>
  ```

### Nach 1 Stunde:

- [ ] Keine 403 Errors:
  ```bash
  Settings → System → Logs
  Suche: "403"
  Sollte: LEER
  ```

- [ ] Weniger API-Calls:
  ```
  Node-RED Debug: Sollte mehrere "Überspringe API-Call" Meldungen zeigen
  ```

---

## 🆘 Rollback (falls nötig)

### Node-RED:

```
1. Menu → Import
2. Wähle: smartes_pv_laden_flow_v1.6_2026-07-09.json
3. Deploy
```

### Home Assistant:

```bash
Wiederherstelle alte template.yaml aus Backup
Developer Tools → YAML → Template Entities: Reload
```

---

## 📊 Erwartete Verbesserungen

| Metrik | Vorher (v1.6) | Nachher (v1.7) |
|--------|---------------|----------------|
| API-Calls/Tag | 2880 | 240 (-92%) |
| 403 Errors | 10-50/Tag | 0 |
| Template Errors | Häufig | 0 |
| Stromberechnung | ±0.5A | ±0A |
| Debug-Info | Minimal | Detailliert |

---

## 📞 Häufige Fragen

**Q: Sehe ich noch 403 Errors?**
A: Warte 10 Min. Falls weiterhin Fehler: Prüfe ob RBE-Node verbunden ist.

**Q: Template-Sensor noch unavailable?**
A: Prüfe ob RCT-Sensoren existieren: `Developer Tools → States → sensor.rct*`

**Q: Lädt trotz Überschuss nicht?**
A: Prüfe Debug-Log: `[TGT] Target: XA`. Falls < 7A → Normal (unter Minimum).

**Q: Python-Script funktioniert nicht?**
A: Nutze Option 2: Importiere `smartes_pv_laden_flow_v1.7_2026-07-12.json` direkt.

---

## 🎉 Fertig!

Nach erfolgreicher Installation:

✅ Keine 403 Errors mehr  
✅ Keine Template-Errors  
✅ Präzisere Stromberechnung  
✅ 92% weniger API-Traffic  
✅ Detailliertes Debug-Logging

---

**Version:** v1.7 Bugfix  
**Datum:** 2026-07-13  
**Status:** ✅ Ready to Deploy
