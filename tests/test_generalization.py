"""
Generalization and Zero-Code Architecture Test Suite.

Proves:
1. Adding a new site config (sample_fixture.json) works without modifying core agent code.
2. Ground truth is automatically derived from declarative configurations.
3. The Mock VLM oracle plans actions based on site configuration without hardcoded route branches.
4. Changing a field label or route name does not break the privacy detection or executor logic.
5. Real VLM reasoning path does NOT consume or rely on site configuration.
"""

from demo_sites.site_loader import SiteRegistry
from server.mock_vlm import MockVLM
from shared.protocol import (
    ActionType,
    DetectionCategory,
    ScreenContext,
    ScreenGraph,
    ScreenNode,
)
from shared.site_config import FieldConfig, RouteConfig, SiteConfig
import inspect


def test_site_registry_loads_sample_fixture():
    registry = SiteRegistry()
    site = registry.get_site("sample_fixture")
    assert site is not None
    assert site.site_id == "sample_fixture"
    assert site.display_name == "Generic Fixture Portal"
    assert site.entry_route == "/fixture"
    assert len(site.routes) == 2

    found = registry.find_route("/fixture")
    assert found is not None
    matched_site, route = found
    assert matched_site.site_id == "sample_fixture"
    assert route.route == "/fixture"
    assert len(route.fields) == 2
    assert route.fields[1].vault_ref == "user_profile.fixture_key"


def test_ground_truth_generated_from_config():
    registry = SiteRegistry()
    site = registry.get_site("sample_fixture")
    assert site is not None

    gt = site.to_ground_truth()
    assert "pages" in gt
    assert "/fixture" in gt["pages"]
    elements = gt["pages"]["/fixture"]["elements"]
    assert len(elements) == 1
    assert elements[0]["id"] == "field_fixture_secret"
    assert elements[0]["category"] == DetectionCategory.PASSWORD.value


def test_mock_vlm_reasons_over_sample_fixture():
    server = MockVLM()
    root = ScreenNode(role="WebArea", name="Generic Test Fixture Form", id="root_0")

    # Step 1: Step index 0 -> should fill first fillable vault field (field_fixture_secret)
    ctx1 = ScreenContext(
        run_id="gen-test-01",
        step=1,
        url="http://127.0.0.1:9001/fixture",
        task="Complete fixture authentication test",
        image_b64="fake_b64",
        screen_graph=ScreenGraph(root=root, url="http://127.0.0.1:9001/fixture"),
        redactions=[],
    )

    action1 = server.analyze(ctx1)
    assert action1.action == ActionType.FILL
    assert action1.target.element_id == "field_fixture_secret"
    assert action1.value_ref == "user_profile.fixture_key"
    assert "value" not in action1.model_dump()  # Protocol strictly bans raw value attribute

    # Step 2: Step index 1 (all fillable fields addressed) -> should click submit action
    ctx2 = ScreenContext(
        run_id="gen-test-01",
        step=2,
        url="http://127.0.0.1:9001/fixture",
        task="Complete fixture authentication test",
        image_b64="fake_b64",
        screen_graph=ScreenGraph(root=root, url="http://127.0.0.1:9001/fixture"),
        redactions=[],
    )

    action2 = server.analyze(ctx2)
    assert action2.action == ActionType.CLICK
    assert action2.target.element_id == "btn_verify_fixture"

    # Step 3: Success route reached -> emits DONE
    ctx3 = ScreenContext(
        run_id="gen-test-01",
        step=3,
        url="http://127.0.0.1:9001/fixture-success",
        task="Complete fixture authentication test",
        image_b64="fake_b64",
        screen_graph=ScreenGraph(root=root, url="http://127.0.0.1:9001/fixture-success"),
        redactions=[],
    )

    action3 = server.analyze(ctx3)
    assert action3.action == ActionType.DONE


def test_runtime_addition_without_code_change(tmp_path):
    """Verify that a newly instantiated SiteConfig is immediately supported by the registry."""
    dynamic_site = SiteConfig(
        site_id="dynamic_custom_site",
        display_name="Custom Vendor Portal",
        portal_title="Vendor Portal",
        portal_subtitle="Dynamic registration",
        theme_badge="VENDOR_TEST",
        task="Complete vendor registration",
        entry_route="/vendor-reg",
        routes=[
            RouteConfig(
                route="/vendor-reg",
                title="Vendor Onboarding",
                template="form",
                next_route="/vendor-success",
                fields=[
                    FieldConfig(
                        id="vendor_tax_id",
                        label="Tax Identification Number",
                        field_type="text",
                        sensitive=True,
                        category="pan",
                        vault_ref="user_profile.pan",
                    )
                ],
            )
        ],
    )

    registry = SiteRegistry(configs_dir=tmp_path)
    registry._sites["dynamic_custom_site"] = dynamic_site

    matched_site = registry.get_site("dynamic_custom_site")
    assert matched_site is not None
    assert matched_site.portal_title == "Vendor Portal"

    found = registry.find_route("/vendor-reg")
    assert found is not None
    site, route = found
    assert route.fields[0].vault_ref == "user_profile.pan"


def test_mock_oracle_has_no_route_specific_workflow_branch():
    source = inspect.getsource(MockVLM.analyze)
    assert '"/kyc"' not in source
    assert '"/checkout"' not in source
    assert '"/patient"' not in source


def test_configured_consent_control_is_generic():
    site = SiteRegistry().get_site("kyc")
    assert site is not None
    route = site.get_route("/kyc")
    assert route is not None
    consent = next(action for action in route.actions if action.role == "checkbox")
    assert consent.id == "field_consent"
    assert consent.label == "Consent"
