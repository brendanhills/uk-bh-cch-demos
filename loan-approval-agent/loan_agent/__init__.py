# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Loan Approval Agent package."""

import os
import google.auth

# CRITICAL: To avoid 404 errors in this environment (matching gemini_3.py success),
# we must unset these environment variables before the genai client is initialized.
os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
os.environ.pop("GOOGLE_CLOUD_LOCATION", None)

# Set these so the SDK defaults to Vertex AI correctly
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

from .agent import loan_manager

__all__ = ["loan_manager"]
