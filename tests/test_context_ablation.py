from eval.context_ablation import safe_variant_context
from tests.test_real_vlm import context


def test_context_ablation_removes_graph_and_legend_as_requested():
    base = context()
    screenshot_only = safe_variant_context(base, "screenshot_only")
    graph_only = safe_variant_context(base, "screenshot_graph")
    assert screenshot_only.screen_graph.root.children == []
    assert screenshot_only.redactions == []
    assert graph_only.screen_graph.root.children
    assert graph_only.redactions == []
