"""Single source of truth: ordered map of output filename -> lesson HTML.

Imported by both build.py and build_print.py so the lesson set stays in sync.
"""
import part1, part2, part3, part4, part5, part6, part7, part8
import glossary

CONTENT = {
    "01-what-is-ragas.html": part1.LESSON_01,
    "02-architecture.html": part1.LESSON_02,
    "03-evaluation-lifecycle.html": part1.LESSON_03,
    "04-single-turn-sample.html": part2.LESSON_04,
    "05-multi-turn-sample.html": part2.LESSON_05,
    "06-two-datasets.html": part2.LESSON_06,
    "07-evaluate.html": part2.LESSON_07,
    "08-experiment.html": part2.LESSON_08,
    "09-metrics-overview.html": part3.LESSON_09,
    "10-rag-metrics.html": part3.LESSON_10,
    "11-custom-metrics.html": part3.LESSON_11,
    "12-traditional-metrics.html": part3.LESSON_12,
    "13-metric-base.html": part4.LESSON_13,
    "14-metric-result.html": part4.LESSON_14,
    "15-faithfulness-internals.html": part4.LESSON_15,
    "16-context-metrics-internals.html": part4.LESSON_16,
    "17-answer-metrics-internals.html": part4.LESSON_17,
    "18-agent-metrics-internals.html": part4.LESSON_18,
    "19-prompt-system.html": part5.LESSON_19,
    "20-prompt-advanced.html": part5.LESSON_20,
    "21-llm-abstraction.html": part5.LESSON_21,
    "22-embedding-abstraction.html": part5.LESSON_22,
    "23-executor.html": part5.LESSON_23,
    "24-callbacks-cost-cache.html": part5.LESSON_24,
    "25-testgen-overview.html": part6.LESSON_25,
    "26-knowledge-graph.html": part6.LESSON_26,
    "27-transforms.html": part6.LESSON_27,
    "28-persona-scenario.html": part6.LESSON_28,
    "29-synthesizers.html": part6.LESSON_29,
    "30-testset-generator.html": part6.LESSON_30,
    "31-experiments-deep.html": part7.LESSON_31,
    "32-backends.html": part7.LESSON_32,
    "33-optimization-training.html": part7.LESSON_33,
    "34-integrations-frameworks.html": part7.LESSON_34,
    "35-integrations-observability.html": part7.LESSON_35,
    "36-source-debug-contribute.html": part7.LESSON_36,
    "37-cli.html": part7.LESSON_37,
    "38-capstone.html": part8.LESSON_38,
    "39-glossary.html": glossary.LESSON_GLOSSARY,
}
