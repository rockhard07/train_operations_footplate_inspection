-- Database Migration: Add Inspector Tracking to Footplate Inspections
-- Run this SQL in Supabase SQL Editor

-- ============================================================================
-- TABLE CREATION
-- ============================================================================

-- Step 1: Create users table (if not already created by auth)
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL UNIQUE,
  full_name VARCHAR(255),
  role VARCHAR(50) NOT NULL DEFAULT 'manager',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 2: Create employees table
CREATE TABLE IF NOT EXISTS public.employees (
  employee_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  designation VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Create footplate_inspections table
CREATE TABLE IF NOT EXISTS public.footplate_inspections (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  employee_id VARCHAR(50) NOT NULL REFERENCES public.employees(employee_id),
  inspection_date DATE NOT NULL,
  submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Inspector information (who did the inspection)
  inspected_by_user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  inspected_by_name VARCHAR(255),
  inspected_by_role VARCHAR(50),
  
  -- Scores totals
  part_a_total INT DEFAULT 0,
  part_b_total INT DEFAULT 0,
  part_c_total INT DEFAULT 0,
  overall_total INT DEFAULT 0,
  
  -- Observations
  observations TEXT,
  defects_identified TEXT,
  corrective_actions TEXT,
  
  -- Device tracking
  ip_address VARCHAR(50),
  device_info VARCHAR(255),
  
  UNIQUE(employee_id, inspection_date)
);

-- Step 4: Create inspection_scores table
CREATE TABLE IF NOT EXISTS public.inspection_scores (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  inspection_id BIGINT NOT NULL REFERENCES public.footplate_inspections(id) ON DELETE CASCADE,
  part CHAR(1) NOT NULL,
  section VARCHAR(100),
  item_no INT NOT NULL,
  item_text TEXT,
  max_marks INT NOT NULL DEFAULT 1,
  marks_awarded INT NOT NULL DEFAULT 0
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Step 5: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_inspections_by_employee 
ON public.footplate_inspections(employee_id, inspection_date DESC);

CREATE INDEX IF NOT EXISTS idx_inspections_by_inspector 
ON public.footplate_inspections(inspected_by_user_id, inspection_date DESC);

CREATE INDEX IF NOT EXISTS idx_inspections_by_inspector_date 
ON public.footplate_inspections(inspected_by_user_id, submitted_at DESC);

CREATE INDEX IF NOT EXISTS idx_inspections_by_role 
ON public.footplate_inspections(inspected_by_role, submitted_at DESC);

CREATE INDEX IF NOT EXISTS idx_inspection_scores_by_inspection 
ON public.inspection_scores(inspection_id);

CREATE INDEX IF NOT EXISTS idx_inspection_scores_by_part 
ON public.inspection_scores(inspection_id, part);

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS) - Optional
-- ============================================================================

-- Enable RLS on tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.footplate_inspections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.inspection_scores ENABLE ROW LEVEL SECURITY;

-- Allow all authenticated users to read employees
CREATE POLICY "Enable read access for authenticated users on employees"
  ON public.employees
  FOR SELECT
  TO authenticated
  USING (true);

-- Allow authenticated users to read inspections
CREATE POLICY "Enable read access for authenticated users on inspections"
  ON public.footplate_inspections
  FOR SELECT
  TO authenticated
  USING (true);

-- Allow users to insert inspections (created by them)
CREATE POLICY "Enable insert access for authenticated users on inspections"
  ON public.footplate_inspections
  FOR INSERT
  TO authenticated
  WITH CHECK (inspected_by_user_id = auth.uid());

-- Allow reading inspection scores
CREATE POLICY "Enable read access for authenticated users on scores"
  ON public.inspection_scores
  FOR SELECT
  TO authenticated
  USING (true);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify table structure
SELECT 'footplate_inspections columns:' as info;
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'footplate_inspections'
ORDER BY ordinal_position;

SELECT 'inspection_scores columns:' as info;
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'inspection_scores'
ORDER BY ordinal_position;

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Insert sample employees
INSERT INTO public.employees (employee_id, name, designation) VALUES
  ('EMP001', 'Rajesh Kumar', 'Train Driver'),
  ('EMP002', 'Priya Sharma', 'Train Driver'),
  ('EMP003', 'Amit Patel', 'Train Driver')
ON CONFLICT (employee_id) DO NOTHING;

-- ============================================================================
-- AUTO-INSERT TRIGGER (Optional - for auth users)
-- ============================================================================

-- Create trigger to auto-insert users on auth signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name, role)
  VALUES (new.id, new.email, new.user_metadata->>'full_name', 'manager');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- ============================================================================
-- QUERIES FOR EXECUTIVE DASHBOARD
-- ============================================================================

-- Query: Get inspector statistics (last 30 days)
SELECT 
  inspected_by_name,
  inspected_by_role,
  COUNT(*) as total_inspections,
  MAX(submitted_at) as last_inspection_date
FROM public.footplate_inspections
WHERE submitted_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY inspected_by_user_id, inspected_by_name, inspected_by_role
ORDER BY last_inspection_date DESC;

-- Query: Get inspection counts by employee (last 30 days)
SELECT 
  employee_id,
  COUNT(*) as inspection_count,
  AVG(overall_total) as avg_score,
  MAX(submitted_at) as last_inspection
FROM public.footplate_inspections
WHERE submitted_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY employee_id
ORDER BY last_inspection DESC;

-- Query: Get all inspections this month
SELECT 
  id,
  employee_id,
  inspection_date,
  inspected_by_name,
  overall_total
FROM public.footplate_inspections
WHERE EXTRACT(YEAR FROM inspection_date) = EXTRACT(YEAR FROM CURRENT_DATE)
  AND EXTRACT(MONTH FROM inspection_date) = EXTRACT(MONTH FROM CURRENT_DATE)
ORDER BY inspection_date DESC;

-- ============================================================================
-- CLEANUP (if needed)
-- ============================================================================

-- Drop tables (uncomment only if you need to reset)
-- DROP TABLE IF EXISTS public.inspection_scores CASCADE;
-- DROP TABLE IF EXISTS public.footplate_inspections CASCADE;
-- DROP TABLE IF EXISTS public.employees CASCADE;
-- DROP TABLE IF EXISTS public.users CASCADE;

-- ============================================================================
-- End of Migration
-- ============================================================================
