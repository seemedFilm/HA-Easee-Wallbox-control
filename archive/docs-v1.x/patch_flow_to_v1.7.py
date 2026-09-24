#!/usr/bin/env python3
"""
Automatischer Patcher für Node-RED Flow v1.6 -> v1.7
Behebt: 403 Errors, Template-Fehler, Stromberechnung

Usage:
    python patch_flow_to_v1.7.py

Output:
    smartes_pv_laden_flow_v1.7_2026-07-12.json
"""

import json
import re
from datetime import datetime

# Input/Output Files
INPUT_FILE = "smartes_pv_laden_flow_v1.6_2026-07-09.json"
OUTPUT_FILE = "smartes_pv_laden_flow_v1.7_2026-07-12.json"

def patch_flow(flow_data):
    """Wendet alle Patches auf den Flow an"""

    for node in flow_data:
        node_type = node.get('type', '')
        node_name = node.get('name', '')

        # Patch 1: Tab-Info aktualisieren
        if node_type == 'tab':
            node['label'] = 'Smartes PV-Laden 1.7 (Bugfix)'
            node['info'] = '''Intelligentes PV-Überschussladen für Easee Wallbox mit RCT Wechselrichter version 1.7

Bugfixes v1.7:
- Math.round() statt floor() -> Präzisere Stromberechnung
- API-Call Validierung -> Verhindert 403 Errors
- RBE-Filter für Dynamic Limit -> Keine redundanten Calls
- Hysterese auf 3 Min erhöht -> Weniger API-Traffic
- Hysterese-Schwelle auf 1A -> Stabileres Verhalten
- Debug-Logging verbessert -> Besseres Troubleshooting'''
            print("[OK] Tab-Info aktualisiert")

        # Patch 2: Standard-Konfiguration - Hysterese auf 3 Min
        if node_name == 'Standard-Konfiguration':
            func_code = node.get('func', '')
            func_code = func_code.replace(
                'hysteresis_time: config.hysteresis_time || 2, // Minuten',
                'hysteresis_time: config.hysteresis_time || 3, // Minuten (erhöht für Easee API)'
            )
            node['func'] = func_code
            print("[OK] Hysterese-Zeit auf 3 Min erhöht")

        # Patch 3: Lade-Logik - Math.round() + API-Validierung + Debug
        if node_name == 'Lade-Logik & Modus-Auswahl':
            func_code = node.get('func', '')

            # 3a: Math.floor -> Math.round
            func_code = func_code.replace(
                'return Math.floor(current);',
                'return Math.round(current);  // v1.7: round statt floor für Präzision'
            )
            print("[OK] Math.round() statt Math.floor()")

            # 3b: Hysterese-Schwelle 2 -> 1
            func_code = func_code.replace(
                'Math.abs(targetCurrent - chargingState.last_current) <= 2',
                'Math.abs(targetCurrent - chargingState.last_current) <= 1  // v1.7: 1A Schwelle'
            )
            print("[OK] Hysterese-Schwelle auf 1A")

            # 3c: API-Call Validierung einfügen
            api_validation = '''
// === v1.7: API-Call Validierung (403 Error Prevention) ===
const lastSetCurrent = flow.get('last_api_current') || 0;
const lastApiCall = flow.get('last_api_timestamp') || 0;
const timeSinceLastCall = (now - lastApiCall) / 1000;

// Regel 1: Kein API-Call wenn Strom gleich
if (action === 'charge' && targetCurrent === lastSetCurrent) {
    node.warn('[v1.7] Überspringe API-Call: Strom unverändert (' + targetCurrent + 'A)');
    action = 'hold';
}

// Regel 2: Min. 60s zwischen API-Calls
if (action === 'charge' && timeSinceLastCall < 60 && targetCurrent !== lastSetCurrent) {
    node.warn('[v1.7] API-Call zu früh (' + Math.round(timeSinceLastCall) + 's). Warte...');
    action = 'hold';
}

// Regel 3: Nur signifikante Änderungen (≥1A)
if (action === 'charge' && Math.abs(targetCurrent - lastSetCurrent) < 1) {
    node.warn('[v1.7] Stromänderung zu gering: ' + lastSetCurrent + 'A -> ' + targetCurrent + 'A');
    targetCurrent = lastSetCurrent;
    action = 'hold';
}

// Tracking für nächsten Call
if (action === 'charge' || action === 'start') {
    flow.set('last_api_current', targetCurrent);
    flow.set('last_api_timestamp', now);
}
// === Ende API-Validierung ===
'''
            # Einfügen NACH Hysterese, VOR "Update Charging State"
            func_code = func_code.replace(
                '// Update Charging State',
                api_validation + '\n// Update Charging State'
            )
            print("[OK] API-Call Validierung hinzugefügt")

            # 3d: Debug-Logging einfügen
            debug_logging = '''
// === v1.7: Debug-Logging ===
if (action !== 'hold') {
    node.warn('═══════════════════════════════════');
    node.warn('[BAT] Überschuss: ' + surplus + 'W');
    node.warn('[A] Berechnet: ' + calculateCurrent(surplus) + 'A (roh)');
    node.warn('[TGT] Target: ' + targetCurrent + 'A (nach Limits)');
    node.warn('[MODE] Modus: ' + newMode);
    node.warn('[ACT]  Action: ' + action);
    const hystMinutes = chargingState.last_current_change ?
        Math.round((now - chargingState.last_current_change) / 1000 / 60) : 0;
    node.warn('[TIME]  Hysterese: ' + (hystMinutes > 0 ? hystMinutes + ' Min' : 'erstmalig'));
    node.warn('═══════════════════════════════════');
}
// === Ende Debug ===
'''
            # Einfügen VOR "// Route zu entsprechendem Output"
            func_code = func_code.replace(
                '// Route zu entsprechendem Output',
                debug_logging + '\n// Route zu entsprechendem Output'
            )
            print("[OK] Debug-Logging hinzugefügt")

            node['func'] = func_code

        # Patch 4: RBE-Filter für Dynamic Limit hinzufügen
        # Wird zwischen "Wallbox fortsetzen" und "Dynamic Limit" eingefügt
        if node_name == 'Wallbox fortsetzen (easee.action_command)':
            # Wir fügen später einen neuen RBE-Node hinzu und passen Wires an
            pass

    # Patch 5: Neuen RBE-Node hinzufügen
    rbe_node = {
        "id": "rbe_dynamic_limit_v17",
        "type": "rbe",
        "z": "ceb487b98620db29",
        "name": "Filter identische Stromwerte (v1.7)",
        "func": "rbe",
        "gap": "",
        "start": "",
        "inout": "out",
        "septopics": False,
        "property": "payload.control.target_current",
        "topi": "topic",
        "x": 700,
        "y": 600,
        "wires": [
            []  # Wird mit Dynamic Limit Node verbunden
        ]
    }

    # Finde Dynamic Limit Node ID
    dynamic_limit_id = None
    for node in flow_data:
        if node.get('name') == 'Circuit Dynamic Limit setzen':
            dynamic_limit_id = node['id']
            break

    if dynamic_limit_id:
        rbe_node['wires'] = [[dynamic_limit_id]]
        flow_data.append(rbe_node)
        print("[OK] RBE-Filter Node hinzugefügt")

        # Patch 6: Verbindungen aktualisieren
        for node in flow_data:
            # "Wallbox fortsetzen" -> RBE statt direkt Dynamic Limit
            if node.get('name') == 'Wallbox fortsetzen (easee.action_command)':
                node['wires'] = [['rbe_dynamic_limit_v17']]
                print("[OK] Wallbox fortsetzen -> RBE verbunden")

            # "Lade-Logik" Output 3 (Adjust) -> RBE statt direkt Dynamic Limit
            if node.get('name') == 'Lade-Logik & Modus-Auswahl':
                wires = node.get('wires', [])
                if len(wires) >= 3:
                    # Output 3 (Index 2) = Adjust Current
                    wires[2] = ['rbe_dynamic_limit_v17']
                    node['wires'] = wires
                    print("[OK] Lade-Logik Output 3 -> RBE verbunden")

    return flow_data


