import os
import math
import pretty_midi
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from typing import Dict


def draw_midi(midi_file: str, labels: bool = False):
    plt.style.use("dark_background")

    midi = pretty_midi.PrettyMIDI(midi_file)

    _, ax = plt.subplots(figsize=(12, 4))

    for note in midi.instruments[0].notes:
        rect = patches.Rectangle(
            (note.start, note.pitch), note.end - note.start, 1, color="green"
        )
        ax.add_patch(rect)

    if labels:
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("MIDI Note")
    ax.set_yticks([])
    ax.set_title(f"{Path(midi_file).stem}")

    plt.box(False)
    plt.ylim(20, 108)  # MIDI note range for a piano
    plt.xlim(0, np.ceil(midi.instruments[0].notes[-1].end))
    return plt.gcf()

#################################  metrics  ###################################
################################  all in one  #################################


def all_metrics(midi: pretty_midi.PrettyMIDI, config) -> Dict:
    num_bins = int(math.ceil(midi.get_end_time() / config["bin_length"]))
    metrics = {
        "pitch_histogram": list(midi.get_pitch_class_histogram()),
        "tempo": midi.estimate_tempo(),
        "file_len": midi.get_end_time(),
        "note_count": sum(len(instrument.notes) for instrument in midi.instruments),
        "velocities": [{"total_velocity": 0, "count": 0} for _ in range(num_bins)],
        "lengths": [0.0] * num_bins,
        "energies": [0.0] * num_bins,
        "simultaneous_counts": [0] * num_bins,
        "key": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
        # "unique_notes": set()
    }

    notes_in_keys = {
        "C": ['C', 'D', 'E', 'F', 'G', 'A', 'B'], # C Major
        "C#": ['C#', 'D#', 'F', 'F#', 'G#', 'A#', 'C'], # C# (or Db) Major
        "D": ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'], # D Major
        "D#": ['D#', 'F', 'G', 'G#', 'A#', 'C', 'D'], # D# (or Eb) Major
        "E": ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'], # E Major
        "F": ['F', 'G', 'A', 'A#', 'C', 'D', 'E'], # F Major
        "F#": ['F#', 'G#', 'A#', 'B', 'C#', 'D#', 'F'], # F# (or Gb) Major
        "G": ['G', 'A', 'B', 'C', 'D', 'E', 'F#'], # G Major
        "G#": ['G#', 'A#', 'C', 'C#', 'D#', 'F', 'G'], # G# (or Ab) Major
        "A": ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'], # A Major
        "A#": ['A#', 'C', 'D', 'D#', 'F', 'G', 'A'], # A# (or Bb) Major
        "B": ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#'] # B Major
    }

    # metrics that are calculated from notes
    for instrument in midi.instruments:
        for note in instrument.notes:
            note_name = pretty_midi.note_number_to_name(note.pitch)[:-1]
            start_bin = int(note.start // config["bin_length"])
            end_bin = int(note.end // config["bin_length"])
            metrics["lengths"].append(note.end - note.start)
            # metrics["unique_notes"].add(pretty_midi.note_number_to_name(note.pitch)[:-1])


            for bin in range(start_bin, min(end_bin + 1, num_bins)):
                metrics["velocities"][bin]["total_velocity"] += note.velocity
                metrics["velocities"][bin]["count"] += 1
                metrics["simultaneous_counts"][bin] += 1

            # key
            for k in metrics["key"]:
                if note_name not in notes_in_keys[k]:
                    metrics["key"].remove(k)

    metrics["lengths"] = sum(metrics["lengths"]) / len(metrics["lengths"])

    # metrics that are calculated from other metrics
    metrics["energies"] = [
        config["w1"] * (vel["total_velocity"] / vel["count"])
        + config["w2"] * metrics["lengths"]
        for vel in metrics["velocities"]
        if vel["count"] > 0
    ]

    return metrics


############################  individual functions  ###########################


def average_note_length(midi: pretty_midi.PrettyMIDI) -> float:
    """
    Calculate the average length of notes in a MIDI file.

    Parameters:
    midi (PrettyMIDI): The prettyMIDI container object for the MIDI file.

    Returns:
    float: The average length of notes in the MIDI file in seconds. If the file
    has no notes, it returns 0.
    """
    note_lengths = []

    for instrument in midi.instruments:
        for note in instrument.notes:
            note_lengths.append(note.end - note.start)

    if note_lengths:
        average_length = sum(note_lengths) / len(note_lengths)
    else:
        average_length = 0.0

    return average_length


def total_number_of_notes(midi: pretty_midi.PrettyMIDI) -> int:
    """
    Calculate the total number of notes in a MIDI file.

    Parameters:
    midi (PrettyMIDI): The prettyMIDI container object for the MIDI file.

    Returns:
    int: The total number of notes in the MIDI file.
    """

    return sum(len(instrument.notes) for instrument in midi.instruments)


def total_velocity(
    midi: pretty_midi.PrettyMIDI, bin_length=None
) -> list[dict[str, int]]:
    """
    Calculate the total velocity of all notes for each time bin in a MIDI file.

    Parameters:
    midi (PrettyMIDI): The prettyMIDI container object for the MIDI file.
    bin_length (float): The length of time each bin should occupy. (default 1s)

    Returns:
    list: A list whose values are the total velocity and number of notes in that bin.
    """
    if bin_length == None:
        bin_length = midi.get_end_time()
    num_bins = int(math.ceil(midi.get_end_time() / bin_length))
    bin_velocities = [{"total_velocity": 0, "count": 0} for _ in range(num_bins)]

    for instrument in midi.instruments:
        for note in instrument.notes:
            start_bin = int(note.start // bin_length)
            end_bin = int(note.end // bin_length)

            for bin in range(start_bin, min(end_bin + 1, num_bins)):
                bin_velocities[bin]["total_velocity"] += note.velocity
                bin_velocities[bin]["count"] += 1

    return bin_velocities


def simultaneous_notes(midi: pretty_midi.PrettyMIDI, bin_length=None) -> list[int]:
    """
    Calculate the number of simultaneous notes being played each second in a MIDI file.

    Parameters:
    midi (PrettyMIDI): The prettyMIDI container object for the MIDI file.
    bin_length (float): The length of time each bin should occupy. (default 1s)

    Returns:
    list: A list whose values are the number of simultaneous notes being played in that second.
    """
    if bin_length == None:
        bin_length = midi.get_end_time()
    num_bins = int(math.ceil(midi.get_end_time() / bin_length))
    simultaneous_notes_counts = [0] * num_bins

    for instrument in midi.instruments:
        for note in instrument.notes:
            start_bin = int(note.start // bin_length)
            end_bin = int(note.end // bin_length)

            for bin in range(start_bin, min(end_bin + 1, num_bins)):
                simultaneous_notes_counts[bin] += 1

    return simultaneous_notes_counts


def energy(
    midi: pretty_midi.PrettyMIDI,
    w1: float = 0.5,
    w2: float = 0.5,
    bin_length=None,
) -> list[float]:
    """
    Calculate the number of simultaneous notes being played each second in a MIDI file.

    Parameters:
    midi (PrettyMIDI): The prettyMIDI container object for the MIDI file.
    bin_length (float): The length of time each bin should occupy. (default is clip length)

    Returns:
    list: A list whose values are the number of simultaneous notes being played in that second.
    """
    if bin_length == None:
        bin_length = midi.get_end_time()
    num_bins = int(math.ceil(midi.get_end_time() / bin_length))
    energies = [0.0] * num_bins
    v = total_velocity(midi, bin_length)
    l = average_note_length(midi)

    for instrument in midi.instruments:
        for note in instrument.notes:
            start_bin = int(note.start // bin_length)
            end_bin = int(note.end // bin_length)

            for bin in range(start_bin, min(end_bin + 1, num_bins)):
                energies[bin] += (
                    w1 * (v[bin]["total_velocity"] / v[bin]["count"]) + w2 * l
                )

    return energies


def norm(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))
