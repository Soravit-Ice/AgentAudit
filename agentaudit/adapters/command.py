import asyncio
import json
import shlex
import subprocess
import time
from typing import Any

from agentaudit.adapters.base import BaseAdapter
from agentaudit.exceptions import AdapterError


class CommandAdapter(BaseAdapter):
    """A Command adapter to execute local scripts or command-line tools."""

    async def execute(self, input_text: str) -> tuple[str, list[str] | None, float]:
        if not self.config.command:
            raise AdapterError("Command Adapter configuration requires 'command' parameter.")

        cmd_str = self.config.command
        start_time = time.perf_counter()

        try:
            # Safely split command tokens to prevent shell execution vulnerabilities
            raw_tokens = shlex.split(cmd_str)
            if not raw_tokens:
                raise AdapterError("Command string split returned empty token list.")

            # Route input: either replace {input} placeholder in arguments, or pass via stdin
            if any("{input}" in token for token in raw_tokens):
                tokens = [t.replace("{input}", input_text) for t in raw_tokens]
                proc = await asyncio.create_subprocess_exec(
                    tokens[0],
                    *tokens[1:],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
            else:
                proc = await asyncio.create_subprocess_exec(
                    raw_tokens[0],
                    *raw_tokens[1:],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate(input=input_text.encode("utf-8"))

            latency_ms = (time.perf_counter() - start_time) * 1000.0

            if proc.returncode != 0:
                err_msg = stderr.decode("utf-8").strip()
                raise AdapterError(f"Command '{cmd_str}' failed (exit code {proc.returncode}): {err_msg}")

            output_raw = stdout.decode("utf-8").strip()

            # Attempt to parse output as a JSON dictionary to fetch structured fields (e.g. answer and sources)
            try:
                data = json.loads(output_raw)
                if isinstance(data, dict):
                    output_key = self.config.output_key or "output"
                    sources_key = self.config.sources_key or "sources"

                    # Fetch using nested path helpers if required, or direct mapping
                    def _get_value(d: dict[str, Any], key_path: str) -> Any:
                        parts = key_path.split(".")
                        val: Any = d
                        for part in parts:
                            if isinstance(val, dict) and part in val:
                                val = val[part]
                            else:
                                return None
                        return val

                    output_text = _get_value(data, output_key)
                    if output_text is None:
                        output_text = data.get(output_key, output_raw)

                    sources = _get_value(data, sources_key)
                    if sources is None:
                        sources = data.get(sources_key)

                    if sources is not None:
                        if isinstance(sources, str):
                            sources = [sources]
                        elif not isinstance(sources, list):
                            sources = []

                    return str(output_text), sources, latency_ms
            except json.JSONDecodeError:
                # If output is not JSON, we return the raw command string stdout
                pass

            return output_raw, None, latency_ms

        except Exception as e:
            if isinstance(e, AdapterError):
                raise
            raise AdapterError(f"Command adapter execution failed: {e}") from e
