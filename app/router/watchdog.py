"""Process group lifecycle and timeout watchdog for CLI harnesses."""

import asyncio
import os
import signal
import subprocess
import time
from typing import List, Optional

from app.router.schemas import WatchdogResult


class WatchdogTimeoutError(Exception):
    """Raised when a subprocess exceeds its execution deadline."""

    pass


class SubprocessWatchdog:
    """Spawns subprocesses in isolated process groups with graceful SIGTERM->SIGKILL escalation."""

    @staticmethod
    def _kill_group(pgid: int, sig: int) -> None:
        """Send signal to process group safely."""
        try:
            os.killpg(pgid, sig)
        except ProcessLookupError:
            pass

    @classmethod
    def run_sync(
        cls,
        cmd: List[str],
        timeout_sec: float = 60.0,
        grace_period_sec: float = 2.0,
        env: Optional[dict] = None,
    ) -> WatchdogResult:
        """Execute command synchronously in a dedicated process session."""
        start_time = time.time()
        # start_new_session=True runs os.setsid, creating a dedicated process group
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
            env=env,
        )
        pgid = proc.pid
        timed_out = False
        stdout = ""
        stderr = ""

        try:
            stdout, stderr = proc.communicate(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            timed_out = True
            # 1. Graceful SIGTERM to entire process group
            cls._kill_group(pgid, signal.SIGTERM)

            # 2. Await grace period
            try:
                stdout, stderr = proc.communicate(timeout=grace_period_sec)
            except subprocess.TimeoutExpired:
                pass

            # 3. Always escalate to SIGKILL to eliminate any grandchildren that ignored SIGTERM
            cls._kill_group(pgid, signal.SIGKILL)
            try:
                stdout, stderr = proc.communicate(timeout=1.0)
            except subprocess.TimeoutExpired:
                # Force close pipes if still held open by stubborn children
                if proc.stdout:
                    proc.stdout.close()
                if proc.stderr:
                    proc.stderr.close()
                proc.wait()

        duration_ms = int((time.time() - start_time) * 1000)

        if timed_out:
            raise WatchdogTimeoutError(
                f"Command {' '.join(cmd[:2])} timed out after {timeout_sec}s and process group {pgid} was terminated."
            )

        return WatchdogResult(
            stdout=stdout or "",
            stderr=stderr or "",
            exit_code=proc.returncode if proc.returncode is not None else 0,
            duration_ms=duration_ms,
            timed_out=timed_out,
        )

    @classmethod
    async def run_async(
        cls,
        cmd: List[str],
        timeout_sec: float = 60.0,
        grace_period_sec: float = 2.0,
        env: Optional[dict] = None,
    ) -> WatchdogResult:
        """Execute command asynchronously in a dedicated process session."""
        start_time = time.time()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
            env=env,
        )
        pgid = proc.pid

        try:
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout_sec,
                )
                duration_ms = int((time.time() - start_time) * 1000)
                return WatchdogResult(
                    stdout=stdout_bytes.decode("utf-8", errors="replace"),
                    stderr=stderr_bytes.decode("utf-8", errors="replace"),
                    exit_code=proc.returncode if proc.returncode is not None else 0,
                    duration_ms=duration_ms,
                    timed_out=False,
                )
            except (asyncio.TimeoutError, TimeoutError):
                # 1. Graceful SIGTERM
                cls._kill_group(pgid, signal.SIGTERM)

                # 2. Wait grace period
                try:
                    await asyncio.wait_for(proc.wait(), timeout=grace_period_sec)
                except (asyncio.TimeoutError, TimeoutError):
                    pass

                # 3. Always escalate to SIGKILL to eliminate any grandchildren that ignored SIGTERM
                cls._kill_group(pgid, signal.SIGKILL)
                try:
                    await asyncio.wait_for(proc.communicate(), timeout=1.0)
                except (asyncio.TimeoutError, TimeoutError, Exception):
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=0.5)
                    except Exception:
                        pass

                duration_ms = int((time.time() - start_time) * 1000)
                raise WatchdogTimeoutError(
                    f"Command {' '.join(cmd[:2])} timed out after {timeout_sec}s and process group {pgid} was terminated."
                )
        except asyncio.CancelledError:
            # Reaping on async cancellation
            cls._kill_group(pgid, signal.SIGKILL)
            try:
                await asyncio.wait_for(proc.wait(), timeout=0.5)
            except Exception:
                pass
            raise
