# Common Mistakes Test Suite

> Diese Tests dokumentieren häufige Fehler und deren korrekte Lösungen
> Basierend auf realen Fehlern von OpenClaw und anderen Agenten

import pytest
import requests
import os
import re

# API Konfiguration
API_KEY = os.getenv("LEMLIST_API_KEY", "test-key")
BASE_URL = "https://api.lemlist.com/api"
HEADERS = {"Content-Type": "application/json"}

def get_auth():
    """Basic Auth mit leerem Username"""
    return ("", API_KEY)

class TestCommonMistakes:
    """Test-Klasse für häufige Fehler"""
    
    def test_01_grep_p_not_portable(self):
        """
        FEHLER: grep -P verwenden
        Dies funktioniert nicht auf allen Systemen (z.B. macOS, Alpine Linux)
        """
        # Falscher Code (nicht portabel):
        # result = os.popen("echo '{{test}}' | grep -oP '\{\{[^}]+\}\'").read()
        
        # Richtiger Code (portabel):
        text = "{{variable}}"
        result = re.findall(r'\{\{[^}]+\}\}', text)
        
        assert result == ["{{variable}}"]
        print("✅ Lösung: Verwende Python regex (re.findall) statt grep -P")
    
    def test_02_contactId_lookup_broken(self):
        """
        FEHLER: /leads?contactId=... verwenden
        Dieser Endpunkt funktioniert nicht wie erwartet
        """
        # Falscher Versuch:
        # response = requests.get(f"{BASE_URL}/leads?contactId=ctc_xxx", auth=get_auth())
        # -> Gibt Fehler oder ungültige Antwort
        
        # Richtiger Weg: Campaign-Lead Endpunkt nutzen
        # 1. Lead-ID aus Campaign holen
        # 2. Einzelnen Lead abfragen
        
        print("✅ Lösung: Nutze /campaigns/{id}/leads/{leadId} statt contactId lookup")
        assert True  # Dokumentationstest
    
    def test_03_lead_variables_wrong_endpoint(self):
        """
        FEHLER: /leads/{id}/variables verwenden
        Diese Endpunkte sind BROKEN
        """
        # Falscher Versuch:
        # response = requests.post(
        #     f"{BASE_URL}/leads/lea_xxx/variables",
        #     json={"var": "value"},
        #     auth=get_auth()
        # )
        # -> {"error": "Variables not found"}
        
        # Richtiger Weg: Campaign-Lead PATCH
        # PATCH /campaigns/{campaignId}/leads/{leadId}
        # Body: {"variables": {"var": "value"}}
        
        print("✅ Lösung: Nutze PATCH /campaigns/{id}/leads/{id} mit variables im Body")
        assert True  # Dokumentationstest
    
    def test_04_campaign_delete_not_supported(self):
        """
        FEHLER: DELETE /campaigns/{id} versuchen
        Diese Methode gibt 405 Method Not Allowed
        """
        # Falscher Versuch:
        # response = requests.delete(f"{BASE_URL}/campaigns/cam_xxx", auth=get_auth())
        # -> 405 Method Not Allowed
        
        # Richtiger Weg: Archivieren statt löschen
        # PATCH /campaigns/{id}
        # Body: {"archived": true}
        
        print("✅ Lösung: Nutze PATCH mit {\"archived\": true} statt DELETE")
        assert True  # Dokumentationstest
    
    def test_05_lead_list_only_ids(self):
        """
        FEHLER: Erwarten dass /campaigns/{id}/leads vollständige Daten gibt
        Dieser Endpunkt gibt nur _id, state, contactId zurück
        """
        # Falscher Versuch:
        # response = requests.get(f"{BASE_URL}/campaigns/{id}/leads", auth=get_auth())
        # leads = response.json()
        # email = leads[0]["email"]  # -> KeyError! Nicht vorhanden
        
        # Richtiger Weg:
        # 1. Lead-IDs holen
        # 2. Jeden Lead einzeln abfragen für vollständige Daten
        
        print("✅ Lösung: /leads gibt nur IDs -> Einzelabfrage nötig für Details")
        assert True  # Dokumentationstest
    
    def test_06_patch_response_string_bug(self):
        """
        BEKANNTER BUG: PATCH gibt variables als String "[object Object]" zurück
        Dies ist ein API-Bug auf Lemlist-Seite
        """
        # Problem:
        # PATCH Response enthält:
        # {"variables": "[object Object]"}  # String statt Objekt!
        
        # Workaround:
        # PATCH ausführen, dann GET für Verifikation
        
        print("✅ Workaround: PATCH funktioniert, aber Verifikation via GET nötig")
        assert True  # Dokumentationstest


class TestCorrectWorkflows:
    """Korrekte Workflows als positive Beispiele"""
    
    def test_correct_lead_variable_update(self):
        """
        KORREKT: Lead-Variable aktualisieren
        """
        workflow = """
        1. Campaign ID kennen (z.B. cam_xxx)
        2. Lead ID kennen (z.B. lea_xxx)
        3. PATCH /campaigns/{campaignId}/leads/{leadId}
           Body: {"variables": {"key": "value"}}
        4. Verifikation: GET /campaigns/{campaignId}/leads/{leadId}
        """
        print(workflow)
        assert True
    
    def test_correct_lead_detail_fetch(self):
        """
        KORREKT: Lead-Details mit Variablen abrufen
        """
        workflow = """
        1. GET /campaigns/{campaignId}/leads
           -> Liste mit Lead-IDs
        2. Für jeden Lead:
           GET /campaigns/{campaignId}/leads/{leadId}
           -> Vollständige Daten inkl. Variablen
        """
        print(workflow)
        assert True
    
    def test_correct_campaign_archive(self):
        """
        KORREKT: Campaign archivieren
        """
        workflow = """
        PATCH /campaigns/{campaignId}
        Body: {"archived": true}
        """
        print(workflow)
        assert True


if __name__ == "__main__":
    print("=" * 60)
    print("COMMON MISTAKES TEST SUITE")
    print("=" * 60)
    print()
    print("Diese Tests dokumentieren häufige Fehler und deren Lösungen.")
    print("Keine echten API-Calls - nur Dokumentation und Education.")
    print()
    
    # Alle Tests ausführen
    test_class = TestCommonMistakes()
    for method in dir(test_class):
        if method.startswith("test_"):
            print(f"\n--- {method} ---")
            getattr(test_class, method)()
    
    print("\n" + "=" * 60)
    print("ALLE TESTS BESTANDEN (Dokumentation)")
    print("=" * 60)
