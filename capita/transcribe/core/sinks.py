import json
import os
import textwrap
from .models import TranscriptionEvent

class RealTimeJsonSink:
    """
    Progressively writes TranscriptionEvents to a JSON file.
    Requirement: No post-processing. Writes as events are emitted.
    """
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.file = None
        self.first_item = True

    def open(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.file = open(self.output_path, "w")
        self.file.write("[\n")
        self.file.flush()

    def emit(self, event: TranscriptionEvent):
        """Writes a single event to the file immediately."""
        if not self.file or not event.is_final or event.event_type != "transcript":
            return
        
        if not self.first_item:
            self.file.write(",\n")
        
        self.file.write("  " + json.dumps(event.to_dict()))
        self.file.flush()
        self.first_item = False

    def close(self):
        if self.file:
            self.file.write("\n]\n")
            self.file.close()
            self.file = None

class TerminalSink:
    """Renders TranscriptionEvents in a multi-column terminal layout."""
    def __init__(self, channels: int = 2):
        self.channels = channels
        self.last_printed_channel = None
        self.last_was_final = True
        self.last_line_count = 0
        
        # Colors
        self.COLOR_SPEAKER_1 = "\033[92m" # Green
        self.COLOR_SPEAKER_2 = "\033[93m" # Yellow
        self.COLOR_DRAFT = "\033[90m"    # Grey
        self.COLOR_RESET = "\033[0m"

    def emit(self, event: TranscriptionEvent):
        if event.event_type != "transcript":
            self._print_event(event)
            return

        # Smart overwrite logic for real-time typing effect
        if not self.last_was_final and self.last_printed_channel == event.speaker_id:
            for _ in range(self.last_line_count):
                print("\033[F\033[K", end="", flush=True)

        prefix = "" if event.is_final else "... "
        colors = [self.COLOR_SPEAKER_1, self.COLOR_SPEAKER_2, self.COLOR_SPEAKER_1, self.COLOR_SPEAKER_2]
        color = colors[(event.speaker_id - 1) % 4] if event.is_final else self.COLOR_DRAFT
        
        text = event.text
        if event.is_final:
            speaker_label = f"Speaker {event.speaker_id}"
            text = f"{speaker_label}: [{event.start_sec:05.1f}s] \"{text}\" [{event.end_sec:05.1f}s]"
        else:
            text = f"[{event.start_sec:05.1f}s] \"{text}\""

        colored_content = f"{color}{prefix}{text}{self.COLOR_RESET}"
        
        # Column formatting
        COL_WIDTH = 38
        COL_SPACING = 2
        offset_str = " " * ((event.speaker_id - 1) * (COL_WIDTH + COL_SPACING))
        
        wrapper = textwrap.TextWrapper(
            width=offset_str.__len__() + COL_WIDTH, 
            initial_indent=offset_str, 
            subsequent_indent=offset_str + " " * 4
        )
        wrapped = wrapper.fill(colored_content)
        print(wrapped, flush=True)

        self.last_was_final = event.is_final
        self.last_printed_channel = event.speaker_id
        self.last_line_count = len(wrapped.split("\n"))

    def _print_event(self, event: TranscriptionEvent):
        """Prints non-transcript markers (e.g. VAD, heartbeats) in a unified style."""
        color = "\033[90m" # Grey for all system events
        
        if event.event_type == "heartbeat":
            # Just a subtle activity dot
            print(f"{color}.{self.COLOR_RESET}", end="", flush=True)
            return

        # Handle VAD / Speech Activity Events
        event_label = "???"
        if "begin" in event.event_type: event_label = "TALKING"
        elif "end" in event.event_type: event_label = "SILENT"
        else: event_label = event.event_type.upper()

        content = f"<{event_label} @ {event.start_sec:05.1f}s>"
        
        # Consistent spacing for two-column layout
        COL_WIDTH = 38
        COL_SPACING = 2
        offset_str = " " * ((event.speaker_id - 1) * (COL_WIDTH + COL_SPACING))
        
        # Move to a new line for VAD events to avoid overwriting heartbeats
        print(f"\n{offset_str}{color}{content}{self.COLOR_RESET}", flush=True)
        
        self.last_was_final = True # Reset overwrite state
        self.last_line_count = 1
