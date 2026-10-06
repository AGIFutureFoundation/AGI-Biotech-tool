# XR and Hand Tracking

The workspace is WebXR: `immersive-vr` and `immersive-ar` from the same page that runs on a desktop. There
is no app to install and no store review.

## Input

| Input | How it works |
| --- | --- |
| **Hands** | `XRHand` joint poses. Pinch to grab a molecule, two-hand pinch to scale and rotate it, point to select a residue |
| **Controllers** | A ray with a trigger, for headsets without hand tracking or users who prefer it |
| **Wrist panel** | A small panel anchored to the left wrist, carrying status and the common actions, so the controls travel with you instead of floating where you left them |
| **Voice** | See [Voice and Agent Control](Voice-and-Agent-Control). In a headset your hands are holding a protein, and voice is what is left |
| **Mouse and keyboard** | The full interface, undiminished. The desktop path is not a degraded mode |

## Multi-user

Shared sessions put several people in the same scene with the same structure, each seeing the others' hands
and the pose they are manipulating. Presence and pose are synchronised; the molecular state is
authoritative on one peer so two people cannot dock the same ligand into two different answers.

## Environments

glTF scenes load as backgrounds, with automatic scaling so an imported scene arrives at a sane size
relative to a human. HDRI lighting comes from Poly Haven. A locomotion layer handles teleport and
smooth movement for scenes larger than the room.

This is less frivolous than it sounds: a reviewer who can hold a pose at arm's length in a room, rather
than rotating it with a mouse in a rectangle, catches geometry problems that a screenshot hides.

## Testing XR without a headset

`?emulate=quest3` renders the headset interface in a desktop browser — wrist panel, controller rays,
room-scale layout — driven by mouse and keyboard. Most of the XR work in this repository was built and
reviewed this way.

It is an emulator, so it proves layout and logic, not comfort. Frame timing, stereo convergence, and
whether the wrist panel is actually reachable are things only a headset tells you.

## Ray-Ban Meta and camera glasses

**Ray-Ban Meta glasses cannot render this workspace.** They have no display and no WebXR runtime. Any
claim that a 3D molecular viewer runs on them is false.

What they can do is audio: a microphone and speakers on your face. So the glasses path is a **voice
companion** — ask about the target you are working on, hear the answer, trigger a dock, be told the result
— with the visual workspace on a headset or a screen elsewhere. That is a genuinely useful mode for someone
at a bench with gloves on, and it is described as what it is rather than as "AR glasses support".

## Mobile

The page works on a phone: touch orbit and pinch zoom, a layout that reflows, and controls sized for a
thumb. A phone will not run the heaviest dynamics well, and it says so rather than quietly dropping frames.

## Verifying this page

XR cannot be verified offline — it needs a headset, or at minimum a browser and a bound port, neither of
which the current environment provides. What *is* verified offline is everything the XR layer calls into:
the structure parsing, the docking, the analysis and the tool registry. See [Testing](Testing).

This is the largest untested surface in the product. [Known Limits](Known-Limits) says so too.
