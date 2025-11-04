/**
 * Testes unitários para services/addressEnrichmentService.js
 * Testa enriquecimento de endereços via ViaCEP e geocoding
 */

import addressEnrichmentService from "../../services/addressEnrichmentService";

// Mock do geocodingService
jest.mock("../../services/geocodingService", () => ({
  default: {
    geocode: jest.fn(),
  },
}));

// Mock do serviceLogger
jest.mock("../../utils/logger", () => ({
  serviceLogger: {
    setContext: jest.fn(() => ({
      cache: jest.fn(),
      service: jest.fn(),
      enrichment: jest.fn(),
      warn: jest.fn(),
      error: jest.fn(),
    })),
  },
}));

describe("addressEnrichmentService", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Limpar cache antes de cada teste
    addressEnrichmentService.clearCache();
  });

  describe("consultarViaCEP", () => {
    beforeEach(() => {
      // Mock do fetch global
      global.fetch = jest.fn();
    });

    test("deve consultar CEP válido", async () => {
      const mockViaCepResponse = {
        cep: "01001-000",
        logradouro: "Praça da Sé",
        bairro: "Sé",
        localidade: "São Paulo",
        uf: "SP",
        ibge: "3550308",
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockViaCepResponse),
      });

      const result = await addressEnrichmentService.consultarViaCEP("01001000");

      expect(global.fetch).toHaveBeenCalledWith(
        "https://viacep.com.br/ws/01001000/json/",
        { timeout: 10000 }
      );
      expect(result).toEqual(mockViaCepResponse);
    });

    test("deve rejeitar CEP inválido", async () => {
      const result = await addressEnrichmentService.consultarViaCEP("123");

      expect(result).toBeNull();
    });

    test("deve lidar com CEP não encontrado", async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ erro: true }),
      });

      const result = await addressEnrichmentService.consultarViaCEP("99999999");

      expect(result).toBeNull();
    });

    test("deve usar cache para consultas repetidas", async () => {
      const mockViaCepResponse = {
        cep: "01001-000",
        logradouro: "Praça da Sé",
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockViaCepResponse),
      });

      // Primeira consulta
      await addressEnrichmentService.consultarViaCEP("01001000");
      // Segunda consulta (deve usar cache)
      const result = await addressEnrichmentService.consultarViaCEP("01001000");

      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockViaCepResponse);
    });
  });

  describe("enriquecerComViaCEP", () => {
    beforeEach(() => {
      global.fetch = jest.fn();
    });

    test("deve enriquecer endereço com dados do ViaCEP", async () => {
      const mockViaCepResponse = {
        logradouro: "Praça da Sé",
        bairro: "Sé",
        localidade: "São Paulo",
        uf: "SP",
        ibge: "3550308",
        gia: "1004",
        siafi: "7107",
        ddd: "11",
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockViaCepResponse),
      });

      const addressData = {
        street: "",
        number: "123",
        neighborhood: "",
        city: "",
        state: "",
        zip_code: "01001000",
        country: "BR",
        type: "commercial",
        is_principal: true,
      };

      const result = await addressEnrichmentService.enriquecerComViaCEP(addressData);

      expect(result.street).toBe("Praça da Sé");
      expect(result.neighborhood).toBe("Sé");
      expect(result.city).toBe("São Paulo");
      expect(result.state).toBe("SP");
      expect(result.ibge_city_code).toBe(3550308);
      expect(result.enrichment_source).toBe("viacep");
    });

    test("deve preservar dados existentes", async () => {
      const mockViaCepResponse = {
        logradouro: "Praça da Sé",
        bairro: "Sé",
        localidade: "São Paulo",
        uf: "SP",
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockViaCepResponse),
      });

      const addressData = {
        street: "Rua Original", // Deve ser preservado
        number: "456", // Deve ser preservado
        neighborhood: "",
        city: "",
        state: "",
        zip_code: "01001000",
        country: "BR",
        type: "commercial",
        is_principal: true,
      };

      const result = await addressEnrichmentService.enriquecerComViaCEP(addressData);

      expect(result.street).toBe("Rua Original"); // Preservado
      expect(result.number).toBe("456"); // Preservado
      expect(result.neighborhood).toBe("Sé"); // Enriquecido
    });

    test("deve retornar dados originais se ViaCEP falhar", async () => {
      global.fetch.mockRejectedValue(new Error("Network error"));

      const addressData = {
        street: "Rua Original",
        zip_code: "01001000",
      };

      const result = await addressEnrichmentService.enriquecerComViaCEP(addressData);

      expect(result).toEqual(addressData);
    });
  });

  describe("adicionarCoordenadas", () => {
    test("deve adicionar coordenadas via geocoding", async () => {
      const geocodingService = require("../../services/geocodingService").default;

      geocodingService.geocode.mockResolvedValue({
        latitude: "-23.550520",
        longitude: "-46.633308",
        formatted_address: "Praça da Sé, São Paulo, SP",
        geocoding_accuracy: "exact",
        geocoding_source: "nominatim",
      });

      const addressData = {
        street: "Praça da Sé",
        city: "São Paulo",
        state: "SP",
      };

      const result = await addressEnrichmentService.adicionarCoordenadas(addressData);

      expect(result.latitude).toBe("-23.550520");
      expect(result.longitude).toBe("-46.633308");
      expect(result.geocoding_accuracy).toBe("exact");
      expect(result.coordinates_source).toBe("nominatim");
    });

    test("deve tentar múltiplas variações de endereço", async () => {
      const geocodingService = require("../../services/geocodingService").default;

      // Primeiro geocoding falha, segundo funciona
      geocodingService.geocode
        .mockResolvedValueOnce(null)
        .mockResolvedValueOnce({
          latitude: "-23.550520",
          longitude: "-46.633308",
        });

      const addressData = {
        street: "Praça da Sé",
        city: "São Paulo",
        state: "SP",
      };

      const result = await addressEnrichmentService.adicionarCoordenadas(addressData);

      expect(geocodingService.geocode).toHaveBeenCalledTimes(2);
      expect(result.latitude).toBe("-23.550520");
    });
  });

  describe("enriquecerEnderecoCompleto", () => {
    beforeEach(() => {
      global.fetch = jest.fn();
    });

    test("deve enriquecer endereço completamente", async () => {
      // Mock ViaCEP
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          logradouro: "Praça da Sé",
          bairro: "Sé",
          localidade: "São Paulo",
          uf: "SP",
        }),
      });

      // Mock geocoding
      const geocodingService = require("../../services/geocodingService").default;
      geocodingService.geocode.mockResolvedValue({
        latitude: "-23.550520",
        longitude: "-46.633308",
      });

      const addressData = {
        street: "",
        zip_code: "01001000",
        country: "BR",
      };

      const result = await addressEnrichmentService.enriquecerEnderecoCompleto(addressData);

      expect(result.street).toBe("Praça da Sé");
      expect(result.city).toBe("São Paulo");
      expect(result.latitude).toBe("-23.550520");
      expect(result.longitude).toBe("-46.633308");
    });
  });

  describe("enriquecerMultiplosEnderecos", () => {
    beforeEach(() => {
      global.fetch = jest.fn();
    });

    test("deve enriquecer múltiplos endereços", async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          logradouro: "Rua Teste",
          localidade: "São Paulo",
          uf: "SP",
        }),
      });

      const addresses = [
        { zip_code: "01001000", street: "" },
        { zip_code: "02002000", street: "" },
      ];

      const result = await addressEnrichmentService.enriquecerMultiplosEnderecos(addresses);

      expect(result).toHaveLength(2);
      expect(result[0].street).toBe("Rua Teste");
      expect(result[1].street).toBe("Rua Teste");
    });

    test("deve continuar processando mesmo se um endereço falhar", async () => {
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ logradouro: "Rua 1" }),
        })
        .mockRejectedValueOnce(new Error("Network error"));

      const addresses = [
        { zip_code: "01001000", street: "" },
        { zip_code: "99999999", street: "" },
      ];

      const result = await addressEnrichmentService.enriquecerMultiplosEnderecos(addresses);

      expect(result).toHaveLength(2);
      expect(result[0].street).toBe("Rua 1");
      expect(result[1].street).toBe(""); // Falhou, retornou original
    });
  });
});