"""Examples of using the domain layer.

Run from the repository root after the architecture scaffold is merged:

    python -m examples.domain_usage
"""

from domain.models import Agency, Audit
from domain.modules import MODULES, score_module


def example_register_and_score():
    """Minimal demo path expressed with domain objects."""
    agency = Agency(
        name="Costa Blanca Homes",
        location="Alicante, Spain",
        team_size=4,
        specialization="Residential coastal",
        website="https://example-agency.es",
    )
    print(f"Agency: {agency.name} ({agency.location})")

    audit = Audit(
        agency_id="demo-agency-1",
        channels="WhatsApp, Phone, Idealista",
        pain="Slow response to leads, manual follow-ups",
        existing_crm="Spreadsheets",
        objectives="Faster qualification and more viewings",
    )

    scores = [score_module(m, audit) for m in MODULES]
    scores.sort(key=lambda s: s.score, reverse=True)

    print("\nTop 5 opportunities:")
    for s in scores[:5]:
        print(f"  {s.module_id:3} {s.score:3}  {s.priority:12}  {s.name}")

    return agency, audit, scores


def example_filter_by_domain():
    """Show how a product UI or service can filter the same scores."""
    _, audit, scores = example_register_and_score()
    sales = [s for s in scores if s.domain == "Sales"]
    print(f"\nSales modules above 60: {len([s for s in sales if s.score >= 60])}")
    return sales


if __name__ == "__main__":
    example_register_and_score()
    example_filter_by_domain()
