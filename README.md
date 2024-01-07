# MIDI Segmentation Experiments
This repo holds my experiments using self-similarity matrices to segment MIDI files.

## TODOs

1. Clean up timing (no silence at start/end)
2. Experiment with different sampling rates for chromagrams
3. Formalize code to automatically calculate following metrics for each segment:
   1. id of parent sequence
   2. position in parent sequence
   3. pitch histogram
   4. tempo
   5. energy (some weighted combination of velocity, note freq., etc.)
   6. average note length
   7. number of notes
   8. total segment length
   9. note density
4. think about how to handle "overlapping" loops (see segments 1 and 2 in ableton screenshot below)

## Audio
I started by trying out audio-based segmentation, since that is much more common and well-documented.

### Resources
#### SSMNet
Run the model from *Self-similarity-based and Novelty-based Loss for Music Structure Analysis* by Geoffroy Peeters.
<img width="1008" alt="ssmnet" src="https://github.com/finlaymiller/ssm/assets/31632894/76d86472-5f81-4d0a-9191-6254c47269f1">

It generates both SSMs and novelty curves from raw audio (converted to log-mel spectrograms). See the [ssmsnet_chunk](ssmnet_chunk.ipynb) notebook for an example.

#### Müller Textbook
[*Fundamentals of Music Processing*](https://www.audiolabs-erlangen.de/resources/MIR/FMP/C0/C0.html) by Meinard Müller does a really great job of laying out how to use python to work with music.

### Experiments
I wanted to get some experience working with SSMs, and audio is much better documented than MIDI. I experimented with varying the SSM settings using an audio file of the Moonlight Sonata (see `media/moonight_sonata.wav`):

<img width="860" alt="ssm_audio" src="https://github.com/finlaymiller/ssm/assets/31632894/e84c4dd4-48ec-43cd-aea8-3cf09df63769">

Note: the novelty curves should have been inverted before plotting, but the spikes are still correctly aligned.

Code [here](ssm_audio.ipynb).

## MIDI
### Resources
I made a simple toy example file:
<img width="1207" alt="ssm_toy" src="https://github.com/finlaymiller/ssm/assets/31632894/afcdc3e8-c885-4e26-acdf-f9c45d045388">

the goal was to be able to segment it roughly like this:
<img width="1141" alt="ssm_toy_segmented" src="https://github.com/finlaymiller/ssm/assets/31632894/0ecbce83-6485-4eb6-961d-273838848b73">

though additional chunks between the chords would work as well.

### Experiments
#### Chroma
Lower sample rates looked promising:

![midi_chroma](https://github.com/finlaymiller/ssm/assets/31632894/b907f8c5-e1ad-4daf-a09e-5fe5143ad918)

Code [here](ssm_midi.ipynb).

#### Long Files
When working with long (>1 minute) files things are a bit harder to visually parse:
![pr_long](https://github.com/finlaymiller/ssm/assets/31632894/7c398ae6-f524-41ac-8643-e309797f640a)

So for now the best bet is probably to apply the config that worked best for shorter files and trust that. Result of segmenting `data/inputs/MIDI1` can be found in `data/outputs/MIDI1`. Once segmented we can load them into ableton (hold ⌘ while dragging all segments in to a midi channel to drop them into one track sequentially). 
<img width="1512" alt="live" src="https://github.com/finlaymiller/ssm/assets/31632894/c04cb445-7b52-4a5f-afca-b288c0a2a9c4">

Note the first segment (pictured in the second track). A segment was created while the first still had notes active, which, beyond being somewhat interesting that that would happen at all, removes our ability to seamlessly play segments sequentially.

Code [here](segment_midi.ipynb).

#### Piano Roll
Also possible to work with the raw piano roll. Started dialling in the SSM parameters but will need a bit more work to maintain keep the novelty curve and the SSM the same resolution.
![ssm_midi](https://github.com/finlaymiller/ssm/assets/31632894/d0bfb50d-d2b0-4885-98cf-de49e0e4f68f)
