"""
Script to set up Supabase tables with schema and sample data.
Run this once to initialize the database.
Uses requests library for REST API calls.
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseRest:
    """Simple Supabase REST client for migration."""
    
    def __init__(self, url: str, key: str):
        self.rest_url = f"{url}/rest/v1"
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def select(self, table: str):
        """Select all from table."""
        response = requests.get(f"{self.rest_url}/{table}?select=*", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def insert(self, table: str, data: dict):
        """Insert a row."""
        response = requests.post(f"{self.rest_url}/{table}", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def count(self, table: str):
        """Count rows in table."""
        headers = {**self.headers, "Prefer": "count=exact"}
        response = requests.head(f"{self.rest_url}/{table}?select=*", headers=headers)
        return int(response.headers.get("content-range", "0/0").split("/")[-1] or 0)

def run_migration():
    """Execute SQL migration to create tables and insert sample data."""
    
    # Get Supabase credentials
    url = os.getenv("DB_URL")
    service_role_key = os.getenv("SERVICE_ROLE_KEY")
    
    if not url or not service_role_key:
        print("❌ Error: DB_URL and SERVICE_ROLE_KEY must be set in .env file")
        sys.exit(1)
    
    print(f"🔌 Connecting to Supabase at {url[:30]}...")
    
    try:
        # Create Supabase REST client
        supabase = SupabaseRest(url, service_role_key)
        
        print("\n📊 Checking existing data...")
        
        # Check if tables already have data
        try:
            drugs_count = supabase.count("drugs")
            encounters_count = supabase.count("encounters")
            
            print(f"   • drugs table: {drugs_count} rows")
            print(f"   • encounters table: {encounters_count} rows")
            
            if drugs_count > 0 or encounters_count > 0:
                print("\n⚠️  Tables already contain data.")
                response = input("   Do you want to proceed? This may duplicate data. (y/N): ")
                if response.lower() != 'y':
                    print("❌ Migration cancelled.")
                    return
        except Exception as e:
            print(f"   Tables don't exist yet (this is normal for first run)")
        
        print("\n📝 Note: Table creation and RLS policies must be run in Supabase SQL Editor.")
        print("   The schema file is located at: Chat/data/supabase_schema.sql")
        print("   Please run the CREATE TABLE and RLS policy statements there first.\n")
        
        # Insert sample drugs data
        print("💊 Inserting drugs data...")
        drugs_data = [
            {
                "name": "Oxycodone",
                "common_name": "Oxy, Percs, Roxy",
                "category": "Opioid",
                "effects": "Pain relief, euphoria, drowsiness, respiratory depression",
                "risks": "High addiction potential, overdose risk, respiratory failure, constipation",
                "treatment": "Medically assisted treatment (MAT) with buprenorphine or methadone, counseling, naloxone for overdose"
            },
            {
                "name": "Fentanyl",
                "common_name": "Duragesic, Actiq, China White",
                "category": "Synthetic Opioid",
                "effects": "Extreme pain relief, euphoria, sedation, respiratory depression",
                "risks": "Extremely high overdose risk (50-100x stronger than morphine), respiratory failure, death",
                "treatment": "Immediate naloxone administration, MAT with buprenorphine/methadone, intensive counseling, harm reduction strategies"
            },
            {
                "name": "Cocaine",
                "common_name": "Coke, Blow, Snow, Crack",
                "category": "Stimulant",
                "effects": "Increased energy, euphoria, alertness, elevated heart rate and blood pressure",
                "risks": "Heart attack, stroke, seizures, paranoia, addiction, nasal damage (if snorted)",
                "treatment": "Behavioral therapy (CBT, contingency management), support groups, medication for co-occurring conditions"
            },
            {
                "name": "Methamphetamine",
                "common_name": "Meth, Crystal, Ice, Speed",
                "category": "Stimulant",
                "effects": "Intense euphoria, increased energy, decreased appetite, hyperfocus",
                "risks": "Severe dental damage, psychosis, heart problems, stroke, cognitive decline, addiction",
                "treatment": "Behavioral therapy (CBT, Matrix Model), contingency management, support groups, dental care"
            },
            {
                "name": "Heroin",
                "common_name": "Smack, Dope, H, Black Tar",
                "category": "Opioid",
                "effects": "Euphoria, pain relief, sedation, respiratory depression",
                "risks": "High addiction risk, overdose, infectious diseases (HIV, hepatitis), collapsed veins",
                "treatment": "MAT with buprenorphine/methadone/naltrexone, counseling, naloxone for overdose, harm reduction"
            },
            {
                "name": "Cannabis",
                "common_name": "Marijuana, Weed, Pot, THC",
                "category": "Cannabinoid",
                "effects": "Relaxation, altered perception, increased appetite, reduced anxiety (or increased in some)",
                "risks": "Impaired memory and learning, respiratory issues (if smoked), potential for psychological dependence",
                "treatment": "Counseling, behavioral therapy (if problematic use), support groups, addressing underlying mental health"
            },
            {
                "name": "Alcohol",
                "common_name": "Booze, Liquor, Beer, Wine",
                "category": "Depressant",
                "effects": "Relaxation, lowered inhibitions, impaired judgment and coordination",
                "risks": "Liver disease, addiction, accidents, withdrawal seizures, cardiovascular problems",
                "treatment": "Detoxification (with medical supervision), counseling, medications (disulfiram, naltrexone, acamprosate), AA"
            },
            {
                "name": "Benzodiazepines",
                "common_name": "Benzos, Xanax, Valium, Ativan",
                "category": "Sedative",
                "effects": "Anxiety relief, sedation, muscle relaxation, amnesia",
                "risks": "High addiction potential, dangerous withdrawal (seizures), respiratory depression when combined with opioids",
                "treatment": "Gradual tapering under medical supervision, counseling, addressing underlying anxiety disorders"
            }
        ]
        
        inserted_drugs = 0
        for drug in drugs_data:
            try:
                result = supabase.insert("drugs", drug)
                inserted_drugs += 1
                print(f"   ✓ Inserted: {drug['name']}")
            except Exception as e:
                if "duplicate" in str(e).lower() or "unique" in str(e).lower() or "23505" in str(e):
                    print(f"   ⊗ Skipped (already exists): {drug['name']}")
                else:
                    print(f"   ✗ Error inserting {drug['name']}: {e}")
        
        print(f"\n   Total drugs inserted: {inserted_drugs}/{len(drugs_data)}")
        
        # Insert sample encounters data
        print("\n📋 Inserting encounter history data...")
        encounters_data = [
            {"user_id": "user_001", "encounter_date": "2024-01-15 10:30:00", "substance": "Oxycodone", "encounter_type": "relapse", "notes": "Used after 30 days clean. Felt overwhelmed by stress at work.", "days_clean": 0, "support_session": False, "medication_prescribed": None},
            {"user_id": "user_001", "encounter_date": "2024-01-20 14:00:00", "substance": "Oxycodone", "encounter_type": "cravings", "notes": "Strong cravings today but did not use. Reached out to sponsor.", "days_clean": 5, "support_session": True, "medication_prescribed": "Buprenorphine"},
            {"user_id": "user_001", "encounter_date": "2024-01-25 09:00:00", "substance": None, "encounter_type": "support_session", "notes": "Group therapy session. Discussed coping strategies.", "days_clean": 10, "support_session": True, "medication_prescribed": "Buprenorphine"},
            {"user_id": "user_001", "encounter_date": "2024-02-01 11:30:00", "substance": None, "encounter_type": "milestone", "notes": "Reached 17 days clean. Feeling hopeful.", "days_clean": 17, "support_session": False, "medication_prescribed": "Buprenorphine"},
            {"user_id": "user_001", "encounter_date": "2024-02-10 16:00:00", "substance": "Oxycodone", "encounter_type": "near_miss", "notes": "Almost relapsed but called crisis line. Very close call.", "days_clean": 26, "support_session": True, "medication_prescribed": "Buprenorphine"},
            {"user_id": "user_002", "encounter_date": "2024-01-10 18:00:00", "substance": "Methamphetamine", "encounter_type": "relapse", "notes": "Used after 60 days. Triggered by old friends.", "days_clean": 0, "support_session": False, "medication_prescribed": None},
            {"user_id": "user_002", "encounter_date": "2024-01-17 10:00:00", "substance": None, "encounter_type": "support_session", "notes": "Started outpatient program. Feeling motivated.", "days_clean": 7, "support_session": True, "medication_prescribed": None},
            {"user_id": "user_002", "encounter_date": "2024-01-24 14:30:00", "substance": "Methamphetamine", "encounter_type": "cravings", "notes": "Strong cravings at night. Using distraction techniques.", "days_clean": 14, "support_session": False, "medication_prescribed": None},
            {"user_id": "user_002", "encounter_date": "2024-01-31 09:00:00", "substance": None, "encounter_type": "milestone", "notes": "Three weeks clean. Sleeping better now.", "days_clean": 21, "support_session": True, "medication_prescribed": None},
            {"user_id": "user_002", "encounter_date": "2024-02-07 12:00:00", "substance": None, "encounter_type": "support_session", "notes": "Individual counseling. Working on triggers.", "days_clean": 28, "support_session": True, "medication_prescribed": None},
            {"user_id": "user_003", "encounter_date": "2024-01-05 20:00:00", "substance": "Alcohol", "encounter_type": "relapse", "notes": "Drank at social event. Did not plan ahead.", "days_clean": 0, "support_session": False, "medication_prescribed": None},
            {"user_id": "user_003", "encounter_date": "2024-01-12 08:30:00", "substance": None, "encounter_type": "support_session", "notes": "AA meeting. Got a new sponsor.", "days_clean": 7, "support_session": True, "medication_prescribed": "Naltrexone"},
            {"user_id": "user_003", "encounter_date": "2024-01-19 15:00:00", "substance": "Alcohol", "encounter_type": "cravings", "notes": "Cravings after stressful day. Did not drink.", "days_clean": 14, "support_session": False, "medication_prescribed": "Naltrexone"},
            {"user_id": "user_003", "encounter_date": "2024-01-26 11:00:00", "substance": None, "encounter_type": "milestone", "notes": "Three weeks sober. Feeling proud.", "days_clean": 21, "support_session": True, "medication_prescribed": "Naltrexone"},
            {"user_id": "user_003", "encounter_date": "2024-02-02 17:30:00", "substance": None, "encounter_type": "support_session", "notes": "Group therapy. Shared my story.", "days_clean": 28, "support_session": True, "medication_prescribed": "Naltrexone"}
        ]
        
        inserted_encounters = 0
        for encounter in encounters_data:
            try:
                result = supabase.insert("encounters", encounter)
                inserted_encounters += 1
                print(f"   ✓ Inserted: {encounter['user_id']} - {encounter['encounter_type']}")
            except Exception as e:
                print(f"   ✗ Error: {e}")
        
        print(f"\n   Total encounters inserted: {inserted_encounters}/{len(encounters_data)}")
        
        print("\n✅ Migration completed successfully!")
        print("\n📊 Final verification:")
        drugs_final = supabase.select("drugs")
        encounters_final = supabase.select("encounters")
        print(f"   • drugs: {len(drugs_final)} total rows")
        print(f"   • encounters: {len(encounters_final)} total rows")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("   SUPABASE DATABASE MIGRATION")
    print("=" * 60)
    run_migration()
    print("\n" + "=" * 60)
