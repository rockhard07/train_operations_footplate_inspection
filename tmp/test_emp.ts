import { createClient } from '@supabase/supabase-js'; console.log('test')
import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
dotenv.config({ path: '../other_website/.env.local' });
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!);
async function main() {
  const { data } = await supabase.from('employees').select('status, name, employee_id').limit(10);
  console.log(data);
}
main();
