/**
 * Testes unitários para services/cnpjService.js
 * Testa consulta CNPJ, validação e formatação
 */

import { consultarCNPJ, validarFormatoCNPJ, formatarCNPJ } from "../../services/cnpjService";

// Mock do axios
jest.mock("axios", () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
  })),
}));

// Mock do http config
jest.mock("../../config/http", () => ({
  createAxiosConfig: jest.fn(() => ({})),
}));

describe("cnpjService", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("consultarCNPJ", () => {
    test("deve consultar CNPJ numérico válido", async () => {
      const mockAxios = require("axios").create();
      const mockResponse = {
        data: {
          success: true,
          data: {
            people: {
              name: "Empresa Teste Ltda",
              trade_name: "Empresa Teste",
              tax_id: "12345678000199",
            },
            addresses: [
              {
                street: "Rua Teste",
                city: "São Paulo",
                state: "SP",
              },
            ],
          },
        },
      };

      mockAxios.get.mockResolvedValue(mockResponse);

      const result = await consultarCNPJ("12345678000199");

      expect(mockAxios.get).toHaveBeenCalledWith(
        "/api/v1/cnpj/publico/consultar/12345678000199"
      );
      expect(result).toEqual(mockResponse.data.data);
    });

    test("deve rejeitar CNPJ com tamanho inválido", async () => {
      await expect(consultarCNPJ("123456789")).rejects.toThrow(
        "CNPJ deve ter 14 caracteres"
      );
    });

    test("deve retornar dados básicos para CNPJ alfanumérico", async () => {
      const result = await consultarCNPJ("ABC12345678901");

      expect(result.people.name).toBe("");
      expect(result.people.trade_name).toBe("");
      expect(result.people.tax_id).toBe("ABC12345678901");
      expect(result.addresses).toHaveLength(1);
    });

    test("deve lidar com erro da API", async () => {
      const mockAxios = require("axios").create();
      mockAxios.get.mockRejectedValue({
        response: {
          data: {
            detail: "CNPJ não encontrado",
          },
        },
      });

      await expect(consultarCNPJ("99999999000199")).rejects.toThrow(
        "CNPJ não encontrado"
      );
    });
  });

  describe("validarFormatoCNPJ", () => {
    test("deve validar CNPJ numérico válido", () => {
      expect(validarFormatoCNPJ("12345678000199")).toBe(true);
      expect(validarFormatoCNPJ("12.345.678/0001-99")).toBe(true);
    });

    test("deve validar CNPJ alfanumérico válido", () => {
      expect(validarFormatoCNPJ("ABC12345678901")).toBe(true);
      expect(validarFormatoCNPJ("ABC.123.456/7890-1")).toBe(true);
    });

    test("deve rejeitar CNPJ com tamanho inválido", () => {
      expect(validarFormatoCNPJ("123456789")).toBe(false);
      expect(validarFormatoCNPJ("")).toBe(false);
    });
  });

  describe("formatarCNPJ", () => {
    test("deve formatar CNPJ numérico", () => {
      expect(formatarCNPJ("12345678000199")).toBe("12.345.678/0001-99");
    });

    test("deve formatar CNPJ alfanumérico", () => {
      expect(formatarCNPJ("ABC12345678901")).toBe("ABC.123.456/7890-1");
    });

    test("deve retornar CNPJ inválido sem formatação", () => {
      expect(formatarCNPJ("123")).toBe("123");
    });
  });
});