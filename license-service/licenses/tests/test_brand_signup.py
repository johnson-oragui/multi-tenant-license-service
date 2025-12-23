"""
Test Brand Signup
"""

import pytest
from django.urls import reverse

from licenses.models import Brand
from licenses.tests.helpers import hash_value


@pytest.mark.django_db
def test_a_brand_signup_success(client):
    """
    Test brand signup success
    """
    url = reverse("brand-signup")

    response = client.post(
        url,
        data={"name": "RankMath"},
        format="json",
    )

    assert response.status_code == 201

    payload = response.json()

    assert "api_key" in payload["data"]
    assert payload["data"]["name"] == "RankMath"
    assert Brand.objects.filter(name="RankMath").exists()


@pytest.mark.django_db
def test_b_brand_signup_duplicate_name(client):
    """
    Test brand signup duplicate name
    """
    Brand.objects.create(name="RankMath", api_key=hash_value("abc"))

    url = reverse("brand-signup")

    response = client.post(
        url,
        data={"name": "RankMath"},
        format="json",
    )

    assert response.status_code == 409

    response = client.post(
        url,
        data={"name": "rankmath"},
        format="json",
    )

    assert response.status_code == 409
