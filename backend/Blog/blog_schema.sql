-- Blog Posts Table
-- Stores blog posts with metadata

CREATE TABLE IF NOT EXISTS blog_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    author TEXT NOT NULL,
    category TEXT NOT NULL,
    tags TEXT[], -- Array of tags
    image_url TEXT,
    published BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_blog_posts_created_at ON blog_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_blog_posts_category ON blog_posts(category);
CREATE INDEX IF NOT EXISTS idx_blog_posts_published ON blog_posts(published);
CREATE INDEX IF NOT EXISTS idx_blog_posts_author ON blog_posts(author);

-- Create a full text search index for title and content
CREATE INDEX IF NOT EXISTS idx_blog_posts_search ON blog_posts USING gin(to_tsvector('english', title || ' ' || content));

-- Insert some sample blog posts
INSERT INTO blog_posts (title, content, excerpt, author, category, tags, published) VALUES
(
    'Understanding Substance Use Recovery',
    'Recovery from substance use is a journey that requires patience, support, and understanding. In this comprehensive guide, we explore the various stages of recovery and what to expect along the way.\n\nRecovery is not a linear process. It involves ups and downs, victories and setbacks. Understanding this helps set realistic expectations and reduces the stigma around relapse.\n\nKey components of successful recovery include:\n- Building a strong support network\n- Developing healthy coping mechanisms\n- Addressing underlying mental health issues\n- Creating structure and routine\n- Setting achievable goals\n\nRemember, recovery is possible and help is always available.',
    'A comprehensive guide to understanding the recovery journey from substance use.',
    'Recovery Team',
    'Recovery',
    ARRAY['recovery', 'support', 'health', 'wellness'],
    true
),
(
    'The Science Behind Addiction',
    'Addiction is a complex brain disorder that affects millions of people worldwide. Understanding the neuroscience behind addiction can help reduce stigma and improve treatment approaches.\n\nAddiction involves changes in the brain''s reward system, particularly affecting neurotransmitters like dopamine. These changes make it difficult to experience pleasure from normal activities and increase cravings for the substance.\n\nImportant facts about addiction:\n- Addiction is a medical condition, not a moral failing\n- It affects brain chemistry and decision-making\n- Treatment is effective and recovery is possible\n- Early intervention improves outcomes\n- Support from family and community is crucial\n\nModern neuroscience has revolutionized our understanding of addiction, leading to more effective, evidence-based treatments.',
    'Learn about the neurological basis of addiction and how it affects the brain.',
    'Dr. Sarah Johnson',
    'Education',
    ARRAY['addiction', 'neuroscience', 'education', 'brain'],
    true
),
(
    'Supporting a Loved One in Recovery',
    'When someone you care about is struggling with substance use, knowing how to help can be challenging. This guide provides practical tips for supporting your loved one while maintaining your own wellbeing.\n\nEffective support strategies:\n\n1. Educate Yourself: Learn about addiction and recovery to better understand what your loved one is experiencing.\n\n2. Communicate with Compassion: Use non-judgmental language and express your concerns with love.\n\n3. Set Healthy Boundaries: Support doesn''t mean enabling. It''s okay to set limits.\n\n4. Encourage Professional Help: Suggest therapy, support groups, or treatment programs.\n\n5. Take Care of Yourself: You can''t pour from an empty cup. Seek support for yourself too.\n\nRemember, recovery is their journey, but your support can make a significant difference.',
    'Practical advice for family members and friends supporting someone in recovery.',
    'Lisa Martinez',
    'Support',
    ARRAY['family', 'support', 'relationships', 'caregiving'],
    true
),
(
    'Harm Reduction: A Compassionate Approach',
    'Harm reduction is a set of practical strategies aimed at reducing negative consequences associated with drug use. This approach recognizes that while abstinence may be the ultimate goal for some, it may not be immediately achievable for everyone.\n\nCore principles of harm reduction:\n- Meeting people where they are without judgment\n- Respecting individual autonomy and dignity\n- Prioritizing immediate safety and health\n- Providing evidence-based interventions\n- Recognizing substance use as a complex, multi-faceted issue\n\nExamples of harm reduction strategies:\n- Needle exchange programs\n- Supervised consumption sites\n- Naloxone distribution\n- Drug checking services\n- Safe use education\n\nHarm reduction saves lives and creates pathways to recovery.',
    'Understanding harm reduction principles and their role in public health.',
    'Public Health Team',
    'Harm Reduction',
    ARRAY['harm reduction', 'public health', 'safety', 'prevention'],
    true
),
(
    'Mental Health and Substance Use',
    'The relationship between mental health and substance use is complex and bidirectional. Many people with substance use disorders also experience mental health challenges, and vice versa.\n\nCommon co-occurring conditions:\n- Depression\n- Anxiety disorders\n- PTSD\n- Bipolar disorder\n- ADHD\n\nIntegrated treatment is essential: Addressing both mental health and substance use simultaneously leads to better outcomes than treating them separately.\n\nSigns you may need integrated treatment:\n- Using substances to cope with difficult emotions\n- Mental health symptoms that worsen with substance use\n- Difficulty maintaining abstinence due to mental health challenges\n- History of trauma or adverse childhood experiences\n\nIf you''re struggling with both mental health and substance use, know that specialized help is available and recovery is possible.',
    'Exploring the connection between mental health disorders and substance use.',
    'Dr. Michael Chen',
    'Mental Health',
    ARRAY['mental health', 'dual diagnosis', 'therapy', 'treatment'],
    true
);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_blog_posts_updated_at 
    BEFORE UPDATE ON blog_posts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
