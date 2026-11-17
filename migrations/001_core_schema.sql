-- Core multi-tenant schema for Real Estate Automation OS
-- Use with Supabase or plain PostgreSQL + RLS

-- Organizations (tenants)
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Membership (links auth.users to organizations)
CREATE TABLE IF NOT EXISTS organization_members (
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL, -- references auth.users(id) in Supabase
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (organization_id, user_id)
);

-- Agencies (business profile)
CREATE TABLE IF NOT EXISTS agencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    website TEXT,
    location TEXT,
    team_size INTEGER,
    specialization TEXT,
    existing_crm TEXT,
    communication_channels JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agency Audits
CREATE TABLE IF NOT EXISTS agency_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    lead_sources JSONB,
    processes JSONB, -- qualification, follow-up, viewings, etc.
    bottlenecks TEXT[],
    objectives TEXT,
    raw_input JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS (example - full policies to be added)
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE agencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE agency_audits ENABLE ROW LEVEL SECURITY;

-- Force RLS
ALTER TABLE agencies FORCE ROW LEVEL SECURITY;
ALTER TABLE agency_audits FORCE ROW LEVEL SECURITY;

-- Helper function (Supabase style)
CREATE OR REPLACE FUNCTION is_organization_member(org_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT EXISTS (
    SELECT 1 FROM organization_members
    WHERE organization_id = org_id AND user_id = auth.uid()
  );
$$;

-- Basic policies (expand for all operations)
CREATE POLICY "Members can view own organization agencies"
  ON agencies FOR SELECT
  USING (is_organization_member(organization_id));

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agencies_org ON agencies(organization_id);
CREATE INDEX IF NOT EXISTS idx_audits_org ON agency_audits(organization_id);
CREATE INDEX IF NOT EXISTS idx_members_user ON organization_members(user_id);
