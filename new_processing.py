import time
import pretty_midi
import wave
from pydub import AudioSegment
import tar_utilities
import random
import re

def find_actual_start_time(mid):
    start_time = 1e8
    for instrument in mid.instruments:
        for note in instrument.notes:
            if note.start < start_time:
                start_time = note.start

    return(start_time)

def subset_midi_segment(file_name,actual_start,actual_end):
    mid = pretty_midi.PrettyMIDI(file_name)
    # Adjust times based on actual time start of midi
    adjustment = find_actual_start_time(mid)
    start_adj = actual_start + adjustment
    end_adj = actual_end + adjustment
    final_start = 0
    final_end = actual_end - actual_start
    new_mid = pretty_midi.PrettyMIDI() # Create new midi object

    # Extract notes, pitch bends, and control changes and add to new midi object
    for instrument in mid.instruments:
        # Create new instrument to add to new midi object: 
        new_instrument = pretty_midi.Instrument(instrument.program, instrument.is_drum, pretty_midi.program_to_instrument_name(instrument.program))
        new_mid.instruments.append(new_instrument)

        # Add notes 
        for i in range(len(instrument.notes)): # For each note in the instrument... 
            note = instrument.notes[i]

            validity = (note.start < note.end and note.start < end_adj and note.end > start_adj)
            within_range = (note.start >= start_adj) and (note.end <= end_adj) and validity
            change_start = (note.start < start_adj) and (note.end <= end_adj) and validity
            change_end = (note.start >= start_adj) and (note.end > end_adj) and validity

            if within_range: # If it's within the range, 
                new_note = pretty_midi.Note(note.velocity, note.pitch, note.start - start_adj, note.end - start_adj)
                new_mid.instruments[-1].notes.append(new_note) # Add the note 

            elif change_start: # If the note starts before the range, 
                new_note = pretty_midi.Note(note.velocity, note.pitch, 0, note.end - start_adj) # Update start time
                new_mid.instruments[-1].notes.append(new_note) # Add the note 

            elif change_end: # If the note ends after the range, 
                new_note = pretty_midi.Note(note.velocity, note.pitch, note.start - start_adj, final_end) # Update start time
                new_mid.instruments[-1].notes.append(new_note) # Add the note 

        # Add pitch_bends
        for i in range(len(instrument.pitch_bends)): # For each note in the instrument... 
            pitch_bend = instrument.pitch_bends[i]
            if (pitch_bend.time > start_adj) and (pitch_bend.time < end_adj): # If it's within the range, 
                new_pitch_bend = pretty_midi.PitchBend(pitch_bend.pitch,pitch_bend.time - start_adj)
                new_mid.instruments[-1].pitch_bends.append(new_pitch_bend) # Add to our new midi 

        # Add control_changes
        for i in range(len(instrument.control_changes)): # For each note in the instrument... 
            control_change = instrument.control_changes[i]
            if (control_change.time > start_adj) and (control_change.time < end_adj): # If it's within the range, 
                new_control_change = pretty_midi.ControlChange(control_change.number,control_change.value,control_change.time - start_adj)
                new_mid.instruments[-1].control_changes.append(new_control_change) # Add to our new midi 

    # Extract time signature changes
    for time_sig in mid.time_signature_changes:
        if len(new_mid.time_signature_changes) < 1: # If this is the first time sig, add it
            new_time_sig = pretty_midi.TimeSignature(time_sig.numerator,time_sig.denominator,0) # Fix the start time if needed 
            new_mid.time_signature_changes.append(new_time_sig)

        elif time_sig.time <= start_adj: # If this is not the first, and we are still before the start time
            new_mid.time_signature_changes.pop() # Remove last item 
            new_time_sig = pretty_midi.TimeSignature(time_sig.numerator,time_sig.denominator,0) # Fix the start time if needed 
            new_mid.time_signature_changes.append(new_time_sig)

        elif time_sig.time < end_adj:
            new_time_sig = pretty_midi.TimeSignature(time_sig.numerator,time_sig.denominator,time_sig.time - start_adj) 
            new_mid.time_signature_changes.append(new_time_sig)

    # Extract key signature changes
    for key_sig in mid.key_signature_changes:
        if len(new_mid.key_signature_changes) < 1: # If this is the first key sig, add it
            new_key_sig = pretty_midi.KeySignature(key_sig.key_number,0) # Fix the start key if needed 
            new_mid.key_signature_changes.append(new_key_sig)

        elif key_sig.time <= start_adj: # If this is not the first, and we are still before the start key
            new_mid.key_signature_changes.pop() # Remove last item 
            new_key_sig = pretty_midi.KeySignature(key_sig.key_number,0) # Fix the start key if needed 
            new_mid.key_signature_changes.append(new_key_sig)

        elif key_sig.time < end_adj:
            new_key_sig = pretty_midi.KeySignature(key_sig.key_number,key_sig.time - start_adj) 
            new_mid.key_signature_changes.append(new_key_sig)

    return new_mid

def subset_audio_segment(file_path,actual_start,actual_end):
    # Convert secs to milsecs:
    actual_start = actual_start * 1000
    actual_end = actual_end * 1000

    sound = AudioSegment.from_file(file_path, format="wav")
    print(len(sound))
    trimmed_sound = sound[actual_start:actual_end]
    new_file_path = re.sub(r"\.wav",r"-001.wav", file_path)
    trimmed_sound.export(new_file_path, format="wav")