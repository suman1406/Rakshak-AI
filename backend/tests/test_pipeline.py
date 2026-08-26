from app.pipeline import PipelineResult, to_diagnosis

def test_high_confidence_has_safe_language():
    result = to_diagnosis(PipelineResult(16, 12, 43, 90, .94, 'moderate', .2))
    assert result['confidence_band'] == 'high'
    assert 'not a confirmed diagnosis' in result['explanation']

def test_low_confidence_is_uncertain():
    result = to_diagnosis(PipelineResult(10, 2, 8, 40, .48, 'uncertain', 0))
    assert result['confidence_band'] == 'low'
    assert result['disease'] == 'uncertain_condition'

