# Testing Documentation

**Project**: Deepfake Detection System
**Testing Framework**: pytest
**Last Updated**: December 27, 2025

---

## Overview

This document describes the unit test suite for the deepfake detection system. Tests focus on core logic and functionality, with external dependencies (LLM APIs, FFmpeg) appropriately mocked.

**Testing Philosophy**: Tests verify correctness of core algorithms and data transformations without requiring external resources or API calls.

---

## Test Coverage

### Modules Tested

1. **video_processor.py** - Video processing and frame extraction
2. **llm_analyzer.py** - LLM integration and prompt engineering
3. **detector.py** - Detection pipeline orchestration
4. **output_formatter.py** - Result formatting and output

### Coverage Summary

| Module | Test File | Test Classes | Test Methods | Coverage Focus |
|--------|-----------|--------------|--------------|----------------|
| video_processor.py | test_video_processor.py | 5 | 13 | Frame sampling, metadata parsing, validation |
| llm_analyzer.py | test_llm_analyzer.py | 8 | 20 | Prompt construction, response parsing, mock analysis |
| detector.py | test_detector.py | 7 | 14 | Pipeline orchestration, batch processing |
| output_formatter.py | test_output_formatter.py | 6 | 17 | Console/JSON formatting, file operations |

**Total**: 26 test classes, 67 test methods

---

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests for Specific Module

```bash
pytest tests/test_video_processor.py
pytest tests/test_llm_analyzer.py
pytest tests/test_detector.py
pytest tests/test_output_formatter.py
```

### Run Tests with Coverage Report

```bash
pytest --cov=src --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run Specific Test Class or Method

```bash
# Run specific test class
pytest tests/test_video_processor.py::TestFrameSampling

