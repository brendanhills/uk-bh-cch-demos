CREATE TABLE ideas (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    submitter VARCHAR(100) NOT NULL CHECK (submitter ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'),
    submission_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    request_type VARCHAR(50),
    business_owner VARCHAR(100),
    roi VARCHAR(255), -- Return on Investment, e.g., 1234567.89 or 99.99 for percentage
    strategic_impact TEXT,
    stage VARCHAR(50) DEFAULT 'Draft', -- e.g., 'Draft', 'Review', 'Approved', 'Implemented'
    pdf_url VARCHAR(255), -- Assuming this stores a URL or path to a PDF
    summary TEXT,
    business_unit VARCHAR(100), -- Corrected spelling from 'buisness_unit'
    impact_area VARCHAR(100),
    urgency SMALLINT CHECK (urgency >= 1 AND urgency <= 5), -- Assuming a rating from 1 (low) to 5 (high)
    proposition_area VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    pr_faq_doc JSONB
);

-- Optional: Add an index for frequently searched columns like submitter or business_owner
CREATE INDEX idx_ideas_submitter ON ideas (submitter);
CREATE INDEX idx_ideas_business_owner ON ideas (business_owner);
CREATE INDEX idx_ideas_stage ON ideas (stage);


-- Table to store the history of status changes for each idea
CREATE TABLE idea_status_history (
    id SERIAL PRIMARY KEY,
    idea_id INTEGER NOT NULL,
    stage VARCHAR(50),
    status_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_idea
        FOREIGN KEY(idea_id)
        REFERENCES ideas(id)
        ON DELETE CASCADE -- If an idea is deleted, its status history will also be deleted
);

CREATE INDEX idx_idea_status_history_idea_id ON idea_status_history (idea_id);

-- Function to insert into idea_status_history
CREATE OR REPLACE FUNCTION log_idea_stage_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the stage has actually changed
    IF NEW.stage IS DISTINCT FROM OLD.stage THEN
        INSERT INTO idea_status_history (idea_id, stage)
        VALUES (NEW.id, NEW.stage);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the function after an update on the ideas table
CREATE TRIGGER ideas_stage_update_trigger
AFTER UPDATE ON ideas
FOR EACH ROW
EXECUTE FUNCTION log_idea_stage_change();

-- Enum type for relationship between ideas
CREATE TYPE relationship_type AS ENUM ('extends', 'duplicate', 'supersedes');

-- Table to store relationships between ideas
CREATE TABLE linked_ideas (
    id SERIAL PRIMARY KEY,
    idea_id_from INTEGER NOT NULL,
    idea_id_to INTEGER NOT NULL,
    relationship relationship_type NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_idea_from
        FOREIGN KEY(idea_id_from)
        REFERENCES ideas(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_idea_to
        FOREIGN KEY(idea_id_to)
        REFERENCES ideas(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_linked_ideas_idea_id_from ON linked_ideas (idea_id_from);
CREATE INDEX idx_linked_ideas_idea_id_to ON linked_ideas (idea_id_to);