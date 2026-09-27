import contextlib
import io
import os
import runpy
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


class StartupTests(unittest.TestCase):
    def test_missing_configuration_exits_with_failure(self):
        genai = ModuleType("google.generativeai")
        google = ModuleType("google")
        google.generativeai = genai
        dotenv = ModuleType("dotenv")
        dotenv.load_dotenv = lambda: None
        modules = {"requests": ModuleType("requests"), "google": google,
                   "google.generativeai": genai, "dotenv": dotenv}
        with patch.dict(sys.modules, modules), patch.dict(os.environ, {}, clear=True):
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as error:
                runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"))
        self.assertEqual(error.exception.code, 1)

    def test_configured_module_loads_on_supported_python(self):
        genai = ModuleType("google.generativeai")
        genai.configure = lambda **kwargs: None
        google = ModuleType("google")
        google.generativeai = genai
        dotenv = ModuleType("dotenv")
        dotenv.load_dotenv = lambda: None
        modules = {"requests": ModuleType("requests"), "google": google,
                   "google.generativeai": genai, "dotenv": dotenv}
        with patch.dict(sys.modules, modules), patch.dict(os.environ, {
            "API_KEY": "dummy", "WEBHOOK_URL": "https://example.invalid/webhook"
        }, clear=True):
            result = runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"))
        self.assertTrue(callable(result["main"]))
