#!/usr/bin/env python3
"""Runs every code example marked `test` in the docs against a real hardcharger-server.

    scripts/verify_examples.py [--page PATH_FRAGMENT] [--list] [--keep]

A fenced block takes part when its info string has the word `test`:

    ```python test
    ```console test profile=metrics
    ```sql test profile=rbac fresh

Options in the info string:

    profile=NAME   the server it runs against (tests/profiles.yaml; default `default`)
    server=none    needs no server; server=self: the block starts its own
    fresh          restart the server (and its database) before this block
    exit=N         the exit status the block must end with (default 0)
    background     run it in the background until the page ends (a server it starts)
    file=NAME      write the block to NAME in the page's directory instead of running it
    run=CMD        with file=: run CMD (in the page's directory) to check the file
    kind=repl      a console transcript of an interactive shell, driven with pexpect
    release        the block downloads a Hardcharger release (the installer, a tarball, the
                   Python package's server). While the releases are internal, CI has no token
                   for them, so the block gets a release mirror built from the server under
                   test (HARDCHARGER_INSTALL_MIRROR, HARDCHARGER_VERSION, the tarball in its
                   directory) and HARDCHARGER_SERVER_BINARY: it exercises the real installer
                   script and the real package, with this build instead of a download
    stop           stop the page's background processes (and run their cleanup) first
    cleanup=CMD    run CMD when the page ends or its background stops (`docker rm -f NAME`)

A block right after a tested block whose info string has the word `output` is that
block's expected output. `console` blocks carry their own: lines starting with `$ ` are
commands, the lines after each one its expected output. In expected output, `…` matches
any text within a line, and a line that is only `…` matches any number of lines.

Every page runs in a fresh directory (also its HOME), with a clean environment: PATH,
HOME, TMPDIR, LANG, the docs' example credentials, and what the profile adds. Nothing
from the caller's shell (credentials included) reaches an example.

Needs HARDCHARGER_DOCS_BIN_DIR: a directory with hardcharger-server and hardcharger.
Without it, or without what a profile needs (PostgreSQL, S3, Java, Go, Node), the run
FAILS: a missing prerequisite never turns into a skipped example. A run in which no
example ran fails too.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import os
import pathlib
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "src" / "content" / "docs"
PROFILES = ROOT / "tests" / "profiles.yaml"
FIXTURES = ROOT / "tests" / "fixtures"
MIRROR: pathlib.Path | None = None  # the release mirror, made on first use
VENV = pathlib.Path(os.environ.get("HARDCHARGER_DOCS_VENV", ROOT / ".venv"))  # Python with the drivers
FENCE = re.compile(r"^(?P<indent>\s*)(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
ELLIPSIS = "…"
PORT, HEALTH_PORT = 31337, 31338


class Failure(Exception):
    pass


@dataclasses.dataclass
class Block:
    page: pathlib.Path
    line: int
    lang: str
    meta: dict
    words: set
    code: str
    expected: str | None = None

    @property
    def where(self) -> str:
        return f"{self.page.relative_to(ROOT)}:{self.line}"


def parse_info(info: str) -> tuple[str, dict, set]:
    try:
        tokens = shlex.split(info)
    except ValueError:
        tokens = info.split()
    if not tokens:
        return "", {}, set()
    lang, meta, words = tokens[0], {}, set()
    for token in tokens[1:]:
        if "=" in token:
            key, _, value = token.partition("=")
            meta[key] = value
        else:
            words.add(token)
    return lang, meta, words


def extract(page: pathlib.Path) -> list[Block]:
    lines = page.read_text(encoding="utf-8").splitlines()
    blocks: list[Block] = []
    i = 0
    previous_tested: Block | None = None
    while i < len(lines):
        match = FENCE.match(lines[i])
        if not match:
            if lines[i].strip():
                previous_tested = None if not lines[i].strip().startswith(("<", "</")) else previous_tested
            i += 1
            continue
        fence, indent = match["fence"], len(match["indent"])
        lang, meta, words = parse_info(match["info"].strip())
        start = i + 1
        j = start
        while j < len(lines) and not re.match(r"^\s*" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$", lines[j]):
            j += 1
        body = "\n".join(line[indent:] if line[:indent].strip() == "" else line for line in lines[start:j])
        if "test" in words:
            block = Block(page=page, line=i + 1, lang=lang, meta=meta, words=words, code=body + "\n")
            blocks.append(block)
            previous_tested = block
        elif "output" in words and previous_tested is not None:
            previous_tested.expected = body + "\n"
            previous_tested = None
        else:
            previous_tested = None
        i = j + 1
    return blocks


ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def matches(expected: str, actual: str) -> bool:
    # Exact: output into pipes and files must carry no color codes (the interactive shell's
    # transcript is compared after its terminal codes are stripped, in repl()).
    want = [line.rstrip() for line in expected.rstrip("\n").splitlines()]
    have = [line.rstrip() for line in actual.rstrip("\n").splitlines()]

    def line_ok(pattern: str, text: str) -> bool:
        if ELLIPSIS not in pattern:
            return pattern == text
        regex = ".*".join(re.escape(part) for part in pattern.split(ELLIPSIS))
        return re.fullmatch(regex, text) is not None

    def walk(w: int, h: int) -> bool:
        if w == len(want):
            return h == len(have)
        if want[w] == ELLIPSIS:
            return any(walk(w + 1, k) for k in range(h, len(have) + 1))
        return h < len(have) and line_ok(want[w], have[h]) and walk(w + 1, h + 1)

    return walk(0, 0)


def free(port: int) -> bool:
    """Nothing is listening on the port (a socket in TIME_WAIT doesn't count)."""
    for _ in range(600):  # up to a minute: a server just stopped (ours or a neighbour's) may still be closing
        with socket.socket() as s:
            s.settimeout(0.2)
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return True
        time.sleep(0.1)
    return False


def wait_for(url: str, seconds: float, process: subprocess.Popen | None = None) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            raise Failure(f"the server exited with status {process.returncode} before {url} answered")
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise Failure(f"{url} did not answer within {seconds:.0f} s")


def need_env(name: str, why: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise Failure(f"{name} is not set ({why}); examples that need it fail, never skip")
    return value


class Page:
    def __init__(self, page: pathlib.Path, bin_dir: pathlib.Path, keep: bool):
        self.page = page
        self.bin_dir = bin_dir
        self.dir = pathlib.Path(tempfile.mkdtemp(prefix="hc-docs-"))
        self.keep = keep
        (self.dir / "home").mkdir()
        self.server: subprocess.Popen | None = None
        self.profile: str | None = None
        self.background: list[subprocess.Popen] = []
        self.cleanups: list[str] = []
        self.profiles = yaml.safe_load(PROFILES.read_text())
        self.env = {
            "PATH": os.pathsep.join([str(bin_dir), str(VENV / "bin"), str(ROOT / "tests" / "bin"),
                                     *os.environ.get("HARDCHARGER_DOCS_EXTRA_PATH", "").split(os.pathsep),
                                     "/opt/homebrew/bin", "/usr/local/go/bin", "/usr/local/bin", "/usr/bin", "/bin"]),
            "HOME": str(self.dir / "home"),
            "TMPDIR": str(self.dir),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "TERM": "dumb",
            "NO_COLOR": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_CONFIG_NOSYSTEM": "1",  # no system credential helper (macOS keychain prompts hang)
            "GIT_TERMINAL_PROMPT": "0",
        }
        for name in ("JAVA_HOME", "GOPATH", "GOMODCACHE", "GOCACHE", "GOFLAGS", "GOTOOLCHAIN",
                     "HARDCHARGER_DOCS_JDBC_JAR", "HARDCHARGER_DOCS_GO_REPLACE", "NODE_PATH", "DOCKER_CONFIG",
                     "DOCKER_HOST"):
            if os.environ.get(name):
                self.env[name] = os.environ[name]
        if (ROOT / "node_modules").is_dir():  # ESM imports resolve from the script's directory
            (self.dir / "node_modules").symlink_to(ROOT / "node_modules")
        for fixture in FIXTURES.glob("*"):
            if fixture.is_file():
                shutil.copy(fixture, self.dir / fixture.name)

    # -- servers -----------------------------------------------------------------------
    def start(self, name: str) -> None:
        self.stop()
        profile = self.profiles.get(name)
        if profile is None:
            raise Failure(f"unknown profile {name!r} (tests/profiles.yaml)")
        for port in (PORT, HEALTH_PORT, *profile.get("ports", [])):
            if not free(port):
                raise Failure(f"port {port} is in use: the examples use the documented default ports")
        for script in profile.get("setup", []):
            self.shell(script, what=f"profile {name} setup")
        for fixture in profile.get("needs", []):
            self.need(fixture)
        for command in profile.get("background", []):  # helpers the server needs at startup
            spec = command if isinstance(command, dict) else {"run": command}
            log = open(self.dir / "profile-background.log", "ab")
            helper = subprocess.Popen(args=["bash", "-c", self.expand(spec["run"])], cwd=self.dir, env=self.env,
                                      stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            self.background.append(helper)
            if "wait" in spec:
                wait_for(spec["wait"], 30, helper)
        env = dict(self.env)
        env.update({k: str(v) for k, v in profile.get("env", {}).items()})
        for key, var in profile.get("env_from", {}).items():
            env[key] = self.resolve(var)
        args = [str(self.bin_dir / "hardcharger-server")] + [self.expand(a) for a in profile.get("args", [])]
        log = open(self.dir / f"server-{name}.log", "ab")
        self.server = subprocess.Popen(args=args, cwd=self.dir, env=env, stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=True)
        self.profile = name
        try:
            wait_for(f"http://127.0.0.1:{HEALTH_PORT}/health", 30, self.server)
        except Failure as e:
            raise Failure(f"{e}\n--- server log ---\n{(self.dir / f'server-{name}.log').read_text()[-3000:]}")

    def stop(self) -> None:
        if self.server is not None and self.server.poll() is None:
            os.killpg(self.server.pid, signal.SIGKILL)
            self.server.wait()
        self.server, self.profile = None, None

    def expand(self, text: str) -> str:
        return text.replace("{dir}", str(self.dir))

    def resolve(self, var: str) -> str:
        if var == "pg_uri":
            return self.pg_database()
        return need_env(var, "a profile reads it")

    def pg_database(self) -> str:
        admin = need_env("HARDCHARGER_DOCS_PG_URI", "PostgreSQL for the access-control store")
        name = "docs_" + re.sub(r"[^a-z0-9]", "_", self.page.stem.lower())
        for sql in (f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)', f'CREATE DATABASE "{name}"'):
            subprocess.run(args=["psql", admin, "-v", "ON_ERROR_STOP=1", "-qc", sql], check=True,
                           capture_output=True, text=True)
        return admin.rsplit("/", 1)[0] + "/" + name

    def need(self, fixture: str) -> None:
        if fixture == "s3":
            need_env("HARDCHARGER_DOCS_S3_ENDPOINT", "the S3 gateway for the DuckLake examples")
        elif fixture == "postgres":
            need_env("HARDCHARGER_DOCS_PG_URI", "PostgreSQL")
        else:
            raise Failure(f"unknown fixture {fixture!r}")

    def shell(self, script: str, what: str) -> None:
        done = subprocess.run(args=["bash", "-euo", "pipefail", "-c", self.expand(script)], cwd=self.dir,
                              env=self.env, capture_output=True, text=True, timeout=120)
        if done.returncode != 0:
            raise Failure(f"{what} failed ({done.returncode}):\n{done.stdout}{done.stderr}")

    def stop_background(self) -> None:
        for process in self.background:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        self.background = []
        for command in self.cleanups:
            subprocess.run(args=["bash", "-c", command], cwd=self.dir, env=self.env, capture_output=True, timeout=120)
        self.cleanups = []

    def release(self) -> dict:
        """A release mirror (vX.Y.Z/hardcharger-<platform>.tar.gz and SHA256SUMS, as the
        releases lay them out) made from the server under test, shared by the whole run."""
        global MIRROR
        version = subprocess.run(args=[str(self.bin_dir / "hardcharger-server"), "--version"], capture_output=True,
                                 text=True, check=True).stdout.split()[-1]
        system, machine = os.uname().sysname, os.uname().machine
        platform = {("Linux", "x86_64"): "linux-amd64", ("Linux", "aarch64"): "linux-arm64",
                    ("Darwin", "arm64"): "macos-arm64"}[(system, machine)]
        name = f"hardcharger-{platform}"
        if MIRROR is None:
            MIRROR = pathlib.Path(tempfile.mkdtemp(prefix="hc-mirror-"))
            stage = MIRROR / "stage" / name
            shutil.copytree(self.bin_dir.parent, stage, symlinks=True) if (self.bin_dir.parent / "lib").is_dir() \
                else (stage / "bin").mkdir(parents=True)
            for binary in ("hardcharger-server", "hardcharger"):
                if not (stage / "bin" / binary).exists():
                    shutil.copy2(self.bin_dir / binary, stage / "bin" / binary)
            release = MIRROR / f"v{version}"
            release.mkdir()
            subprocess.run(args=["tar", "-czf", str(release / f"{name}.tar.gz"), "-C", str(stage.parent), name], check=True)
            digest = hashlib.sha256((release / f"{name}.tar.gz").read_bytes()).hexdigest()
            (release / "SHA256SUMS").write_text(f"{digest}  {name}.tar.gz\n")
        shutil.copy(MIRROR / f"v{version}" / f"{name}.tar.gz", self.dir / f"{name}.tar.gz")
        return {"HARDCHARGER_INSTALL_MIRROR": str(MIRROR), "HARDCHARGER_VERSION": version,
                "HARDCHARGER_SERVER_BINARY": str(self.bin_dir / "hardcharger-server")}

    def close(self) -> None:
        self.stop_background()
        self.stop()
        if not self.keep:
            shutil.rmtree(self.dir, ignore_errors=True)

    # -- blocks ------------------------------------------------------------------------
    def run(self, block: Block) -> None:
        if "stop" in block.words:
            self.stop_background()
        server = block.meta.get("server", "profile")
        if server == "profile":
            profile = block.meta.get("profile", "default")
            if self.profile != profile or "fresh" in block.words or self.server is None or self.server.poll() is not None:
                self.start(profile)
        elif server in ("none", "self"):
            if server == "self" or "fresh" in block.words:
                self.stop()
        else:
            raise Failure(f"{block.where}: server= must be none or self, not {server!r}")

        if "cleanup" in block.meta and "background" not in block.words:
            self.cleanups.append(block.meta["cleanup"])  # runs when the page ends, pass or fail
        if "file" in block.meta:
            target = self.dir / block.meta["file"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(block.code)
            if "run" in block.meta:
                self.execute(block, ["bash", "-euo", "pipefail", "-c", block.meta["run"]])
            return
        if block.meta.get("kind") == "repl":
            self.repl(block)
            return

        lang = block.lang
        if lang == "console":
            self.console(block)
        elif lang in ("bash", "sh", "shell"):
            self.execute(block, ["bash", "-euo", "pipefail", "-c", block.code])
        elif lang == "python":
            script = self.dir / f"example_{block.line}.py"
            script.write_text(block.code)
            self.execute(block, [str(VENV / "bin" / "python"), "-I", script.name])
        elif lang == "sql":
            script = self.dir / f"example_{block.line}.sql"
            script.write_text(block.code)
            user = block.meta.get("user", "hardcharger")
            self.execute(block, ["hardcharger", "--host", "localhost", "--username", user, "--quiet", "--bail",
                                 "--file", script.name],
                         extra={"HARDCHARGER_PASSWORD": block.meta.get("password", "change-me")})
        elif lang == "java":
            self.java(block)
        elif lang == "go":
            self.go(block)
        elif lang in ("js", "javascript", "mjs"):
            script = self.dir / f"example_{block.line}.mjs"
            script.write_text(block.code)
            self.execute(block, ["node", script.name])
        elif lang == "yaml" and block.meta.get("kind") == "server-config":
            self.server_config(block)
        else:
            raise Failure(f"{block.where}: no runner for ```{lang} test")

    def execute(self, block: Block, args: list[str], extra: dict | None = None, expected: str | None = None,
                stdin: str | None = None) -> str:
        env = dict(self.env)
        env.update(extra or {})
        if "release" in block.words:
            env.update(self.release())
        if "background" in block.words:
            if "cleanup" in block.meta:
                self.cleanups.append(block.meta["cleanup"])
            log = open(self.dir / f"background_{block.line}.log", "ab")
            process = subprocess.Popen(args=args, cwd=self.dir, env=env, stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            self.background.append(process)
            wait_for(block.meta.get("wait", f"http://127.0.0.1:{HEALTH_PORT}/health").replace("{dir}", str(self.dir)),
                     float(block.meta.get("timeout", 60)), process)
            return ""
        try:
            done = subprocess.run(args=args, cwd=self.dir, env=env, input=stdin, capture_output=True, text=True,
                                  timeout=float(block.meta.get("timeout", 180)))
        except subprocess.TimeoutExpired:
            raise Failure(f"{block.where}: timed out")
        # Programs are judged by what they print; shells (console, bash) by everything a
        # terminal would show.
        output = done.stdout if block.lang in ("python", "java", "go", "js", "javascript", "mjs") else done.stdout + done.stderr
        want_exit = int(block.meta.get("exit", 0))
        if done.returncode != want_exit:
            raise Failure(f"{block.where}: exit status {done.returncode}, expected {want_exit}\n{done.stdout}{done.stderr}")
        expected = expected if expected is not None else block.expected
        if expected is not None and not matches(expected, output):
            raise Failure(f"{block.where}: output differs\n--- expected ---\n{expected}--- actual ---\n{output}")
        return output

    def console(self, block: Block) -> None:
        commands: list[tuple[str, list[str]]] = []
        lines = block.code.rstrip("\n").splitlines()
        i = 0
        while i < len(lines):
            if not lines[i].startswith("$ "):
                raise Failure(f"{block.where}: console output before any $ command: {lines[i]!r}")
            command = [lines[i][2:]]
            heredoc = re.search(r"<<-?\s*'?([A-Za-z_]+)'?", lines[i])
            def incomplete(text: str) -> bool:  # a continued line, an open quote or loop
                if text.endswith("\\"):
                    return True
                check = subprocess.run(args=["bash", "-n", "-c", text], capture_output=True, text=True)
                return "unexpected end of file" in check.stderr or "unexpected EOF" in check.stderr
            while not heredoc and i + 1 < len(lines) and incomplete("\n".join(command)):
                i += 1
                command.append(lines[i])
                heredoc = heredoc or re.search(r"<<-?\s*'?([A-Za-z_]+)'?", lines[i])
            if heredoc:
                end = heredoc.group(1)
                while i + 1 < len(lines):
                    i += 1
                    command.append(lines[i])
                    if lines[i].strip() == end:
                        break
            i += 1
            output = []
            while i < len(lines) and not lines[i].startswith("$ "):
                output.append(lines[i])
                i += 1
            commands.append(("\n".join(command), output))
        # All commands run in one shell, as typed in one terminal: variables carry over. Markers
        # split the combined output back into each command's part.
        script = ["exec 2>&1"]
        for n, (command, _) in enumerate(commands):
            script += [f"printf '\\n__HC_BEGIN_{n}__\\n'", command, f"printf '\\n__HC_END_{n}__ %s\\n' \"$?\""]
        env = dict(self.env)
        if "release" in block.words:
            env.update(self.release())
        try:
            # No pipefail: an interactive shell doesn't have it, and a console block is a terminal.
            done = subprocess.run(args=["bash", "-c", "\n".join(script)], cwd=self.dir, env=env,
                                  capture_output=True, text=True, timeout=float(block.meta.get("timeout", 180)))
        except subprocess.TimeoutExpired:
            raise Failure(f"{block.where}: timed out")
        out = done.stdout
        want_exit = int(block.meta.get("exit", 0))
        for n, (command, expected) in enumerate(commands):
            m = re.search(rf"\n__HC_BEGIN_{n}__\n(.*?)\n__HC_END_{n}__ (\d+)\n", out, flags=re.S)
            if not m:
                raise Failure(f"{block.where}: `{command.splitlines()[0]}` did not finish\n{out}")
            output, status = m.group(1), int(m.group(2))
            if status != want_exit:
                raise Failure(f"{block.where}: `{command.splitlines()[0]}` exited {status}, expected {want_exit}\n{output}")
            if not matches("\n".join(expected) + "\n", output + "\n"):
                raise Failure(f"{block.where}: output of `{command.splitlines()[0]}` differs\n--- expected ---\n"
                              + "\n".join(expected) + f"\n--- actual ---\n{output}\n--- repr ---\n{output!r}")

    def repl(self, block: Block) -> None:
        """A transcript of the interactive shell: `$ command`, then prompts and what follows them.

        The shell runs in a pseudo-terminal; it colors its prompt and redraws typed input, so
        prompts are matched with any escape sequences around them, and each chunk of output is
        compared after the escape sequences and the echoed input are dropped."""
        import pexpect

        lines = block.code.rstrip("\n").splitlines()
        if not lines or not lines[0].startswith("$ "):
            raise Failure(f"{block.where}: a repl transcript starts with `$ command`")
        prompt_text = re.compile(block.meta.get("prompt", r"^[\w.]+> "))
        esc = r"(?:\x1b\[[0-9;?]*[A-Za-z])*"
        child = pexpect.spawn("bash", ["-c", lines[0][2:]], cwd=str(self.dir), env=self.env, encoding="utf-8",
                              timeout=30, dimensions=(50, 200))
        expected_chunks: list[list[str]] = [[]]
        actual_chunks: list[str] = []
        try:
            for line in lines[1:]:
                m = prompt_text.match(line)
                if line.startswith("Password:"):
                    child.expect("Password:")
                    child.sendline("change-me")
                elif m:
                    name = m.group(0)[:-2]  # the prompt without its "> "
                    child.expect(esc + re.escape(name) + esc + re.escape("> "))
                    actual_chunks.append(child.before)
                    expected_chunks.append([])
                    child.sendline(line[m.end():])
                else:
                    expected_chunks[-1].append(line)
            child.expect(pexpect.EOF)
            actual_chunks.append(child.before)
        except pexpect.exceptions.ExceptionPexpect as e:
            raise Failure(f"{block.where}: interactive session failed: {type(e).__name__}\n{ANSI.sub('', str(child.before))}")
        for n, (want, have) in enumerate(zip(expected_chunks, actual_chunks)):
            have_lines = [l for l in ANSI.sub("", have).replace("\r", "").splitlines() if l.strip()]
            if n > 0 and have_lines:
                have_lines = have_lines[1:]  # the echo of what was typed
            want_lines = [l for l in want if l.strip()]
            if want_lines and not matches("\n".join(want_lines) + "\n", "\n".join(have_lines) + "\n"):
                raise Failure(f"{block.where}: interactive output differs\n--- expected ---\n" + "\n".join(want_lines)
                              + "\n--- actual ---\n" + "\n".join(have_lines))

    def java(self, block: Block) -> None:
        jar = need_env("HARDCHARGER_DOCS_JDBC_JAR", "the standalone hardcharger-jdbc.jar for Java examples")
        code = block.code
        if "class " not in code:
            code = ("import java.sql.*;\nimport java.util.*;\n\npublic class Example {\n"
                    "  public static void main(String[] args) throws Exception {\n"
                    + "\n".join("    " + l for l in code.splitlines()) + "\n  }\n}\n")
            name = "Example"
        else:
            name = re.search(r"public\s+class\s+(\w+)", code).group(1)
        source = self.dir / "java" / f"{name}.java"
        source.parent.mkdir(exist_ok=True)
        source.write_text(code)
        self.execute(block, ["bash", "-euo", "pipefail", "-c",
                             f"javac -d java -cp {shlex.quote(jar)} java/{name}.java && "
                             f"java -cp {shlex.quote(jar)}{os.pathsep}java {name}"])

    def go(self, block: Block) -> None:
        # The example's imports resolve as a user's would: the gizmodata modules are fetched
        # from GitHub. They are internal until launch, so GOPRIVATE, and git reaches them with the
        # caller's git configuration and SSH agent (CI: read-only deploy keys). For local work,
        # HARDCHARGER_DOCS_GO_REPLACE="module=path,..." points modules at checkouts instead.
        module = self.dir / f"go_{block.line}"
        module.mkdir()
        (module / "main.go").write_text(block.code)
        replaces = [r for r in os.environ.get("HARDCHARGER_DOCS_GO_REPLACE", "").split(",") if "=" in r]
        edits = "".join(f" && go mod edit -replace {shlex.quote(r)}" for r in replaces)
        script = (f"cd {module.name} && go mod init example.com/docs >/dev/null 2>&1{edits} && "
                  f"go mod tidy && go run .")
        extra = {"GOPRIVATE": "github.com/gizmodata/*", "GOFLAGS": "-mod=mod",
                 "GIT_CONFIG_GLOBAL": os.environ.get("HARDCHARGER_DOCS_GIT_CONFIG",
                                                     str(pathlib.Path.home() / ".gitconfig"))}
        if os.environ.get("SSH_AUTH_SOCK"):
            extra["SSH_AUTH_SOCK"] = os.environ["SSH_AUTH_SOCK"]
        self.execute(block, ["bash", "-euo", "pipefail", "-c", script], extra=extra)

    def server_config(self, block: Block) -> None:
        self.stop()
        config = self.dir / block.meta.get("name", "hardcharger.yaml")
        config.write_text(block.code)
        args = [str(self.bin_dir / "hardcharger-server"), "--config", config.name, "--health-port", str(HEALTH_PORT)]
        env = dict(self.env, HARDCHARGER_ADMIN_PASSWORD="change-me")
        for path in re.findall(r"^\s*\w+:\s*(/\S+)\s*$", block.code, flags=re.M):
            raise Failure(f"{block.where}: a server-config example can't use absolute paths ({path}); "
                          f"use relative ones or a file= block")
        log = open(self.dir / "server-config.log", "ab")
        process = subprocess.Popen(args=args, cwd=self.dir, env=env, stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            wait_for(f"http://127.0.0.1:{HEALTH_PORT}/health", 30, process)
        except Failure as e:
            raise Failure(f"{block.where}: {e}\n{(self.dir / 'server-config.log').read_text()[-2000:]}")
        finally:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--page", action="append", default=[], help="only pages whose path contains this")
    parser.add_argument("--except", dest="except_", action="append", default=[],
                        help="leave out pages whose path contains this (local runs split across machines)")
    parser.add_argument("--list", action="store_true", help="list the tested blocks and exit")
    parser.add_argument("--keep", action="store_true", help="keep each page's directory")
    args = parser.parse_args()

    pages = sorted(p for p in DOCS.rglob("*.md*") if (not args.page or any(f in str(p) for f in args.page))
                   and not any(f in str(p) for f in args.except_))
    by_page = {p: extract(p) for p in pages}
    total = sum(len(b) for b in by_page.values())
    if args.list:
        for blocks in by_page.values():
            for b in blocks:
                print(f"{b.where}  {b.lang}  {' '.join(sorted(b.words))}  {b.meta}")
        print(f"{total} tested blocks")
        return 0
    if total == 0:
        print("no tested examples found: that is a failure, not a pass", file=sys.stderr)
        return 1
    try:
        bin_dir = pathlib.Path(need_env("HARDCHARGER_DOCS_BIN_DIR", "where hardcharger-server and hardcharger are")).resolve()
    except Failure as e:
        print(e, file=sys.stderr)
        return 1
    for name in ("hardcharger-server", "hardcharger"):
        if not (bin_dir / name).is_file():
            print(f"{bin_dir / name} does not exist", file=sys.stderr)
            return 1
    version = subprocess.run(args=[str(bin_dir / "hardcharger-server"), "--version"], capture_output=True, text=True)
    print(f"server: {version.stdout.strip()} ({bin_dir})")

    failures, ran = [], 0
    for page, blocks in by_page.items():
        if not blocks:
            continue
        runner = Page(page=page, bin_dir=bin_dir, keep=args.keep)
        print(f"== {page.relative_to(ROOT)} ({len(blocks)})", flush=True)
        try:
            for block in blocks:
                started = time.monotonic()
                try:
                    runner.run(block)
                    ran += 1
                    print(f"   ok   {block.where} {block.lang} ({time.monotonic() - started:.1f} s)", flush=True)
                except Failure as e:
                    failures.append(str(e))
                    print(f"   FAIL {block.where} {block.lang}\n{e}", flush=True)
                    break  # later blocks on a page build on earlier ones
        finally:
            runner.close()
            if args.keep:
                print(f"   kept {runner.dir}")
    print(f"\n{ran} of {total} examples passed, {len(failures)} failed")
    return 1 if failures or ran != total else 0


if __name__ == "__main__":
    sys.exit(main())
