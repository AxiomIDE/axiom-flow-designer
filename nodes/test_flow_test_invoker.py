from nodes.flow_test_invoker import flow_test_invoker


def test_flow_test_invoker_imports():
    assert callable(flow_test_invoker)
