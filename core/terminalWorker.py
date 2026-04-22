from __future__ import annotations

import os,shlex,shutil,signal,subprocess,threading
from pathlib import Path
from core.dataTypes import *


class TerminalWorker(QObject):
    output = Signal(str)
    runningChanged = Signal(bool)
    cwdChanged = Signal(str)
    clearRequested = Signal()
    completionReady = Signal(str, list)
    commandFinished = Signal(int, bool)

    def __init__(self, adb_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self._cwd = os.getcwd()
        self._adb_path = adb_path
        self._process: Optional[subprocess.Popen[str]] = None
        self._process_lock = threading.RLock()
        self._was_cancelled = False
        self._shell_program, self._shell_args = self._resolve_shell()
        self._path_key = self._detect_path_key()

    @Slot(object)
    def setAdbPath(self, adb_path: Optional[str]) -> None:
        self._adb_path = adb_path

    @Slot(str)
    def executeCommand(self, command: str) -> None:
        command = command.rstrip()
        if not command:
            self.commandFinished.emit(0, False)
            return

        with self._process_lock:
            if self._process is not None:
                self.output.emit("A command is already running. Cancel it before starting another one.")
                self.commandFinished.emit(1, False)
                return

        if self._handle_builtin(command):
            return

        env = self._build_env()
        startupinfo = None
        creationflags = 0

        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)

        try:
            process = subprocess.Popen(
                [self._shell_program, *self._shell_args, command],
                cwd=self._cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=creationflags,
            )
        except FileNotFoundError:
            self.output.emit(f"Shell executable not found: {self._shell_program}")
            self.commandFinished.emit(127, False)
            return
        except Exception as error:
            self.output.emit(f"Failed to start command: {error}")
            self.commandFinished.emit(1, False)
            return

        with self._process_lock:
            self._process = process
            self._was_cancelled = False

        self.runningChanged.emit(True)
        self._start_stream_thread(process.stdout)
        self._start_stream_thread(process.stderr)
        threading.Thread(
            target=self._wait_for_process,
            args=(process,),
            daemon=True,
            name="TerminalWorkerWaiter",
        ).start()

    @Slot()
    def stopCurrent(self) -> None:
        with self._process_lock:
            process = self._process
            if process is None:
                return
            self._was_cancelled = True

        try:
            if os.name == "nt":
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                process.send_signal(signal.SIGINT)
        except Exception:
            pass

        threading.Thread(
            target=self._force_stop_if_needed,
            args=(process,),
            daemon=True,
            name="TerminalWorkerStopper",
        ).start()

    @Slot(str, int)
    def requestCompletion(self, text: str, cursor_position: int) -> None:
        completed_text, candidates = self._complete(text, cursor_position)
        self.completionReady.emit(completed_text, candidates)

    def _handle_builtin(self, command: str) -> bool:
        tokens = self._split_command(command)
        if not tokens:
            self.commandFinished.emit(0, False)
            return True

        command_name = tokens[0].lower()

        if command_name in {"clear", "cls"} and len(tokens) == 1:
            self.clearRequested.emit()
            self.commandFinished.emit(0, False)
            return True

        if command_name == "pwd" and len(tokens) == 1:
            self.output.emit(self._cwd)
            self.commandFinished.emit(0, False)
            return True

        if command_name != "cd":
            return False

        target = self._resolve_cd_target(tokens[1:])
        if target is None:
            self.output.emit("cd: invalid path")
            self.commandFinished.emit(1, False)
            return True

        if not os.path.isdir(target):
            self.output.emit(f"cd: no such directory: {target}")
            self.commandFinished.emit(1, False)
            return True

        self._cwd = os.path.abspath(target)
        self.cwdChanged.emit(self._cwd)
        self.commandFinished.emit(0, False)
        return True

    def _resolve_cd_target(self, args: list[str]) -> Optional[str]:
        if not args:
            return os.path.expanduser("~")

        normalized_args = [self._strip_quotes(arg) for arg in args if arg]
        if not normalized_args:
            return os.path.expanduser("~")

        if os.name == "nt" and normalized_args[0].lower() == "/d":
            normalized_args = normalized_args[1:]
            if not normalized_args:
                return self._cwd

        raw_target = " ".join(normalized_args).strip()
        if not raw_target:
            return self._cwd

        raw_target = os.path.expanduser(raw_target)

        if os.name == "nt" and len(raw_target) == 2 and raw_target[1] == ":":
            raw_target = raw_target + os.sep

        if os.path.isabs(raw_target):
            return raw_target

        return os.path.abspath(os.path.join(self._cwd, raw_target))

    def _wait_for_process(self, process: subprocess.Popen[str]) -> None:
        return_code = process.wait()
        was_cancelled = False

        with self._process_lock:
            if self._process is process:
                was_cancelled = self._was_cancelled
                self._process = None
                self._was_cancelled = False

        self.runningChanged.emit(False)
        self.commandFinished.emit(return_code, was_cancelled)

    def _force_stop_if_needed(self, process: subprocess.Popen[str]) -> None:
        try:
            process.wait(timeout=1.5)
            return
        except Exception:
            pass

        try:
            process.terminate()
            process.wait(timeout=1.5)
            return
        except Exception:
            pass

        try:
            process.kill()
        except Exception:
            pass

    def _start_stream_thread(self, stream) -> None:
        if stream is None:
            return

        threading.Thread(
            target=self._stream_output,
            args=(stream,),
            daemon=True,
            name="TerminalWorkerStream",
        ).start()

    def _stream_output(self, stream) -> None:
        try:
            for line in iter(stream.readline, ""):
                self.output.emit(line.rstrip("\r\n"))
        finally:
            try:
                stream.close()
            except Exception:
                pass

    def _resolve_shell(self) -> tuple[str, list[str]]:
        if os.name == "nt":
            for candidate in ("pwsh.exe", "powershell.exe"):
                shell = shutil.which(candidate)
                if shell:
                    return shell, ["-NoLogo", "-NoProfile", "-Command"]

            fallback = os.environ.get("COMSPEC") or shutil.which("cmd.exe") or "cmd.exe"
            return fallback, ["/d", "/s", "/c"]

        shell = os.environ.get("SHELL")
        if shell and shutil.which(shell):
            return shell, ["-lc"]

        for candidate in ("/bin/bash", "/bin/sh"):
            if os.path.exists(candidate):
                return candidate, ["-lc"]

        return "sh", ["-lc"]

    def _build_env(self) -> dict[str, str]:
        env = os.environ.copy()
        adb_directory = self._normalize_adb_directory(self._adb_path)
        if not adb_directory:
            return env

        existing_path = env.get(self._path_key, "")
        path_items = [item for item in existing_path.split(os.pathsep) if item]
        compare = str.casefold if os.name == "nt" else (lambda value: value)

        if compare(adb_directory) not in {compare(item) for item in path_items}:
            env[self._path_key] = adb_directory if not existing_path else adb_directory + os.pathsep + existing_path

        return env

    def _detect_path_key(self) -> str:
        for key in os.environ:
            if key.lower() == "path":
                return key
        return "Path" if os.name == "nt" else "PATH"

    def _normalize_adb_directory(self, adb_path: Optional[str]) -> Optional[str]:
        if not adb_path:
            return None

        candidate = Path(str(adb_path)).expanduser()
        try:
            candidate = candidate.resolve()
        except Exception:
            candidate = Path(os.path.abspath(str(candidate)))

        if candidate.is_file():
            return str(candidate.parent)
        if candidate.is_dir():
            return str(candidate)
        return None

    def _split_command(self, command: str) -> list[str]:
        try:
            return shlex.split(command, posix=os.name != "nt")
        except ValueError:
            return [item for item in command.strip().split() if item]

    def _strip_quotes(self, value: str) -> str:
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            return value[1:-1]
        return value

    def _complete(self, text: str, cursor_position: int) -> tuple[str, list[str]]:
        cursor_position = max(0, min(cursor_position, len(text)))
        before_cursor = text[:cursor_position]
        after_cursor = text[cursor_position:]
        token_start, tokens_before = self._locate_token(before_cursor)
        current_token = before_cursor[token_start:]
        is_first_token = len(tokens_before) == 0

        if is_first_token and not current_token.strip():
            return text, []

        if self._should_use_path_completion(is_first_token, current_token):
            replacement, candidates = self._complete_path_token(current_token)
        else:
            replacement, candidates = self._complete_command_token(current_token)

        if replacement == current_token:
            return text, candidates

        return before_cursor[:token_start] + replacement + after_cursor, candidates

    def _locate_token(self, text: str) -> tuple[int, list[str]]:
        tokens_before: list[str] = []
        token_start = 0
        segment_start = 0
        quote_char: Optional[str] = None

        for index, char in enumerate(text):
            if char in {"'", '"'}:
                if quote_char is None:
                    quote_char = char
                elif quote_char == char:
                    quote_char = None
                continue

            if char.isspace() and quote_char is None:
                token = text[segment_start:index]
                if token:
                    tokens_before.append(token)
                segment_start = index + 1
                token_start = segment_start

        token_start = segment_start
        return token_start, tokens_before

    def _should_use_path_completion(self, is_first_token: bool, token: str) -> bool:
        stripped_token = token.lstrip('"\'')
        separators = {os.sep}
        if os.altsep:
            separators.add(os.altsep)

        has_path_hint = any(separator in stripped_token for separator in separators)
        has_path_hint = has_path_hint or stripped_token.startswith((".", "~"))

        return not is_first_token or has_path_hint

    def _complete_command_token(self, token: str) -> tuple[str, list[str]]:
        stripped_token = token.lstrip('"\'')
        quote_prefix = token[: len(token) - len(stripped_token)]
        if not stripped_token:
            return token, []

        commands = sorted(self._iter_commands(), key=str.lower)
        matches = [command for command in commands if self._matches(command, stripped_token)]
        if not matches:
            return token, []

        common_prefix = self._common_prefix(matches)
        if len(matches) == 1:
            completed = matches[0]
            return quote_prefix + completed + " ", matches

        if len(common_prefix) > len(stripped_token):
            return quote_prefix + common_prefix, matches

        return token, matches

    def _complete_path_token(self, token: str) -> tuple[str, list[str]]:
        quote_char = token[0] if token[:1] in {"'", '"'} else ""
        raw_token = token[1:] if quote_char else token

        raw_directory, raw_prefix = self._split_path_fragment(raw_token)
        expanded_directory = os.path.expanduser(raw_directory) if raw_directory else ""

        if not expanded_directory:
            search_directory = self._cwd
        elif os.path.isabs(expanded_directory):
            search_directory = os.path.abspath(expanded_directory)
        else:
            search_directory = os.path.abspath(os.path.join(self._cwd, expanded_directory))

        try:
            entries = list(Path(search_directory).iterdir())
        except Exception:
            return token, []

        entries.sort(key=lambda item: (not item.is_dir(), item.name.lower()))
        matches = []
        for entry in entries:
            display_name = entry.name + (os.sep if entry.is_dir() else "")
            if self._matches(display_name, raw_prefix):
                matches.append(display_name)

        if not matches:
            return token, []

        if len(matches) == 1:
            match = matches[0]
            replacement = raw_directory + match
            if not match.endswith(os.sep):
                replacement += " "
            return self._quote_completed_path(replacement, quote_char), matches

        common_prefix = self._common_prefix(matches)
        if len(common_prefix) > len(raw_prefix):
            replacement = raw_directory + common_prefix
            return self._quote_completed_path(replacement, quote_char), matches

        return token, matches

    def _split_path_fragment(self, token: str) -> tuple[str, str]:
        last_separator_index = -1
        separators = [os.sep]
        if os.altsep:
            separators.append(os.altsep)

        for separator in separators:
            last_separator_index = max(last_separator_index, token.rfind(separator))

        if last_separator_index == -1:
            return "", token

        return token[: last_separator_index + 1], token[last_separator_index + 1 :]

    def _quote_completed_path(self, value: str, existing_quote: str) -> str:
        if existing_quote:
            return existing_quote + value

        if " " not in value:
            return value

        stripped_value = value.rstrip()
        suffix = value[len(stripped_value) :]
        return f'"{stripped_value}"{suffix}'

    def _iter_commands(self) -> Iterable[str]:
        env = self._build_env()
        path_value = env.get(self._path_key, "")
        seen: set[str] = set()
        compare = str.casefold if os.name == "nt" else (lambda value: value)

        if os.name == "nt":
            pathext = {
                extension.upper()
                for extension in env.get("PATHEXT", ".COM;.EXE;.BAT;.CMD").split(";")
                if extension
            }
        else:
            pathext = set()

        for raw_directory in path_value.split(os.pathsep):
            if not raw_directory:
                continue

            try:
                directory_entries = os.scandir(raw_directory)
            except OSError:
                continue

            with directory_entries as iterator:
                for entry in iterator:
                    if not entry.is_file():
                        continue

                    name = entry.name
                    command_name = name

                    if os.name == "nt":
                        stem, extension = os.path.splitext(name)
                        if extension.upper() not in pathext:
                            continue
                        command_name = stem
                    elif not os.access(entry.path, os.X_OK):
                        continue

                    dedupe_key = compare(command_name)
                    if dedupe_key in seen:
                        continue

                    seen.add(dedupe_key)
                    yield command_name

    def _matches(self, candidate: str, fragment: str) -> bool:
        if os.name == "nt":
            return candidate.lower().startswith(fragment.lower())
        return candidate.startswith(fragment)

    def _common_prefix(self, values: list[str]) -> str:
        if not values:
            return ""

        if os.name != "nt":
            return os.path.commonprefix(values)

        lowered_values = [value.lower() for value in values]
        lowered_prefix = os.path.commonprefix(lowered_values)
        return values[0][: len(lowered_prefix)]
