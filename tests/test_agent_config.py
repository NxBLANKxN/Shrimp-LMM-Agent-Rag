import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class AgentConfigTests(unittest.TestCase):
    def tearDown(self):
        for module_name in [
            "agent",
            "lmm",
            "transformers",
            "langchain_huggingface",
            "deepagents",
            "deepagents.backends",
            "deepagents.backends.filesystem",
        ]:
            sys.modules.pop(module_name, None)

    def test_agent_registers_memory_and_skills(self):
        calls = {}

        def fake_pipeline(*args, **kwargs):
            calls["pipeline"] = {"args": args, "kwargs": kwargs}
            return "fake_pipeline"

        class FakeHuggingFacePipeline:
            def __init__(self, pipeline):
                self.pipeline = pipeline

        class FakeChatHuggingFace:
            def __init__(self, llm):
                self.llm = llm

        class FakeFilesystemBackend:
            def __init__(self, root_dir):
                self.root_dir = root_dir

        def fake_create_deep_agent(**kwargs):
            calls["create_deep_agent"] = kwargs
            return types.SimpleNamespace(invoke=lambda payload: payload)

        fake_transformers = types.ModuleType("transformers")
        fake_transformers.pipeline = fake_pipeline

        fake_langchain_huggingface = types.ModuleType("langchain_huggingface")
        fake_langchain_huggingface.HuggingFacePipeline = FakeHuggingFacePipeline
        fake_langchain_huggingface.ChatHuggingFace = FakeChatHuggingFace

        fake_deepagents = types.ModuleType("deepagents")
        fake_deepagents.create_deep_agent = fake_create_deep_agent

        fake_deepagents_backends = types.ModuleType("deepagents.backends")
        fake_deepagents_filesystem = types.ModuleType("deepagents.backends.filesystem")
        fake_deepagents_filesystem.FilesystemBackend = FakeFilesystemBackend

        fake_lmm = types.ModuleType("lmm")
        fake_lmm.model = object()
        fake_lmm.processor = types.SimpleNamespace(tokenizer="fake_tokenizer")

        with mock.patch.dict(
            sys.modules,
            {
                "transformers": fake_transformers,
                "langchain_huggingface": fake_langchain_huggingface,
                "deepagents": fake_deepagents,
                "deepagents.backends": fake_deepagents_backends,
                "deepagents.backends.filesystem": fake_deepagents_filesystem,
                "lmm": fake_lmm,
            },
            clear=False,
        ):
            sys.modules.pop("agent", None)
            importlib.import_module("agent")

        create_kwargs = calls["create_deep_agent"]
        self.assertEqual(create_kwargs["memory"], ["/.deepagents/AGENTS.md"])
        self.assertEqual(create_kwargs["skills"], ["/.deepagents/skills/"])
        self.assertEqual(create_kwargs["system_prompt"], "請善用工具來回答使用者的問題。")
        self.assertEqual(create_kwargs["backend"].root_dir, str(PROJECT_ROOT))
        self.assertEqual(
            [tool.__name__ for tool in create_kwargs["tools"]],
            ["search_local_data", "calculate_math"],
        )
        self.assertEqual(calls["pipeline"]["args"][0], "text-generation")

    def test_deepagents_files_follow_expected_names(self):
        agents_path = PROJECT_ROOT / ".deepagents" / "AGENTS.md"
        skill_path = PROJECT_ROOT / ".deepagents" / "skills" / "calculator" / "SKILL.md"

        self.assertTrue(agents_path.exists())
        self.assertTrue(skill_path.exists())

        skill_text = skill_path.read_text(encoding="utf-8")
        self.assertTrue(skill_text.startswith("---"))
        self.assertIn("name: calculator", skill_text)
        self.assertIn("description:", skill_text)


if __name__ == "__main__":
    unittest.main()
