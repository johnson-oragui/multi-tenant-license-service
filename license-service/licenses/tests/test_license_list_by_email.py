"""
Test List Licenses By Email
"""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_a_list_licenses_by_email_success(licenses_bulk, api_client_with_brand_auth):
    """
    Test list licenses by email success
    """
    client, _ = api_client_with_brand_auth
    response = client.post(
        reverse("license-email-listing"),
        data={"customer_email": "user@example.com"},
        format="json",
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["count"] == 25
    assert payload["next"] is not None
    assert payload["previous"] is None

    results = payload["results"]["data"]
    assert len(results) == 20  # default_limit

    # sanity check structure
    first = results[0]
    assert "license_key" in first
    assert "brand" in first
    assert "product" in first


@pytest.mark.django_db
def test_b_list_licenses_limit_param(licenses_bulk, api_client_with_brand_auth):
    """
    Test list licenses limit param
    """
    client, _ = api_client_with_brand_auth
    response = client.post(
        f"{reverse('license-email-listing')}?limit=5",
        data={"customer_email": "user@example.com"},
        format="json",
    )

    payload = response.json()

    assert payload["count"] == 25
    assert len(payload["results"]["data"]) == 5


@pytest.mark.django_db
def test_c_list_licenses_offset_param(
    api_client_with_brand_auth,
    licenses_bulk,
):
    """
    Test list licenses offset param
    """
    client, _ = api_client_with_brand_auth
    response = client.post(
        f"{reverse('license-email-listing')}?limit=10&offset=10",
        data={"customer_email": "user@example.com"},
        format="json",
    )

    payload = response.json()

    assert payload["count"] == 25
    assert len(payload["results"]["data"]) == 10
    assert payload["previous"] is not None
    assert payload["next"] is not None


@pytest.mark.django_db
def test_d_list_licenses_last_page(
    api_client_with_brand_auth,
    licenses_bulk,
):
    """
    Test list licenses last page
    """
    client, _ = api_client_with_brand_auth
    response = client.post(
        f"{reverse('license-email-listing')}?limit=10&offset=20",
        data={"customer_email": "user@example.com"},
        format="json",
    )

    payload = response.json()

    assert payload["count"] == 25
    assert len(payload["results"]["data"]) == 5
    assert payload["next"] is None


@pytest.mark.django_db
def test_e_list_licenses_empty_result(
    api_client_with_brand_auth,
):
    """
    test list licenses empty result
    """
    client, _ = api_client_with_brand_auth
    response = client.post(
        reverse("license-email-listing"),
        data={"customer_email": "empty@example.com"},
        format="json",
    )

    payload = response.json()

    assert payload["count"] == 0
    assert payload["results"]["data"] == []


@pytest.mark.django_db
def test_list_licenses_requires_brand_auth(client: Client):
    """
    Test list licenses requires brand auth
    """

    response = client.post(
        reverse("license-email-listing"),
        data={"customer_email": "user@example.com"},
        format="json",
    )

    assert response.status_code == 401
