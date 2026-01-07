-- ============================================
-- Supabase PostgreSQL Schema for Drug Support System
-- ============================================
-- This schema replaces the SQLite databases with cloud-based Supabase PostgreSQL.
-- Run this in Supabase SQL Editor to create tables with sample data.
-- ============================================

-- ============================================
-- TABLE: drugs
-- Stores information about various substances
-- ============================================
CREATE TABLE IF NOT EXISTS drugs (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    common_name TEXT,
    category TEXT,
    effects TEXT,
    risks TEXT,
    treatment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_drug_name ON drugs(name);
CREATE INDEX IF NOT EXISTS idx_drug_category ON drugs(category);

-- Enable Row Level Security
ALTER TABLE drugs ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Allow public read access (for lookups)
CREATE POLICY "Allow public read access on drugs" 
ON drugs FOR SELECT 
USING (true);

-- RLS Policy: Allow service role full access (for backend CRUD)
CREATE POLICY "Allow service role full access on drugs" 
ON drugs FOR ALL 
USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- TABLE: encounters
-- Stores user encounter history and tracking
-- ============================================
CREATE TABLE IF NOT EXISTS encounters (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    encounter_date TIMESTAMP DEFAULT NOW(),
    substance TEXT,
    encounter_type TEXT,
    notes TEXT,
    days_clean INTEGER,
    support_session BOOLEAN DEFAULT FALSE,
    medication_prescribed TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_user_id ON encounters(user_id);
CREATE INDEX IF NOT EXISTS idx_encounter_date ON encounters(encounter_date);

-- Enable Row Level Security
ALTER TABLE encounters ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can read their own encounters
CREATE POLICY "Users can read own encounters" 
ON encounters FOR SELECT 
USING (auth.jwt() ->> 'user_id' = user_id);

-- RLS Policy: Allow service role full access (for backend operations)
CREATE POLICY "Allow service role full access on encounters" 
ON encounters FOR ALL 
USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- SAMPLE DATA: drugs
-- ============================================
INSERT INTO drugs (name, common_name, category, effects, risks, treatment) VALUES
('Oxycodone', 'Oxy, Percs, Roxy', 'Opioid', 
'Pain relief, euphoria, drowsiness, respiratory depression', 
'High addiction potential, overdose risk, respiratory failure, constipation', 
'Medically assisted treatment (MAT) with buprenorphine or methadone, counseling, naloxone for overdose'),

('Fentanyl', 'Duragesic, Actiq, China White', 'Synthetic Opioid', 
'Extreme pain relief, euphoria, sedation, respiratory depression', 
'Extremely high overdose risk (50-100x stronger than morphine), respiratory failure, death', 
'Immediate naloxone administration, MAT with buprenorphine/methadone, intensive counseling, harm reduction strategies'),

('Cocaine', 'Coke, Blow, Snow, Crack', 'Stimulant', 
'Increased energy, euphoria, alertness, elevated heart rate and blood pressure', 
'Heart attack, stroke, seizures, paranoia, addiction, nasal damage (if snorted)', 
'Behavioral therapy (CBT, contingency management), support groups, medication for co-occurring conditions'),

('Methamphetamine', 'Meth, Crystal, Ice, Speed', 'Stimulant', 
'Intense euphoria, increased energy, decreased appetite, hyperfocus', 
'Severe dental damage, psychosis, heart problems, stroke, cognitive decline, addiction', 
'Behavioral therapy (CBT, Matrix Model), contingency management, support groups, dental care'),

('Heroin', 'Smack, Dope, H, Black Tar', 'Opioid', 
'Euphoria, pain relief, sedation, respiratory depression', 
'High addiction risk, overdose, infectious diseases (HIV, hepatitis), collapsed veins', 
'MAT with buprenorphine/methadone/naltrexone, counseling, naloxone for overdose, harm reduction'),

('Cannabis', 'Marijuana, Weed, Pot, THC', 'Cannabinoid', 
'Relaxation, altered perception, increased appetite, reduced anxiety (or increased in some)', 
'Impaired memory and learning, respiratory issues (if smoked), potential for psychological dependence', 
'Counseling, behavioral therapy (if problematic use), support groups, addressing underlying mental health'),

('Alcohol', 'Booze, Liquor, Beer, Wine', 'Depressant', 
'Relaxation, lowered inhibitions, impaired judgment and coordination', 
'Liver disease, addiction, accidents, withdrawal seizures, cardiovascular problems', 
'Detoxification (with medical supervision), counseling, medications (disulfiram, naltrexone, acamprosate), AA'),

('Benzodiazepines', 'Benzos, Xanax, Valium, Ativan', 'Sedative', 
'Anxiety relief, sedation, muscle relaxation, amnesia', 
'High addiction potential, dangerous withdrawal (seizures), respiratory depression when combined with opioids', 
'Gradual tapering under medical supervision, counseling, addressing underlying anxiety disorders')

ON CONFLICT (name) DO NOTHING;

-- ============================================
-- SAMPLE DATA: encounters
-- ============================================
INSERT INTO encounters (user_id, encounter_date, substance, encounter_type, notes, days_clean, support_session, medication_prescribed) VALUES
('user_001', '2024-01-15 10:30:00', 'Oxycodone', 'relapse', 'Used after 30 days clean. Felt overwhelmed by stress at work.', 0, false, NULL),
('user_001', '2024-01-20 14:00:00', 'Oxycodone', 'cravings', 'Strong cravings today but did not use. Reached out to sponsor.', 5, true, 'Buprenorphine'),
('user_001', '2024-01-25 09:00:00', NULL, 'support_session', 'Group therapy session. Discussed coping strategies.', 10, true, 'Buprenorphine'),
('user_001', '2024-02-01 11:30:00', NULL, 'milestone', 'Reached 17 days clean. Feeling hopeful.', 17, false, 'Buprenorphine'),
('user_001', '2024-02-10 16:00:00', 'Oxycodone', 'near_miss', 'Almost relapsed but called crisis line. Very close call.', 26, true, 'Buprenorphine'),

('user_002', '2024-01-10 18:00:00', 'Methamphetamine', 'relapse', 'Used after 60 days. Triggered by old friends.', 0, false, NULL),
('user_002', '2024-01-17 10:00:00', NULL, 'support_session', 'Started outpatient program. Feeling motivated.', 7, true, NULL),
('user_002', '2024-01-24 14:30:00', 'Methamphetamine', 'cravings', 'Strong cravings at night. Using distraction techniques.', 14, false, NULL),
('user_002', '2024-01-31 09:00:00', NULL, 'milestone', 'Three weeks clean. Sleeping better now.', 21, true, NULL),
('user_002', '2024-02-07 12:00:00', NULL, 'support_session', 'Individual counseling. Working on triggers.', 28, true, NULL),

('user_003', '2024-01-05 20:00:00', 'Alcohol', 'relapse', 'Drank at social event. Did not plan ahead.', 0, false, NULL),
('user_003', '2024-01-12 08:30:00', NULL, 'support_session', 'AA meeting. Got a new sponsor.', 7, true, 'Naltrexone'),
('user_003', '2024-01-19 15:00:00', 'Alcohol', 'cravings', 'Cravings after stressful day. Did not drink.', 14, false, 'Naltrexone'),
('user_003', '2024-01-26 11:00:00', NULL, 'milestone', 'Three weeks sober. Feeling proud.', 21, true, 'Naltrexone'),
('user_003', '2024-02-02 17:30:00', NULL, 'support_session', 'Group therapy. Shared my story.', 28, true, 'Naltrexone');

-- ============================================
-- VERIFICATION QUERIES
-- Run these to verify the tables were created successfully
-- ============================================
-- SELECT COUNT(*) FROM drugs;
-- SELECT COUNT(*) FROM encounters;
-- SELECT * FROM drugs ORDER BY name;
-- SELECT * FROM encounters ORDER BY encounter_date DESC LIMIT 10;
