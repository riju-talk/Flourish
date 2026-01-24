/// <reference types="vite/client" />
/// <reference path="./types/speech.d.ts" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
