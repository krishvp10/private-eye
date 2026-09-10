# PrivateEye Real-VLM Outbound Packet Privacy Evidence

**Evidence source:** `synthetic_local_harness`
**Live real-VLM traffic verified:** NO
**Run ID:** real-privacy-audit-001
**Secrets Monitored:** 21 distinct credential entities
**Zero-Leak Verified:** YES (100% CLEAN)

### Four-Boundary Wire Inspection

| Vault Reference Key | Local Vault | Outbound Request Wire | Model Response Action | Backend Server Logs | Perimeter Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `user_profile.name` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.full_name` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.email` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.phone` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.aadhaar` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.pan` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.dob` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.password` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.pin` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.address` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.card_number` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.cardholder` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.expiry` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.cvv` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.otp` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.uhid` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.diagnosis` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.prescription` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.doctor` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.insurance_id` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |
| `user_profile.fixture_key` | PRESENT_LOCALLY | ABSENT | ABSENT | ABSENT | ✅ PASS |

### Additional Perimeter Guarantees
- **Raw Screenshots Transmitted:** NO
- **Browser Cookies Transmitted:** NO
- **Authentication Headers Transmitted:** NO
- **Fill Actions Constrained to `value_ref`:** YES

> This artifact validates the local privacy-audit harness with synthetic request/response/log inputs. It is not evidence from a live Qwen request until `live_real_vlm_traffic_verified` is true.
