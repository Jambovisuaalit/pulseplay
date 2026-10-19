# M6: pilot measurement
User authorized: pilot and measure delivery time, corrections and useful client matches.
Implement active-work timers, explicit correction ledger, version/item-bound feedback and metrics panel.
Run a 30-delivery synthetic rehearsal with actual automation wall time; do not invent human time or customer feedback.
Keep onboarding separate; ignore open timers, duplicate exports and superseded versions in final-item denominator.
Use internal synthetic labels as fixture outcomes only, not precision or customer validation.
Test full existing suite + metrics regression + SQL/RLS + browser CI; PR based on #6.
