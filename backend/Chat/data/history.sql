-- Chat Service - User History Database Schema
-- Contains medical encounter history for personalized assistance

CREATE TABLE IF NOT EXISTS encounters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    encounter_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    substance TEXT,
    encounter_type TEXT,
    notes TEXT,
    days_clean INTEGER,
    support_session BOOLEAN DEFAULT 0,
    medication_prescribed TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample user history data
INSERT OR IGNORE INTO encounters (user_id, encounter_date, substance, encounter_type, notes, days_clean, support_session, medication_prescribed) VALUES
('user_001', '2025-12-01', 'Oxycodone', 'Initial Assessment', 'Patient seeking help for opioid addiction. Started using 2 years ago after surgery.', 0, 1, NULL),
('user_001', '2025-12-08', 'Oxycodone', 'Treatment Plan', 'Started MAT with buprenorphine. Weekly counseling sessions scheduled.', 7, 1, 'Buprenorphine 8mg'),
('user_001', '2025-12-15', 'Oxycodone', 'Follow-up', 'Patient responding well to treatment. Cravings manageable. Attending support group.', 14, 1, 'Buprenorphine 8mg'),
('user_001', '2025-12-22', 'Oxycodone', 'Progress Check', 'Continued progress. Patient reports improved mood and sleep. No relapse incidents.', 21, 1, 'Buprenorphine 8mg'),
('user_001', '2026-01-05', 'Oxycodone', 'Monthly Review', '35 days clean. Patient developing healthy coping mechanisms. Family therapy added.', 35, 1, 'Buprenorphine 6mg'),

('user_002', '2025-11-15', 'Methamphetamine', 'Crisis Intervention', 'Emergency visit. Patient in active use, seeking immediate help.', 0, 1, NULL),
('user_002', '2025-11-20', 'Methamphetamine', 'Detox', 'Completed 5-day detox program. Started behavioral therapy.', 5, 1, NULL),
('user_002', '2025-12-01', 'Methamphetamine', 'Relapse', 'Patient relapsed after 11 days. Discussing triggers and coping strategies.', 0, 1, NULL),
('user_002', '2025-12-10', 'Methamphetamine', 'Recovery Restart', 'Patient recommitted to recovery. Increased therapy frequency to twice weekly.', 9, 1, NULL),
('user_002', '2026-01-01', 'Methamphetamine', 'Progress Update', '22 days clean. Patient participating in Matrix Model program. Positive outlook.', 22, 1, NULL),

('user_003', '2025-10-20', 'Alcohol', 'Assessment', 'Patient drinking heavily for 10 years. Ready to quit. No prior treatment attempts.', 0, 1, NULL),
('user_003', '2025-10-25', 'Alcohol', 'Medical Detox', 'Completed supervised medical detox. Started naltrexone.', 5, 1, 'Naltrexone 50mg'),
('user_003', '2025-11-10', 'Alcohol', 'Outpatient Program', '16 days sober. Attending AA meetings. Family supportive.', 16, 1, 'Naltrexone 50mg'),
('user_003', '2025-12-01', 'Alcohol', 'Milestone', '37 days sober. Patient reports improved health, better sleep, weight loss.', 37, 1, 'Naltrexone 50mg'),
('user_003', '2026-01-02', 'Alcohol', '2-Month Check', '69 days sober. Patient thriving. Continuing medication and AA attendance.', 69, 1, 'Naltrexone 50mg');

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_id ON encounters(user_id);
CREATE INDEX IF NOT EXISTS idx_encounter_date ON encounters(encounter_date);
