from nodes.flow_error_analyser import flow_error_analyser


def test_flow_error_analyser_imports():
    assert callable(flow_error_analyser)
