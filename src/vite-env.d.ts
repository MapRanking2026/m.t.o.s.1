/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_SUPABASE_URL?: string;
  readonly VITE_SUPABASE_ANON_KEY?: string;
  readonly VITE_DEMO_TENANT_USER_ID_ADMIN?: string;
  readonly VITE_DEMO_TENANT_USER_ID_AM1?: string;
  readonly VITE_DEMO_TENANT_USER_ID_AM2?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
