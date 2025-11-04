/**
 * Company Types - Baseado na estrutura da API
 */

export interface Company {
  id: number;
  person_id: number;
  name: string;
  trade_name?: string;
  tax_id: string;
  status: "active" | "inactive" | "suspended";
  establishments_count?: number;
  clients_count?: number;
  professionals_count?: number;
  users_count?: number;
  created_at: string;
  updated_at?: string;
}

export interface CompanyDetailed extends Company {
  people?: any;
  phones?: any[];
  emails?: any[];
  addresses?: any[];
}

export interface CompanyCreate {
  name: string;
  trade_name?: string;
  tax_id: string;
  status?: "active" | "inactive" | "suspended";
}

export interface CompanyCompleteCreate {
  access_status?: string;
  pj_profile: {
    name: string;
    trade_name?: string;
    tax_id: string;
    incorporation_date?: string;
    tax_regime?: string;
    legal_nature?: string;
    municipal_registration?: string;
  };
  addresses?: {
    street: string;
    number: string;
    details?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
    country?: string;
    type?: string;
    is_principal?: boolean;
  }[];
  phones?: {
    country_code?: string;
    number: string;
    type?: string;
    is_principal?: boolean;
    is_whatsapp?: boolean;
    phone_name?: string;
  }[];
  emails?: {
    email_address: string;
    type?: string;
    is_principal?: boolean;
  }[];
}

export interface CompanyUpdate extends Partial<CompanyCreate> {
  id: number;
}
