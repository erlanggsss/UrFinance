-- ========================================
-- Supabase Permission Fix Script
-- ========================================
-- Run this in Supabase SQL Editor to fix common issues
-- This ensures the bot can access all tables

-- ========================================
-- 1. Disable Row Level Security (for bot access)
-- ========================================
ALTER TABLE invoices DISABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE spending_limits DISABLE ROW LEVEL SECURITY;
ALTER TABLE spending_limits_v2 DISABLE ROW LEVEL SECURITY;
ALTER TABLE platform_users DISABLE ROW LEVEL SECURITY;
ALTER TABLE "user" DISABLE ROW LEVEL SECURITY;
ALTER TABLE premium_data DISABLE ROW LEVEL SECURITY;
ALTER TABLE token DISABLE ROW LEVEL SECURITY;

-- ========================================
-- 2. Grant All Permissions
-- ========================================
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- For anon user (if needed for public API access)
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon;

-- For authenticated users
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ========================================
-- 3. Verify Tables Exist
-- ========================================
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE columns.table_name = tables.table_name) as column_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- ========================================
-- 4. Test Insert (to verify permissions work)
-- ========================================
DO $$
DECLARE
    test_invoice_id BIGINT;
BEGIN
    -- Test invoice insert
    INSERT INTO invoices (shop_name, invoice_date, total_amount, transaction_type, image_path)
    VALUES ('Permission Test Shop', CURRENT_DATE, 99999, 'retail', '/test/permission_test.jpg')
    RETURNING id INTO test_invoice_id;
    
    RAISE NOTICE '✅ Invoice insert successful! ID: %', test_invoice_id;
    
    -- Test invoice_items insert
    INSERT INTO invoice_items (invoice_id, item_name, quantity, unit_price, total_price)
    VALUES (test_invoice_id, 'Test Item', 1, 99999, 99999);
    
    RAISE NOTICE '✅ Invoice items insert successful!';
    
    -- Clean up test data
    DELETE FROM invoice_items WHERE invoice_id = test_invoice_id;
    DELETE FROM invoices WHERE id = test_invoice_id;
    
    RAISE NOTICE '✅ Cleanup successful!';
    RAISE NOTICE '🎉 All permissions are working correctly!';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ Error: %', SQLERRM;
    RAISE NOTICE '⚠️  Please check table permissions and RLS policies';
END $$;

-- ========================================
-- 5. Check RLS Status
-- ========================================
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- ========================================
-- Success Message
-- ========================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ Permission fix script completed!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Check the output above for any errors';
    RAISE NOTICE '2. Verify all tables have RLS disabled (rls_enabled = false)';
    RAISE NOTICE '3. Test your bot by uploading an invoice';
    RAISE NOTICE '========================================';
END $$;
