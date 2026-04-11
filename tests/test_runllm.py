from runllm import parse_llm_response


def test_parse_llm_response_valid_json():
    content = '{"summary": {"overallToneAssessment": "cautious outlook"}}'
    result = parse_llm_response(content)
    assert isinstance(result, dict)
    assert result["summary"]["overallToneAssessment"] == "cautious outlook"


def test_parse_llm_response_json_embedded_in_text():
    content = 'Here is my analysis:\n{"summary": {"overallToneAssessment": "positive"}}\nEnd.'
    result = parse_llm_response(content)
    assert isinstance(result, dict)
    assert result["summary"]["overallToneAssessment"] == "positive"


def test_parse_llm_response_plain_text_returns_string():
    content = "This is plain text with no JSON structure at all."
    result = parse_llm_response(content)
    assert isinstance(result, str)
    assert result == content


def test_parse_llm_response_malformed_json_returns_string():
    content = '{"summary": {"overallToneAssessment": missing_quotes}}'
    result = parse_llm_response(content)
    assert isinstance(result, str)
