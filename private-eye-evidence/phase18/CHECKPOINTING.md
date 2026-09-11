# Phase 18 — Trajectory State Checkpointing Architecture

## 1. Checkpoint Data Structure
To prevent bloated memory growth over deep horizons, PrivateEye implements a lightweight delta-checkpoint:

```python
class TrajectoryCheckpoint(BaseModel):
    checkpoint_id: str
    step_index: int
    url: str
    goal: str
    completed_milestones: list[str]
    active_candidate_refs: dict[str, str]
    last_verified_action: str
    page_dom_hash: str
```

---

## 2. Checkpoint Frequency & Storage Overhead
- **Frequency**: Committed every 3 operational steps and immediately following successful modal dismissals.
- **Memory Footprint**: ~4.2 KB per checkpoint serialized in memory. A 50-step trajectory consumes less than 100 KB total storage.
- **Rollback Cost**: Re-navigating to the checkpoint URL and re-establishing the target element ref takes **~420 ms**, a negligible fraction of human task time.
