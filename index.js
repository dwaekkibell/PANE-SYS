import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ksymuaamkjzoehupdcdp.supabase.co'
const supabaseKey = 'sb_publishable_Mdq1uUvlrQikfraqcZ7vDw_dhGeeBW2'
const supabase = createClient(supabaseUrl, supabaseKey)

async function probarConexion() {
  const { data, error } = await supabase
    .from('producto')
    .select('*')

  if (error) {
    console.error('Error al consultar Supabase:', error.message)
  } else {
    console.log('¡Conexión exitosa! Datos:', data)
  }
}

probarConexion()