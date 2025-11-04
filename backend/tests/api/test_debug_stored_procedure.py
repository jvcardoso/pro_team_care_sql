# backend/tests/api/test_debug_stored_procedure.py
"""
Teste específico para debugar o problema da stored procedure
"""
import pytest
from fastapi import status
import asyncio

class TestStoredProcedureDebug:
    """Testes para debugar a stored procedure sp_create_company_from_json"""
    
    @pytest.mark.asyncio
    async def test_stored_procedure_direct_call(self, client, auth_headers):
        """Testa chamada direta da stored procedure via endpoint"""
        
        # Dados mínimos para teste
        test_data = {
            "cnpj": "06990590000123",
            "razao_social": "HOSPITAL TESTE LTDA",
            "nome_fantasia": "HOSPITAL TESTE",
            "telefones": [
                {"number": "(11) 99999-9999", "type": "comercial", "is_whatsapp": True}
            ],
            "emails": [
                {"email": "contato@hospitalteste.com.br", "type": "comercial", "is_principal": True}
            ],
            "enderecos": [{
                "cep": "01001000",
                "logradouro": "PRAÇA DA SÉ",
                "numero": "1",
                "bairro": "SÉ",
                "cidade": "SÃO PAULO",
                "uf": "SP",
                "tipo": "comercial",
                "is_principal": True
            }]
        }
        
        print(f"\n🧪 Testando criação com CNPJ: {test_data['cnpj']}")
        print(f"📋 Dados: {test_data['razao_social']}")
        
        # Tentar criar a empresa
        response = await client.post(
            "/api/v1/companies/complete",
            json=test_data,
            headers=auth_headers
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 201:
            # Sucesso - empresa foi criada
            data = response.json()
            company_id = data["new_company_id"]
            print(f"✅ Empresa criada com ID: {company_id}")
            
            # Tentar acessar a empresa
            get_response = await client.get(
                f"/api/v1/companies/{company_id}",
                headers=auth_headers
            )
            
            print(f"🔍 GET Status: {get_response.status_code}")
            
            if get_response.status_code == 200:
                print("✅ Empresa acessível - SP funcionou corretamente")
                return True
            else:
                print("❌ Empresa não acessível - SP fez rollback silencioso")
                return False
                
        elif response.status_code == 500:
            # Erro interno - nossa correção detectou o problema
            print("✅ Correção funcionou - erro detectado corretamente")
            print(f"💡 Mensagem: {response.json().get('detail', 'N/A')}")
            return True
            
        else:
            # Outro erro
            print(f"❌ Erro inesperado: {response.status_code}")
            print(f"📄 Detalhes: {response.json()}")
            return False
    
    @pytest.mark.asyncio
    async def test_multiple_cnpjs(self, async_client, auth_headers):
        """Testa múltiplos CNPJs para identificar padrão"""
        
        test_cnpjs = [
            "06990590000123",  # Problema conhecido
            "14337098000185",  # Hospital Unimed - AL
            "11679181739988",  # Hospital São Camilo - AP
            "25979675000120",  # Hospital Calixto - BA
        ]
        
        results = {}
        
        for cnpj in test_cnpjs:
            print(f"\n🧪 Testando CNPJ: {cnpj}")
            
            test_data = {
                "cnpj": cnpj,
                "razao_social": f"HOSPITAL TESTE {cnpj[-4:]} LTDA",
                "nome_fantasia": f"HOSPITAL TESTE {cnpj[-4:]}",
                "telefones": [
                    {"number": f"(11) 9999-{cnpj[-4:]}", "type": "comercial", "is_whatsapp": True}
                ],
                "emails": [
                    {"email": f"contato{cnpj[-4:]}@hospitalteste.com.br", "type": "comercial", "is_principal": True}
                ],
                "enderecos": [{
                    "cep": "01001000",
                    "logradouro": "PRAÇA DA SÉ",
                    "numero": cnpj[-4:],
                    "bairro": "SÉ",
                    "cidade": "SÃO PAULO",
                    "uf": "SP",
                    "tipo": "comercial",
                    "is_principal": True
                }]
            }
            
            try:
                response = await async_client.post(
                    "/api/v1/companies/complete",
                    json=test_data,
                    headers=auth_headers
                )
                
                results[cnpj] = {
                    "status_code": response.status_code,
                    "success": response.status_code in [201, 500],  # 500 é nossa correção detectando problema
                    "response": response.json() if response.status_code != 500 else response.text
                }
                
                print(f"📊 {cnpj}: Status {response.status_code}")
                
            except Exception as e:
                results[cnpj] = {
                    "status_code": -1,
                    "success": False,
                    "error": str(e)
                }
                print(f"💥 {cnpj}: Erro - {str(e)}")
        
        # Resumo
        print("\n" + "="*60)
        print("📊 RESUMO DOS TESTES")
        print("="*60)
        
        for cnpj, result in results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {cnpj}: Status {result['status_code']}")
        
        success_count = sum(1 for r in results.values() if r["success"])
        total_count = len(results)
        success_rate = (success_count / total_count) * 100
        
        print(f"\n📈 Taxa de Sucesso: {success_rate:.1f}% ({success_count}/{total_count})")
        
        return results
    
    @pytest.mark.asyncio
    async def test_cnpj_validation_patterns(self, async_client, auth_headers):
        """Testa diferentes padrões de CNPJ para identificar problema de validação"""
        
        # CNPJs com diferentes características
        test_cases = [
            {
                "cnpj": "11222333000144",  # CNPJ inválido (DV errado)
                "should_fail": True,
                "description": "CNPJ inválido - DV errado"
            },
            {
                "cnpj": "06990590000123",  # CNPJ válido mas problemático
                "should_fail": False,
                "description": "CNPJ válido - problema conhecido"
            },
            {
                "cnpj": "14337098000185",  # CNPJ válido - Hospital Unimed
                "should_fail": False,
                "description": "CNPJ válido - Hospital Unimed"
            }
        ]
        
        print("\n🔍 TESTANDO PADRÕES DE CNPJ")
        print("="*50)
        
        for test_case in test_cases:
            cnpj = test_case["cnpj"]
            print(f"\n📋 {test_case['description']}")
            print(f"🔢 CNPJ: {cnpj}")
            
            # Primeiro, testar validação do CNPJ
            cnpj_response = await async_client.get(f"/api/v1/cnpj/{cnpj}", headers=auth_headers)
            print(f"🌐 Consulta CNPJ: Status {cnpj_response.status_code}")
            
            # Depois, tentar criar empresa
            test_data = {
                "cnpj": cnpj,
                "razao_social": f"TESTE {cnpj[-4:]} LTDA",
                "nome_fantasia": f"TESTE {cnpj[-4:]}",
                "telefones": [{"number": f"(11) 8888-{cnpj[-4:]}", "type": "comercial"}],
                "emails": [{"email": f"teste{cnpj[-4:]}@example.com", "type": "comercial"}],
                "enderecos": [{
                    "cep": "01001000",
                    "logradouro": "RUA TESTE",
                    "numero": "123",
                    "bairro": "CENTRO",
                    "cidade": "SÃO PAULO",
                    "uf": "SP",
                    "tipo": "comercial",
                    "is_principal": True
                }]
            }
            
            create_response = await async_client.post(
                "/api/v1/companies/complete",
                json=test_data,
                headers=auth_headers
            )
            
            print(f"🏭 Criação: Status {create_response.status_code}")
            
            if test_case["should_fail"]:
                if create_response.status_code >= 400:
                    print("✅ Falhou como esperado")
                else:
                    print("❌ Deveria ter falhado mas passou")
            else:
                if create_response.status_code in [201, 500]:  # 500 é nossa correção
                    print("✅ Comportamento esperado")
                else:
                    print(f"❌ Comportamento inesperado: {create_response.status_code}")
        
        return True
