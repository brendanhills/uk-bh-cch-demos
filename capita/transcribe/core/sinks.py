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
        
        # Speaker mapping for arbitrary IDs
        self.speaker_to_col = {} # {speaker_id: column_index}
        
        # History for Reflow (last 10 finalized blocks)
        self.history = [] # List of (event, wrapped_text, line_count)
        
        # Colors
        self.COLOR_SPEAKER_1 = "\033[92m" # Green
        self.COLOR_SPEAKER_2 = "\033[93m" # Yellow
        self.COLOR_DRAFT = "\033[90m"    # Grey
        self.COLOR_RESET = "\033[0m"

    def _get_col(self, speaker_id):
        if speaker_id not in self.speaker_to_col:
            self.speaker_to_col[speaker_id] = len(self.speaker_to_col)
        return self.speaker_to_col[speaker_id]

    def emit(self, event: TranscriptionEvent):
        if event.event_type != "transcript":
            self._print_event(event)
            return

        col_idx = self._get_col(event.speaker_id)

        # REFLOW LOGIC:
        # Check if this finalized event belongs BEFORE the last finalized event in history
        if event.is_final and self.history and event.start_sec < self.history[-1][0].start_sec:
            self._handle_reflow(event)
            return

        # Smart overwrite logic for real-time typing effect
        if not self.last_was_final and self.last_printed_channel == event.speaker_id:
            for _ in range(self.last_line_count):
                print("\033[F\033[K", end="", flush=True)

        prefix = "" if event.is_final else "... "
        colors = [self.COLOR_SPEAKER_1, self.COLOR_SPEAKER_2, self.COLOR_SPEAKER_1, self.COLOR_SPEAKER_2]
        color = colors[col_idx % 4] if event.is_final else self.COLOR_DRAFT
        
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
        offset_str = " " * (col_idx * (COL_WIDTH + COL_SPACING))
        
        wrapper = textwrap.TextWrapper(
            width=offset_str.__len__() + COL_WIDTH, 
            initial_indent=offset_str, 
            subsequent_indent=offset_str + " " * 4
        )
        wrapped = wrapper.fill(colored_content)
        print(wrapped, flush=True)

        if event.is_final:
            self.history.append((event, wrapped, len(wrapped.split("\n"))))
            if len(self.history) > 10: self.history.pop(0)
            self.last_was_final = True
        else:
            self.last_was_final = False
            
        self.last_printed_channel = event.speaker_id
        self.last_line_count = len(wrapped.split("\n"))

    def _handle_reflow(self, new_event):
        """Rewrites the terminal to insert a late-arriving event into history."""
        # Find insertion point
        insert_idx = len(self.history)
        for i, (old_ev, _, _) in enumerate(self.history):
            if new_event.start_sec < old_ev.start_sec:
                insert_idx = i
                break
        
        # Calculate how many lines to move up
        lines_to_clear = 0
        if not self.last_was_final:
            lines_to_clear += self.last_line_count
            
        for i in range(insert_idx, len(self.history)):
            lines_to_clear += self.history[i][2]
            
        # Move up and clear
        for _ in range(lines_to_clear):
            print("\033[F\033[K", end="", flush=True)
            
        # Wrap the new event
        col_idx = self._get_col(new_event.speaker_id)
        color = [self.COLOR_SPEAKER_1, self.COLOR_SPEAKER_2][col_idx % 2]
        text = f"Speaker {new_event.speaker_id}: [{new_event.start_sec:05.1f}s] \"{new_event.text}\" [{new_event.end_sec:05.1f}s]"
        colored_content = f"{color}{text}{self.COLOR_RESET}"
        
        offset_str = " " * (col_idx * (38 + 2))
        wrapper = textwrap.TextWrapper(width=offset_str.__len__() + 38, initial_indent=offset_str, subsequent_indent=offset_str + " " * 4)
        wrapped = wrapper.fill(colored_content)
        
        # Update history and reprint
        self.history.insert(insert_idx, (new_event, wrapped, len(wrapped.split("\n"))))
        if len(self.history) > 10: self.history.pop(0)
        
        for i in range(insert_idx, len(self.history)):
            print(self.history[i][1], flush=True)
            
        self.last_was_final = True
        self.last_line_count = self.history[-1][2]
        self.last_printed_channel = self.history[-1][0].speaker_id

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
        
        col_idx = self._get_col(event.speaker_id)
        offset_str = " " * (col_idx * (38 + 2))
        
        # Move to a new line for VAD events to avoid overwriting heartbeats
        print(f"\n{offset_str}{color}{content}{self.COLOR_RESET}", flush=True)
        
        self.last_was_final = True # Reset overwrite state
        self.last_line_count = 1
