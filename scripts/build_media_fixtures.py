"""Build shared media development inputs offline; refuse to overwrite evidence."""
from observatory.fixtures import load_dataset
from observatory.media_fixtures import (
    MEDIA_DATA, IllustrationFixture, MediaDataset, NarrativeFixture, SpeechFixture, narrative_input,
)


def build():
    cases = {c.id: c for c in load_dataset().cases}
    # Human-readable semantic checklists are kept outside model input.
    narrative_rows = [
        ("S01", ["Hall described without discoveries", "Library door remains locked"], ["Key revealed or possessed", "Desk searched"]),
        ("S02", ["Key discovered but not collected", "Library door remains locked"], ["Key automatically carried", "Door unlocked"]),
        ("S04", ["Library key carried", "Library door remains locked"], ["Key remains available to collect", "Door unlocked"]),
        ("S05", ["Key already carried; no new collection"], ["Duplicate key", "New state change"]),
        ("S06", ["Unlocking failed; door remains locked", "Player lacks the key"], ["Hidden key location", "Door unlocked"]),
        ("S07", ["Library door unlocked", "Key retained", "Player remains in hall"], ["Automatic movement into library", "Key consumed"]),
        ("S10", ["Manual procedure learned", "Power remains off"], ["Fuse installed by reading", "Generator started"]),
        ("S11", ["Spare fuse discovered but not collected", "Toolbox lid closed after inspection"], ["Fuse automatically carried", "Toolbox left open"]),
        ("S12", ["Spare fuse carried", "Toolbox lid closed"], ["Fuse already installed", "Second fuse available"]),
        ("S14", ["Fuse installed and no longer carried", "Generator still stopped"], ["Fuse still in inventory", "Power automatically restored"]),
        ("S16", ["Generator running and power restored", "No ending chosen"], ["Beacon automatically aligned", "Rescue already sent"]),
        ("S18", ["Alignment rejected without manual knowledge", "Power remains on; beacon unaligned"], ["Procedure knowledge invented", "Alignment succeeded"]),
        ("S19", ["Beacon aligned", "Ending not yet chosen"], ["Rescue signal automatically sent", "Shelter automatically selected"]),
        ("S20-rescue", ["Rescue signal received by valley station", "Rescuers arrive after the storm", "Adventure ended"], ["Sheltered ending selected", "Further puzzle actions offered"]),
        ("S21", ["Shelter chosen until morning", "No rescue signal sent", "Adventure ended"], ["Rescue ending", "Manual or alignment claimed necessary"]),
        ("S22", ["Shelter rejected while power is off", "No ending chosen"], ["Sheltered ending", "Power restored"]),
    ]
    narratives = [NarrativeFixture(id=f"N{i:02}", source_case_id=source,
                    input=narrative_input(cases[source]), required_facts=required,
                    forbidden_claims=forbidden + ["Invented interactive objects, characters or unrequested actions"])
                  for i, (source, required, forbidden) in enumerate(narrative_rows, 1)]
    style = ("Restrained storybook digital painting, muted blue-grey and warm wood palette, "
             "diffuse daylight, square 512x512 establishing view, no people, no lettering, "
             "no visible portable quest items.")
    image_rows = [
        ("entrance_hall", ["Dusty desk", "Closed wooden library door", "High frosted glazing"],
         ["Visible key", "Readable door label", "Open library door"]),
        ("library", ["Bookshelves", "Reading stand with open manual", "Stairway"],
         ["Legible puzzle instructions", "Loose key or fuse"]),
        ("workshop", ["Workbench", "Closed toolbox", "Doorway"],
         ["Visible spare fuse", "Open toolbox or exposed contents"]),
        ("generator_room", ["Generator casing", "Wall conduit", "Diffuse daylight"],
         ["Readable indicators", "Sparks, smoke or motion implying running state", "Visible socket contents"]),
        ("telescope_chamber", ["Telescope", "Attached beacon housing", "Console", "Bench", "Enclosed dome"],
         ["Lit beacon", "Rescue party", "Open dome or open sky", "Readable coordinates"]),
    ]
    illustrations = []
    for room, required, forbidden in image_rows:
        forbidden = forbidden + ["People", "Lettering", "Visible portable quest items"]
        prompt = f"Observatory {room.replace('_', ' ')}. {style} Show: {'; '.join(required)}. Omit: {'; '.join(forbidden)}."
        illustrations.append(IllustrationFixture(id=room, prompt=prompt,
                             required_details=required, forbidden_details=forbidden))
    passages = [
        ("You stand in the entrance hall of the abandoned observatory. A dusty desk sits beside the library door.", ["observatory", "entrance hall", "library"]),
        ("You inspect the desk and discover a small library key. It remains on the desk until you collect it.", ["inspect", "library key"]),
        ("You pick up the library key. The library door is still locked.", ["library key", "locked"]),
        ("The key turns in the lock. You can now enter the library, and the key remains in your possession.", ["library", "possession"]),
        ("The instruction manual explains the emergency beacon. Replace the fuse, start the generator, and align the beacon.", ["instruction manual", "emergency beacon", "generator"]),
        ("Inside the workshop toolbox, you discover a spare fuse. After inspection, you close the toolbox lid again.", ["workshop", "toolbox", "spare fuse"]),
        ("You fit the spare fuse into the generator's socket. The fuse is installed, but the generator has not started.", ["generator's socket", "installed"]),
        ("The generator starts. Power is restored to the observatory, but the beacon still needs alignment.", ["generator", "observatory", "alignment"]),
        ("The valley station receives your signal. When the storm passes, rescuers arrive at the observatory.", ["valley station", "rescuers", "observatory"]),
        ("You shelter in the telescope chamber until morning. No rescue signal was sent. You leave when the storm clears.", ["telescope chamber", "rescue signal", "shelter"]),
    ]
    speech = [SpeechFixture(id=f"T{i:02}", text=text, focus_terms=terms)
              for i, (text, terms) in enumerate(passages, 1)]
    return MediaDataset(version="world-v2-media-development-v1", split="development",
        provenance="Assistant-authored from world_spec v2 and development_fixtures.md on 22 September 2026. Narrative outcomes reference development.json. No external story assets, human ratings or model outputs. Speech adapted for toolbox closure and both endings.",
        image_size=(512, 512), shared_style=style, narratives=narratives,
        illustrations=illustrations, speech=speech)


if __name__ == "__main__":
    dataset = build()
    with MEDIA_DATA.open("x", encoding="utf-8") as output:
        output.write(dataset.model_dump_json(indent=2) + "\n")
    print(f"Wrote {len(dataset.narratives)} narrative cases, five image briefs and ten speech passages; no inference.")