# Run specific test method
pytest tests/test_video_processor.py::TestFrameSampling::test_uniform_sampling_basic
```

---

## What is Tested

### 1. Video Processing (`test_video_processor.py`)

**Frame Sampling Strategies**:
- ✅ Uniform sampling returns correct number of evenly-spaced frames
- ✅ Adaptive sampling emphasizes beginning and end frames
- ✅ Handling edge cases (fewer frames than requested, exact match)

**Video Validation**:
- ✅ Detection of non-existent files
- ✅ Validation of file extension (MP4 only)
- ✅ OpenCV video opening checks

**Metadata Extraction**:
- ✅ FFmpeg metadata parsing (mocked)
- ✅ FPS calculation from fraction strings
- ✅ Error handling for invalid metadata

**Frame Extraction**:
- ✅ Correct number of frames extracted
- ✅ Proper BGR to RGB conversion
- ✅ Handling of empty videos

**Timestamp Calculation**:
- ✅ Timestamp generation for extracted frames
- ✅ Sorted order verification

### 2. LLM Analyzer (`test_llm_analyzer.py`)

**Initialization**:
- ✅ Correct provider setup (mock, anthropic, openai)
- ✅ Prompt template loading
- ✅ Default model selection

**Prompt Management**:
- ✅ All three prompts loaded (frame, temporal, synthesis)
- ✅ Fallback to default inline prompts if files missing
- ✅ Prompt content validation

**Response Parsing**:
- ✅ Classification extraction (REAL, FAKE, LIKELY FAKE, etc.)
- ✅ Confidence score extraction (0-100%)
- ✅ Handling of various response formats
- ✅ Default values when parsing fails

**Image Encoding**:
- ✅ Base64 encoding produces valid strings
- ✅ Correct character set in base64 output

**Mock Analysis**:
- ✅ Frame analysis returns structured results
- ✅ Temporal analysis processes multiple frames
- ✅ Synthesis combines evidence correctly

**Evidence Compilation**:
- ✅ Frame observations aggregated
- ✅ Temporal observations formatted
- ✅ Evidence structure validated

### 3. Detector (`test_detector.py`)

**Initialization**:
- ✅ Default and custom parameter handling
- ✅ Factory function creates valid detector
- ✅ LLM analyzer properly initialized

**Frame Selection**:
- ✅ Key frames include first and last
- ✅ Frames are sorted in order
- ✅ No duplicate frame indices
- ✅ Handling when total frames < max frames

**Detection Pipeline**:
- ✅ Successful end-to-end detection (mocked)
- ✅ Invalid video handling
- ✅ Exception handling in pipeline
- ✅ Result structure validation

**Batch Processing**:
- ✅ Multiple videos processed
- ✅ Individual failures don't stop batch
- ✅ Error recording for failed videos

**Result Structure**:
- ✅ All required fields present
- ✅ Classification values are valid
- ✅ Confidence in correct range (0-100)

### 4. Output Formatter (`test_output_formatter.py`)

**Console Formatting**:
- ✅ Report contains all required elements
- ✅ Proper structure with section markers
- ✅ Detailed report includes evidence sections

**JSON Formatting**:
- ✅ Valid JSON output
- ✅ Correct structure (video_path, metadata, detection, analysis, system)
- ✅ Pretty vs. compact formatting
- ✅ Unicode handling

**File Operations**:
- ✅ JSON saved to file correctly
- ✅ Text report saved to file
- ✅ Parent directories created automatically

**Summary Formatting**:
- ✅ Concise single-line summaries
- ✅ All classification types handled

**Emoji Helpers**:
- ✅ Correct emoji for each classification
- ✅ Case-insensitive mapping

**Edge Cases**:
- ✅ Missing optional fields handled gracefully
- ✅ None values don't cause errors
- ✅ Unicode characters preserved

---

## What is NOT Tested

These areas are intentionally excluded from unit tests:

### 1. External API Calls

**Not Tested**:
- Actual Anthropic Claude API calls
- Actual OpenAI GPT-4V API calls
- Real LLM responses

**Reason**:
- API calls incur costs
- Tests would be slow and unreliable
- Network dependency unacceptable for unit tests

**Alternative**: Mock provider is tested instead, which validates integration logic.

### 2. FFmpeg Binary Execution

**Not Tested**:
- Real FFmpeg metadata extraction
- Actual video file processing
- Codec-specific behavior

**Reason**:
- Requires FFmpeg installation
- Requires sample video files
- Platform-dependent behavior

**Alternative**: FFmpeg calls are mocked; response parsing is tested.

### 3. OpenCV Video Reading

**Not Tested**:
- Actual video file opening
- Real frame decoding
- Codec compatibility

**Reason**:
- Requires video files in repository
- Platform-dependent behavior
- Focus on logic, not library functionality

**Alternative**: OpenCV calls are mocked; frame processing logic is tested.

### 4. End-to-End Integration

**Not Tested**:
- Full pipeline with real videos and real LLM APIs
- Actual deepfake detection accuracy
- Performance benchmarks

**Reason**:
- Requires test videos (not yet in repository)
- Requires API access and costs
- Integration testing is separate from unit testing

**Alternative**:
- Integration testing can be performed manually
- Mock mode provides integration validation
- Pipeline orchestration is tested with mocks

### 5. Prompt Effectiveness

**Not Tested**:
- Quality of prompts in guiding LLM
- Actual artifact detection accuracy
- Reasoning quality of LLM outputs

**Reason**:
- Requires evaluation with real videos and LLMs
- Subjective quality assessment
- Beyond scope of unit tests

**Alternative**: Prompt structure and loading is verified; effectiveness measured in evaluation phase.

---

## Test Organization

### Test File Structure

```
tests/
├── __init__.py                    # Test package initialization
├── test_video_processor.py        # Video processing tests
├── test_llm_analyzer.py           # LLM analyzer tests
├── test_detector.py               # Detector orchestration tests
└── test_output_formatter.py       # Output formatting tests
```

### Test Class Naming

Tests are organized into classes by functionality:

```python
class TestFrameSampling:          # Tests for frame sampling logic
class TestVideoValidation:        # Tests for video validation
class TestMetadataExtraction:     # Tests for metadata extraction
...
```

### Test Method Naming

Test methods follow the pattern: `test_<functionality>_<scenario>`

Examples:
- `test_uniform_sampling_basic` - Basic uniform sampling
- `test_format_json_valid` - JSON formatting produces valid JSON
- `test_detect_invalid_video` - Detection handles invalid videos

---

## Mocking Strategy

### Why Mocking?

Unit tests should be:
- **Fast**: No network calls or slow I/O
- **Deterministic**: Same input always produces same output
- **Isolated**: Test one component at a time
- **Independent**: No external dependencies

### What is Mocked?

1. **subprocess.run** - FFmpeg calls
2. **cv2.VideoCapture** - OpenCV video reading
3. **LLM API clients** - Anthropic/OpenAI API calls
4. **VideoProcessor** - In detector tests
5. **OutputFormatter** - In detector integration tests

### Mocking Tools

- `unittest.mock.Mock` - Basic mocking
- `unittest.mock.MagicMock` - Mocking with magic methods
- `unittest.mock.patch` - Patching functions/classes
- `pytest.fixture` - Reusable test data

### Example Mocking Pattern

```python
@patch('subprocess.run')
def test_extract_metadata_success(self, mock_run):
    # Mock FFmpeg response
    mock_run.return_value = Mock(stdout=json.dumps({...}))

    # Test actual code
    processor = VideoProcessor("/fake/video.mp4")
    metadata = processor.extract_metadata()

    # Assert results
    assert metadata['width'] == 1920
