load("//devtools/python/blaze:pytype.bzl", "pytype_strict_binary", "pytype_strict_contrib_test", "pytype_strict_library")
load("//learning/gemini/agents/skill_rules:skills.bzl", "agent_skill")
load("//learning/gemini/agents/skills/skill_creator/scripts:skill_defs.bzl", "validate_skill_test")

package(default_visibility = [
    "//learning/gemini/agents:__subpackages__",
    "//net/slo:__subpackages__",
])

validate_skill_test(
    name = "validate_spec_drift_detector_skill_test",
    with_mdformat = True,
)

agent_skill(
    name = "spec_drift_detector",
    srcs = [
        "SKILL.md",
        "spec_mappings.json",
    ],
    scripts = [
        "scripts/drift_detector.py",
    ],
)

pytype_strict_library(
    name = "drift_detector_lib",
    srcs = ["scripts/drift_detector.py"],
    visibility = ["//visibility:private"],
)

pytype_strict_binary(
    name = "drift_detector",
    srcs = ["scripts/drift_detector_main.py"],
    main = "scripts/drift_detector_main.py",
    deps = [
        ":drift_detector_lib",
    ],
)

pytype_strict_contrib_test(
    name = "drift_detector_test",
    srcs = ["scripts/drift_detector_test.py"],
    deps = [
        ":drift_detector_lib",
        "//third_party/py/absl/testing:absltest",
    ],
)
