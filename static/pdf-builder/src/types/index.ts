// Field Types
export type FieldType =
  | 'text'
  | 'textarea'
  | 'checkbox'
  | 'radio'
  | 'dropdown'
  | 'date'
  | 'signature'
  | 'image'

// Field Definition
export interface Field {
  field_id: string
  name: string
  type: FieldType
  x: number
  y: number
  width: number
  height: number
  font_size?: number
  required?: boolean
  placeholder?: string
  default_value?: string
  options?: string[]
  validation?: {
    pattern?: string
    minLength?: number
    maxLength?: number
    min?: number
    max?: number
  }
}

// Template Definition
export interface Template {
  id: number
  nome: string
  descricao?: string
  caminho_arquivo: string
  campos?: Field[]
  ativo: boolean
  data_criacao: string
  file_size?: number
  num_pages?: number
  width?: number
  height?: number
  num_campos?: number
}

// Form Data (for filling)
export type FormData = Record<string, any>

// API Response Types
export interface ApiResponse<T = any> {
  sucesso: boolean
  mensagem?: string
  [key: string]: any
}

export interface TemplatesResponse extends ApiResponse {
  templates: Template[]
}

export interface TemplateResponse extends ApiResponse {
  template: Template
}

export interface CamposResponse extends ApiResponse {
  campos: Field[]
}

// UI State
export type Mode = 'design' | 'fill'

export interface AppState {
  mode: Mode
  currentTemplate: Template | null
  fields: Field[]
  selectedFieldId: string | null
  formData: FormData
  pdfUrl: string | null
  zoom: number
  showGrid: boolean
  showRulers: boolean
}

// Resize Handle Directions
export type ResizeDirection = 'n' | 's' | 'e' | 'w' | 'ne' | 'nw' | 'se' | 'sw'

// Field Library Item
export interface FieldLibraryItem {
  type: FieldType
  label: string
  icon: string
  description: string
}
