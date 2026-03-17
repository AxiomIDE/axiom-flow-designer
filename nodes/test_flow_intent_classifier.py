from nodes.flow_intent_classifier import flow_intent_classifier


def test_flow_intent_classifier_imports():
    assert callable(flow_intent_classifier)
