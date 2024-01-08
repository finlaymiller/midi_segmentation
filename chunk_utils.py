"""Functions used to calculate MIDI file metrics"""

import math
import pretty_midi


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
    midi: pretty_midi.PrettyMIDI, bin_length: float = 1.0
) -> list[dict[str, int]]:
    """
    Calculate the total velocity of all notes for each time bin in a MIDI file.

    Parameters:
    midi (PrettyMIDI): The prettyMIDI container object for the MIDI file.
    bin_length (float): The length of time each bin should occupy. (default 1s)

    Returns:
    list: A list whose values are the total velocity and number of notes in that bin.
    """
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


def simultaneous_notes(
    midi: pretty_midi.PrettyMIDI, bin_length: float = 1.0
) -> list[int]:
    """
    Calculate the number of simultaneous notes being played each second in a MIDI file.

    Parameters:
    midi (PrettyMIDI): The prettyMIDI container object for the MIDI file.
    bin_length (float): The length of time each bin should occupy. (default 1s)

    Returns:
    list: A list whose values are the number of simultaneous notes being played in that second.
    """
    num_bins = int(math.ceil(midi.get_end_time() / bin_length))
    simultaneous_notes_counts = [0] * num_bins

    for instrument in midi.instruments:
        for note in instrument.notes:
            start_bin = int(note.start // bin_length)
            end_bin = int(note.end // bin_length)

            for bin in range(start_bin, min(end_bin + 1, num_bins)):
                simultaneous_notes_counts[bin] += 1

    return simultaneous_notes_counts
