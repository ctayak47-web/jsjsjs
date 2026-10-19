# Green theme reference validation

The supplied Chess.com Themes screenshot was cropped into per-square reference
examples for the six black piece types, six white piece types, and empty squares.
Multiple examples were retained for pawns, rooks, knights, and bishops.

A local descriptor sanity check on the same screenshot, using the same square
normalization and background-subtraction approach, classified all 32 occupied
starting-position squares correctly and recognized all 32 empty squares as
empty. This is a self-reference test: it verifies crop alignment and template
loading assumptions, but it is NOT an independent accuracy benchmark.

Before relying on live recognition, test captures from actual Chess.com games
at multiple board sizes and device display settings, including highlights,
legal-move dots, animations, dark mode, and flipped orientation. If confidence
is below threshold or the position sanity checks fail, the UI should ask the
user to correct the affected squares rather than pass a guessed position onward.
