# Implementação Backend - Módulo de Atividades com IA

**Responsável:** Dev Backend  
**Tempo Estimado:** 2-3 dias  
**Dependências:** Script SQL executado

---

## 📁 Estrutura de Arquivos

```
backend/app/
├── models/
│   ├── activity.py (novo)
│   ├── activity_content.py (novo)
│   ├── activity_entity.py (novo)
│   └── pendency.py (novo)
├── schemas/
│   ├── activity.py (novo)
│   ├── activity_content.py (novo)
│   ├── activity_entity.py (novo)
│   └── pendency.py (novo)
├── repositories/
│   ├── activity_repository.py (novo)
│   └── pendency_repository.py (novo)
├── services/
│   ├── activity_service.py (novo)
│   ├── pendency_service.py (novo)
│   └── gemini_service.py (novo) ⭐
├── api/v1/
│   ├── activities.py (novo)
│   └── pendencies.py (novo)
└── core/
    └── config.py (adicionar GEMINI_API_KEY)
```

---

## 🔧 Fase 1: Models (SQLAlchemy)

### `models/activity.py`
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class Activity(Base):
    __tablename__ = "Activities"
    __table_args__ = {"schema": "core"}

    ActivityID = Column(Integer, primary_key=True, index=True)
    CompanyID = Column(Integer, ForeignKey("core.Companies.CompanyID"), nullable=False)
    UserID = Column(Integer, ForeignKey("core.Users.UserID"), nullable=False)
    Title = Column(String(255), nullable=False)
    Status = Column(String(50), nullable=False)
    CreationDate = Column(DateTime, default=datetime.utcnow)
    DueDate = Column(DateTime, nullable=True)
    IsActive = Column(Boolean, default=True)

    # Relationships
    contents = relationship("ActivityContent", back_populates="activity", cascade="all, delete-orphan")
    entities = relationship("ActivityEntity", back_populates="activity", cascade="all, delete-orphan")
    pendencies = relationship("Pendency", back_populates="activity", cascade="all, delete-orphan")
```

### `models/activity_content.py`
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class ActivityContent(Base):
    __tablename__ = "ActivityContents"
    __table_args__ = {"schema": "core"}

    ContentID = Column(Integer, primary_key=True, index=True)
    ActivityID = Column(Integer, ForeignKey("core.Activities.ActivityID"), nullable=False)
    RawText = Column(Text, nullable=True)
    RawImagePath = Column(String(500), nullable=True)
    AIExtractionJSON = Column(Text, nullable=True)
    UserCorrectedJSON = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    activity = relationship("Activity", back_populates="contents")
```