def main():
    print("=" * 50)
    print("Node-RED Flow Patcher v1.6 -> v1.7")
    print("=" * 50)
    print()

    # Load Flow
    print(f"[*] Lade Flow: {INPUT_FILE}")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] ERROR: Datei {INPUT_FILE} nicht gefunden!")
        print(f"   Stelle sicher, dass du dich im richtigen Ordner befindest.")
        return 1
    except json.JSONDecodeError as e:
        print(f"[ERROR] ERROR: Ungültiges JSON: {e}")
        return 1

    print(f"[OK] Flow geladen ({len(flow_data)} Nodes)")
    print()

    # Apply Patches
    print("[+] Wende Patches an...")
    print()
    patched_flow = patch_flow(flow_data)
    print()

    # Save Patched Flow
    print(f"[SAVE] Speichere gepatchten Flow: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(patched_flow, f, indent=4, ensure_ascii=False)

    print()
    print("=" * 50)
    print("[OK] Patch erfolgreich!")
    print("=" * 50)
    print()
    print("[>] Nächste Schritte:")
    print("1. Öffne Node-RED")
    print("2. Menu -> Import")
    print(f"3. Wähle: {OUTPUT_FILE}")
    print("4. Deploy")
    print()
    print("[BUG] Bugfixes:")
    print("  - Math.round() statt floor()")
    print("  - API-Call Validierung (403 Prevention)")
    print("  - RBE-Filter für Dynamic Limit")
    print("  - Hysterese 3 Min / 1A Schwelle")
    print("  - Debug-Logging")
    print()

    return 0


if __name__ == '__main__':
    exit(main())
