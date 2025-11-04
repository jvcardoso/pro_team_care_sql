/**
 * Testes unitários para services/geocodingService.js
 * Testa geocoding via backend Nominatim
 */

import geocodingService from "../../services/geocodingService";

// Mock do api service
jest.mock("../../services/api", () => ({
  api: {
    post: jest.fn(),
  },
}));

describe("geocodingService", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    geocodingService.clearCache();
  });

  describe("nominatimGeocode", () => {
    test("deve fazer geocoding via backend", async () => {
      const mockApi = require("../../services/api").api;
      const mockResponse = {
        data: {
          latitude: "-23.550520",
          longitude: "-46.633308",
          formatted_address: "Praça da Sé, São Paulo, SP",
          geocoding_accuracy: "exact",
          geocoding_source: "nominatim",
          api_data: {},
        },
      };

      mockApi.post.mockResolvedValue(mockResponse);

      const result = await geocodingService.nominatimGeocode("Praça da Sé, São Paulo");

      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/geocoding/geocode", {
        address: "Praça da Sé, São Paulo",
      });

      expect(result).toEqual({
        latitude: "-23.550520",
        longitude: "-46.633308",
        formatted_address: "Praça da Sé, São Paulo, SP",
        geocoding_accuracy: "exact",
        geocoding_source: "nominatim",
        google_place_id: null,
        api_data: {},
      });
    });
  });

  describe("geocode", () => {
    test("deve rejeitar endereço vazio", async () => {
      await expect(geocodingService.geocode("")).rejects.toThrow(
        "Endereço não pode estar vazio"
      );
    });

    test("deve usar cache para consultas repetidas", async () => {
      const mockApi = require("../../services/api").api;
      const mockResponse = {
        data: {
          latitude: "-23.550520",
          longitude: "-46.633308",
        },
      };

      mockApi.post.mockResolvedValue(mockResponse);

      // Primeira consulta
      await geocodingService.geocode("Praça da Sé, São Paulo");
      // Segunda consulta (deve usar cache)
      const result = await geocodingService.geocode("Praça da Sé, São Paulo");

      expect(mockApi.post).toHaveBeenCalledTimes(1);
      expect(result.latitude).toBe("-23.550520");
    });

    test("deve lidar com erro do backend", async () => {
      const mockApi = require("../../services/api").api;
      mockApi.post.mockRejectedValue(new Error("API error"));

      const result = await geocodingService.geocode("Endereço inválido");

      expect(result).toBeNull();
    });
  });

  describe("geocodeBrazilianAddress", () => {
    test("deve geocodificar endereço brasileiro", async () => {
      const mockApi = require("../../services/api").api;
      const mockGeoData = {
        latitude: "-23.550520",
        longitude: "-46.633308",
        formatted_address: "Praça da Sé, São Paulo, SP",
      };

      mockApi.post.mockResolvedValue({ data: mockGeoData });

      const viaCepData = {
        logradouro: "Praça da Sé",
        bairro: "Sé",
        localidade: "São Paulo",
        uf: "SP",
      };

      const result = await geocodingService.geocodeBrazilianAddress(viaCepData);

      expect(result).toEqual({
        ...viaCepData,
        ...mockGeoData,
        number: "", // Campo adicionado
        is_validated: true,
        validation_source: "viacep",
        last_validated_at: expect.any(String),
      });
    });

    test("deve retornar dados ViaCEP se geocoding falhar", async () => {
      const mockApi = require("../../services/api").api;
      mockApi.post.mockRejectedValue(new Error("Geocoding failed"));

      const viaCepData = {
        logradouro: "Praça da Sé",
        localidade: "São Paulo",
        uf: "SP",
      };

      const result = await geocodingService.geocodeBrazilianAddress(viaCepData);

      expect(result).toEqual(viaCepData);
    });

    test("deve retornar null se não houver dados ViaCEP", async () => {
      const result = await geocodingService.geocodeBrazilianAddress(null);

      expect(result).toBeNull();
    });
  });

  describe("reverseGeocode", () => {
    test("deve indicar que reverse geocoding não está implementado", async () => {
      const result = await geocodingService.reverseGeocode(-23.550520, -46.633308);

      expect(result).toBeNull();
    });
  });

  describe("clearCache", () => {
    test("deve limpar cache", () => {
      // Adicionar algo ao cache
      geocodingService.cache.set("test", "value");

      geocodingService.clearCache();

      expect(geocodingService.cache.size).toBe(0);
    });
  });
});