### `models/activity_entity.py`
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class ActivityEntity(Base):
    __tablename__ = "ActivityEntities"
    __table_args__ = {"schema": "core"}

    EntityID = Column(Integer, primary_key=True, index=True)
    ActivityID = Column(Integer, ForeignKey("core.Activities.ActivityID"), nullable=False)
    EntityType = Column(String(50), nullable=False)
    EntityName = Column(String(255), nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    activity = relationship("Activity", back_populates="entities")
```

### `models/pendency.py`
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class Pendency(Base):
    __tablename__ = "Pendencies"
    __table_args__ = {"schema": "core"}

    PendencyID = Column(Integer, primary_key=True, index=True)
    ActivityID = Column(Integer, ForeignKey("core.Activities.ActivityID"), nullable=False)
    Description = Column(String(500), nullable=False)
    Owner = Column(String(255), nullable=True)
    Status = Column(String(50), nullable=False, default="Pendente")
    Impediment = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    ResolvedAt = Column(DateTime, nullable=True)

    activity = relationship("Activity", back_populates="pendencies")
```

---

## 📝 Fase 2: Schemas (Pydantic)

### `schemas/activity.py`
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ActivityBase(BaseModel):
    Title: str = Field(..., max_length=255)
    Status: str = Field(..., max_length=50)
    DueDate: Optional[datetime] = None

class ActivityCreate(ActivityBase):
    RawText: Optional[str] = None
    RawImagePath: Optional[str] = None

class ActivityUpdate(BaseModel):
    Title: Optional[str] = None
    Status: Optional[str] = None
    DueDate: Optional[datetime] = None

class ActivityResponse(ActivityBase):
    ActivityID: int
    CompanyID: int
    UserID: int
    CreationDate: datetime
    IsActive: bool

    class Config:
        from_attributes = True

class ActivityWithAISuggestions(ActivityResponse):
    ai_suggestions: Optional[dict] = None  # JSON da IA
```

### `schemas/pendency.py`
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PendencyBase(BaseModel):
    Description: str = Field(..., max_length=500)
    Owner: Optional[str] = Field(None, max_length=255)
    Status: str = Field(default="Pendente", max_length=50)
    Impediment: Optional[str] = None

class PendencyCreate(PendencyBase):
    ActivityID: int

class PendencyUpdate(BaseModel):
    Description: Optional[str] = None
    Owner: Optional[str] = None
    Status: Optional[str] = None
    Impediment: Optional[str] = None
    ResolvedAt: Optional[datetime] = None

class PendencyResponse(PendencyBase):
    PendencyID: int
    ActivityID: int
    CreatedAt: datetime
    ResolvedAt: Optional[datetime] = None

    class Config:
        from_attributes = True
```

---

## 🤖 Fase 3: Serviço Gemini

### `services/gemini_service.py`
```python
import google.generativeai as genai
from typing import Dict, Optional
from app.core.config import settings
import json

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_activity(
        self, 
        title: str, 
        status: str, 
        raw_text: Optional[str] = None,
        raw_image_path: Optional[str] = None
    ) -> Dict:
        """
        Analisa conteúdo e retorna sugestões estruturadas
        """
        prompt = self._build_prompt(title, status, raw_text)
        
        try:
            if raw_image_path:
                # Análise com imagem
                image = genai.upload_file(raw_image_path)
                response = self.model.generate_content([prompt, image])
            else:
                # Análise apenas texto
                response = self.model.generate_content(prompt)
            
            # Parse JSON da resposta
            return self._parse_ai_response(response.text)
        
        except Exception as e:
            return {"error": str(e), "suggestions": {}}

    def _build_prompt(self, title: str, status: str, raw_text: Optional[str]) -> str:
        return f"""
Analise o seguinte conteúdo no contexto de uma atividade de TI.

**Contexto:**
- Título: {title}
- Status: {status}

**Conteúdo:**
{raw_text or "Sem texto adicional"}

**Tarefa:**
Extraia e retorne um JSON com:
1. "pessoas": lista de nomes de pessoas mencionadas
2. "sistemas": lista de sistemas/aplicações mencionados
3. "datas": lista de datas ou prazos identificados
4. "tags": lista de 3-5 tags relevantes (ex: "Gestão de Incidentes", "Requisição de Serviço")
5. "pendencias": lista de objetos com:
   - "descricao": descrição da pendência
   - "responsavel": quem deve agir (se identificável)
   - "impedimento": descrição do bloqueio (se houver)

Retorne APENAS o JSON, sem texto adicional.
"""

    def _parse_ai_response(self, response_text: str) -> Dict:
        try:
            # Remove markdown code blocks se existirem
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            return json.loads(clean_text.strip())
        except json.JSONDecodeError:
            return {
                "error": "Falha ao parsear resposta da IA",
                "raw_response": response_text
            }
```

### `.env` (adicionar)
```bash
GEMINI_API_KEY=your_api_key_here
```

---

## 🔄 Fase 4: Repository + Service

### `repositories/activity_repository.py`
```python
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.activity import Activity
from app.models.activity_content import ActivityContent
from app.schemas.activity import ActivityCreate, ActivityUpdate

class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, activity_data: ActivityCreate, company_id: int, user_id: int) -> Activity:
        activity = Activity(
            CompanyID=company_id,
            UserID=user_id,
            Title=activity_data.Title,
            Status=activity_data.Status,
            DueDate=activity_data.DueDate
        )
        self.db.add(activity)
        self.db.flush()  # Get ActivityID
        
        # Criar content
        content = ActivityContent(
            ActivityID=activity.ActivityID,
            RawText=activity_data.RawText,
            RawImagePath=activity_data.RawImagePath
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def get_by_id(self, activity_id: int, company_id: int) -> Optional[Activity]:
        return self.db.query(Activity).filter(
            Activity.ActivityID == activity_id,
            Activity.CompanyID == company_id,
            Activity.IsActive == True
        ).first()

    def get_all(self, company_id: int, skip: int = 0, limit: int = 100) -> List[Activity]:
        return self.db.query(Activity).filter(
            Activity.CompanyID == company_id,
            Activity.IsActive == True
        ).offset(skip).limit(limit).all()

    def update(self, activity_id: int, company_id: int, data: ActivityUpdate) -> Optional[Activity]:
        activity = self.get_by_id(activity_id, company_id)
        if not activity:
            return None
        
        for key, value in data.dict(exclude_unset=True).items():
            setattr(activity, key, value)
        
        self.db.commit()
        self.db.refresh(activity)
        return activity
```

### `services/activity_service.py`
```python
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.repositories.activity_repository import ActivityRepository
from app.services.gemini_service import GeminiService
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityWithAISuggestions
import json

class ActivityService:
    def __init__(self, db: Session):
        self.repository = ActivityRepository(db)
        self.gemini = GeminiService()

    async def create_with_ai_analysis(
        self, 
        activity_data: ActivityCreate, 
        company_id: int, 
        user_id: int
    ) -> ActivityWithAISuggestions:
        """
        Cria atividade e retorna com sugestões da IA
        """
        # Criar atividade
        activity = self.repository.create(activity_data, company_id, user_id)
        
        # Analisar com IA
        ai_suggestions = await self.gemini.analyze_activity(
            title=activity_data.Title,
            status=activity_data.Status,
            raw_text=activity_data.RawText,
            raw_image_path=activity_data.RawImagePath
        )
        
        # Salvar JSON da IA
        if activity.contents:
            activity.contents[0].AIExtractionJSON = json.dumps(ai_suggestions)
            self.repository.db.commit()
        
        # Retornar com sugestões
        return ActivityWithAISuggestions(
            **activity.__dict__,
            ai_suggestions=ai_suggestions
        )

    def get_by_id(self, activity_id: int, company_id: int) -> Optional[Activity]:
        return self.repository.get_by_id(activity_id, company_id)

    def get_all(self, company_id: int, skip: int = 0, limit: int = 100) -> List[Activity]:
        return self.repository.get_all(company_id, skip, limit)

    def update(self, activity_id: int, company_id: int, data: ActivityUpdate) -> Optional[Activity]:
        return self.repository.update(activity_id, company_id, data)
```

---

## 🌐 Fase 5: Endpoints

### `api/v1/activities.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_active_user
from app.services.activity_service import ActivityService
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse, ActivityWithAISuggestions
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ActivityWithAISuggestions, status_code=201)
async def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria nova atividade e retorna com sugestões da IA
    """
    service = ActivityService(db)
    return await service.create_with_ai_analysis(
        activity, 
        current_user.CompanyID, 
        current_user.UserID
    )

@router.get("/", response_model=List[ActivityResponse])
def list_activities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista atividades da empresa
    """
    service = ActivityService(db)
    return service.get_all(current_user.CompanyID, skip, limit)

@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Busca atividade por ID
    """
    service = ActivityService(db)
    activity = service.get_by_id(activity_id, current_user.CompanyID)
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return activity

@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza atividade
    """
    service = ActivityService(db)
    activity = service.update(activity_id, current_user.CompanyID, data)
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return activity
```

### Registrar rotas em `api/v1/__init__.py`
```python
from app.api.v1 import activities, pendencies

api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(pendencies.router, prefix="/pendencies", tags=["pendencies"])
```

---

## ✅ Checklist

- [ ] Criar models (4 arquivos)
- [ ] Criar schemas (4 arquivos)
- [ ] Criar GeminiService
- [ ] Adicionar GEMINI_API_KEY no .env
- [ ] Criar repositories
- [ ] Criar services
- [ ] Criar endpoints
- [ ] Registrar rotas
- [ ] Testar com Postman/Swagger

---

## 🧪 Teste Manual

```bash
# 1. Criar atividade
curl -X POST "http://localhost:8000/api/v1/activities" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Title": "Teste RDM CHG001",
    "Status": "Pendente",
    "RawText": "Conversa com Vania sobre testes. Daniel precisa aprovar."
  }'

# 2. Listar atividades
curl -X GET "http://localhost:8000/api/v1/activities" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
