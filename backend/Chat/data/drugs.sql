-- Chat Service - Drugs Database Schema
-- Contains comprehensive drug information for lookup and RAG

CREATE TABLE IF NOT EXISTS drugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    common_name TEXT,
    category TEXT,
    effects TEXT,
    risks TEXT,
    treatment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample drug data
INSERT OR IGNORE INTO drugs (name, common_name, category, effects, risks, treatment) VALUES
('Oxycodone', 'Oxy, OC', 'Opioid', 
 'Pain relief, euphoria, drowsiness, respiratory depression',
 'High addiction potential, overdose risk, respiratory failure, tolerance development',
 'Medication-assisted treatment (methadone, buprenorphine), counseling, behavioral therapy, support groups'),

('Fentanyl', 'Apache, China White', 'Synthetic Opioid',
 'Extreme pain relief, euphoria, sedation, respiratory depression',
 'Extremely high overdose risk, rapid addiction, respiratory arrest, death with small amounts',
 'Naloxone for overdose reversal, MAT with methadone or buprenorphine, intensive counseling, medical supervision'),

('Cocaine', 'Coke, Blow, Snow', 'Stimulant',
 'Increased energy, alertness, confidence, euphoria, increased heart rate',
 'Cardiovascular problems, stroke, seizures, anxiety, paranoia, addiction',
 'Behavioral therapy, cognitive behavioral therapy, contingency management, support groups'),

('Methamphetamine', 'Meth, Crystal, Ice', 'Stimulant',
 'Intense euphoria, increased energy, alertness, decreased appetite',
 'Severe dental problems, skin sores, anxiety, violent behavior, psychosis, neurotoxicity',
 'Behavioral therapy, cognitive behavioral therapy, contingency management, Matrix Model treatment'),

('Heroin', 'Smack, H, Junk', 'Opioid',
 'Intense euphoria, pain relief, drowsiness, sedation',
 'High addiction potential, overdose risk, infectious diseases (HIV, Hepatitis), respiratory depression',
 'Medication-assisted treatment (methadone, buprenorphine, naltrexone), counseling, residential treatment'),

('Cannabis', 'Marijuana, Weed, Pot', 'Cannabinoid',
 'Relaxation, altered perception, increased appetite, pain relief',
 'Impaired memory, coordination issues, potential for psychological dependence, respiratory issues when smoked',
 'Behavioral therapy, cognitive behavioral therapy, motivational enhancement therapy, support groups'),

('Alcohol', 'Booze, Liquor', 'Depressant',
 'Relaxation, reduced inhibitions, impaired judgment, sedation',
 'Liver damage, addiction, withdrawal complications, increased accident risk, long-term health issues',
 'Detoxification, medication (naltrexone, acamprosate, disulfiram), AA/12-step programs, behavioral therapy'),

('Benzodiazepines', 'Benzos, Xanax, Valium', 'Depressant',
 'Anxiety reduction, sedation, muscle relaxation, sleep induction',
 'Physical dependence, dangerous withdrawal, overdose risk (especially with alcohol), cognitive impairment',
 'Gradual tapering under medical supervision, cognitive behavioral therapy, support groups');

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_drug_name ON drugs(name);
CREATE INDEX IF NOT EXISTS idx_drug_category ON drugs(category);
