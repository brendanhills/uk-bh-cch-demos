load("//devtools/python/blaze:pytype.bzl", "pytype_strict_library")
load("//learning/gemini/agents/skill_rules:skills.bzl", "agent_skill")
load("//learning/gemini/agents/skills/skill_creator/scripts:skill_defs.bzl", "validate_skill_test")

package(default_visibility = ["//learning/gemini/agents/skills:__subpackages__"])

agent_skill(
    name = "c4astart",
    srcs = [
        "SKILL.md",
        "references/upload_guide.md",
        "scripts/get_application.py",
        "scripts/upload_zip.py",
    ],
)

validate_skill_test(
    name = "validate_c4astart_skill_test",
)

pytype_strict_library(
    name = "scripts/get_application",
    srcs = ["scripts/get_application.py"],
)

pytype_strict_library(
    name = "scripts/upload_zip",
    srcs = ["scripts/upload_zip.py"],
)
