"""
Output Sinks for the Transcription Pipeline.
Handles UI rendering (Terminal) and persistent logging (JSON).
"""

import json
import os
import textwrap
from collections import defaultdict
from .models import TranscriptionEvent

class RealTimeJsonSink:
    """
    Progressively writes TranscriptionEvents to a temporary buffer and 
    finalizes a valid JSON array on close.
    """
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.file = None
        self._events = []

    def open(self):
        """Initializes the output directory."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        # We don't open the file yet, we buffer in memory for this demo
        # or we could use a .jsonl approach. For simplicity, we buffer objects.
        self._events = []

    def emit(self, event: TranscriptionEvent):
        """Buffers a finalized transcript event."""
        if not event.is_final or event.event_type != "transcript":
            return
        self._events.append(event.to_dict())

    def close(self):
        """Writes the buffered events as a valid JSON array."""
        try:
            with open(self.output_path, "w") as f:
                json.dump(self._events, f, indent=2)
        except Exception:
            pass

class TerminalSink:
    """
    Renders TranscriptionEvents in a high-fidelity, multi-column CLI layout.
    Supports real-time 'typing' effects and chronological reflow.
    """
    COL_WIDTH = 38
    COL_SPACING = 2

    def __init__(self):
        # UI State
        self.last_printed_channel = None
        self.last_was_final = True
        self.last_line_count = 0
        
        # Mapping for consistent column assignment
        self.speaker_to_col = {} # {speaker_id: column_index}
        
        # Track active speakers (per model if metadata exists) to drive subtle UI
        self.active_counts = defaultdict(int) 
        
        # History for Dynamic Reflow (last 10 finalized utterances)
        self.history = [] # List of (event, wrapped_text, line_count)
        
        # ANSI Escape Colors
        self.COLOR_SPEAKER_1 = "\033[92m" # Green
        self.COLOR_SPEAKER_2 = "\033[93m" # Yellow
        self.COLOR_DRAFT = "\033[90m"    # Grey (for Interims)
        self.COLOR_RESET = "\033[0m"

    def _get_col(self, speaker_id):
        """Maps an arbitrary speaker ID to a fixed UI column (0 or 1)."""
        if speaker_id not in self.speaker_to_col:
            # Prefer 1-indexed speaker IDs to their corresponding columns
            if isinstance(speaker_id, int) and 1 <= speaker_id <= 8:
                self.speaker_to_col[speaker_id] = speaker_id - 1
            else:
                self.speaker_to_col[speaker_id] = len(self.speaker_to_col)
        return self.speaker_to_col[speaker_id]

    def _format_event(self, event: TranscriptionEvent, col_idx: int, is_final: bool):
        """Helper to format a transcript event with correct columns and wrapping."""
        prefix = "" if is_final else "... "
        colors = [self.COLOR_SPEAKER_1, self.COLOR_SPEAKER_2]
        color = colors[col_idx % len(colors)] if is_final else self.COLOR_DRAFT
        
        if is_final:
            model_label = f"[{event.metadata['model']}] " if event.metadata and "model" in event.metadata else ""
            text = f"{model_label}Speaker {event.speaker_id}: [{event.start_sec:05.1f}s] \"{event.text}\" [{event.end_sec:05.1f}s]"
        else:
            text = f"[{event.start_sec:05.1f}s] \"{event.text}\""

        full_text = f"{prefix}{text}"
        offset_str = " " * (col_idx * (self.COL_WIDTH + self.COL_SPACING))
        
        # Wrap plain text first to avoid ANSI length issues
        wrapper = textwrap.TextWrapper(
            width=self.COL_WIDTH, 
            initial_indent="", 
            subsequent_indent="    "
        )
        lines = wrapper.wrap(full_text)
        
        colored_lines = [f"{offset_str}{color}{line}{self.COLOR_RESET}" for line in lines]
        return "\n".join(colored_lines)

    def emit(self, event: TranscriptionEvent):
        """Main rendering entry point."""
        if event.event_type != "transcript":
            self._print_marker(event)
            return

        col_idx = self._get_col(event.speaker_id)

        # 1. DYNAMIC REFLOW:
        # If a finalized event belongs BEFORE our most recent output, we must rewrite.
        if event.is_final and self.history and event.start_sec < self.history[-1][0].start_sec:
            self._handle_reflow(event)
            return

        # 2. OVERWRITE/NEWLINE LOGIC:
        if getattr(self, "last_was_inline", False):
            # If we were printing heartbeats, clear that line first
            print("\r\033[K", end="", flush=True)
            self.last_was_inline = False

        if not self.last_was_final:
            # Always clear the last interim line before printing anything new
            for _ in range(self.last_line_count):
                print("\033[F\033[K", end="", flush=True)

        # 3. FORMATTING:
        wrapped = self._format_event(event, col_idx, event.is_final)
        
        # Output to stdout
        print(wrapped, flush=True)

        # 4. UPDATE UI STATE:
        if event.is_final:
            self.history.append((event, wrapped, len(wrapped.split("\n"))))
            if len(self.history) > 50: self.history.pop(0)
            self.last_was_final = True
        else:
            self.last_was_final = False
            
        self.last_printed_channel = event.speaker_id
        self.last_line_count = len(wrapped.split("\n"))
        self.last_was_inline = False

    def _handle_reflow(self, new_event):
        """Surgically inserts a late-arriving event into the terminal history."""
        # Find chronological insertion point
        insert_idx = len(self.history)
        for i, (old_ev, _, _) in enumerate(self.history):
            if new_event.start_sec < old_ev.start_sec:
                insert_idx = i
                break
        
        # Calculate lines to rollback
        lines_to_clear = 0
        if not self.last_was_final:
            lines_to_clear += self.last_line_count
            
        for i in range(insert_idx, len(self.history)):
            lines_to_clear += self.history[i][2]
            
        # Execute rollback
        # 1. Clear current line (handles heartbeats/dots or cursor position)
        print("\r\033[K", end="", flush=True)
        
        # 2. Move up and clear history lines
        for _ in range(lines_to_clear):
            print("\033[F\033[K", end="", flush=True)
            
        # Re-render new event
        col_idx = self._get_col(new_event.speaker_id)
        wrapped = self._format_event(new_event, col_idx, True)
        
        # Update history
        self.history.insert(insert_idx, (new_event, wrapped, len(wrapped.split("\n"))))
        if len(self.history) > 50: self.history.pop(0)
        
        # Reprint timeline
        for i in range(insert_idx, len(self.history)):
            print(self.history[i][1], flush=True)
            
        self.last_was_final = True
        self.last_line_count = self.history[-1][2]
        self.last_printed_channel = self.history[-1][0].speaker_id
        self.last_was_inline = False

    def _print_marker(self, event: TranscriptionEvent):
        """Renders system markers (VAD, Heartbeats) in a unified, subtle style."""
        color = "\033[90m" # Grey
        
        # 1. Update Internal VAD State
        if "begin" in event.event_type:
            model_id = event.metadata.get("model", "default")
            self.active_counts[(event.speaker_id, model_id)] = 1
            return
        if "end" in event.event_type:
            model_id = event.metadata.get("model", "default")
            self.active_counts[(event.speaker_id, model_id)] = 0
            return

        # 2. Render Heartbeat
        if event.event_type == "heartbeat":
            is_any_talking = any(v > 0 for v in self.active_counts.values())
            char = "+" if is_any_talking else "."
            
            # Show heartbeat in all relevant columns
            col_idx = self._get_col(event.speaker_id)
            offset_str = " " * (col_idx * (self.COL_WIDTH + self.COL_SPACING))
            print(f"{offset_str}{color}{char}{self.COLOR_RESET}", end="", flush=True)
            self.last_was_inline = True
            return

        # Suppress all other marker types (verbose TALKING/SILENT lines)
