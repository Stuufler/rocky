# Code Usage Examples

Short, runnable examples that show how the domain layer is intended to be used.  
They stay inside the demo boundary: no agents, no external calls, pure Python.

## 1. Register agency + score modules

```python
from domain.models import Agency, Audit
from domain.modules import MODULES, score_module

agency = Agency(
    name="Costa Blanca Homes",
    location="Alicante, Spain",
    team_size=4,
    specialization="Residential coastal",
)

audit = Audit(
    agency_id="demo-1",
    channels="WhatsApp, Phone, Idealista",
    pain="Slow response to leads, manual follow-ups",
    existing_crm="Spreadsheets",
)

scores = sorted(
    (score_module(m, audit) for m in MODULES),
    key=lambda s: s.score,
    reverse=True,
)

for s in scores[:5]:
    print(f"{s.module_id}  {s.score}  {s.priority}  {s.name}")
```

## 2. Filter results (product-style query)

```python
sales_high = [s for s in scores if s.domain == "Sales" and s.score >= 70]
print(f"High-priority sales modules: {len(sales_high)}")
```

## 3. How a thin application service would look

```python
from domain.models import Agency, Audit
from domain.modules import MODULES, score_module

class AssessmentService:
    def run(self, agency: Agency, audit: Audit):
        scores = [score_module(m, audit) for m in MODULES]
        scores.sort(key=lambda s: s.score, reverse=True)
        return {
            "agency": agency.model_dump(),
            "top_opportunities": [s.model_dump() for s in scores[:5]],
            "all_scores": [s.model_dump() for s in scores],
        }

# Usage
service = AssessmentService()
result = service.run(agency, audit)
```

## Notes

- All logic is deterministic and lives in `domain/`.
- The FastAPI demo can call the same functions once the architecture scaffold is in place.
- Later a repository can persist the `Agency`, `Audit` and `OpportunityScore` objects without changing these examples.
