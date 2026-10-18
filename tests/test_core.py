from core import TripPreferences, Itinerary, DayPlan, Activity, Budget, itinerary_markdown
import pytest

def test_duration_validation():
    with pytest.raises(ValueError):
        TripPreferences(destination='Tunisia', duration_days=0)

def test_markdown_export():
    plan = Itinerary(title='Tunisia Trip', summary='A test', destination='Tunisia', currency='EUR',
        days=[DayPlan(day=1,theme='Food',activities=[Activity(time='12:00',title='Lunch',description='Local food',estimated_cost=20)])],
        budget=Budget(accommodation=100,food=50,transportation=20,activities=10,miscellaneous=20,total=200),
        tips=['Bring water'],assumptions=['Illustrative prices'])
    assert 'Tunisia Trip' in itinerary_markdown(plan)
