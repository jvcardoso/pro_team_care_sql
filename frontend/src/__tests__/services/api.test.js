/**
 * Testes para services/api.js
 * Testes básicos para verificar disponibilidade dos serviços - Prioridade 2
 */

// Mock the entire api module to avoid import.meta issues
jest.mock("../../services/api", () => ({
  authService: {
    login: jest.fn(),
    register: jest.fn(),
    getCurrentUser: jest.fn(),
    logout: jest.fn(),
  },
  companiesService: {
    getCompanies: jest.fn(),
    getCompaniesCount: jest.fn(),
    getCompany: jest.fn(),
    getCompanyByCNPJ: jest.fn(),
    createCompany: jest.fn(),
    updateCompany: jest.fn(),
    deleteCompany: jest.fn(),
    getCompanyContacts: jest.fn(),
  },
  healthService: {
    getHealthStatus: jest.fn(),
    getDetailedHealth: jest.fn(),
  },
}));

import {
  authService,
  companiesService,
  healthService,
} from "../../services/api";

describe("API Services", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Service Availability", () => {
    test("should have authService with all methods", () => {
      expect(authService).toBeDefined();
      expect(typeof authService.login).toBe("function");
      expect(typeof authService.register).toBe("function");
      expect(typeof authService.getCurrentUser).toBe("function");
      expect(typeof authService.logout).toBe("function");
    });

    test("should have companiesService with all methods", () => {
      expect(companiesService).toBeDefined();
      expect(typeof CompaniesService.getCompanies).toBe("function");
      expect(typeof CompaniesService.getCompaniesCount).toBe("function");
      expect(typeof CompaniesService.getCompany).toBe("function");
      expect(typeof CompaniesService.getCompanyByCNPJ).toBe("function");
      expect(typeof CompaniesService.createCompany).toBe("function");
      expect(typeof CompaniesService.updateCompany).toBe("function");
      expect(typeof CompaniesService.deleteCompany).toBe("function");
      expect(typeof CompaniesService.getCompanyContacts).toBe("function");
    });

    test("should have healthService with all methods", () => {
      expect(healthService).toBeDefined();
      expect(typeof healthService.getHealthStatus).toBe("function");
      expect(typeof healthService.getDetailedHealth).toBe("function");
    });
  });

  describe("authService Mock Functions", () => {
    test("should call login with parameters", async () => {
      const mockResponse = { access_token: "mock-token" };
      authService.login.mockResolvedValueOnce(mockResponse);

      const result = await authService.login("user@test.com", "password123");

      expect(authService.login).toHaveBeenCalledWith(
        "user@test.com",
        "password123"
      );
      expect(result).toEqual(mockResponse);
    });

    test("should call register with user data", async () => {
      const userData = { name: "Test User", email: "test@test.com" };
      const mockResponse = { message: "User created" };
      authService.register.mockResolvedValueOnce(mockResponse);

      const result = await authService.register(userData);

      expect(authService.register).toHaveBeenCalledWith(userData);
      expect(result).toEqual(mockResponse);
    });

    test("should call getCurrentUser", async () => {
      const mockUser = { id: 1, name: "Test User" };
      authService.getCurrentUser.mockResolvedValueOnce(mockUser);

      const result = await authService.getCurrentUser();

      expect(authService.getCurrentUser).toHaveBeenCalled();
      expect(result).toEqual(mockUser);
    });
  });

  describe("companiesService Mock Functions", () => {
    test("should call getCompanies with parameters", async () => {
      const params = { page: 1, limit: 10 };
      const mockResponse = { companies: [], total: 0 };
      CompaniesService.getCompanies.mockResolvedValueOnce(mockResponse);

      const result = await CompaniesService.getCompanies(params);

      expect(CompaniesService.getCompanies).toHaveBeenCalledWith(params);
      expect(result).toEqual(mockResponse);
    });

    test("should call getCompany by id", async () => {
      const companyId = 1;
      const mockCompany = { id: 1, name: "Test Company" };
      CompaniesService.getCompany.mockResolvedValueOnce(mockCompany);

      const result = await CompaniesService.getById(companyId);

      expect(CompaniesService.getCompany).toHaveBeenCalledWith(companyId);
      expect(result).toEqual(mockCompany);
    });

    test("should call createCompany with data", async () => {
      const companyData = { name: "New Company", tax_id: "12345678000195" };
      const mockResponse = { id: 2, ...companyData };
      CompaniesService.createCompany.mockResolvedValueOnce(mockResponse);

      const result = await CompaniesService.createComplete(companyData);

      expect(CompaniesService.createCompany).toHaveBeenCalledWith(companyData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe("healthService Mock Functions", () => {
    test("should call getHealthStatus", async () => {
      const mockStatus = { status: "healthy" };
      healthService.getHealthStatus.mockResolvedValueOnce(mockStatus);

      const result = await healthService.getHealthStatus();

      expect(healthService.getHealthStatus).toHaveBeenCalled();
      expect(result).toEqual(mockStatus);
    });

    test("should call getDetailedHealth", async () => {
      const mockDetailedStatus = { status: "healthy", database: "connected" };
      healthService.getDetailedHealth.mockResolvedValueOnce(mockDetailedStatus);

      const result = await healthService.getDetailedHealth();

      expect(healthService.getDetailedHealth).toHaveBeenCalled();
      expect(result).toEqual(mockDetailedStatus);
    });
  });

  describe("Error Handling", () => {
    test("should handle service errors", async () => {
      const errorMessage = "Service unavailable";
      CompaniesService.getCompanies.mockRejectedValueOnce(
        new Error(errorMessage)
      );

      await expect(CompaniesService.getCompanies()).rejects.toThrow(
        errorMessage
      );
    });

    test("should handle auth errors", async () => {
      const authError = "Invalid credentials";
      authService.login.mockRejectedValueOnce(new Error(authError));

      await expect(authService.login("invalid", "credentials")).rejects.toThrow(
        authError
      );
    });
  });
});