```

---

## Test Data

### Fixtures

Sample data is provided via pytest fixtures:

```python
@pytest.fixture
def sample_results():
    """Sample detection results for testing."""
    return {
        'classification': 'LIKELY FAKE',
        'confidence': 75,
        ...
    }
```

### Temporary Files

Tests use pytest's `tmp_path` fixture for file I/O:

```python
def test_save_json(self, sample_results, tmp_path):
    output_file = tmp_path / "result.json"
    OutputFormatter.save_json(sample_results, str(output_file))
    assert output_file.exists()
```

---

## Running Tests in CI/CD

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Test Maintenance

### Adding New Tests

When adding new functionality:

1. Write tests first (TDD) or alongside code
2. Follow existing naming conventions
3. Mock external dependencies
4. Add test to appropriate test file
5. Update this documentation

### Updating Tests

When modifying code:

1. Update corresponding tests
2. Ensure tests still pass
3. Add tests for new edge cases
4. Maintain or improve coverage

---

## Coverage Goals

### Current Coverage

Run `pytest --cov=src` to see current coverage.

**Achieved Coverage** (as of December 29, 2025):
- **Overall**: 81% coverage
- **detector.py**: 96% coverage
- **output_formatter.py**: 92% coverage
- **llm_analyzer.py**: 77% coverage
- **video_processor.py**: 69% coverage

### Target Coverage

- **Core modules**: 60-70% coverage ✅ **EXCEEDED** (achieved 81%)
- **Utility modules**: 50-60% coverage
- **Integration**: Tested via mocks

### Coverage Interpretation

**High coverage ≠ Perfect tests**, but:
- Ensures core functionality is exercised
- Catches regressions
- Documents expected behavior

---

## Common Issues

### Issue: Tests fail with "ModuleNotFoundError"

**Solution**: Install test dependencies
```bash
pip install -r requirements.txt
```

### Issue: Tests fail with import errors

**Solution**: Run pytest from project root
```bash
cd /path/to/deepfake-detection
pytest
```

### Issue: Mocking doesn't work as expected

**Solution**: Check patch path is correct
```python
# Patch where it's used, not where it's defined
@patch('src.detector.VideoProcessor')  # Correct
@patch('src.video_processor.VideoProcessor')  # Wrong for detector tests
```

---

## Future Testing Enhancements

### Potential Additions

1. **Integration Tests**:
   - Test full pipeline with mock videos
   - Test with small sample videos in repository

2. **Performance Tests**:
   - Benchmark frame extraction speed
   - Measure memory usage

3. **Property-Based Tests**:
   - Use hypothesis for random input testing
   - Verify invariants hold for all inputs

4. **Regression Tests**:
   - Save known outputs
   - Ensure changes don't break previous behavior

---

## Test Quality Guidelines

### Good Test Characteristics

- ✅ **Clear**: Test name explains what is tested
- ✅ **Focused**: One concept per test
- ✅ **Independent**: Tests don't depend on each other
- ✅ **Deterministic**: Same results every time
- ✅ **Fast**: Runs in milliseconds

### Test Code Quality

- Use descriptive variable names
- Add comments for complex setups
- Keep tests simple and readable
- Follow DRY principle with fixtures

---

## Resources

### pytest Documentation

- [Official pytest docs](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [pytest mocking](https://docs.pytest.org/en/stable/monkeypatch.html)

### unittest.mock Documentation

- [Official mock docs](https://docs.python.org/3/library/unittest.mock.html)
- [Mock object documentation](https://docs.python.org/3/library/unittest.mock.html#the-mock-class)

---

## Summary

The test suite provides:
- ✅ **Confidence**: Core functionality is verified
- ✅ **Regression Protection**: Changes won't break existing features
- ✅ **Documentation**: Tests show how code should be used
- ✅ **Maintainability**: Safe refactoring with test coverage

**Run tests regularly** to ensure system correctness and catch issues early.

---

**Last Updated**: December 27, 2025
**Test Framework**: pytest 7.4.0+
**Python Version**: 3.9+
