"""
Deterministic Mock VLM for PrivateEye.
Allows 100% offline, GPU-free integration and testing of the end-to-end KYC flow.
The mock VLM inspects the current URL, screen graph, and step to return the next AgentAction.
"""

from typing import Optional
from shared.protocol import (
    ActionTarget,
    ActionType,
    AgentAction,
    ScreenContext,
)


class MockVLM:
    """Simulates an intelligent VLM reasoning over sanitized context."""

    def __init__(self) -> None:
        self.step_counter = 0

    def analyze(self, context: ScreenContext) -> AgentAction:
        url = context.url.lower()
        self.step_counter += 1

        # Route 1: Login Page
        if "/login" in url:
            # The demo login ships with deterministic synthetic credentials already
            # present, so a single semantic click advances the workflow.
            return AgentAction(
                action=ActionType.CLICK,
                target=ActionTarget(kind="a11y", role="button", name="Sign In", element_id="btn_login"),
                reason="Credentials already prefilled or automated single-click login.",
            )

        # Route 2: KYC Form Page
        if "/kyc" in url:
            # Step through the form or submit once filled
            # Deterministic KYC workflow sequence based on step
            if context.step <= 1:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Full Name", element_id="field_name"),
                    value_ref="user_profile.name",
                    reason="Fill required Name field from local vault.",
                )
            elif context.step == 2:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Email Address", element_id="field_email"),
                    value_ref="user_profile.email",
                    reason="Fill required Email field from local vault.",
                )
            elif context.step == 3:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Phone Number", element_id="field_phone"),
                    value_ref="user_profile.phone",
                    reason="Fill required Phone field from local vault.",
                )
            elif context.step == 4:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Aadhaar Number", element_id="field_aadhaar"),
                    value_ref="user_profile.aadhaar",
                    reason="Fill required Aadhaar field from local vault.",
                )
            elif context.step == 5:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="PAN Number", element_id="field_pan"),
                    value_ref="user_profile.pan",
                    reason="Fill required PAN field from local vault.",
                )
            elif context.step == 6:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Date of Birth", element_id="field_dob"),
                    value_ref="user_profile.dob",
                    reason="Fill date of birth from local vault.",
                )
            elif context.step == 7:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Security PIN", element_id="field_pin"),
                    value_ref="user_profile.pin",
                    reason="Fill security PIN from local vault.",
                )
            elif context.step == 8:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Residential Address", element_id="field_address"),
                    value_ref="user_profile.address",
                    reason="Fill address from local vault.",
                )
            elif context.step == 9:
                return AgentAction(
                    action=ActionType.CLICK,
                    target=ActionTarget(kind="a11y", role="checkbox", name="Consent", element_id="field_consent"),
                    reason="Agree to terms and consent checkbox.",
                )
            else:
                return AgentAction(
                    action=ActionType.CLICK,
                    target=ActionTarget(kind="a11y", role="button", name="Submit Application", element_id="btn_submit"),
                    reason="All KYC inputs completed; proceed to submission.",
                )

        # Route 3: Checkout Page (Banking & Financial)
        if "/checkout" in url:
            if context.step <= 1:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Card Number", element_id="field_card_number"),
                    value_ref="user_profile.card_number",
                    reason="Fill card number securely using local vault reference.",
                )
            elif context.step == 2:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Cardholder Name", element_id="field_cardholder"),
                    value_ref="user_profile.cardholder",
                    reason="Fill cardholder name from local vault.",
                )
            elif context.step == 3:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Expiration Date", element_id="field_expiry"),
                    value_ref="user_profile.expiry",
                    reason="Fill card expiry date from local vault.",
                )
            elif context.step == 4:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Security Code", element_id="field_cvv"),
                    value_ref="user_profile.cvv",
                    reason="Fill card CVV securely from local vault.",
                )
            elif context.step == 5:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="One-Time Password", element_id="field_otp"),
                    value_ref="user_profile.otp",
                    reason="Fill transaction OTP securely from local vault.",
                )
            else:
                return AgentAction(
                    action=ActionType.CLICK,
                    target=ActionTarget(kind="a11y", role="button", name="Pay", element_id="btn_pay"),
                    reason="All checkout fields filled; proceed to payment authorization.",
                )

        # Route 4: Patient Admission Page (Healthcare & Medical)
        if "/patient" in url:
            if context.step <= 1:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Universal Health ID", element_id="field_uhid"),
                    value_ref="user_profile.uhid",
                    reason="Fill ABHA/UHID identifier from local vault.",
                )
            elif context.step == 2:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Patient Full Name", element_id="field_patient_name"),
                    value_ref="user_profile.name",
                    reason="Fill patient name from local vault.",
                )
            elif context.step == 3:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Date of Birth", element_id="field_dob"),
                    value_ref="user_profile.dob",
                    reason="Fill patient DOB from local vault.",
                )
            elif context.step == 4:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Emergency Contact Number", element_id="field_phone"),
                    value_ref="user_profile.phone",
                    reason="Fill emergency contact phone number from local vault.",
                )
            elif context.step == 5:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Clinical Diagnosis", element_id="field_diagnosis"),
                    value_ref="user_profile.diagnosis",
                    reason="Fill clinical diagnosis from local vault.",
                )
            elif context.step == 6:
                return AgentAction(
                    action=ActionType.FILL,
                    target=ActionTarget(kind="a11y", role="textbox", name="Active Medications", element_id="field_prescription"),
                    value_ref="user_profile.prescription",
                    reason="Fill active medications and prescription from local vault.",
                )
            else:
                return AgentAction(
                    action=ActionType.CLICK,
                    target=ActionTarget(kind="a11y", role="button", name="Confirm Clinical Admission", element_id="btn_admit_patient"),
                    reason="Patient intake form complete; proceed with admission.",
                )

        # Route 5: Success Page
        if "/success" in url:
            return AgentAction(
                action=ActionType.DONE,
                reason="Target workflow completed successfully. Verification confirmed.",
            )

        # Fallback default
        return AgentAction(
            action=ActionType.DONE,
            reason=f"Reached unhandled page: {context.url}",
        )
