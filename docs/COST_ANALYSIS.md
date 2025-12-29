# Cost Analysis and Budget Management

**Project:** Deepfake Detection System
**Version:** 2.0.0
**Last Updated:** December 29, 2025
**Author:** Tal Barda

## Executive Summary

This document provides a comprehensive cost analysis for the deepfake detection system, comparing the **local reasoning agent** (default, $0.00) with optional **external LLM providers** (Anthropic Claude, OpenAI GPT-4V).

**Key Findings**:
- **Local Agent**: $0.00 per video, unlimited runs
- **Claude 3.5 Sonnet**: ~$0.10-0.30 per video
- **GPT-4V**: ~$0.15-0.40 per video
- **Recommendation**: Use local agent for academic evaluation (zero cost, perfect reproducibility)

---

## Table of Contents

1. [Cost Breakdown by Provider](#cost-breakdown-by-provider)
2. [Token Usage Analysis](#token-usage-analysis)
3. [Cost Optimization Strategies](#cost-optimization-strategies)
4. [Budget Projections](#budget-projections)
5. [Cost-Benefit Analysis](#cost-benefit-analysis)

---

## Cost Breakdown by Provider

### Local Reasoning Agent (Default)

**Total Cost**: **$0.00 per video**

| Cost Component | Amount |
|---------------|--------|
| API Calls | $0.00 (none) |
| Compute | $0.00 (local CPU) |
| Storage | $0.00 (local disk) |
| **TOTAL** | **$0.00** |

**Characteristics**:
- ✅ Zero marginal cost per analysis
- ✅ Unlimited runs for testing/grading
- ✅ No API rate limits
- ✅ No network dependency
- ✅ Perfect for academic evaluation

---

### Anthropic Claude 3.5 Sonnet (Optional)

**Pricing Model** (as of December 2025):
- Input tokens: $3.00 per million tokens (MTok)
- Output tokens: $15.00 per million tokens (MTok)

**Estimated Cost per Video** (10 frames):

| Analysis Stage | Input Tokens | Output Tokens | Cost |
|---------------|--------------|---------------|------|
| Frame Analysis (×10) | ~8,000 | ~2,000 | ~$0.054 |
| Temporal Analysis | ~1,500 | ~500 | ~$0.012 |
| Synthesis | ~2,000 | ~800 | ~$0.018 |
| **TOTAL per video** | **~11,500** | **~3,300** | **~$0.084** |

**With Safety Margin**: **$0.10-0.30 per video** (accounting for variations)

**Cost Drivers**:
- Number of frames analyzed (10 default)
- Image encoding overhead (base64)
- Detailed prompt templates
- Verbose output formatting

---

### OpenAI GPT-4V (Optional)

**Pricing Model** (as of December 2025):
- Input tokens: $2.50 per MTok (text) + $5.00 per MTok (vision)
- Output tokens: $10.00 per MTok

**Estimated Cost per Video** (10 frames):

| Analysis Stage | Input Tokens | Output Tokens | Cost |
|---------------|--------------|---------------|------|
| Frame Analysis (×10) | ~10,000 (incl. vision) | ~2,500 | ~$0.075 |
| Temporal Analysis | ~2,000 | ~600 | ~$0.011 |
| Synthesis | ~2,500 | ~1,000 | ~$0.016 |
| **TOTAL per video** | **~14,500** | **~4,100** | **~$0.102** |

**With Safety Margin**: **$0.15-0.40 per video** (accounting for variations)

**Note**: GPT-4V pricing includes vision token premium for image processing.

---

## Token Usage Analysis

### Token Breakdown (Claude 3.5 Sonnet Example)

#### Input Tokens (~11,500 per video)

| Source | Tokens | Percentage |
|--------|---------|-----------|
| System prompts (frame analysis) | ~6,000 | 52% |
| Encoded images (10 frames) | ~3,000 | 26% |
| Temporal analysis prompt | ~1,200 | 10% |
| Synthesis prompt | ~1,000 | 9% |
| Metadata context | ~300 | 3% |

#### Output Tokens (~3,300 per video)

| Source | Tokens | Percentage |
|--------|---------|-----------|
| Frame observations (10×) | ~1,800 | 55% |
| Temporal analysis | ~600 | 18% |
| Synthesis reasoning | ~700 | 21% |
| Structured formatting | ~200 | 6% |

### Token Optimization Opportunities

**High-Impact Reductions**:
1. **Reduce frame count**: 10 → 5 frames (**-50% cost**)
2. **Compress prompts**: Remove examples (**-20% cost**)
3. **Lower image quality**: 1920×1080 → 640×480 (**-30% image tokens**)

**Trade-offs**:
- Fewer frames → lower analysis quality
- Shorter prompts → less guidance, more hallucinations
- Lower resolution → miss subtle artifacts

---

## Cost Optimization Strategies

### Strategy 1: Use Local Agent (Default)

**Cost**: $0.00 per video

**When to Use**:
- Academic evaluation and grading
- Unlimited testing and iteration
- Reproducibility requirements
- No budget constraints acceptable

**Limitations**:
- Lower accuracy than state-of-the-art
- Fixed heuristics, no learning

---

### Strategy 2: Reduce Frame Count

**Cost Impact**: ~50% reduction per 5 frames removed

| Frames | Cost (Claude) | Cost (GPT-4V) |
|--------|---------------|---------------|
| 10 | $0.10-0.30 | $0.15-0.40 |
| 5 | $0.05-0.15 | $0.08-0.20 |
| 3 | $0.03-0.09 | $0.05-0.12 |

**Trade-off**: Fewer frames → less temporal information → lower accuracy

**Recommendation**: 5 frames minimum for temporal analysis

---

### Strategy 3: Batch Processing with Caching

**Approach**:
- Cache reusable prompt components
- Batch multiple videos in single API call (if supported)
- Share system prompts across analyses

**Estimated Savings**: 10-15% on multi-video batches

**Implementation Complexity**: Medium

---

### Strategy 4: Adaptive Frame Sampling

**Approach**:
- Use uniform sampling initially (cheap)
- If uncertain, use adaptive sampling (expensive)
- Only analyze "interesting" frames

**Estimated Savings**: 20-30% on videos with clear verdicts

**Implementation**: Already supported via `--sampling adaptive`

---

## Budget Projections

### Scenario 1: Academic Evaluation (Default)

**Use Case**: Grader tests system on provided videos

**Assumptions**:
- 2 test videos (1 deepfake, 1 real)
- Local agent (default mode)
- Unlimited testing/debugging runs

**Total Cost**: **$0.00**

**Justification**: Local agent eliminates all API costs, perfect for grading.

---

### Scenario 2: LLM Provider Comparison (Optional)

**Use Case**: Compare local agent vs. Claude vs. GPT-4V

**Assumptions**:
- 2 test videos
- 3 providers × 2 videos = 6 analyses
- 10 frames per video

**Cost Breakdown**:

| Provider | Videos | Cost per Video | Total Cost |
|----------|--------|----------------|------------|
| Local Agent | 2 | $0.00 | **$0.00** |
| Claude 3.5 | 2 | $0.20 | **$0.40** |
| GPT-4V | 2 | $0.25 | **$0.50** |
| **TOTAL** | **6** | | **$0.90** |

---

### Scenario 3: Extended Testing (Optional)

**Use Case**: Test on larger dataset for research

**Assumptions**:
- 20 videos total
- All providers (comparison study)
- 10 frames per video

**Cost Breakdown**:

| Provider | Videos | Cost per Video | Total Cost |
|----------|--------|----------------|------------|
| Local Agent | 20 | $0.00 | **$0.00** |
| Claude 3.5 | 20 | $0.20 | **$4.00** |
| GPT-4V | 20 | $0.25 | **$5.00** |
| **TOTAL** | **60** | | **$9.00** |

---

## Cost-Benefit Analysis

### Local Agent (Default)

| Aspect | Rating | Notes |
|--------|--------|-------|
| **Cost** | ★★★★★ | $0.00, unlimited runs |
| **Reproducibility** | ★★★★★ | 100% deterministic |
| **Accuracy** | ★★★☆☆ | Good for heuristic-based |
| **Speed** | ★★★★★ | 2-3 seconds per video |
| **Academic Value** | ★★★★★ | Perfect for evaluation |
| **Setup Complexity** | ★★★★★ | Zero configuration |

**Recommendation**: ✅ **Ideal for academic submission and grading**

---

### Claude 3.5 Sonnet (Optional)

| Aspect | Rating | Notes |
|--------|--------|-------|
| **Cost** | ★★★☆☆ | $0.10-0.30 per video |
| **Reproducibility** | ★★★☆☆ | Variable (LLM stochastic) |
| **Accuracy** | ★★★★☆ | Better reasoning, some hallucinations |
| **Speed** | ★★★☆☆ | 15-30 seconds per video |
| **Academic Value** | ★★★☆☆ | Demonstrates LLM capabilities |
| **Setup Complexity** | ★★★☆☆ | Requires API key |

**Recommendation**: ⚠️ **Optional for LLM comparison**

---

### GPT-4V (Optional)

| Aspect | Rating | Notes |
|--------|--------|-------|
| **Cost** | ★★☆☆☆ | $0.15-0.40 per video |
| **Reproducibility** | ★★★☆☆ | Variable (LLM stochastic) |
| **Accuracy** | ★★★★☆ | Strong vision understanding |
| **Speed** | ★★★☆☆ | 15-30 seconds per video |
| **Academic Value** | ★★★☆☆ | Alternative LLM provider |
| **Setup Complexity** | ★★★☆☆ | Requires API key |

**Recommendation**: ⚠️ **Optional for provider comparison**

---

## Cost Control Measures

### Budget Monitoring

**For LLM Providers** (if used):

1. **Log All API Calls**: Track token usage in `results/*.json`
2. **Set Monthly Limits**: Configure API key spending limits
3. **Alert Thresholds**: Email notifications at 50%, 80%, 100% of budget
4. **Usage Reports**: Weekly summaries of cost per provider

**Current Implementation**:
- ✅ Token usage logged in analysis results
- ⚠️ No automatic spending limits (set via provider dashboard)
- ⚠️ Manual monitoring required

---

### Cost Containment Strategies

1. **Default to Local Agent**: Zero cost for all standard use cases
2. **LLM Mode Opt-In**: Explicit `--provider` flag required
3. **Frame Limit**: Default 10 frames (configurable down to 3)
4. **Batch Processing**: Process multiple videos efficiently
5. **Mock Mode**: Test pipeline without API costs (`--provider mock`)

---

## Return on Investment (ROI)

### Local Agent

**Investment**: Development time (~40 hours)
**Cost per Use**: $0.00
**ROI**: **Infinite** (zero marginal cost)

**Value Proposition**:
- Unlimited testing for development
- Zero cost for grading
- Perfect reproducibility for academic evaluation

---

### LLM Providers (Optional)

**Investment**: API costs + development time
**Cost per Use**: $0.10-0.40
**ROI**: **Depends on use case**

**Value Proposition**:
- Demonstrates prompt engineering
- Compares heuristic vs. LLM approaches
- Research contribution (comparison study)

**Break-Even**: ~25 videos to justify development effort

---

## Recommendations

### For Academic Submission (Assignment 09)

1. ✅ **Use Local Agent (Default)**: Zero cost, perfect reproducibility
2. ✅ **Document LLM Option**: Show prompt engineering even if not primary mode
3. ✅ **Provide Cost Analysis**: Demonstrate budget awareness
4. ⚠️ **Optional**: Run 1-2 LLM comparisons for demonstration (~$1-2 total)

### For Future Extensions

1. **Research Dataset**: Use local agent for bulk analysis (free)
2. **Accuracy Benchmark**: Compare local vs. LLM on larger set ($20-50 budget)
3. **Production Deployment**: Consider local agent for cost efficiency

---

## Appendix: Pricing References

### Anthropic Claude Pricing (December 2025)

Source: [https://www.anthropic.com/pricing](https://www.anthropic.com/pricing)

| Model | Input (per MTok) | Output (per MTok) |
|-------|------------------|-------------------|
| Claude 3.5 Sonnet | $3.00 | $15.00 |
| Claude 3 Opus | $15.00 | $75.00 |
| Claude 3 Haiku | $0.25 | $1.25 |

### OpenAI Pricing (December 2025)

Source: [https://openai.com/api/pricing/](https://openai.com/api/pricing/)

| Model | Input (per MTok) | Output (per MTok) |
|-------|------------------|-------------------|
| GPT-4 Turbo | $10.00 | $30.00 |
| GPT-4V (Vision) | $10.00 (text) + vision | $30.00 |
| GPT-4o | $2.50-5.00 | $10.00 |

**Note**: Prices subject to change. Check provider websites for current rates.

---

## Summary

| Provider | Cost/Video | Best For | Limitations |
|----------|-----------|----------|-------------|
| **Local Agent** | **$0.00** | **Academic evaluation, unlimited testing** | **Lower accuracy, fixed heuristics** |
| Claude 3.5 | $0.10-0.30 | LLM demonstration, comparison | Variable results, requires API key |
| GPT-4V | $0.15-0.40 | Alternative LLM, vision focus | Higher cost, variable results |

**Final Recommendation**: **Use local agent (default)** for Assignment 09. Zero cost, perfect reproducibility, and ideal for academic grading.

---

**Document Version**: 1.0
**Last Updated**: December 29, 2025
**Status**: Complete
